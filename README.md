# ⚖️ AI Document Comparison Assistant

An AI-powered document analysis application built using **Python, Streamlit, Google Gemini API, pypdf, and python-docx**. Upload two PDF documents to generate summaries, identify similarities and differences, detect conflicting information, compare key details, and download a structured comparison report.

## 🚀 Live Demo

**Try the application:**  
https://ai-document-comparison-assistant-eaqetfzesul47rzhcarqt6.streamlit.app/

**GitHub Repository:**  
`ADD_YOUR_GITHUB_REPOSITORY_URL_HERE`

---

## 🌟 Features

### 1. PDF Upload and Validation
- Upload two PDF documents: Document A (Baseline) and Document B (Revised).
- Validate PDF files and handle corrupted or empty documents.
- Detect PDFs without extractable text, including scanned image-only documents.
- Identify identical documents.

### 2. Document Analysis
- Extract text from both PDFs.
- Display page counts, character counts, and word counts.
- Preview extracted text before running the comparison.

### 3. AI-Powered Comparison
Uses the Google Gemini API to analyze the extracted document text and generate:

- **Document A Summary** — overview of the baseline document.
- **Document B Summary** — overview of the revised document.
- **Similarities** — shared terms, provisions, and information.
- **Differences** — additions, removals, modifications, and potential contradictions.
- **Key Details Comparison** — dates, names, amounts, deadlines, and other important values.
- **Overall Conclusion** — summary of the major changes and their potential impact.
- **Limitations** — important caveats and evidence-grounding notes.

AI-generated findings should be reviewed against the original documents, especially for legal, financial, and other high-impact decisions.

### 4. Downloadable Reports
- Download a formatted Microsoft Word (`.docx`) comparison report.
- Export the comparison results as a Markdown (`.md`) report.

### 5. User Interface
- Interactive Streamlit interface.
- Organized comparison sections and document previews.
- Loading indicators and error handling.
- Session reset functionality for new comparisons.

### 6. Automated Testing
The project includes a pytest test suite designed to cover:
- Invalid and missing files.
- Corrupted and empty PDFs.
- PDF text extraction and validation.
- Text chunking and comparison-section parsing.
- API-key and API-error handling.
- DOCX and Markdown report generation.
- Identical and modified documents.

Run the tests locally to confirm the current results before reporting a passing test count.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.10+ | Core application logic |
| Streamlit | Web interface |
| Google Gemini API | AI-powered summarization and comparison |
| `google-genai` or configured Gemini SDK | Gemini API integration |
| pypdf | PDF text extraction |
| python-docx | Word report generation |
| python-dotenv | Local environment variable management |
| pytest | Automated testing |
| Git and GitHub | Version control and source code hosting |
| Streamlit Community Cloud | Application deployment |

---

## 📂 Project Structure

```text
ai-document-comparison-assistant/
├── app.py
├── document_reader.py
├── comparison.py
├── report_generator.py
├── requirements.txt
├── pytest.ini
├── conftest.py
├── .env.example
├── .gitignore
├── README.md
├── tests/
│   └── test_assistant.py
└── sample_documents/
    ├── README.md
    └── create_sample_pdfs.py
```

*The structure above reflects the documented project layout. Include generated sample PDFs only if they exist in your repository.*

---

## 💻 Local Installation and Setup

### Prerequisites

- Python 3.10 or later.
- Git.
- A Google Gemini API key.
- Internet access for API requests.

### Step 1: Clone the repository

Replace the URL with your actual GitHub repository URL.

```powershell
git clone ADD_YOUR_GITHUB_REPOSITORY_URL_HERE
cd ai-document-comparison-assistant
```

If the project is already on your computer, navigate to its folder instead.

### Step 2: Create a virtual environment

```powershell
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt and run:

```cmd
.venv\Scripts\activate.bat
```

### Step 3: Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Configure the Gemini API key

Get an API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

Create a local `.env` file from the example:

```powershell
Copy-Item .env.example .env
```

Add your API key to `.env`, following the variable name expected by your application:

```env
GEMINI_API_KEY=your_actual_api_key
```

**Security:** Never commit your actual `.env` file or expose your API key in source code, screenshots, or public repositories.

### Step 5: Run automated tests

```powershell
python -m pytest -v
```

Review the output and confirm that the tests pass.

### Step 6: Launch the application

```powershell
python -m streamlit run app.py
```

Open the local address displayed in the terminal, usually:

http://localhost:8501

---

## 📖 How to Use the Application

1. Open the [live application](https://ai-document-com
