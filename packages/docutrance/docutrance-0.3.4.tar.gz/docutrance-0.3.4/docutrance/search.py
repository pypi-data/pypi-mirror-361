from copy import deepcopy
from sentence_transformers import SentenceTransformer
from typing import Dict, List
import spacy
import pandas as pd
from opensearchpy import OpenSearch

from docutrance.util import lemmatize, remove_stopwords


def preprocess_input(
        query_input: str,
        lemmatizer: spacy,
        encoder: SentenceTransformer=None) -> Dict[str, str]:
    """
    Lemmatizes and removes stopwords from the input query string.
    Returns original, lemmatized, and stripped (stopwords removed) versions.
    """
    if not query_input:
        return {}
    raw = query_input.strip()
    stripped = remove_stopwords(lemmatizer, raw)
    lemmatized = lemmatize(lemmatizer, stripped).replace('\n', ' ')
    
    preprocessed = {
        "raw": raw,
        "stripped": stripped,
        "lemmatized": lemmatized
    }
    if encoder:
        preprocessed.update({"embedding": encoder.encode(query_input)})
    return preprocessed

def compose_subquery(
        processed_input: Dict[str, str],
        subquery_kwargs: Dict
) -> Dict:
    """
    Composes a single OpenSearch subquery from processed input and subquery parameters.
    """
    kwargs = deepcopy(subquery_kwargs)
    possible_types = ["knn", "neural", "match", "match_phrase", "multi_match"]
    subquery_type = kwargs.pop("subquery_type")
    if subquery_type not in possible_types:
        raise ValueError(f"Not configured to produce {subquery_type} type subquery. Please select one of {possible_types}")

    if subquery_type == 'knn':
        input_key = 'vector'
    elif subquery_type == 'neural':
        input_key = 'query_text'
    else:
        input_key = 'query'

    input_value = processed_input[kwargs.pop("input_type")]
    input = {input_key: input_value}

    if subquery_type == "multi_match":
        subquery = {subquery_type: {**input, **kwargs}}
    else:
        field = kwargs.pop("field")
        subquery = {subquery_type: {field: {**input, **kwargs}}}
    
    return subquery

def compose_subqueries(
        processed_input: Dict[str, str],
        all_subquery_kwargs: List[Dict]
) -> List[Dict]:
    """
    Constructs a list of subqueries based on input and individual subquery parameters.
    """
    subqueries = [compose_subquery(processed_input, kwargs) for kwargs in all_subquery_kwargs] if processed_input else []
    if len(subqueries) ==1:
        subqueries = subqueries[0]
    return subqueries

def compose_bool_query(
        should: List[Dict] = [],
        must: List[Dict] = [],
        must_not: List[Dict] = [],
        filter: List[Dict] = []
) -> Dict:
    """
    Builds a standard boolean query using 'should' and 'filter' clauses.
    """
    query_body = {
        "query": {
            "bool": {}
        }
    }
    if should:
        query_body["query"]["bool"]["should"] = should
    if must:
        query_body["query"]["bool"]["must"] = must
    if must_not:
        query_body["query"]["bool"]["must_not"] = must_not
    if filter:
        query_body["query"]["bool"]["filter"] = filter
    
    return query_body

def compose_hybrid_query(
    subqueries: List[Dict],
    filter: List[Dict] = []
) -> Dict:
    """
    Builds a hybrid query with optional post-filter clauses.
    """
    query_body = {
        "query": {
            "hybrid": {
                "queries": subqueries
            }
        }
    }
    if filter:
        query_body["post_filter"] = {"bool": {"must": filter}}
    
    return query_body


def compose_sort() -> Dict:
    """
    Returns default sort configuration: by relevance score (desc), then order (asc).
    """
    return {
        "sort": [
            {"_score": {"order": "desc"}},
            {"volume": {"order": "asc"}},
            {"order": {"order": "asc"}}
        ]
    }

