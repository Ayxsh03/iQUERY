"""
Text Chunker — splits raw page text into overlapping chunks suitable
for embedding and vector retrieval.

Uses LangChain's RecursiveCharacterTextSplitter which tries paragraph,
sentence, then word boundaries before hard-splitting — preserving meaning.
"""

from typing import List, Dict, Any

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import get_settings


def chunk_pages(pages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Take a list of page dicts (from loader.py) and return a flat list
    of chunk dicts, each ready to be embedded and stored.

    Each chunk dict:
        {
            "text":       str,   # chunk text
            "source":     str,   # original filename
            "page":       int,   # page number this chunk came from
            "chunk_index": int,  # sequential index across the document
        }
    """
    settings = get_settings()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    all_chunks: List[Dict[str, Any]] = []
    chunk_index = 0

    for page in pages:
        raw_text = page["text"]
        splits = splitter.split_text(raw_text)

        for split in splits:
            text = split.strip()
            if not text:
                continue
            all_chunks.append({
                "text": text,
                "source": page["source"],
                "page": page["page"],
                "chunk_index": chunk_index,
            })
            chunk_index += 1

    return all_chunks
