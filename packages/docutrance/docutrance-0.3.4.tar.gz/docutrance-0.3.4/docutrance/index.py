from bs4 import BeautifulSoup
from deepdiff import DeepDiff
import fitz
from opensearchpy import OpenSearch
import os
import pandas as pd
from pathlib import Path
import requests
from sentence_transformers import SentenceTransformer
import spacy
from typing import List, Callable
from tqdm import tqdm
from urllib.parse import urlparse

from docutrance.util import (
    lemmatize,
    load_text
)

def get_wikipedia_content(url: str) -> dict:
    """Fetch and parse Wikipedia page content."""
    title = urlparse(url).path.split("/wiki/")[-1]
    endpoint = f"https://en.wikipedia.org/api/rest_v1/page/html/{title}"
    headers = {"User-Agent": "WikiScraperBot/1.0"}

    response = requests.get(endpoint, headers=headers)
    if response.status_code != 200:
        print(f"[Error] Failed to fetch '{title}': {response.status_code}")
        return None

    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    paragraphs = soup.find_all("p")
    body = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

    return {
        "title": soup.title.get_text() if soup.title else title.replace("_", " "),
        "body": body
    }

def get_title_and_author(file: Path) -> dict:
    """Extract title and author from PDF metadata."""
    doc = fitz.open(file)
    metadata = doc.metadata
    return {
        "title": metadata["title"],
        "author": metadata["author"].split(', ')
    }

def get_body(file: Path) -> dict:
    """Extract full text body from a file."""
    return {
        "body": load_text(file)
    }

def parse_file_name(file: Path) -> dict:
    """Parse metadata from structured file name."""
    parts = file.stem.split('-')
    volume = int(parts[0][-2:])
    order = int(parts[1])
    section = int(parts[2][-2:])
    chapter = (
        "Introduction" if parts[3] == 'Intro' else
        "References" if parts[3] == "References" else
        f"Chapter {int(parts[3][-2:])}"
    )
    return {
        "volume": volume,
        "order": order,
        "section": section,
        "chapter": chapter,
        "document_id": f"{str(volume).zfill(2)}-{str(order).zfill(3)}"
    }

def init_document_dataframe(
    files: List[Path],
    field_fns: List[Callable],
    output_path: str,
    restart: bool = False
) -> pd.DataFrame:
    """Create or load a document metadata index."""
    if os.path.exists(output_path) and not restart:
        df = pd.read_parquet(output_path)
        print(f"Loaded index dataframe from {output_path}")
        return df

    rows = []
    for file in tqdm(files, desc='Building index dataframe'):
        row = {"file": file.stem}
        for fn in field_fns:
            row.update(fn(file))
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_parquet(output_path)
    print(f"Saved index dataframe to {output_path}")
    return df

def preprocess_document_dataframe(
    document_df: pd.DataFrame,
    output_path: str,
    column_mappings: dict = None,
    restart: bool=False
) -> pd.DataFrame:
    """Apply preprocessing functions to specified columns if not already present."""

    df = document_df

    if not column_mappings:
        return df
    
    if all(column in df.columns for column in column_mappings) and not restart:
        print("Index dataframe has already been preprocessed")
        return df

    for column, mapping in column_mappings.items():
        if column not in df.columns:
            source_col = mapping.get("source")
            preprocess_fn = mapping.get("function")

            if source_col not in df.columns:
                raise ValueError(f"Source column '{source_col}' not found in DataFrame.")

            df[column] = df[source_col].apply(preprocess_fn)
    
    print(f"Preprocessed index dataframe. Saved to {output_path}")
    return df

def build_document_dataframe(
    files: list[Path],
    field_fns: List[Callable],
    output_path: str,
    column_mappings: dict=None,
    restart: bool=False
):
    """Build and optionally preprocess a document DataFrame from files."""
    df = init_document_dataframe(files, field_fns, output_path, restart=restart)
    df = preprocess_document_dataframe(df, output_path, column_mappings=column_mappings, restart=restart)
    return df

def get_paragraphs(text, min_length=8):
    """Split text into cleaned paragraphs of minimum length."""

    paragraphs = text.split('\n\n')
    paragraphs = [p.replace('\n', ' ').strip() for p in paragraphs if not p.endswith('**')]
   
    for character in ['_', '*']:
        paragraphs = [p.replace(character, '') for p in paragraphs]
    
    paragraphs = [p for p in paragraphs if len(p.split()) >= min_length]
    return paragraphs

