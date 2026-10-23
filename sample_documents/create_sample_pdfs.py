"""
create_sample_pdfs.py
---------------------
Generates two sample PDF files (sample_contract_v1.pdf and sample_contract_v2.pdf)
using pure Python without requiring any third-party PDF compilation tools.
These sample files allow immediate testing of the AI Document Comparison Assistant.
"""

import os


def generate_simple_pdf(filename: str, title: str, paragraphs: list):
    """Generates a valid, readable PDF 1.4 document containing the provided text paragraphs."""
    content_stream = "BT\n/F1 16 Tf\n50 750 Td\n"
    content_stream += f"({_escape_pdf(title)}) Tj\nET\n"

    # Body text
    y_offset = 710
    for para in paragraphs:
        if not para.strip():
            y_offset -= 12
            continue

        # Wrap long lines roughly
        words = para.split()
        line = ""
        for word in words:
            if len(line) + len(word) + 1 > 75:
                content_stream += f"BT\n/F1 10 Tf\n50 {y_offset} Td\n({_escape_pdf(line)}) Tj\nET\n"
                y_offset -= 15
                line = word
            else:
                line = f"{line} {word}".strip()

        if line:
            content_stream += f"BT\n/F1 10 Tf\n50 {y_offset} Td\n({_escape_pdf(line)}) Tj\nET\n"
            y_offset -= 18

        if y_offset < 60:
            break

    stream_bytes = content_stream.encode("latin-1", "replace")
    stream_length = len(stream_bytes)

    objects = [
        # Obj 1: Catalog
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        # Obj 2: Pages
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        # Obj 3: Page
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n",
        # Obj 4: Contents stream
        f"4 0 obj\n<< /Length {stream_length} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream\nendobj\n",
        # Obj 5: Font
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
    ]

    # Write PDF file
    with open(filename, "wb") as f:
        f.write(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        offset = len(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

        for obj in objects:
            offsets.append(offset)
            f.write(obj)
            offset += len(obj)

        xref_pos = offset
        f.write(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        f.write(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            f.write(f"{off:010d} 00000 n \n".encode("latin-1"))

        f.write(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))

    print(f"Generated sample PDF: {filename}")


def _escape_pdf(text: str) -> str:
    """Escapes special characters in PDF strings."""
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Sample Document A: Baseline Employment Agreement
    doc_a_paragraphs = [
        "EMPLOYMENT AGREEMENT (VERSION 1.0 - BASELINE)",
        "This Employment Agreement is entered into on January 15, 2024, by and between Apex Innovations LLC (the 'Company'), a California limited liability company, and Johnathan Doe (the 'Employee').",
        "1. POSITION AND DUTIES: The Employee is hired for the position of Senior Software Engineer. The Employee will report directly to the Chief Technology Officer.",
        "2. COMPENSATION: The Company will pay the Employee a base annual salary of $120,000 USD, payable in accordance with the Company's standard bi-weekly payroll practices.",
        "3. EFFECTIVE DATE: The Employee's employment shall commence on February 1, 2024.",
        "4. REMOTE WORK POLICY: The Employee is authorized to perform 100% remote work from any domestic location within the United States.",
        "5. TERMINATION AND NOTICE: Either party may terminate this agreement with thirty (30) days written advance notice.",
        "6. NON-COMPETE RESTRICTIONS: The Employee agrees not to compete with the Company within the State of California for a period of six (6) months following the termination of employment.",
        "7. GOVERNING LAW: This agreement shall be construed under the laws of the State of California."
    ]

    # Sample Document B: Revised Employment Agreement
    doc_b_paragraphs = [
        "EMPLOYMENT AGREEMENT (VERSION 2.0 - REVISED)",
        "This Employment Agreement is entered into on March 1, 2024, by and between Apex Innovations Global Corp (the 'Company'), a Delaware corporation, and Johnathan Doe (the 'Employee').",
        "1. POSITION AND DUTIES: The Employee is promoted to Lead AI Engineer. The Employee will report directly to the Vice President of Artificial Intelligence.",
        "2. COMPENSATION: The Company will pay the Employee an increased base annual salary of $145,000 USD, plus an annual performance bonus of up to 15%, payable in accordance with payroll practices.",
        "3. EFFECTIVE DATE: The revised terms of employment shall commence on March 15, 2024.",
        "4. REMOTE WORK POLICY: Hybrid Policy - The Employee must work at least three (3) days per week in the headquarters office in San Francisco, California.",
        "5. TERMINATION AND NOTICE: Either party may terminate this agreement with sixty (60) days written advance notice.",
        "6. NON-COMPETE RESTRICTIONS: The Employee agrees not to compete with the Company nationwide across the United States for a period of twelve (12) months following termination.",
        "7. INTELLECTUAL PROPERTY & AI ASSIGNMENT: All neural networks, algorithms, source code, and training workflows developed during employment are exclusive property of Apex Innovations Global Corp.",
        "8. GOVERNING LAW: This agreement shall be construed under the laws of the State of Delaware."
    ]

    file_a = os.path.join(script_dir, "sample_contract_v1.pdf")
    file_b = os.path.join(script_dir, "sample_contract_v2.pdf")

    generate_simple_pdf(file_a, "Apex Innovations - Employment Agreement v1", doc_a_paragraphs)
    generate_simple_pdf(file_b, "Apex Innovations - Employment Agreement v2", doc_b_paragraphs)
    print("Sample PDF files created successfully!")


if __name__ == "__main__":
    main()