def compose_query_body(type_: str, **kwargs) -> Dict:
    """Compose an OpenSearch query body based on query type and input."""

    query_input = kwargs.get('query_input')
    processed_input = kwargs.get('processed_input')


    if query_input is None and processed_input is None:
        query_body = {"query": {"match_all": {}}}
    else:
        if type_ not in ['hybrid', 'bool']:
            raise ValueError("Must input query type." if not type_ else f"{type_} type query is not supported. Choose 'bool' or 'hybrid'")
        
        if not processed_input and query_input:
            processed_input = preprocess_input(
                query_input,
                kwargs.pop('lemmatizer', None),
                kwargs.pop('model', None)
            )

        subqueries = compose_subqueries(processed_input, kwargs.get('subqueries'))

        if type_ == 'bool':
            query_body = compose_bool_query(
                should=subqueries,
                must=kwargs.get('must', []),
                must_not=kwargs.get('must_not', []),
                filter=kwargs.get('filter', [])
            )
        else:
            query_body = compose_hybrid_query(
                subqueries=subqueries,
                filter=kwargs.get('filter', [])
            )
    
    for key in ['size', 'highlight']:
        value = kwargs.get(key)
        if value is not None:
            query_body[key] = value

    return query_body

def post_process_response(
        response: dict,
        k: int=60,
        column_map: dict=None,
        agg_map: dict=None,
        weight: float=1.0
):
    """Aggregate and rerank OpenSearch response hits into a grouped DataFrame."""
    agg_map = agg_map or {'_score': 'sum'}
    rows = []
    hits = response["hits"]["hits"]
    if not hits:
        return pd.DataFrame()

    for hit in hits:
        row = hit['_source'].copy()
        row['_id'] = hit['_id']
        row['_score'] = hit['_score']
        if 'highlight' in hit.keys():
            for column in hit['highlight']:
                row[f'{column}_highlight'] =hit['highlight'][column]
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if column_map:
        df.rename(columns=column_map, inplace=True)

    agg_map = {k:v for k,v in agg_map.items() if k in df.columns}
    grouped = df.groupby('document_id').agg(agg_map).reset_index()
    grouped['rank'] = grouped._score.rank(method='first', ascending=False)
    grouped['rff'] = weight / (k + grouped["rank"])
    grouped.drop(columns='rank', inplace=True)
    return grouped

def select_highlights(row):
    """Select top highlights from available highlight fields in a result row."""
    select_ = lambda column: row[column][:2] if column in row.keys() else []

    keyword = select_('keyword_highlight')
    semantic = select_('semantic_highlight')
    highlights = keyword + semantic
    return highlights[:3]

def combine_responses(
        responses: list[pd.DataFrame],
        document_df: pd.DataFrame
):
    """Merge multiple reranked responses and enrich with document metadata."""
    df = pd.concat(responses)
    highlight_columns = [col for col in df.columns if 'highlight' in col]

    for col in highlight_columns:
        df[col] = df[col].apply(lambda x: x if isinstance(x, list) else [])
    agg_map = {**{'rff': 'sum'}, **{c: 'sum' for c in highlight_columns}}

    df = df.groupby('document_id').agg(agg_map)
    df['rank'] = df.rff.rank(method='first', ascending=False)
    df = df.drop(columns='rff').sort_values('rank').reset_index()
    df['highlights'] = df.apply(lambda x: select_highlights(x), axis=1)

    return df.merge(document_df, how='left', on='document_id')

def hybrid_search_pipeline(
    document_df: pd.DataFrame,
    processed_input: dict,
    client: OpenSearch,
    jobs: list[tuple],
    must: list[dict]=None,
    max_size: int = 50
):
    """Run hybrid search queries over multiple indices and combine ranked results."""
    responses = []

    if processed_input == {}:
        if must:
            fields, values = zip(*[
                (field, vals)
                for condition in must
                for field, vals in condition["terms"].items()
            ])
            
            for field, val in zip(fields, values):
                if pd.api.types.is_object_dtype(document_df[field]) and document_df[field].apply(lambda x: isinstance(x, list)).any():
                    # Column contains lists: check if any item in the list is in val
                    document_df = document_df[document_df[field].apply(lambda x: any(item in val for item in x))]
                else:
                    # Scalar column
                    document_df = document_df[document_df[field].isin(val)]

        return document_df

    for i, job in enumerate(jobs):
        kwargs, index, column_map, agg_map, weight = job
        body = compose_query_body(
            **kwargs,
            must=must,
            processed_input=processed_input
        )
        response = client.search(body=body, index=index, size=200)

        df = post_process_response(response, column_map=column_map, agg_map=agg_map, weight=weight)
        responses.append(df)

    ranked = combine_responses(responses, document_df).head(max_size)
    return ranked
