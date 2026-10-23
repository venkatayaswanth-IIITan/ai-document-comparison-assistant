"""
app.py
------
Main Streamlit application for the AI Document Comparison Assistant.
Provides a modern, responsive user interface for PDF upload, validation,
text extraction preview, side-by-side AI comparative analysis, and DOCX reporting.
"""

from datetime import datetime
import os
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables
load_dotenv()

# Internal project modules
from document_reader import extract_pdf_data, DocumentData
from comparison import (
    compare_documents,
    generate_single_summary,
    get_default_api_key,
    AVAILABLE_MODELS,
    DEFAULT_MODEL,
    ComparisonResult,
)
from report_generator import create_comparison_docx


# -----------------------------------------------------------------------------
# Streamlit Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Document Comparison Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------------------------------------------------------
# Custom Styling (CSS)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }

    /* Header Banner Styling */
    .hero-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #1E3A8A 100%);
        border-radius: 16px;
        padding: 2.2rem 2.4rem;
        color: #FFFFFF;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.4rem;
        letter-spacing: -0.02em;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #94A3B8;
        font-weight: 400;
        line-height: 1.5;
        margin-bottom: 0;
    }
    .badge-pill {
        display: inline-block;
        background: rgba(59, 130, 246, 0.2);
        color: #60A5FA;
        border: 1px solid rgba(96, 165, 250, 0.3);
        padding: 0.2rem 0.7rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.6rem;
    }

    /* Document Card Styling */
    .doc-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1.4rem;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.2rem;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .doc-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }
    .doc-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #1E293B;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .stat-row {
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
        padding-top: 0.8rem;
        border-top: 1px solid #F1F5F9;
    }
    .stat-item {
        flex: 1;
        background: #F8FAFC;
        border-radius: 8px;
        padding: 0.6rem 0.8rem;
        text-align: center;
    }
    .stat-label {
        font-size: 0.75rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        font-weight: 500;
    }
    .stat-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.1rem;
    }

    /* Result Tab Container */
    .result-section-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 1.8rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.03);
        margin-top: 1rem;
        line-height: 1.7;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding: 0.55rem 1.4rem;
        transition: all 0.2s ease;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        margin-top: 3.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid #E2E8F0;
        color: #94A3B8;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Initialize Session State
# -----------------------------------------------------------------------------
if "comparison_result" not in st.session_state:
    st.session_state.comparison_result = None

if "doc_a_data" not in st.session_state:
    st.session_state.doc_a_data = None

if "doc_b_data" not in st.session_state:
    st.session_state.doc_b_data = None

if "last_compared_keys" not in st.session_state:
    st.session_state.last_compared_keys = None


def reset_session():
    """Clears all comparison data and uploads from session state."""
    st.session_state.comparison_result = None
    st.session_state.doc_a_data = None
    st.session_state.doc_b_data = None
    st.session_state.last_compared_keys = None
    st.rerun()


# -----------------------------------------------------------------------------
# Sidebar Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Settings & Configuration")

    # API Key Handling (Reads from .env or manual user override)
    env_api_key = get_default_api_key()
    has_env_key = bool(env_api_key)

    if has_env_key:
        st.success("✅ Gemini API Key detected from `.env` file.")
        api_key_input = st.text_input(
            "API Key (Leave blank to use `.env` key)",
            value="",
            type="password",
            placeholder="Using key from .env",
            help="Your key is securely loaded from .env. You may type a different key here to override it.",
        )
        active_api_key = api_key_input.strip() if api_key_input.strip() else env_api_key
    else:
        st.warning("⚠️ No `GEMINI_API_KEY` found in `.env`.")
        api_key_input = st.text_input(
            "Enter Google Gemini API Key",
            type="password",
            placeholder="AIzaSy...",
            help="Get your free API key at https://aistudio.google.com/app/apikey",
        )
        active_api_key = api_key_input.strip()

    st.markdown("---")

    # Model Selection
    selected_model = st.selectbox(
        "🧠 Gemini Model",
        options=AVAILABLE_MODELS,
        index=0,
        help="Select the Gemini model variant. 'gemini-2.5-flash' is recommended for speed and accuracy.",
    )

    st.markdown("---")

    # Reset Option
    if st.button("🔄 Reset / Clear Session", use_container_width=True, on_click=reset_session):
        st.toast("Session reset successfully.", icon="🧹")

    st.markdown("---")
    st.markdown(
        """
        **About AI Document Comparison**
        - Compares baseline vs. revised PDFs.
        - Identifies additions, removals & contradictions.
        - Extracts dates, amounts, names, & deadlines.
        - Strictly grounded in extracted text.
        """
    )


