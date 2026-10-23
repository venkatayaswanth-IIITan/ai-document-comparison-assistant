"""
document_reader.py
------------------
Handles PDF reading, text extraction, data validation, and text chunking
using the pypdf library.
"""

from dataclasses import dataclass, field
from io import BytesIO
import os
from typing import Dict, List, Optional, Union
import pypdf


# Maximum recommended character count before chunking or safety truncation
# ~80,000 characters corresponds to approx. 20,000 words
MAX_RECOMMENDED_CHARS = 100_000


@dataclass
class DocumentData:
    """Stores extracted information and validation status for an uploaded PDF."""
    filename: str
    page_count: int = 0
    char_count: int = 0
    word_count: int = 0
    text: str = ""
    preview: str = ""
    pages: List[Dict[str, Union[int, str]]] = field(default_factory=list)
    is_valid: bool = False
    error_message: Optional[str] = None
    warning_message: Optional[str] = None


def extract_pdf_data(uploaded_file) -> DocumentData:
    """
    Extracts text and metadata from an uploaded PDF file object (or file path/BytesIO).

    Args:
        uploaded_file: A Streamlit UploadedFile, file-like BytesIO object, or file path.

    Returns:
        DocumentData dataclass containing text, counts, previews, and error/warning flags.
    """
    if uploaded_file is None:
        return DocumentData(
            filename="Unknown",
            is_valid=False,
            error_message="No file was provided for extraction."
        )

    # Determine file name
    if isinstance(uploaded_file, (str, os.PathLike)):
        filename = os.path.basename(str(uploaded_file))
        if not os.path.exists(str(uploaded_file)):
            return DocumentData(
                filename=filename,
                is_valid=False,
                error_message=f"File not found: '{filename}'."
            )
    else:
        filename = getattr(uploaded_file, "name", "uploaded_document.pdf")

    # Validate file extension
    if not filename.lower().endswith(".pdf"):
        return DocumentData(
            filename=filename,
            is_valid=False,
            error_message=f"Invalid file type for '{filename}'. Only PDF files are supported."
        )

    try:
        # If it's a Streamlit UploadedFile or BytesIO, read bytes or reset stream pointer
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        # Initialize pypdf reader
        reader = pypdf.PdfReader(uploaded_file)

        # Check for empty PDF (no pages)
        page_count = len(reader.pages)
        if page_count == 0:
            return DocumentData(
                filename=filename,
                page_count=0,
                is_valid=False,
                error_message=f"The file '{filename}' contains 0 pages (empty document)."
            )

        extracted_pages: List[Dict[str, Union[int, str]]] = []
        full_text_parts: List[str] = []

        # Iterate through pages and extract text
        for index, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text() or ""
            except Exception as page_err:
                page_text = ""
                # Keep processing other pages even if one fails
                print(f"Warning: Failed to extract text from page {index + 1} of {filename}: {page_err}")

            clean_page_text = page_text.strip()
            extracted_pages.append({
                "page_number": index + 1,
                "text": clean_page_text,
                "char_count": len(clean_page_text),
                "word_count": len(clean_page_text.split()) if clean_page_text else 0
            })

            if clean_page_text:
                full_text_parts.append(clean_page_text)

        full_text = "\n\n".join(full_text_parts).strip()
        total_chars = len(full_text)
        total_words = len(full_text.split()) if full_text else 0

        # Validate if any text was actually extractable
        if total_chars == 0:
            return DocumentData(
                filename=filename,
                page_count=page_count,
                char_count=0,
                word_count=0,
                text="",
                preview="",
                pages=extracted_pages,
                is_valid=False,
                error_message=(
                    f"'{filename}' was opened ({page_count} page(s)), but no machine-readable text "
                    "could be extracted. The file appears to be a scanned image or protected PDF. "
                    "Please upload a PDF containing selectable text."
                )
            )

        # Prepare a clean preview snippet (up to 1,000 characters)
        preview = full_text[:1000] + ("..." if total_chars > 1000 else "")

        # Check for exceptionally large documents
        warning_msg = None
        if total_chars > MAX_RECOMMENDED_CHARS:
            warning_msg = (
                f"Document is very large ({total_chars:,} characters, {total_words:,} words). "
                "Processing may take longer than usual."
            )

        return DocumentData(
            filename=filename,
            page_count=page_count,
            char_count=total_chars,
            word_count=total_words,
            text=full_text,
            preview=preview,
            pages=extracted_pages,
            is_valid=True,
            error_message=None,
            warning_message=warning_msg
        )

    except pypdf.errors.PdfReadError as pdf_err:
        return DocumentData(
            filename=filename,
            is_valid=False,
            error_message=f"Could not read PDF '{filename}'. File may be corrupted, encrypted, or invalid: {str(pdf_err)}"
        )
    except Exception as err:
        return DocumentData(
            filename=filename,
            is_valid=False,
            error_message=f"An unexpected error occurred while processing '{filename}': {str(err)}"
        )


def chunk_document_text(text: str, max_chunk_chars: int = 40_000, overlap_chars: int = 2_000) -> List[str]:
    """
    Safely splits large text into overlapping chunks if necessary.

    Args:
        text: Raw document text to divide.
        max_chunk_chars: Maximum character length per chunk.
        overlap_chars: Overlapping characters to preserve context across boundaries.

    Returns:
        List of text chunks.
    """
    if len(text) <= max_chunk_chars:
        return [text]

    chunks = []
    start = 0
    total_len = len(text)

    while start < total_len:
        end = min(start + max_chunk_chars, total_len)

        # Try to break at a paragraph or newline boundary rather than mid-word
        if end < total_len:
            last_break = text.rfind("\n\n", start, end)
            if last_break == -1 or last_break <= start:
                last_break = text.rfind("\n", start, end)
            if last_break == -1 or last_break <= start:
                last_break = text.rfind(". ", start, end)

            if last_break > start + (max_chunk_chars // 2):
                end = last_break + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= total_len:
            break
        start = max(end - overlap_chars, start + 1)

    return chunks
