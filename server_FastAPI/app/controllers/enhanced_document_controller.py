"""
Enhanced Document Processing Controller for OmniSearch AI.
Handles the complete document processing workflow with Gemini RAG and web enhancement.
"""

import uuid
from typing import List, Optional
from fastapi import HTTPException, UploadFile
from datetime import datetime
from app.services.enhanced_summary_service import EnhancedSummaryService
from app.services.document_converter import DocumentConverterService
from app.services.gemini_rag_service import GeminiRAGService

class EnhancedDocumentController:
    """Controller for enhanced document processing workflows."""
    
    def __init__(self):
        self.enhanced_summary_service = EnhancedSummaryService()
        self.document_converter = DocumentConverterService()
        self.gemini_rag_service = GeminiRAGService()
    
    async def process_single_document(self, file: UploadFile, workspace_id: str = None) -> dict:
        """
        Process a single document through the complete enhanced workflow.
        
        Args:
            file: Uploaded file
            workspace_id: Optional workspace identifier
            
        Returns:
            Complete processing result with enhanced summary
        """
        try:
            # Validate file
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Check if file format is supported
            supported_formats = self.document_converter.get_supported_formats()
            file_extension = "." + file.filename.split(".")[-1].lower()
            
            if file_extension not in supported_formats:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
                )
            
            # Read file content
            file_content = await file.read()
            file.file.seek(0)  # Reset file pointer for potential reuse
            
            # Generate unique file ID
            file_id = str(uuid.uuid4())
            
            # Process document through enhanced workflow
            result = await self.enhanced_summary_service.process_document_with_web_enhancement(
                file=file.file,
                filename=file.filename,
                file_id=file_id
            )
            
            # Add workspace info if provided
            if workspace_id:
                result["workspace_id"] = workspace_id
            
            return {
                "success": True,
                "message": "Document processed successfully through enhanced workflow",
                "data": result
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Enhanced document processing failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Document processing failed: {str(e)}"
            )
    
    async def process_multiple_documents(self, files: List[UploadFile], workspace_id: str = None) -> dict:
        """
        Process multiple documents through the enhanced workflow.
        
        Args:
            files: List of uploaded files
            workspace_id: Optional workspace identifier
            
        Returns:
            Batch processing results with enhanced summaries
        """
        try:
            if not files:
                raise HTTPException(status_code=400, detail="No files provided")
            
            if len(files) > 10:  # Reasonable limit for batch processing
                raise HTTPException(status_code=400, detail="Too many files. Maximum 10 files allowed per batch.")
            
            # Prepare files for batch processing
            file_list = []
            supported_formats = self.document_converter.get_supported_formats()
            
            for file in files:
                if not file.filename:
                    continue
                
                file_extension = "." + file.filename.split(".")[-1].lower()
                if file_extension not in supported_formats:
                    print(f"Skipping unsupported file: {file.filename}")
                    continue
                
                await file.seek(0)
                file_list.append((file.file, file.filename))
            
            if not file_list:
                raise HTTPException(status_code=400, detail="No supported files found in the batch")
            
            # Process all documents
            results = await self.enhanced_summary_service.batch_process_documents(file_list)
            
            # Add workspace info if provided
            if workspace_id:
                for result in results:
                    result["workspace_id"] = workspace_id
            
            # Generate comparative analysis if multiple successful results
            successful_results = [r for r in results if r.get("status") == "success"]
            comparative_analysis = None
            
            if len(successful_results) >= 2:
                try:
                    comparative_analysis = await self.enhanced_summary_service.generate_comparative_analysis(successful_results)
                except Exception as e:
                    print(f"Comparative analysis failed: {e}")
                    comparative_analysis = {"error": "Comparative analysis could not be generated"}
            
            return {
                "success": True,
                "message": f"Processed {len(file_list)} documents through enhanced workflow",
                "data": {
                    "individual_results": results,
                    "comparative_analysis": comparative_analysis,
                    "processing_summary": {
                        "total_submitted": len(files),
                        "total_processed": len(results),
                        "successful_processing": len(successful_results),
                        "failed_processing": len(results) - len(successful_results),
                        "comparative_analysis_generated": comparative_analysis is not None and "error" not in comparative_analysis,
                        "timestamp": datetime.now().isoformat()
                    }
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Batch document processing failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Batch processing failed: {str(e)}"
            )
    
    async def convert_document_to_json(self, file: UploadFile) -> dict:
        """
        Convert a single document to JSON format only (no summarization).
        
        Args:
            file: Uploaded file
            
        Returns:
            JSON representation of the document
        """
        try:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Check supported formats
            supported_formats = self.document_converter.get_supported_formats()
            file_extension = "." + file.filename.split(".")[-1].lower()
            
            if file_extension not in supported_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
                )
            
            # Convert to JSON
            json_document = await self.document_converter.convert_to_json(
                file=file.file,
                filename=file.filename
            )
            
            return {
                "success": True,
                "message": "Document successfully converted to JSON format",
                "data": json_document
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Document to JSON conversion failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"JSON conversion failed: {str(e)}"
            )
    
    async def generate_document_summary_only(self, file: UploadFile) -> dict:
        """
        Generate summary for document without web enhancement.
        
        Args:
            file: Uploaded file
            
        Returns:
            Document summary using Gemini RAG
        """
        try:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # First convert to JSON
            json_document = await self.document_converter.convert_to_json(
                file=file.file,
                filename=file.filename
            )
            
            if "error" in json_document:
                raise HTTPException(status_code=400, detail=f"Document conversion failed: {json_document['error']}")
            
            # Generate summary using Gemini RAG
            summary = await self.gemini_rag_service.generate_document_summary(json_document)
            
            return {
                "success": True,
                "message": "Document summary generated successfully",
                "data": {
                    "document_metadata": {
                        "document_id": json_document.get("document_id"),
                        "filename": json_document.get("filename"),
                        "file_extension": json_document.get("file_extension"),
                        "total_characters": json_document.get("metadata", {}).get("total_characters", 0),
                        "total_words": json_document.get("metadata", {}).get("total_words", 0)
                    },
                    "summary": summary
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Document summary generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Summary generation failed: {str(e)}"
            )
    
    async def get_supported_formats(self) -> dict:
        """Get list of supported document formats."""
        try:
            format_info = self.document_converter.get_format_info()
            
            return {
                "success": True,
                "message": "Supported formats retrieved successfully",
                "data": {
                    "supported_extensions": list(format_info.keys()),
                    "format_details": format_info,
                    "total_formats": len(format_info),
                    "capabilities": [
                        "Document to JSON conversion",
                        "Gemini RAG summarization", 
                        "Web search integration",
                        "Enhanced summary generation",
                        "Batch processing",
                        "Comparative analysis"
                    ]
                }
            }
            
        except Exception as e:
            print(f"Failed to get supported formats: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Could not retrieve supported formats: {str(e)}"
            )
    
    async def get_service_health(self) -> dict:
        """Get health status of all integrated services."""
        try:
            # Get stats from all services
            enhanced_service_stats = self.enhanced_summary_service.get_service_stats()
            converter_stats = {
                "service_name": "DocumentConverterService",
                "supported_formats": len(self.document_converter.get_supported_formats()),
                "format_list": self.document_converter.get_supported_formats()
            }
            rag_service_stats = self.gemini_rag_service.get_service_stats()
            
            return {
                "success": True,
                "message": "Service health check completed",
                "data": {
                    "overall_status": "healthy",
                    "services": {
                        "enhanced_summary_service": enhanced_service_stats,
                        "document_converter": converter_stats,
                        "gemini_rag_service": rag_service_stats
                    },
                    "system_capabilities": [
                        "Multi-format document processing",
                        "Gemini-powered RAG summarization",
                        "Web-enhanced analysis",
                        "Batch processing support",
                        "Comparative document analysis"
                    ],
                    "health_check_timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"Service health check failed: {e}")
            return {
                "success": False,
                "message": "Service health check failed",
                "data": {
                    "overall_status": "degraded",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            }
    
    async def generate_search_tags_for_document(self, file: UploadFile) -> dict:
        """Generate searchable tags for a document."""
        try:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Convert to JSON first
            json_document = await self.document_converter.convert_to_json(
                file=file.file,
                filename=file.filename
            )
            
            if "error" in json_document:
                raise HTTPException(status_code=400, detail=f"Document conversion failed: {json_document['error']}")
            
            # Generate search tags
            search_tags = await self.gemini_rag_service.generate_search_tags(json_document)
            
            return {
                "success": True,
                "message": "Search tags generated successfully",
                "data": {
                    "document_id": json_document.get("document_id"),
                    "filename": json_document.get("filename"),
                    "search_tags": search_tags,
                    "tag_count": len(search_tags),
                    "generation_timestamp": datetime.now().isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"Search tag generation failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Search tag generation failed: {str(e)}"
            )
    
    async def get_urls_from_document(self, file: UploadFile) -> dict:
        """Extract URLs array from document processing without full enhancement."""
        try:
            if not file.filename:
                raise HTTPException(status_code=400, detail="No file provided")
            
            # Check supported formats
            supported_formats = self.document_converter.get_supported_formats()
            file_extension = "." + file.filename.split(".")[-1].lower()
            
            if file_extension not in supported_formats:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file format: {file_extension}. Supported formats: {', '.join(supported_formats)}"
                )
            
            start_time = datetime.now()
            
            # Step 1: Convert document to JSON
            json_document = await self.document_converter.convert_to_json(
                file=file.file,
                filename=file.filename
            )
            
            if "error" in json_document:
                raise HTTPException(status_code=400, detail=f"Document conversion failed: {json_document['error']}")
            
            # Step 2: Generate search tags
            search_tags = await self.gemini_rag_service.generate_search_tags(json_document)
            
            # Step 3: Perform web search to get URLs (limited to 3-4 URLs)
            web_results = await self.enhanced_summary_service._search_web_for_related_content(search_tags)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Extract just the URLs array
            urls_array = []
            for url_info in web_results.get("website_urls", []):
                urls_array.append({
                    "url": url_info.get("url", ""),
                    "title": url_info.get("title", "Unknown Title"),
                    "snippet": url_info.get("snippet", "No description available"),
                    "search_tag": url_info.get("search_tag", "general"),
                    "relevance_score": url_info.get("relevance_score", 0.5)
                })
            
            return {
                "success": True,
                "message": "URLs extracted successfully from document",
                "data": {
                    "document_id": json_document.get("document_id"),
                    "filename": json_document.get("filename"),
                    "file_extension": json_document.get("file_extension"),
                    "search_tags_used": search_tags[:4],  # Show which tags were used
                    "urls": urls_array,  # Array of collected URLs
                    "total_urls_found": len(urls_array),
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"URL extraction failed: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"URL extraction failed: {str(e)}"
            )
