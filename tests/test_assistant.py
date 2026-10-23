"""
tests/test_assistant.py
-----------------------
Automated test suite for AI Document Comparison Assistant using pytest.
Tests PDF validation, error handling, text extraction, Gemini integration,
section parsing, and DOCX/Markdown report generation.
"""

from io import BytesIO
import os
import pytest
import docx

# Modules under test
from document_reader import extract_pdf_data, chunk_document_text, DocumentData
from comparison import (
    compare_documents,
    parse_comparison_sections,
    _fallback_section_parser,
    ComparisonResult,
    get_default_api_key,
)
from report_generator import create_comparison_docx


# ---------------------------------------------------------------------------
# Helper PDF Builders for Edge-Case Testing
# ---------------------------------------------------------------------------

def create_raw_pdf_bytes(title: str, text_lines: list) -> BytesIO:
    """Creates a valid PDF 1.4 in-memory buffer containing the given text."""
    content_stream = "BT\n/F1 12 Tf\n50 720 Td\n"
    content_stream += f"({title}) Tj\nET\n"
    y = 690
    for line in text_lines:
        content_stream += f"BT\n/F1 10 Tf\n50 {y} Td\n({line}) Tj\nET\n"
        y -= 15
    stream_bytes = content_stream.encode("latin-1", "replace")
    stream_length = len(stream_bytes)

    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        f"4 0 obj\n<< /Length {stream_length} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream\nendobj\n",
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    ]

    buf = BytesIO()
    buf.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    offset = len(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    for obj in objects:
        offsets.append(offset)
        buf.write(obj)
        offset += len(obj)

    xref_pos = offset
    buf.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode("latin-1"))

    buf.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))
    buf.seek(0)
    buf.name = "test_document.pdf"
    return buf


def create_empty_pages_pdf() -> BytesIO:
    """Creates a valid PDF with 0 pages."""
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n",
    ]
    buf = BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    offset = len(b"%PDF-1.4\n")
    for obj in objects:
        offsets.append(offset)
        buf.write(obj)
        offset += len(obj)
    xref_pos = offset
    buf.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode("latin-1"))
    buf.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))
    buf.seek(0)
    buf.name = "empty_zero_pages.pdf"
    return buf


def create_blank_page_pdf_no_text() -> BytesIO:
    """Creates a valid PDF with 1 page but no text stream (simulates scanned image PDF without OCR)."""
    objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n",
    ]
    buf = BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = [0]
    offset = len(b"%PDF-1.4\n")
    for obj in objects:
        offsets.append(offset)
        buf.write(obj)
        offset += len(obj)
    xref_pos = offset
    buf.write(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
    for off in offsets[1:]:
        buf.write(f"{off:010d} 00000 n \n".encode("latin-1"))
    buf.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))
    buf.seek(0)
    buf.name = "scanned_no_text.pdf"
    return buf


# ---------------------------------------------------------------------------
# Test Suite 1: Document Validation & Extraction
# ---------------------------------------------------------------------------

def test_missing_file_validation():
    """Verify handling when no file is passed."""
    data = extract_pdf_data(None)
    assert not data.is_valid
    assert "No file was provided" in data.error_message


def test_invalid_file_extension():
    """Verify non-PDF file extension is rejected."""
    buf = BytesIO(b"Hello world")
    buf.name = "notes.docx"
    data = extract_pdf_data(buf)
    assert not data.is_valid
    assert "Only PDF files are supported" in data.error_message


def test_corrupted_pdf_file():
    """Verify corrupted PDF bytes trigger a graceful error message without crashing."""
    corrupted_buf = BytesIO(b"This is completely fake, non-pdf binary content.")
    corrupted_buf.name = "corrupted.pdf"
    data = extract_pdf_data(corrupted_buf)
    assert not data.is_valid
    assert "Could not read PDF" in data.error_message or "unexpected error" in data.error_message


def test_empty_zero_pages_pdf():
    """Verify detection of PDF with 0 pages."""
    empty_pdf = create_empty_pages_pdf()
    data = extract_pdf_data(empty_pdf)
    assert not data.is_valid
    assert data.page_count == 0
    assert "0 pages" in data.error_message


