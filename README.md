# ⚖️ AI Document Comparison Assistant

An intelligent, enterprise-grade document comparison application built with **Python**, **Streamlit**, the **Google Gemini API**, **pypdf**, and **python-docx**.

This tool enables users to upload two PDF documents (e.g., contracts, proposals, policies, or agreements), validates their structure and extractable text, generates executive summaries, surfaces differences and contradictions, compares key entities (dates, names, financials, deadlines), and produces audit-ready downloadable **DOCX** comparison reports.

---

## 🌟 Key Features

1. **Dual PDF Ingestion & Robust Validation**:
   - Upload Document A (Baseline) and Document B (Revised).
   - Validates missing inputs, non-PDF file formats, corrupted binaries, empty PDFs (0 pages), and scanned image-only PDFs lacking machine-readable text.
   - Detects identical documents and alerts the user immediately.
2. **Metadata & Text Inspection**:
   - Calculates page count, character count, and word count.
   - Provides live previews of extracted text before analysis.
3. **Evidence-Grounded AI Analysis**:
   - Powered by **Google Gemini API** (`gemini-2.5-flash`, `gemini-1.5-flash`, or `gemini-1.5-pro`).
   - Grounded strictly in extracted text—no hallucinated facts or unverified assumptions.
   - Distinct sections:
     - 📑 **Summary of Document A**
     - 📑 **Summary of Document B**
     - 🤝 **Shared Provisions & Similarities**
     - ⚡ **Differences, Additions, Removals & Contradictions**
     - 🔍 **Key Details Comparison (Dates, Names, Amounts, Deadlines)**
     - 🎯 **Overall Conclusion & Strategic Impact**
     - ⚠️ **Limitations & Evidence Grounding Statement**
4. **Downloadable DOCX & Markdown Reports**:
   - Generates a styled, publication-ready Microsoft Word document (`.docx`) with metadata tables, formatted headers, and bulleted evidence matrices.
   - Provides quick-export Markdown (`.md`) reports.
5. **Modern, Responsive UI**:
   - Custom typography, card metrics, tabs, interactive sidebar, loading states, and instant session reset.
6. **Enterprise Security & Privacy**:
   - API keys are managed locally via `.env` and excluded from Git tracking via `.gitignore`.
7. **Comprehensive Automated Test Suite**:
   - 17 automated unit and integration tests using `pytest` covering all edge cases.

---

## 📂 Project Directory Structure

```text
ai-document-comparison-assistant/
├── app.py                      # Main Streamlit web application & UI
├── document_reader.py          # PDF text extraction, validation & stats (pypdf)
├── comparison.py               # Gemini AI engine, grounded prompts & section parsing
├── report_generator.py         # DOCX comparison report builder (python-docx)
├── requirements.txt            # Python dependencies (Streamlit, Gemini, pypdf, docx, pytest)
├── pytest.ini                  # Pytest configuration file
├── conftest.py                 # Pytest test discovery & sys.path configuration
├── .env.example                # Template for environment variables (safe to commit)
├── .gitignore                  # Git exclusions for secrets (.env), virtualenvs, & caches
├── README.md                   # Comprehensive project documentation
├── tests/                      # Automated test suite
│   └── test_assistant.py       # 17 unit and integration tests
└── sample_documents/           # Directory for sample test PDFs
    ├── README.md               # Explanation of test contracts & scenarios
    ├── create_sample_pdfs.py   # Script to generate test PDFs
    ├── sample_contract_v1.pdf  # Baseline Employment Agreement
    └── sample_contract_v2.pdf  # Revised Employment Agreement
```

---

## 🚀 Quick Start Guide (Windows)

Follow these step-by-step instructions. No prior coding experience is required!

### Step 1: Open Terminal (PowerShell or Command Prompt)
Press `Win + S`, type **PowerShell**, and open **Windows PowerShell**.

Navigate to the project directory:
```powershell
cd d:\ai-document-comparison-assistant
```

---

### Step 2: Create and Activate a Python Virtual Environment

Creating an isolated virtual environment keeps your project clean and avoids package conflicts:

```powershell
# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```