# -----------------------------------------------------------------------------
# Main Header
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero-header">
        <span class="badge-pill">Enterprise AI Analysis</span>
        <div class="hero-title">⚖️ AI Document Comparison Assistant</div>
        <p class="hero-subtitle">
            Upload two PDF documents to instantly detect changes, verify clauses,
            surface contradictions, and generate audit-ready comparison reports grounded strictly in document evidence.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Step 1: Upload Documents
# -----------------------------------------------------------------------------
st.markdown("### 📁 Step 1: Upload Comparison Documents")
col_upload_a, col_upload_b = st.columns(2)

with col_upload_a:
    uploaded_file_a = st.file_uploader(
        "📄 Document A (Original / Baseline)",
        type=["pdf"],
        key="file_uploader_a",
        help="Upload the baseline or original PDF document.",
    )

with col_upload_b:
    uploaded_file_b = st.file_uploader(
        "📄 Document B (Revised / Secondary)",
        type=["pdf"],
        key="file_uploader_b",
        help="Upload the revised or comparative PDF document.",
    )


# -----------------------------------------------------------------------------
# Process & Validate Uploaded Documents
# -----------------------------------------------------------------------------
doc_a: DocumentData = None
doc_b: DocumentData = None

if uploaded_file_a:
    doc_a = extract_pdf_data(uploaded_file_a)
    st.session_state.doc_a_data = doc_a

if uploaded_file_b:
    doc_b = extract_pdf_data(uploaded_file_b)
    st.session_state.doc_b_data = doc_b