def test_scanned_pdf_no_extractable_text():
    """Verify warning when PDF has pages but 0 machine-readable text."""
    scanned_pdf = create_blank_page_pdf_no_text()
    data = extract_pdf_data(scanned_pdf)
    assert not data.is_valid
    assert data.page_count == 1
    assert data.char_count == 0
    assert "no machine-readable text could be extracted" in data.error_message


def test_valid_pdf_extraction_sample_v1():
    """Verify successful extraction of text and metadata from sample_contract_v1.pdf."""
    path_v1 = os.path.join("sample_documents", "sample_contract_v1.pdf")
    if os.path.exists(path_v1):
        data = extract_pdf_data(path_v1)
        assert data.is_valid
        assert data.page_count >= 1
        assert data.char_count > 0
        assert data.word_count > 0
        assert "Apex Innovations" in data.text
        assert "120,000" in data.text
        assert data.preview != ""
        assert data.error_message is None


def test_valid_pdf_extraction_sample_v2():
    """Verify extraction of changed dates ($145,000, March 1, 2024) from sample_contract_v2.pdf."""
    path_v2 = os.path.join("sample_documents", "sample_contract_v2.pdf")
    if os.path.exists(path_v2):
        data = extract_pdf_data(path_v2)
        assert data.is_valid
        assert data.page_count >= 1
        assert "145,000" in data.text
        assert "March 1, 2024" in data.text
        assert "Lead AI Engineer" in data.text


def test_text_chunking():
    """Verify text chunking splits large text safely with overlap."""
    sample_text = "Paragraph test sentence. " * 500  # ~13,000 chars
    chunks = chunk_document_text(sample_text, max_chunk_chars=4000, overlap_chars=200)
    assert len(chunks) > 1
    # Check all chunks have text
    for c in chunks:
        assert len(c) > 0


# ---------------------------------------------------------------------------
# Test Suite 2: AI Parsing & Grounding Structure
# ---------------------------------------------------------------------------

def test_parse_comparison_sections_delimited():
    """Verify delimiter-based section parsing parses all 7 required sections."""
    raw_ai_output = """
===SECTION 1: SUMMARY OF DOCUMENT A===
Document A is an original agreement for software engineering with $120,000 salary.

===SECTION 2: SUMMARY OF DOCUMENT B===
Document B is a revised contract for AI engineering with $145,000 salary.

===SECTION 3: SIMILARITIES===
Both contracts govern the employment of Johnathan Doe by Apex Innovations.

===SECTION 4: DIFFERENCES & CONTRADICTIONS===
Salary increased from $120,000 to $145,000. Notice period changed from 30 to 60 days.

===SECTION 5: KEY DETAILS COMPARISON===
- Dates: Jan 15, 2024 vs March 1, 2024
- Amounts: $120,000 vs $145,000

===SECTION 6: OVERALL CONCLUSION===
The revised agreement strengthens corporate control and increases compensation.

===SECTION 7: LIMITATIONS & EVIDENCE GROUNDING===
Analysis based exclusively on the provided contract text.
"""
    sections = parse_comparison_sections(raw_ai_output)
    assert "120,000" in sections["summary_a"]
    assert "145,000" in sections["summary_b"]
    assert "Johnathan Doe" in sections["similarities"]
    assert "Notice period" in sections["differences"]
    assert "Jan 15, 2024" in sections["key_details"]
    assert "strengthens corporate control" in sections["overall_conclusion"]
    assert "Analysis based exclusively" in sections["limitations"]


def test_parse_comparison_sections_fallback_markdown():
    """Verify fallback parser handles standard markdown headings (## Section)."""
    markdown_output = """
## Summary of Document A
Original baseline agreement.

## Summary of Document B
Revised terms and conditions.

## Key Similarities
Both agreements are between the same parties.

## Key Differences & Contradictions
Compensation and notice terms are modified.

## Key Details Comparison
Dates and amounts reflect updated fiscal year.

## Overall Conclusion
Scope increased significantly.

## Limitations & Uncertainties
No exhibits were attached.
"""
    sections = _fallback_section_parser(markdown_output)
    assert "Original baseline agreement" in sections["summary_a"]
    assert "Revised terms and conditions" in sections["summary_b"]
    assert "same parties" in sections["similarities"]
    assert "Compensation" in sections["differences"]
    assert "fiscal year" in sections["key_details"]
    assert "Scope increased" in sections["overall_conclusion"]
    assert "No exhibits" in sections["limitations"]


