"""
comparison.py
-------------
Integrates with the Google Gemini API to produce grounded, evidence-based
summaries, similarity & difference analyses, key detail matrices, and conclusions.
"""

from dataclasses import dataclass
import os
import re
from typing import Dict, Optional
import warnings
from dotenv import load_dotenv

# Filter deprecation FutureWarning from legacy fallback library
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

# Load local environment variables if available
load_dotenv()


# Supported Gemini Models
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]
DEFAULT_MODEL = "gemini-2.5-flash"


@dataclass
class ComparisonResult:
    """Holds the complete parsed comparison output across all required sections."""
    summary_a: str
    summary_b: str
    similarities: str
    differences: str
    key_details: str
    overall_conclusion: str
    limitations: str
    raw_response: str
    model_used: str
    is_success: bool = True
    error_message: Optional[str] = None


def get_default_api_key() -> str:
    """Retrieves the Gemini API key from environment variables or empty string."""
    return os.getenv("GEMINI_API_KEY", "").strip()


def _call_gemini_api(prompt: str, api_key: str, model_name: str = DEFAULT_MODEL) -> str:
    """
    Calls the Gemini API with automatic fallback between the modern 'google-genai' SDK
    and the legacy 'google-generativeai' SDK for seamless environment compatibility.
    """
    if not api_key or not api_key.strip():
        raise ValueError("Google Gemini API key is required. Please provide a valid key.")

    clean_key = api_key.strip()
    errors = []

    # Attempt 1: Modern google-genai SDK
    try:
        from google import genai
        client = genai.Client(api_key=clean_key)
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )
        if response and response.text:
            return response.text
    except ImportError:
        pass
    except Exception as e:
        errors.append(f"google-genai error: {str(e)}")

    # Attempt 2: Legacy google-generativeai SDK
    try:
        import google.generativeai as genai_legacy
        genai_legacy.configure(api_key=clean_key)
        model = genai_legacy.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        if response and response.text:
            return response.text
    except ImportError:
        pass
    except Exception as e:
        errors.append(f"google-generativeai error: {str(e)}")

    # If both failed or libraries missing
    if errors:
        raise RuntimeError(f"Gemini API invocation failed: {' | '.join(errors)}")
    else:
        raise ImportError(
            "Neither 'google-genai' nor 'google-generativeai' package could be loaded. "
            "Please install dependencies via: pip install -r requirements.txt"
        )


def generate_single_summary(
    doc_name: str,
    doc_text: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL
) -> str:
    """
    Generates a standalone, grounded summary of a single document.
    """
    prompt = f"""You are a professional document analyst. Provide a clear, comprehensive summary of the document below.

STRICT GROUNDING RULES:
1. Rely ONLY on the provided text below.
2. Do not invent, extrapolate, or assume any facts not stated in the document.
3. If an important detail (e.g., date, party name, price, deadline) is absent, state: "Not mentioned in the document".

DOCUMENT NAME: {doc_name}
DOCUMENT CONTENT:
\"\"\"
{doc_text}
\"\"\"

Please structure the summary with these sections:
- Executive Overview
- Main Purpose & Scope
- Key Parties & Entities
- Core Terms & Requirements
- Important Dates & Deadlines
- Financial Terms (if any)
"""
    return _call_gemini_api(prompt, api_key, model_name)