# -----------------------------------------------------------------------------
# Step 2: Document Inspection & Previews
# -----------------------------------------------------------------------------
if doc_a or doc_b:
    st.markdown("### 📊 Step 2: Document Verification & Statistics")
    stat_col_a, stat_col_b = st.columns(2)

    # Document A Card
    with stat_col_a:
        if doc_a:
            if doc_a.is_valid:
                st.markdown(
                    f"""
                    <div class="doc-card">
                        <div class="doc-title">
                            <span>📄 Document A: {doc_a.filename}</span>
                            <span style="color: #10B981; font-size: 0.85rem; font-weight: 600;">✓ Valid PDF</span>
                        </div>
                        <div class="stat-row">
                            <div class="stat-item">
                                <div class="stat-label">Pages</div>
                                <div class="stat-value">{doc_a.page_count}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Characters</div>
                                <div class="stat-value">{doc_a.char_count:,}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Words</div>
                                <div class="stat-value">{doc_a.word_count:,}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if doc_a.warning_message:
                    st.warning(f"⚠️ {doc_a.warning_message}")

                with st.expander(f"👁️ Preview Extracted Text ({doc_a.filename})"):
                    st.text_area(
                        "Document A Extracted Text",
                        value=doc_a.preview,
                        height=160,
                        disabled=True,
                        key="preview_text_a",
                    )
            else:
                st.error(f"❌ **Document A Error:** {doc_a.error_message}")
        else:
            st.info("Waiting for Document A upload...")

    # Document B Card
    with stat_col_b:
        if doc_b:
            if doc_b.is_valid:
                st.markdown(
                    f"""
                    <div class="doc-card">
                        <div class="doc-title">
                            <span>📄 Document B: {doc_b.filename}</span>
                            <span style="color: #10B981; font-size: 0.85rem; font-weight: 600;">✓ Valid PDF</span>
                        </div>
                        <div class="stat-row">
                            <div class="stat-item">
                                <div class="stat-label">Pages</div>
                                <div class="stat-value">{doc_b.page_count}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Characters</div>
                                <div class="stat-value">{doc_b.char_count:,}</div>
                            </div>
                            <div class="stat-item">
                                <div class="stat-label">Words</div>
                                <div class="stat-value">{doc_b.word_count:,}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                if doc_b.warning_message:
                    st.warning(f"⚠️ {doc_b.warning_message}")

                with st.expander(f"👁️ Preview Extracted Text ({doc_b.filename})"):
                    st.text_area(
                        "Document B Extracted Text",
                        value=doc_b.preview,
                        height=160,
                        disabled=True,
                        key="preview_text_b",
                    )
            else:
                st.error(f"❌ **Document B Error:** {doc_b.error_message}")
        else:
            st.info("Waiting for Document B upload...")


# -----------------------------------------------------------------------------
# Step 3: Run AI Comparison
# -----------------------------------------------------------------------------
st.markdown("---")
st.markdown("### ⚡ Step 3: Execute AI Comparative Analysis")

can_proceed = (
    doc_a is not None
    and doc_b is not None
    and doc_a.is_valid
    and doc_b.is_valid
)

if can_proceed and doc_a.text.strip() == doc_b.text.strip():
    st.info("ℹ️ **Identical Content Detected:** Document A and Document B contain identical text. The analysis will verify that all provisions, dates, and terms are unchanged.")


if not active_api_key:
    st.info("💡 **Please provide a Gemini API Key** in the sidebar to enable AI comparison.")

btn_col1, btn_col2 = st.columns([2, 5])
with btn_col1:
    compare_button = st.button(
        "🚀 Run Document Comparison",
        type="primary",
        disabled=(not can_proceed or not active_api_key),
        use_container_width=True,
    )

if not can_proceed:
    if not (doc_a and doc_b):
        st.caption("Please upload both Document A and Document B to start comparison.")
    elif doc_a and not doc_a.is_valid:
        st.caption("Please resolve issues with Document A before proceeding.")
    elif doc_b and not doc_b.is_valid:
        st.caption("Please resolve issues with Document B before proceeding.")

if compare_button and can_proceed and active_api_key:
    with st.spinner("Analyzing documents with Google Gemini AI... Please wait..."):
        result: ComparisonResult = compare_documents(
            doc_a_name=doc_a.filename,
            doc_a_text=doc_a.text,
            doc_b_name=doc_b.filename,
            doc_b_text=doc_b.text,
            api_key=active_api_key,
            model_name=selected_model,
        )

        st.session_state.comparison_result = result
        st.session_state.last_compared_keys = (doc_a.filename, doc_b.filename, selected_model)

        if result.is_success:
            st.success("✅ Comparison analysis completed successfully!")
        else:
            st.error(f"❌ Comparison failed: {result.error_message}")


# -----------------------------------------------------------------------------
# Step 4: Display Results & Reports
# -----------------------------------------------------------------------------
current_result: ComparisonResult = st.session_state.comparison_result

if current_result and current_result.is_success:
    st.markdown("---")
    st.markdown("### 📑 Step 4: Comparison Results & Analysis")

    # Render Tabs for Section Navigation
    tabs = st.tabs([
        "📄 Summary: Doc A",
        "📄 Summary: Doc B",
        "🤝 Similarities",
        "⚡ Differences & Changes",
        "🔍 Key Details Matrix",
        "🎯 Overall Conclusion",
        "⚠️ Limitations & Grounding",
    ])

    with tabs[0]:
        st.markdown(f"#### Executive Summary: {doc_a.filename if doc_a else 'Document A'}")
        st.markdown(
            f'<div class="result-section-box">{current_result.summary_a}</div>',
            unsafe_allow_html=True,
        )

    with tabs[1]:
        st.markdown(f"#### Executive Summary: {doc_b.filename if doc_b else 'Document B'}")
        st.markdown(
            f'<div class="result-section-box">{current_result.summary_b}</div>',
            unsafe_allow_html=True,
        )

    with tabs[2]:
        st.markdown("#### Shared Provisions & Key Similarities")
        st.markdown(
            f'<div class="result-section-box">{current_result.similarities}</div>',
            unsafe_allow_html=True,
        )

    with tabs[3]:
        st.markdown("#### Differences, Additions, Removals & Contradictions")
        st.markdown(
            f'<div class="result-section-box">{current_result.differences}</div>',
            unsafe_allow_html=True,
        )

    with tabs[4]:
        st.markdown("#### Key Details Comparison (Dates, Names, Amounts, Deadlines)")
        st.markdown(
            f'<div class="result-section-box">{current_result.key_details}</div>',
            unsafe_allow_html=True,
        )

    with tabs[5]:
        st.markdown("#### Strategic Conclusion & Impact Assessment")
        st.markdown(
            f'<div class="result-section-box">{current_result.overall_conclusion}</div>',
            unsafe_allow_html=True,
        )

    with tabs[6]:
        st.markdown("#### Evidence Grounding & Document Limitations")
        st.markdown(
            f'<div class="result-section-box">{current_result.limitations}</div>',
            unsafe_allow_html=True,
        )

    # -------------------------------------------------------------------------
    # Step 5: Downloadable DOCX & Markdown Reports
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.markdown("### 📥 Step 5: Export & Download Comparison Report")

    # Prepare metadata dictionaries for report generator
    doc_a_meta = {
        "filename": doc_a.filename if doc_a else "Document A",
        "page_count": doc_a.page_count if doc_a else 0,
        "char_count": doc_a.char_count if doc_a else 0,
        "word_count": doc_a.word_count if doc_a else 0,
    }
    doc_b_meta = {
        "filename": doc_b.filename if doc_b else "Document B",
        "page_count": doc_b.page_count if doc_b else 0,
        "char_count": doc_b.char_count if doc_b else 0,
        "word_count": doc_b.word_count if doc_b else 0,
    }

    comparison_dict = {
        "summary_a": current_result.summary_a,
        "summary_b": current_result.summary_b,
        "similarities": current_result.similarities,
        "differences": current_result.differences,
        "key_details": current_result.key_details,
        "overall_conclusion": current_result.overall_conclusion,
        "limitations": current_result.limitations,
    }

    # Generate DOCX stream in memory
    try:
        docx_stream = create_comparison_docx(
            doc_a_meta=doc_a_meta,
            doc_b_meta=doc_b_meta,
            comparison_data=comparison_dict,
            model_name=current_result.model_used,
        )

        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"comparison_report_{timestamp_str}.docx"

        d_col1, d_col2 = st.columns([2, 5])
        with d_col1:
            st.download_button(
                label="📄 Download DOCX Report",
                data=docx_stream.getvalue(),
                file_name=report_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="primary",
                use_container_width=True,
            )
        with d_col2:
            # Also offer quick Markdown export
            markdown_report = f"""# AI Document Comparison Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Model:** {current_result.model_used}  
**Document A:** {doc_a_meta['filename']} ({doc_a_meta['page_count']} pages, {doc_a_meta['char_count']} chars)  
**Document B:** {doc_b_meta['filename']} ({doc_b_meta['page_count']} pages, {doc_b_meta['char_count']} chars)  

---

## 1. Summary of Document A
{current_result.summary_a}

## 2. Summary of Document B
{current_result.summary_b}

## 3. Similarities
{current_result.similarities}

## 4. Differences & Contradictions
{current_result.differences}

## 5. Key Details Comparison
{current_result.key_details}

## 6. Overall Conclusion
{current_result.overall_conclusion}

## 7. Limitations & Grounding
{current_result.limitations}
"""
            st.download_button(
                label="📝 Download Markdown (.md) Report",
                data=markdown_report,
                file_name=f"comparison_report_{timestamp_str}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    except Exception as docx_err:
        st.error(f"Error generating DOCX report: {docx_err}")


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="app-footer">
        <strong>AI Document Comparison Assistant</strong> • Built with Streamlit, Google Gemini AI, pypdf & python-docx •
        Internship Project Implementation
    </div>
    """,
    unsafe_allow_html=True,
)