> **Note on PowerShell Script Execution Policy:**  
> If you see an error like `cannot be loaded because running scripts is disabled on this system`, run this command in PowerShell, then activate again:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> .\venv\Scripts\Activate.ps1
> ```

---

### Step 3: Install Required Dependencies

Install all dependencies listed in `requirements.txt`:
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 4: Configure Your Google Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey) to generate a free API key.
2. Create a file named `.env` in the root of `ai-document-comparison-assistant`:
   ```powershell
   Copy-Item .env.example .env
   ```
3. Open `.env` in Notepad or VS Code and paste your API key:
   ```env
   GEMINI_API_KEY=AIzaSyYourActualKeyHere
   ```
*(You can also enter your API key directly in the application's sidebar if you prefer).*

---

### Step 5: (Optional) Generate Sample Comparison PDFs

Generate two sample contracts (`sample_contract_v1.pdf` and `sample_contract_v2.pdf`) to immediately test the system:
```powershell
python sample_documents\create_sample_pdfs.py
```

---

### Step 6: Run Automated Tests (Pytest)

Run the automated test suite to verify file validation, PDF extraction, error handling, section parsing, and report generation:

```powershell
python -m pytest -v
```

All 17 tests verify:
- Missing file validation (`None` input, non-existent paths)
- Non-PDF extension rejection
- Corrupted PDF handling
- Empty PDF detection (0 pages)
- Scanned PDF detection (no extractable text)
- Extraction of text, page count, and character count
- Safe text chunking with context overlap
- Section parsing (both delimited and markdown headers)
- Gemini API error handling (empty key and invalid key rejection)
- DOCX report structure and metadata tables
- Markdown report generation
- Identical document comparison
- Changed dates, amounts, roles, and notice periods
- DOCX byte integrity for web downloads

---

### Step 7: Launch the Streamlit Application

Start the web application:
```powershell
streamlit run app.py
```

Streamlit will open in your default browser at:
```text
http://localhost:8501
```

---

## 🧪 How to Use the Application

1. **Upload Documents**:
   - Drag and drop your baseline document into **Document A**.
   - Drag and drop your revised document into **Document B**.
2. **Review Extracted Data**:
   - Verify page counts, character counts, and word counts.
   - Click **Preview Extracted Text** to inspect the extracted content.
   - If both documents have identical text, an informational banner will notify you.
3. **Execute AI Comparison**:
   - Ensure your Gemini API Key is configured in the sidebar or `.env`.
   - Select your preferred model (e.g., `gemini-2.5-flash`).
   - Click **🚀 Run Document Comparison**.
4. **Explore Findings**:
   - Navigate across the 7 tabs to review summaries, additions, removals, contradictions, and dates/amounts.
5. **Download the Report**:
   - Click **📄 Download DOCX Report** to download the formatted Word document for team sharing or archiving.
   - Click **📝 Download Markdown (.md) Report** for markdown archives.
6. **Reset Session**:
   - Click **🔄 Reset / Clear Session** in the sidebar to reset all state and test new files.

---

## 🛠️ Technology Stack Breakdown

| Technology | Purpose |
| :--- | :--- |
| **Python 3.10+** | Core programming language |
| **Streamlit** | Interactive modern web user interface |
| **Google Gemini API** (`google-genai` / `google-generativeai`) | Generative AI models for grounded summarization and comparison |
| **pypdf** | Robust PDF parsing, page extraction, and text validation |
| **python-docx** | Programmatic generation of styled Microsoft Word (.docx) reports |
| **python-dotenv** | Secure environment variable handling for API credentials |
| **pytest** | Automated testing framework |
| **Git & GitHub** | Source code version control and repository management |

---

## 📦 Setting Up Git & GitHub Version Control

The `.gitignore` file is configured to strictly exclude `.env`, `.venv`, and cache files. You can safely initialize and push your repository:

```powershell
# 1. Initialize git in the project root
git init

# 2. Check git status (notice .env and .venv are ignored)
git status

# 3. Stage all trackable files
git add .

# 4. Create your initial commit
git commit -m "feat: complete AI Document Comparison Assistant with tests"

# 5. Create a repository on GitHub (e.g., ai-document-comparison-assistant)
# 6. Link and push to your GitHub repository:
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-document-comparison-assistant.git
git push -u origin main
```

---

## ❓ Troubleshooting & FAQs

- **Issue: "No machine-readable text could be extracted"**  
  *Cause:* The uploaded PDF consists of scanned images without an OCR text layer.  
  *Solution:* Use a PDF that contains selectable text (e.g. exported from Microsoft Word, Google Docs, or digitally created).

- **Issue: "Gemini API invocation failed"**  
  *Cause:* The API key might be incorrect, inactive, or quota exceeded.  
  *Solution:* Check your key on [Google AI Studio](https://aistudio.google.com/app/apikey) and verify that you have internet connectivity.

- **Issue: "ModuleNotFoundError: No module named 'streamlit'"**  
  *Cause:* The virtual environment is either not activated or dependencies were not installed.  
  *Solution:* Activate your virtual environment (`.\venv\Scripts\Activate.ps1`) and run `pip install -r requirements.txt`.

---

## 📄 License & Attribution

Developed for academic and internship evaluation. Grounded in strict document analysis principles. All rights reserved.
