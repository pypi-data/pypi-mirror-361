import pandas as pd
from pathlib import Path

import streamlit as st
from docutrance.search import compose_query_body
import numpy as np
import json

def get_aggs(client, index):
    aggs = client.search(index=index, body={
    "size": 0,
    "aggs": {
        "volumes": {
            "terms": {
                "field": "volume",  
                "size": 100
            }
        },
        "authors": {
            "terms": {
                "field": "author",
                "size": 100
            }
        }
    }
    })["aggregations"]
    all_volumes = sorted([b["key"] for b in aggs["volumes"]["buckets"]])
    all_authors = sorted([b["key"] for b in aggs["authors"]["buckets"]])
    return all_volumes, all_authors

def format_download_link(b64data, filename, title):
    """Return an HTML download link for base64-encoded PDF data."""
    href = f'<a href="data:application/pdf;base64,{b64data}" download="{filename}">{title}</a>'
    return href

def format_hit(author, volume, section, chapter, title, file, document_dir, highlights):
    """Format author and document metadata into a readable string."""
    file_path = Path(document_dir) / f'V{str(volume).zfill(2)}' / f'{file}.parquet' if document_dir else None
    volume = f"Volume {volume}"
    metadata = [volume]
    if section:
        metadata.append(f"Section {section}")
    if chapter:
        metadata.append(chapter)

    metadata = f'*{", ".join(metadata)}*'
    title = f'### [{title}]({file_path})' if file_path else f'### {title}'

    if isinstance(author, np.ndarray):
        author = [a for a in author.tolist() if a and a.strip()]
        if author:
            author = ', '.join(author)
            metadata = f'**{author}** | {metadata}'
    
    if highlights:
        highlights = '---\n\n' + '\n\n---\n\n'.join(highlights)
    return title, metadata, highlights


def render_query_debugger(query_body):
    """
    Displays the raw and parsed query body for debugging.
    """
    st.markdown("### 🐞 Debugging: Current Query State")

    """ Show raw query string """
    st.markdown("**Raw Query:**")
    st.text(str(query_body))

    """ Attempt to parse and pretty-print JSON """
    st.markdown("**Parsed JSON (if applicable):**")
    try:
        if isinstance(query_body, str):
            parsed = json.loads(query_body)
        else:
            parsed = query_body

        if isinstance(parsed, (dict, list)):
            st.code(json.dumps(parsed, indent=2, ensure_ascii=False), language="json")
        else:
            st.warning("Parsed query is not a dict or list.")
    except Exception as e:
        st.warning(f"Could not parse query as JSON: {e}")


def setup_page(title):
    """
    Sets page configuration and title.
    """
    st.set_page_config(page_title=title, layout="wide")
    st.title(title)


def initialize_session_state():
    """
    Sets up session state on first load.  Client & hybrid-pipeline
    registration only happen once.
    """
    defaults = {
        "query_input": "",
        "query_body": compose_query_body('bool'),  # or {} if you build later
        "page_number": 1,
        "filters_applied": False,
        "selected_authors": [],
        "selected_volumes": []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def render_sidebar(client, index_name):
    """
    Renders sidebar filters, reset and pagination controls.
    """
    st.sidebar.markdown("### 🎯 Refine Your Search")
    st.sidebar.caption("Use the filters below to narrow down your results.")

    """ Fetch available values for filters """
    all_volumes, all_authors = get_aggs(client, index_name)

    """ Ensure session state keys are initialized """
    if "selected_volumes" not in st.session_state:
        st.session_state.selected_volumes = []
    if "selected_authors" not in st.session_state:
        st.session_state.selected_authors = []
    if "query_input" not in st.session_state:
        st.session_state.query_input = ""
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1
    if "filters_applied" not in st.session_state:
        st.session_state.filters_applied = False

    """ Reset button clears all filters and restarts search """
    reset_button = st.sidebar.button("🔄 Reset", type="secondary")
    if reset_button:
        st.session_state.selected_volumes = []
        st.session_state.selected_authors = []
        st.session_state.query_input = ""
        st.session_state.page_number = 1
        st.session_state.filters_applied = False
        st.rerun()

    """ Filter selection widgets """
    st.sidebar.multiselect("📚 Volume", all_volumes, key="selected_volumes")
    st.sidebar.multiselect("👤 Author", all_authors, key="selected_authors")

    """ Apply filter button """
    col1, col2 = st.sidebar.columns(2)
    with col1:
        apply_filters = st.button("🔎 Apply Filters", type="secondary")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📄 Page Navigation")

    """ Pagination controls """
    if st.sidebar.button("⬅️ Previous") and st.session_state.page_number > 1:
        st.session_state.page_number -= 1
    if st.sidebar.button("➡️ Next"):
        st.session_state.page_number += 1

    """ Manual page input """
    page_input = st.sidebar.text_input("Jump to page", value=str(st.session_state.page_number))
    if page_input.isdigit():
        st.session_state.page_number = max(1, int(page_input))

    """ Mark filters as applied when the user clicks Apply """
    if apply_filters:
        st.session_state.filters_applied = True
        st.session_state.page_number = 1


def render_main_input(user_prompt):
    """
    Renders the main search input box.
    """
    query_input = st.text_input(
        user_prompt[0],
        placeholder=user_prompt[1],
        value=st.session_state.get("query_input", ""),
        key="query_input"
    )
    return query_input


def get_filter_input():
    """
    Collects selected filters from session state into a list of field-value tuples.
    """
    must = []
    for field, values in zip (
        ['volume', 'author'], 
        [st.session_state.selected_volumes, st.session_state.selected_authors ]):
        if values:
            values = values if isinstance(values, list) else [values]
            must.append({"terms": {field: values}})
    
    return must



def render_results(results: pd.DataFrame, document_dir: str=None, page_size=10):
    """
    Displays paginated search results with titles, metadata, and highlights.
    """
    page = st.session_state.page_number
    total_hits = len(results)

    if results.empty:
        st.warning("No results found.")

    offset = (page - 1) * page_size
    page_hits = results.iloc[offset : page * page_size]
    st.markdown(f"### Showing page {page} of {((total_hits - 1) // page_size) + 1}")

    for _, hit in page_hits.iterrows():
        title, metadata, highlights = format_hit(
            hit['author'],
            hit['volume'],
            hit['section'],
            hit['chapter'],
            hit['title'],
            hit['file'],
            document_dir,
            hit.get('highlights')
        )
        st.markdown (title)
        st.markdown (metadata)
        if highlights:
            st.markdown(highlights)
        st.markdown("---")

