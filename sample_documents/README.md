# Sample Documents for Testing

This directory is designed to store sample PDF files to test the **AI Document Comparison Assistant**.

## Included Test Files

When you run `python create_sample_pdfs.py` inside this folder (or run the app setup), two realistic sample contracts will be generated:

1. **`sample_contract_v1.pdf` (Baseline Employment Agreement)**
   - Parties: *Apex Innovations LLC* and *Johnathan Doe*
   - Role: Senior Software Engineer
   - Base Salary: $120,000 / year
   - Effective Date: January 15, 2024
   - Notice Period: 30 days
   - Remote Work: 100% remote allowed
   - Non-Compete: 6 months within California

2. **`sample_contract_v2.pdf` (Revised Employment Agreement)**
   - Parties: *Apex Innovations Global Corp* (Changed entity name) and *Johnathan Doe*
   - Role: Lead AI Engineer (Changed job title)
   - Base Salary: $145,000 / year (Increased salary)
   - Effective Date: March 1, 2024 (Updated start date)
   - Notice Period: 60 days (Stricter notice period)
   - Remote Work: Hybrid - 3 days in office (Changed work policy)
   - Non-Compete: 12 months nationwide (Extended non-compete duration & scope)
   - Added Clause: Section 8 - Intellectual Property & AI Model Assignment

## How to Test
1. Launch the Streamlit application:
   ```powershell
   streamlit run app.py
   ```
2. Upload `sample_contract_v1.pdf` under **Document A (Baseline)**.
3. Upload `sample_contract_v2.pdf` under **Document B (Revised)**.
4. Click **🚀 Run Document Comparison**.
5. Observe how the AI Assistant catches every addition, salary raise, changed date, stricter notice period, and altered remote policy!
6. Click **📄 Download DOCX Report** to obtain the generated comparison document.