def get_sentence_boundaries(
        paragraph: str,
        model: spacy
):
    """Return sentence boundary character offsets using spaCy."""
    doc = model(paragraph)
    sentence_boundaries = [(sent.start_char, sent.end_char) for sent in doc.sents]
    return sentence_boundaries

def get_segment_boundary(
        offset_mapping: list[tuple]
):
    """Get start and stop character offsets for a segment."""
    return offset_mapping[1][0], offset_mapping[-2][1]

def get_segment_boundaries(
        section: str,
        model: SentenceTransformer,
        max_length: int=128,
        stride: int=96
        ):
    """Return list of segment boundaries based on tokenizer offset mappings."""
    tokenizer = model.tokenizer
    inputs = tokenizer(
        section,
        truncation=True,
        return_overflowing_tokens=True,
        max_length=max_length,
        stride=stride,
        return_attention_mask=False,
        return_token_type_ids=False,
        return_offsets_mapping=True
        )
    segment_boundaries = [get_segment_boundary(mapping) for mapping in inputs["offset_mapping"]]
    return segment_boundaries

def smooth_segment_boundaries(row):
    """Adjust segment boundaries to align with nearest sentence boundaries and deduplicate."""
    smoothed = []
    segments = row['segment_boundaries']
    sentences = row['sentence_boundaries']

    if not segments or not sentences:
        return []

    starts = [start for start, _ in sentences]
    stops = [stop for _, stop in sentences]

    for seg_start, seg_stop in segments:
        # Find the closest sentence start ≥ seg_start
        candidate_starts = [x for x in starts if x >= seg_start]
        new_start = min(candidate_starts) if candidate_starts else starts[-1]

        # Find the closest sentence stop ≤ seg_stop
        candidate_stops = [x for x in stops if x <= seg_stop]
        new_stop = max(candidate_stops) if candidate_stops else stops[0]

        smoothed.append((new_start, new_stop))

    # --- Deduplicate by start or end, keeping the pair with the largest span
    # Convert to DataFrame for convenience
    df = pd.DataFrame(smoothed, columns=["start", "stop"])
    df["span"] = df["stop"] - df["start"]

    # Keep max span per start
    df = df.sort_values("span", ascending=False).drop_duplicates(subset=["start"], keep="first")
    # Keep max span per stop
    df = df.sort_values("span", ascending=False).drop_duplicates(subset=["stop"], keep="first")

    df.sort_values('start', inplace=True)
    return list(df[["start", "stop"]].itertuples(index=False, name=None))


def build_segment_dataframe(
        document_df: pd.DataFrame,
        spacy_model: spacy,
        sentence_model: SentenceTransformer
):
    """Split documents into segments, align with sentence boundaries, and embed."""
    # Enable tqdm progress bars in pandas
    tqdm.pandas()

    segment_df = document_df[['document_id', 'body']].copy()

    # Apply get_sections with a progress bar
    print('Splitting documents into paragraphs. . .')
    segment_df['paragraph'] = segment_df['body'].progress_apply(lambda x: get_paragraphs(x))
    segment_df = segment_df.explode('paragraph').dropna(subset=['paragraph']).reset_index(drop=True)

    print("Getting sentence boundaries. . .")
    segment_df['sentence_boundaries'] = segment_df.paragraph.progress_apply(lambda x: get_sentence_boundaries(x, spacy_model))

    print("Getting segment boundaries. . ." )
    segment_df['segment_boundaries'] = segment_df.paragraph.progress_apply(lambda x: get_segment_boundaries(x, sentence_model))
    
    print("Smoothing segment boundaries. . .")
    segment_df['smoothed_boundaries'] = segment_df.progress_apply(lambda x: smooth_segment_boundaries(x), axis=1)

    print("Extracting segments. . .")
    segment_df['segment'] = segment_df.progress_apply(lambda x: [x.paragraph[b[0]: b[1]] for b in x.smoothed_boundaries], axis=1)

    print("Embedding segments. . .")
    segment_df = segment_df[['document_id', 'segment']].explode('segment').reset_index(drop=True)
    segment_df['segment_embedding'] = segment_df.segment.progress_apply(lambda x: sentence_model.encode(x))

    print("Assigning segment ids. . .")
    segment_df['segment_index'] = segment_df.groupby('document_id').cumcount()
    segment_df['segment_id'] = segment_df.progress_apply(
        lambda row: f"{row['document_id']}-{str(row['segment_index']).zfill(4)}",
        axis=1
    )


    return segment_df[['segment_id', 'document_id', 'segment', 'segment_embedding']].reset_index(drop=True)

