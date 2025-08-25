"""
Placeholder transformers module (not wired into the app).

This file sketches lightweight interfaces for transformer-based processing
for each content type handled by the system (PDF, DOCX, EXCEL, CSV, TEXT,
JSON, XML, HTML, MARKDOWN, PPTX, IMAGE_OCR) and for the summarization steps
that mirror `RAGSystem` (general, key points, technical, executive, analysis,
and categorization).

Notes:
- This module is intentionally NOT imported anywhere.
- No heavy dependencies are required. All functions are no-op stubs that
  return structured placeholders describing intended behavior.
- You may later replace bodies with real pipelines (e.g., encoder-decoder
  models, LLM calls, layout-aware OCR, table extractors) and then wire them
  in via dependency injection.
"""

from typing import Any, Dict, Optional


def _placeholder_response(name: str, extra: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Return a standardized placeholder response."""
    response: Dict[str, Any] = {
        "status": "not_connected",
        "pipeline": name,
        "message": "This is a placeholder. No actual transformer is executed.",
    }
    if extra:
        response.update(extra)
    return response


# File-type processing stubs

def process_pdf_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("pdf_transformer", {"input_keys": list(extracted.keys())})


def process_docx_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("docx_transformer", {"input_keys": list(extracted.keys())})


def process_excel_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("excel_transformer", {"sheet_names": extracted.get("sheet_names")})


def process_csv_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("csv_transformer", {"columns": extracted.get("columns")})


def process_text_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("text_transformer", {"total_words": extracted.get("total_words")})


def process_json_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("json_transformer", {"keys": extracted.get("keys")})


def process_xml_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("xml_transformer", {"root_tag": extracted.get("root_tag")})


def process_html_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("html_transformer", {"title": extracted.get("title")})


def process_markdown_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("markdown_transformer", {"headings": extracted.get("headings")})


def process_pptx_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("pptx_transformer", {"total_slides": extracted.get("total_slides")})


def process_image_ocr_with_transformer(extracted: Dict[str, Any]) -> Dict[str, Any]:
    return _placeholder_response("image_ocr_transformer", {"has_text": bool(extracted.get("extracted_text"))})


# Summarization and analysis stubs

def generate_general_summary(context: str) -> Dict[str, Any]:
    return _placeholder_response("general_summary_transformer", {"context_preview": context[:120]})


def generate_key_points(context: str) -> Dict[str, Any]:
    return _placeholder_response("key_points_transformer", {"context_preview": context[:120]})


def generate_technical_summary(context: str) -> Dict[str, Any]:
    return _placeholder_response("technical_summary_transformer", {"context_preview": context[:120]})


def generate_executive_summary(context: str) -> Dict[str, Any]:
    return _placeholder_response("executive_summary_transformer", {"context_preview": context[:120]})


def generate_analysis(context: str) -> Dict[str, Any]:
    return _placeholder_response("analysis_transformer", {"context_preview": context[:120]})


def categorize_for_web_search(context: str) -> Dict[str, Any]:
    return _placeholder_response("categorization_transformer", {"context_preview": context[:120]})