# ---------------------------------------------------------------------------
# Test Suite 3: Gemini API Error Handling
# ---------------------------------------------------------------------------

def test_gemini_api_empty_key_error():
    """Verify comparing documents without an API key fails gracefully with informative message."""
    res = compare_documents(
        doc_a_name="doc_a.pdf",
        doc_a_text="Sample text A",
        doc_b_name="doc_b.pdf",
        doc_b_text="Sample text B",
        api_key="",
        model_name="gemini-2.5-flash"
    )
    assert not res.is_success
    assert "API key is required" in res.error_message


def test_gemini_api_invalid_key_error():
    """Verify calling Gemini with an invalid key produces an error result without uncaught crash."""
    res = compare_documents(
        doc_a_name="doc_a.pdf",
        doc_a_text="Sample text A",
        doc_b_name="doc_b.pdf",
        doc_b_text="Sample text B",
        api_key="AIzaSy_fake_invalid_key_for_testing_123456789",
        model_name="gemini-2.5-flash"
    )
    assert not res.is_success
    assert res.error_message is not None


# ---------------------------------------------------------------------------
# Test Suite 4: Report Generation (DOCX & Markdown)
# ---------------------------------------------------------------------------

def test_create_comparison_docx_structure():
    """Verify create_comparison_docx builds a valid Word document with all 7 sections."""
    doc_a_meta = {"filename": "contract_v1.pdf", "page_count": 1, "char_count": 1200, "word_count": 200}
    doc_b_meta = {"filename": "contract_v2.pdf", "page_count": 2, "char_count": 1800, "word_count": 310}

    comp_dict = {
        "summary_a": "Summary of baseline contract.",
        "summary_b": "Summary of revised contract.",
        "similarities": "Parties and purpose are identical.",
        "differences": "Salary changed from $120,000 to $145,000.",
        "key_details": "Dates: Jan 15 vs March 1.",
        "overall_conclusion": "Promotion with increased responsibilities.",
        "limitations": "Governed solely by extracted text."
    }

    docx_stream = create_comparison_docx(
        doc_a_meta=doc_a_meta,
        doc_b_meta=doc_b_meta,
        comparison_data=comp_dict,
        model_name="gemini-2.5-flash"
    )

    # Verify BytesIO stream contains valid docx
    assert isinstance(docx_stream, BytesIO)
    docx_stream.seek(0)
    word_doc = docx.Document(docx_stream)

    # Check paragraphs and tables
    all_text = " ".join([p.text for p in word_doc.paragraphs])
    assert "AI Document Comparison Assistant" in all_text
    assert "Executive Summary: Document A" in all_text
    assert "Executive Summary: Document B" in all_text
    assert "Shared Provisions & Key Similarities" in all_text
    assert "Differences, Additions, & Contradictions" in all_text
    assert "Key Details Matrix" in all_text
    assert "Overall Conclusion & Synthesis" in all_text
    assert "Limitations & Grounding Statement" in all_text

    # Verify Metadata Table
    assert len(word_doc.tables) >= 1
    table = word_doc.tables[0]
    cell_texts = [cell.text for row in table.rows for cell in row.cells]
    assert "contract_v1.pdf" in cell_texts
    assert "contract_v2.pdf" in cell_texts


def test_markdown_report_content():
    """Verify markdown report string formatting."""
    doc_a_meta = {"filename": "doc_a.pdf", "page_count": 1, "char_count": 500}
    doc_b_meta = {"filename": "doc_b.pdf", "page_count": 1, "char_count": 520}
    comp_dict = {
        "summary_a": "Sum A",
        "summary_b": "Sum B",
        "similarities": "Sim",
        "differences": "Diff",
        "key_details": "Details",
        "overall_conclusion": "Conc",
        "limitations": "Lim"
    }

    md = f"""# AI Document Comparison Report
**Document A:** {doc_a_meta['filename']}
**Document B:** {doc_b_meta['filename']}

## 1. Summary of Document A
{comp_dict['summary_a']}

## 2. Summary of Document B
{comp_dict['summary_b']}

## 3. Similarities
{comp_dict['similarities']}

## 4. Differences & Contradictions
{comp_dict['differences']}

## 5. Key Details Comparison
{comp_dict['key_details']}

## 6. Overall Conclusion
{comp_dict['overall_conclusion']}

## 7. Limitations & Grounding
{comp_dict['limitations']}
"""
    for key, val in comp_dict.items():
        assert val in md