def is_index_different(
    client: OpenSearch,
    index_name: str,
    index_body: dict
) -> bool:
    """Check if an OpenSearch index differs from the expected settings and mappings."""

    old_settings = client.indices.get_settings(index=index_name)[index_name]["settings"]["index"]
    old_mappings = client.indices.get_mapping(index=index_name)[index_name]["mappings"]

    # Strip out dynamic or irrelevant fields
    new_settings = index_body.get("settings", {}).get("index", {})
    relevant_old_settings = {k: old_settings.get(k) for k in new_settings}

    settings_diff = DeepDiff(relevant_old_settings, new_settings, ignore_order=True)
    mappings_diff = DeepDiff(old_mappings, index_body.get("mappings", {}), ignore_order=True)

    if settings_diff or mappings_diff:
        print("⚠️ Index configuration mismatch detected. Recreating index...")
        print("Settings diff:", settings_diff)
        print("Mappings diff:", mappings_diff)
        return True
    else:
        print(f"ℹ️ Index '{index_name}' already exists and matches expected configuration.")
        return False

def init_opensearch_index(
        client: OpenSearch, 
        index_name: str, 
        settings: dict, 
        mappings:dict
        ):

    body = {
        "settings": settings,
        "mappings": mappings
    }
    """Create or recreate an OpenSearch index if it doesn't exist or differs from configuration."""

    if not client.indices.exists(index=index_name):
        print(f"ℹ️ Initiating new index, {index_name}")
        client.indices.create(index=index_name, body=body)
        print(f"Created index {index_name} with configuration {body}")

    elif is_index_different(client, index_name, body):
        client.indices.delete(index=index_name)
        print(f"🗑️ Deleted old index '{index_name}'.")
        client.indices.create(index=index_name, body=body)
        print(f"Created index {index_name} with configuration {body}")

def index_documents(
    df: pd.DataFrame,
    client: OpenSearch,
    index_name: str,
    index_settings: dict,
    index_mappings: dict,
    id_column: str
):
    """Index documents from a DataFrame into an OpenSearch index."""
    init_opensearch_index(client, index_name, index_settings, index_mappings)

    indexed_count = 0
    rows = [{column: df.loc[idx, column] for column in df.columns} for idx in df.index]
    for row in tqdm(rows, desc = f"Indexing documents to {index_name}"):
        index_kwargs = {
            "index": index_name,
            "id": row.pop(id_column),
            "body": row
        }
        try:
            client.index(**index_kwargs)
            indexed_count += 1
        except Exception as e:
            print(f"❌ Failed to index {index_kwargs['id']}: {e}")
    
    if indexed_count:
        print(f"✅ Successfully indexed {indexed_count} documents.")
    else:
        print("⚠️ No documents were indexed.")

def build_wikipedia_index(
    urls: list,
    lemmatizer: spacy,
    encoder: SentenceTransformer,
    output_path: str
    ):
    """Given a list of wikipedia links, extracts and preprocesses data for indexing."""
    tqdm.pandas(desc= "Extracting data from Wikipedia. ..")

    df = pd.DataFrame({'url': urls})
    df['document_id'] = df.index.map(lambda x: str(x).zfill(3))
    df[['title', 'body']] = df.url.progress_apply(lambda x: pd.Series(get_wikipedia_content(x)))
    df.dropna(inplace=True)
    
    tqdm.pandas(desc='Lemmatizing body. . .')
    df['body_lemmatized'] = df.body.progress_apply(lambda x: lemmatize(lemmatizer, x))

    tqdm.pandas(desc='Computing title embeddings. . .')
    df['title_embedding'] = df.title.progress_apply(lambda x: encoder.encode(x))

    df.to_parquet(output_path)
    print(f'Saved output to {output_path}')
    

    return df