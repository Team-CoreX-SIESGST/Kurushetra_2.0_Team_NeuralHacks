"""
Enhanced Document Processing Routes for OmniSearch AI.
API endpoints for the complete document processing workflow with Gemini RAG and web enhancement.
"""

from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from app.controllers.enhanced_document_controller import EnhancedDocumentController
from app.utils.api_response import create_response

# Create router
router = APIRouter(prefix="/api/v1/enhanced-documents", tags=["Enhanced Document Processing"])

# Initialize controller
enhanced_doc_controller = EnhancedDocumentController()

@router.post("/process/single")
async def process_single_document(
    file: UploadFile = File(...),
    workspace_id: Optional[str] = Form(None)
):
    """
    Process a single document through the complete enhanced workflow.
    
    This endpoint:
    1. Converts the document to JSON format
    2. Generates a comprehensive summary using Gemini RAG
    3. Creates search tags for web research
    4. Performs web search for related content
    5. Generates an enhanced summary combining document and web data
    
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.process_single_document(file, workspace_id)
        return create_response(
            success=result["success"], 
            message=result["message"], 
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.post("/process/batch")
async def process_multiple_documents(
    files: List[UploadFile] = File(...),
    workspace_id: Optional[str] = Form(None)
):
    """
    Process multiple documents through the enhanced workflow with comparative analysis.
    
    This endpoint processes up to 10 documents simultaneously and provides:
    - Individual enhanced summaries for each document
    - Comparative analysis across all successfully processed documents
    - Processing statistics and metadata
    
    **Maximum files:** 10 per batch
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.process_multiple_documents(files, workspace_id)
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.post("/convert/json")
async def convert_document_to_json(file: UploadFile = File(...)):
    """
    Convert a document to structured JSON format without summarization.
    
    This endpoint only performs document-to-JSON conversion with:
    - Structured content extraction
    - Metadata generation  
    - Format-specific processing
    - No AI summarization or web enhancement
    
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.convert_document_to_json(file)
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.post("/summarize/basic")
async def generate_document_summary_only(file: UploadFile = File(...)):
    """
    Generate a basic document summary using Gemini RAG without web enhancement.
    
    This endpoint provides:
    - Document conversion to JSON
    - Gemini RAG-powered summarization
    - Key topics and insights extraction
    - No web search or enhanced analysis
    
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.generate_document_summary_only(file)
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.post("/tags/generate")
async def generate_search_tags_for_document(file: UploadFile = File(...)):
    """
    Generate searchable tags for a document using Gemini AI.
    
    This endpoint:
    - Converts document to JSON format
    - Analyzes content using Gemini
    - Generates relevant search tags
    - Returns tags suitable for web search
    
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.generate_search_tags_for_document(file)
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.post("/urls/extract")
async def get_urls_from_document(file: UploadFile = File(...)):
    """
    Extract related URLs from document processing without full enhancement.
    
    This endpoint processes the document to JSON, generates search tags,
    performs web searches, and returns an array of 3-4 relevant URLs
    without generating the full enhanced summary.
    
    Returns:
    - Array of related URLs with titles, snippets, and relevance scores
    - Search tags used for web discovery
    - Processing metadata and timing
    
    **Supported formats:** .txt, .md, .pdf, .docx, .rtf, .odt, .csv
    """
    try:
        result = await enhanced_doc_controller.get_urls_from_document(file)
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.get("/formats/supported")
async def get_supported_formats():
    """
    Get list of supported document formats and system capabilities.
    
    Returns:
    - Supported file extensions
    - MIME type mappings
    - System capabilities
    - Format-specific details
    """
    try:
        result = await enhanced_doc_controller.get_supported_formats()
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except HTTPException as e:
        return create_response(
            success=False,
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

@router.get("/health")
async def get_service_health():
    """
    Get health status of all integrated services.
    
    Returns:
    - Overall system health
    - Individual service statistics
    - System capabilities
    - Service integration status
    """
    try:
        result = await enhanced_doc_controller.get_service_health()
        return create_response(
            success=result["success"],
            message=result["message"],
            data=result["data"]
        )
    except Exception as e:
        return create_response(
            success=False,
            message=f"Health check failed: {str(e)}",
            status_code=500
        )

@router.get("/")
async def enhanced_document_service_info():
    """
    Get information about the Enhanced Document Processing Service.
    
    Returns basic service information and available endpoints.
    """
    return create_response(
        success=True,
        message="Enhanced Document Processing Service",
        data={
            "service_name": "Enhanced Document Processing API",
            "version": "1.0.0",
            "description": "Complete document processing workflow with Gemini RAG and web enhancement",
            "capabilities": [
                "Multi-format document conversion to JSON",
                "Gemini-powered RAG summarization",
                "Intelligent web search integration", 
                "Enhanced summary generation",
                "Batch processing with comparative analysis",
                "Search tag generation"
            ],
            "supported_formats": [".txt", ".md", ".pdf", ".docx", ".rtf", ".odt", ".csv"],
            "endpoints": [
                {
                    "path": "/process/single",
                    "method": "POST", 
                    "description": "Process single document through complete enhanced workflow"
                },
                {
                    "path": "/process/batch",
                    "method": "POST",
                    "description": "Process multiple documents with comparative analysis"
                },
                {
                    "path": "/convert/json",
                    "method": "POST",
                    "description": "Convert document to JSON format only"
                },
                {
                    "path": "/summarize/basic",
                    "method": "POST",
                    "description": "Generate basic summary using Gemini RAG"
                },
                {
                    "path": "/tags/generate",
                    "method": "POST",
                    "description": "Generate searchable tags for document"
                },
                {
                    "path": "/urls/extract",
                    "method": "POST",
                    "description": "Extract related URLs array from document without full enhancement"
                },
                {
                    "path": "/formats/supported",
                    "method": "GET",
                    "description": "Get supported file formats and capabilities"
                },
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "Check service health and status"
                }
            ],
            "workflow_steps": [
                "1. Document Upload and Validation",
                "2. Document to JSON Conversion", 
                "3. Gemini RAG Summarization",
                "4. Search Tag Generation",
                "5. Web Search for Related Content",
                "6. Enhanced Summary Generation"
            ],
            "key_features": [
                "Gemini-only AI processing (no Llama dependency)",
                "Comprehensive web research integration",
                "Multi-document comparative analysis",
                "Structured JSON document representation",
                "Scalable batch processing",
                "Real-time health monitoring"
            ]
        }
    )
