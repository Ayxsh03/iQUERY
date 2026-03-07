"""
Document Loader — extracts raw text from PDF, DOCX, and TXT files.
Returns a list of page-level text strings along with source metadata.
"""

import io
from pathlib import Path
from typing import List, Dict, Any

import PyPDF2
import docx


def load_document(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """
    Parse a document from raw bytes and return a list of page/section dicts.

    Each dict has:
        {
            "text": str,           # raw extracted text
            "page": int,           # page or section number (1-indexed)
            "source": str,         # original filename
        }
    """
    suffix = Path(filename).suffix.lower()

    if suffix == ".pdf":
        return _load_pdf(file_bytes, filename)
    elif suffix in (".docx", ".doc"):
        return _load_docx(file_bytes, filename)
    elif suffix == ".txt":
        return _load_txt(file_bytes, filename)
    else:
        raise ValueError(
            f"Unsupported file type '{suffix}'. Supported: .pdf, .docx, .txt"
        )


def _load_pdf(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Extract text page-by-page from a PDF."""
    pages = []
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:  # skip blank pages
            pages.append({
                "text": text,
                "page": i + 1,
                "source": filename,
            })

    if not pages:
        raise ValueError(f"No extractable text found in '{filename}'.")

    return pages


def _load_docx(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Extract text paragraph-by-paragraph from a DOCX file."""
    doc = docx.Document(io.BytesIO(file_bytes))
    full_text = "\n".join(
        para.text for para in doc.paragraphs if para.text.strip()
    )

    if not full_text.strip():
        raise ValueError(f"No extractable text found in '{filename}'.")

    # Treat the whole DOCX as a single "page" for simplicity
    return [{"text": full_text, "page": 1, "source": filename}]


def _load_txt(file_bytes: bytes, filename: str) -> List[Dict[str, Any]]:
    """Decode and return a plain-text file as a single document."""
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    text = text.strip()
    if not text:
        raise ValueError(f"'{filename}' is empty.")

    return [{"text": text, "page": 1, "source": filename}]