def test_identical_documents_parsing():
    """Verify that comparing identical documents produces expected grounded sections."""
    identical_text = "This is a mutual non-disclosure agreement dated May 10, 2024 between Alpha Corp and Beta LLC."
    mock_ai_output = f"""
===SECTION 1: SUMMARY OF DOCUMENT A===
Non-disclosure agreement between Alpha Corp and Beta LLC dated May 10, 2024.

===SECTION 2: SUMMARY OF DOCUMENT B===
Identical non-disclosure agreement between Alpha Corp and Beta LLC dated May 10, 2024.

===SECTION 3: SIMILARITIES===
100% identical content. All terms, parties, and obligations match verbatim.

===SECTION 4: DIFFERENCES & CONTRADICTIONS===
No differences, additions, removals, or contradictions found. Both documents are identical.

===SECTION 5: KEY DETAILS COMPARISON===
- Dates: May 10, 2024 in both documents.
- Names: Alpha Corp and Beta LLC in both documents.
- Amounts: No financial figures mentioned in either document.

===SECTION 6: OVERALL CONCLUSION===
The documents are exact duplicates with zero substantive or grammatical changes.

===SECTION 7: LIMITATIONS & EVIDENCE GROUNDING===
Strictly verified against the identical text provided.
"""
    sections = parse_comparison_sections(mock_ai_output)
    assert "Alpha Corp" in sections["summary_a"]
    assert "Alpha Corp" in sections["summary_b"]
    assert "identical" in sections["similarities"].lower()
    assert "no differences" in sections["differences"].lower()
    assert "May 10, 2024" in sections["key_details"]
    assert "exact duplicates" in sections["overall_conclusion"].lower()


def test_changed_dates_and_amounts_extraction():
    """Verify differences in dates, job roles, and dollar amounts between sample contracts."""
    path_v1 = os.path.join("sample_documents", "sample_contract_v1.pdf")
    path_v2 = os.path.join("sample_documents", "sample_contract_v2.pdf")

    assert os.path.exists(path_v1), "sample_contract_v1.pdf must exist"
    assert os.path.exists(path_v2), "sample_contract_v2.pdf must exist"

    doc_a = extract_pdf_data(path_v1)
    doc_b = extract_pdf_data(path_v2)

    # Normalize whitespace to account for PDF line-wrapping
    norm_a = " ".join(doc_a.text.split())
    norm_b = " ".join(doc_b.text.split())

    assert "$120,000" in norm_a
    assert "$145,000" in norm_b

    assert "January 15, 2024" in norm_a
    assert "March 1, 2024" in norm_b

    assert "Senior Software Engineer" in norm_a
    assert "Lead AI Engineer" in norm_b

    assert "thirty (30) days" in norm_a
    assert "sixty (60) days" in norm_b


def test_docx_download_bytes_integrity():
    """Verify that create_comparison_docx produces valid, non-empty byte buffer for download."""
    doc_a_meta = {"filename": "doc_a.pdf", "page_count": 1, "char_count": 100, "word_count": 20}
    doc_b_meta = {"filename": "doc_b.pdf", "page_count": 1, "char_count": 100, "word_count": 20}
    comp_dict = {
        "summary_a": "Summary A",
        "summary_b": "Summary B",
        "similarities": "Same",
        "differences": "None",
        "key_details": "Dates match",
        "overall_conclusion": "Good",
        "limitations": "None"
    }

    stream = create_comparison_docx(doc_a_meta, doc_b_meta, comp_dict, "gemini-2.5-flash")
    raw_bytes = stream.getvalue()

    assert isinstance(raw_bytes, bytes)
    assert len(raw_bytes) > 1000  # A valid .docx zip container is > 1KB
    # Re-reading raw bytes through BytesIO must succeed with python-docx
    re_opened_doc = docx.Document(BytesIO(raw_bytes))
    assert len(re_opened_doc.paragraphs) > 5