def compare_documents(
    doc_a_name: str,
    doc_a_text: str,
    doc_b_name: str,
    doc_b_text: str,
    api_key: str,
    model_name: str = DEFAULT_MODEL
) -> ComparisonResult:
    """
    Performs an in-depth, side-by-side comparative analysis of two documents.
    """
    prompt = f"""You are an expert AI Document Comparison and Legal/Contract Analyst.
You are comparing two documents:
- Document A (Original / Baseline): "{doc_a_name}"
- Document B (Revised / Secondary): "{doc_b_name}"

CRITICAL GROUNDING AND EVIDENCE RULES:
1. Rely ONLY on the explicit text provided for Document A and Document B.
2. DO NOT hallucinate, infer, or assume facts not present in either document.
3. If specific information is missing or ambiguous, state explicitly: "Not specified in [Document A / Document B]".
4. Point out direct contradictions, additions, removals, and unchanged provisions with precision.

DOCUMENT A ("{doc_a_name}") CONTENT:
\"\"\"
{doc_a_text}
\"\"\"

DOCUMENT B ("{doc_b_name}") CONTENT:
\"\"\"
{doc_b_text}
\"\"\"

Please analyze both documents and output your analysis EXACTLY using the seven delimited sections below.
Do not omit any section header.

===SECTION 1: SUMMARY OF DOCUMENT A===
- Purpose and overview of Document A.
- Core terms, parties, and obligations established in Document A.

===SECTION 2: SUMMARY OF DOCUMENT B===
- Purpose and overview of Document B.
- Core terms, parties, and obligations established in Document B.

===SECTION 3: SIMILARITIES===
- Shared provisions, identical requirements, and unchanged terms across both documents.
- Common objectives and mutual definitions.

===SECTION 4: DIFFERENCES & CONTRADICTIONS===
- Additions: What is present in Document B that was not in Document A?
- Removals: What was omitted from Document B that was present in Document A?
- Contradictions & Revisions: Conflicting clauses, changed obligations, or altered conditions between Document A and Document B.

===SECTION 5: KEY DETAILS COMPARISON===
Provide a side-by-side comparison (or bulleted comparative breakdown) specifically addressing:
1. Dates & Deadlines (Doc A vs. Doc B)
2. Names & Parties (Doc A vs. Doc B)
3. Financial Amounts, Fees, & Pricing (Doc A vs. Doc B)
4. Scope, Deliverables, & Requirements (Doc A vs. Doc B)
5. Penalties, Liabilities, & Termination (Doc A vs. Doc B)

===SECTION 6: OVERALL CONCLUSION===
- High-level synthesis of what the changes signify (e.g., stricter terms, expanded scope, updated timeline, liability shift).
- Impact assessment for the stakeholders involved.

===SECTION 7: LIMITATIONS & EVIDENCE GROUNDING===
- List any gaps, unreadable text, ambiguous terms, or missing context in either document.
- Explicit confirmation that this comparison is strictly limited to the extracted text provided.
"""

    try:
        raw_text = _call_gemini_api(prompt, api_key, model_name)
        sections = parse_comparison_sections(raw_text)

        return ComparisonResult(
            summary_a=sections.get("summary_a", "Summary A not generated."),
            summary_b=sections.get("summary_b", "Summary B not generated."),
            similarities=sections.get("similarities", "Similarities section not generated."),
            differences=sections.get("differences", "Differences section not generated."),
            key_details=sections.get("key_details", "Key Details section not generated."),
            overall_conclusion=sections.get("overall_conclusion", "Conclusion not generated."),
            limitations=sections.get("limitations", "Limitations not generated."),
            raw_response=raw_text,
            model_used=model_name,
            is_success=True,
            error_message=None
        )
    except Exception as e:
        return ComparisonResult(
            summary_a="",
            summary_b="",
            similarities="",
            differences="",
            key_details="",
            overall_conclusion="",
            limitations="",
            raw_response="",
            model_used=model_name,
            is_success=False,
            error_message=str(e)
        )


def parse_comparison_sections(raw_text: str) -> Dict[str, str]:
    """
    Parses the delimited raw output from Gemini into structured section strings.
    """
    section_patterns = [
        ("summary_a", r"===SECTION 1: SUMMARY OF DOCUMENT A===(.*?)(?====SECTION 2|\Z)"),
        ("summary_b", r"===SECTION 2: SUMMARY OF DOCUMENT B===(.*?)(?====SECTION 3|\Z)"),
        ("similarities", r"===SECTION 3: SIMILARITIES===(.*?)(?====SECTION 4|\Z)"),
        ("differences", r"===SECTION 4: DIFFERENCES & CONTRADICTIONS===(.*?)(?====SECTION 5|\Z)"),
        ("key_details", r"===SECTION 5: KEY DETAILS COMPARISON===(.*?)(?====SECTION 6|\Z)"),
        ("overall_conclusion", r"===SECTION 6: OVERALL CONCLUSION===(.*?)(?====SECTION 7|\Z)"),
        ("limitations", r"===SECTION 7: LIMITATIONS & EVIDENCE GROUNDING===(.*?)(?=\Z)"),
    ]

    parsed: Dict[str, str] = {}
    for key, pattern in section_patterns:
        match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
        if match:
            parsed[key] = match.group(1).strip()
        else:
            parsed[key] = ""

    # If delimiter parsing yielded empty results (model formatted slightly differently),
    # fallback to intelligent heading parsing
    if not any(parsed.values()):
        parsed = _fallback_section_parser(raw_text)

    return parsed


def _fallback_section_parser(text: str) -> Dict[str, str]:
    """Fallback parser for markdown heading formats (e.g. ## Section 1 or ## Summary)."""
    result = {
        "summary_a": "",
        "summary_b": "",
        "similarities": "",
        "differences": "",
        "key_details": "",
        "overall_conclusion": "",
        "limitations": "",
    }

    chunks = re.split(r"\n(?=#{1,3}\s+)", text)
    for chunk in chunks:
        lower_chunk = chunk.lower()
        if "summary of document a" in lower_chunk or ("summary" in lower_chunk and "document a" in lower_chunk):
            result["summary_a"] = chunk.strip()
        elif "summary of document b" in lower_chunk or ("summary" in lower_chunk and "document b" in lower_chunk):
            result["summary_b"] = chunk.strip()
        elif "similarit" in lower_chunk:
            result["similarities"] = chunk.strip()
        elif "differenc" in lower_chunk or "contradiction" in lower_chunk:
            result["differences"] = chunk.strip()
        elif "key detail" in lower_chunk or "detail" in lower_chunk:
            result["key_details"] = chunk.strip()
        elif "conclusion" in lower_chunk:
            result["overall_conclusion"] = chunk.strip()
        elif "limitation" in lower_chunk:
            result["limitations"] = chunk.strip()

    # If still mostly empty, store full text under summary_a to avoid data loss
    if not any(result.values()):
        result["summary_a"] = text

    return result
