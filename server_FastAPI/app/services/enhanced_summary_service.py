"""
Enhanced Summary service for OmniSearch AI.
Combines document summaries with web search results and sends to Gemini for improved summary generation.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.gemini_service import GeminiService
from app.services.gemini_rag_service import GeminiRAGService
from app.services.web_search import WebSearchService
from app.services.document_converter import DocumentConverterService

class EnhancedSummaryService:
    """Service that combines document analysis with web research for comprehensive summaries."""
    
    def __init__(self):
        self.gemini_service = GeminiService()
        self.gemini_rag_service = GeminiRAGService()
        self.web_search_service = WebSearchService()
        self.document_converter = DocumentConverterService()
    
    async def process_document_with_web_enhancement(self, file, filename: str, file_id: str = None) -> Dict[str, Any]:
        """
        Complete workflow: Convert document -> Generate summary -> Web search -> Enhanced summary.
        
        Args:
            file: File binary data
            filename: Original filename
            file_id: Optional file identifier
            
        Returns:
            Complete analysis with document summary and web-enhanced insights
        """
        try:
            start_time = datetime.now()
            
            # Step 1: Convert document to JSON
            json_document = await self.document_converter.convert_to_json(file, filename, file_id)
            
            if "error" in json_document:
                return {
                    "document_id": json_document.get("document_id", "unknown"),
                    "filename": filename,
                    "status": "conversion_failed",
                    "error": json_document["error"],
                    "processing_time": (datetime.now() - start_time).total_seconds()
                }
            
            # Step 2: Generate initial document summary using Gemini RAG
            document_summary = await self.gemini_rag_service.generate_document_summary(json_document)
            
            # Step 3: Generate search tags for web research
            search_tags = await self.gemini_rag_service.generate_search_tags(json_document)
            
            # Step 4: Perform web search using generated tags
            web_results = await self._search_web_for_related_content(search_tags)
            
            # Step 5: Generate enhanced summary combining document and web data
            enhanced_summary = await self._generate_enhanced_summary(
                document_summary, 
                web_results, 
                json_document
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "document_id": json_document.get("document_id"),
                "filename": filename,
                "status": "success",
                "original_document": {
                    "metadata": json_document.get("metadata", {}),
                    "file_extension": json_document.get("file_extension"),
                    "mime_type": json_document.get("mime_type")
                },
                "document_summary": document_summary,
                "web_research": {
                    "search_tags": search_tags,
                    "website_urls": web_results.get("website_urls", []),
                    "total_urls_found": web_results.get("total_urls", 0)
                },
                "enhanced_summary": enhanced_summary,
                "processing_metadata": {
                    "processing_time": processing_time,
                    "timestamp": datetime.now().isoformat(),
                    "workflow_steps": [
                        "Document Conversion",
                        "Initial Summarization", 
                        "Tag Generation",
                        "Web Search",
                        "Enhanced Summary"
                    ]
                }
            }
            
        except Exception as e:
            print(f"Enhanced document processing failed: {e}")
            return {
                "document_id": file_id or "unknown",
                "filename": filename,
                "status": "processing_failed",
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _search_web_for_related_content(self, search_tags: List[str]) -> Dict[str, Any]:
        """Search the web for content related to document tags."""
        try:
            if not search_tags:
                return {"website_urls": [], "total_urls": 0}
            
            # Use the enhanced web search with tags (reduced to 1 result per tag for 3-4 total URLs)
            web_results = await self.web_search_service.search_by_tags(
                tags=search_tags[:4],  # Limit to max 4 tags
                max_results_per_tag=1  # 1 result per tag = 3-4 total URLs
            )
            
            return web_results
            
        except Exception as e:
            print(f"Web search for related content failed: {e}")
            return {"website_urls": [], "total_urls": 0, "error": str(e)}
    
    async def _generate_enhanced_summary(
        self, 
        document_summary: Dict[str, Any], 
        web_results: Dict[str, Any],
        json_document: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate enhanced summary combining document analysis with web research."""
        try:
            await self.gemini_service.initialize()
            
            # Prepare web content for analysis
            web_content = self._extract_web_content_summary(web_results)
            
            # Create prompt for enhanced summary
            prompt = f"""
            Create an enhanced comprehensive summary by combining document analysis with web research findings.
            
            DOCUMENT ANALYSIS:
            - Filename: {document_summary.get('filename', 'Unknown')}
            - Type: {document_summary.get('document_type', 'Unknown')}
            - Original Summary: {document_summary.get('summary', '')}
            - Key Topics: {', '.join(document_summary.get('key_topics', []))}
            - Main Concepts: {', '.join(document_summary.get('main_concepts', []))}
            - Document Insights: {'; '.join(document_summary.get('insights', []))}
            
            WEB RESEARCH FINDINGS:
            {web_content}
            
            Please create an enhanced analysis in JSON format:
            {{
                "enhanced_summary": "A comprehensive summary that integrates document content with web research context and broader implications",
                "contextual_insights": [
                    "How this document relates to broader trends or topics",
                    "Additional context from web research",
                    "Industry or domain-specific insights"
                ],
                "related_topics": [
                    "Broader topic 1 from web research",
                    "Related concept 2",
                    "Connected theme 3"
                ],
                "practical_applications": [
                    "How this information can be applied",
                    "Potential use cases",
                    "Actionable insights"
                ],
                "further_research_suggestions": [
                    "What to explore next",
                    "Related topics to investigate",
                    "Additional resources to consider"
                ],
                "confidence_score": 0.85,
                "enhancement_quality": "high"
            }}
            
            Focus on:
            1. Connecting document content with broader context from web research
            2. Identifying patterns and relationships not obvious from document alone  
            3. Providing actionable insights and practical applications
            4. Suggesting areas for further exploration
            5. Maintaining accuracy while adding valuable context
            
            Return ONLY the JSON object, no other text.
            """
            
            response = await self.gemini_service._make_gemini_request(prompt)
            
            if response:
                try:
                    # Parse JSON response
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        enhanced_data = json.loads(json_str)
                        
                        # Ensure all required fields exist
                        required_fields = [
                            "enhanced_summary", "contextual_insights", "related_topics",
                            "practical_applications", "further_research_suggestions"
                        ]
                        
                        for field in required_fields:
                            if field not in enhanced_data:
                                enhanced_data[field] = self._get_default_enhanced_field(field)
                        
                        # Add metadata
                        enhanced_data["web_sources_used"] = len(web_results.get("website_urls", []))
                        enhanced_data["document_topics_expanded"] = len(document_summary.get("key_topics", []))
                        enhanced_data["generation_timestamp"] = datetime.now().isoformat()
                        
                        return enhanced_data
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse enhanced summary JSON: {e}")
                    return self._create_fallback_enhanced_summary(document_summary, web_results)
            
            return self._create_fallback_enhanced_summary(document_summary, web_results)
            
        except Exception as e:
            print(f"Enhanced summary generation failed: {e}")
            return self._create_fallback_enhanced_summary(document_summary, web_results)
    
    def _extract_web_content_summary(self, web_results: Dict[str, Any]) -> str:
        """Extract and summarize web search results for context."""
        try:
            website_urls = web_results.get("website_urls", [])
            
            if not website_urls:
                return "No relevant web content found for additional context."
            
            content_summary = f"Found {len(website_urls)} relevant web resources:\\n\\n"
            
            for i, url_info in enumerate(website_urls[:5]):  # Limit to top 5 results
                title = url_info.get("title", "Unknown Title")
                snippet = url_info.get("snippet", "No description available")
                url = url_info.get("url", "")
                search_tag = url_info.get("search_tag", "general")
                
                content_summary += f"{i+1}. {title}\\n"
                content_summary += f"   Source: {url}\\n"
                content_summary += f"   Context: {snippet}\\n"
                content_summary += f"   Related to: {search_tag}\\n\\n"
            
            return content_summary
            
        except Exception as e:
            print(f"Web content extraction failed: {e}")
            return "Web content extraction failed."
    
    def _get_default_enhanced_field(self, field: str):
        """Get default values for enhanced summary fields."""
        defaults = {
            "enhanced_summary": "Enhanced analysis could not be completed with available data.",
            "contextual_insights": ["Document contains relevant information for further analysis"],
            "related_topics": ["Related topics could not be determined"],
            "practical_applications": ["Further analysis needed to determine applications"],
            "further_research_suggestions": ["Consider exploring related topics in your field"],
            "confidence_score": 0.5,
            "enhancement_quality": "limited"
        }
        return defaults.get(field, [])
    
    def _create_fallback_enhanced_summary(
        self, 
        document_summary: Dict[str, Any], 
        web_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create fallback enhanced summary when Gemini processing fails."""
        try:
            web_count = len(web_results.get("website_urls", []))
            key_topics = document_summary.get("key_topics", [])
            
            enhanced_summary = f"This document analysis has been supplemented with {web_count} related web resources. "
            if key_topics:
                enhanced_summary += f"The main topics ({', '.join(key_topics[:3])}) provide context for further research."
            
            return {
                "enhanced_summary": enhanced_summary,
                "contextual_insights": [
                    f"Document summary generated successfully",
                    f"Found {web_count} related web resources",
                    "Manual review recommended for deeper insights"
                ],
                "related_topics": key_topics[:5] if key_topics else ["Manual topic extraction needed"],
                "practical_applications": [
                    "Document provides information for analysis",
                    "Web resources offer additional context",
                    "Combined data useful for research"
                ],
                "further_research_suggestions": [
                    "Review related web resources",
                    "Explore document topics in more detail",
                    "Consider domain-specific analysis"
                ],
                "confidence_score": 0.6,
                "enhancement_quality": "basic",
                "web_sources_used": web_count,
                "document_topics_expanded": len(key_topics),
                "generation_timestamp": datetime.now().isoformat(),
                "fallback_reason": "Enhanced analysis used simplified approach"
            }
            
        except Exception as e:
            print(f"Fallback enhanced summary creation failed: {e}")
            return {
                "enhanced_summary": "Enhanced summary could not be generated",
                "contextual_insights": [],
                "related_topics": [],
                "practical_applications": [],
                "further_research_suggestions": [],
                "confidence_score": 0.1,
                "enhancement_quality": "failed",
                "error": str(e)
            }
    
    async def batch_process_documents(self, files_list: List[tuple]) -> List[Dict[str, Any]]:
        """Process multiple documents with web enhancement."""
        try:
            results = []
            for file, filename in files_list:
                try:
                    result = await self.process_document_with_web_enhancement(file, filename)
                    results.append(result)
                except Exception as e:
                    print(f"Failed to process {filename}: {e}")
                    results.append({
                        "filename": filename,
                        "status": "failed",
                        "error": str(e)
                    })
            return results
        except Exception as e:
            print(f"Batch processing failed: {e}")
            return []
    
    async def generate_comparative_analysis(self, enhanced_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comparative analysis across multiple enhanced summaries."""
        try:
            if len(enhanced_summaries) < 2:
                return {"error": "At least 2 documents required for comparative analysis"}
            
            await self.gemini_service.initialize()
            
            # Prepare data for comparison
            comparison_data = []
            for i, summary in enumerate(enhanced_summaries):
                doc_info = {
                    "document": i + 1,
                    "filename": summary.get("filename", f"Document {i+1}"),
                    "summary": summary.get("enhanced_summary", {}).get("enhanced_summary", ""),
                    "key_topics": summary.get("document_summary", {}).get("key_topics", []),
                    "insights": summary.get("enhanced_summary", {}).get("contextual_insights", [])
                }
                comparison_data.append(doc_info)
            
            prompt = f"""
            Analyze and compare the following enhanced document summaries to find patterns, relationships, and insights.
            
            Documents to Compare:
            {json.dumps(comparison_data, indent=2)}
            
            Provide a comparative analysis in JSON format:
            {{
                "comparative_summary": "Overview of how these documents relate to each other",
                "common_themes": ["Theme 1", "Theme 2", "Theme 3"],
                "unique_insights": [
                    "What makes document 1 unique",
                    "Distinctive aspect of document 2",
                    "Special characteristic of other documents"
                ],
                "cross_document_patterns": [
                    "Pattern observed across multiple documents",
                    "Recurring concept or approach",
                    "Shared methodology or focus"
                ],
                "synthesis_opportunities": [
                    "How these documents could be combined",
                    "Opportunities for integration",
                    "Collaborative insights possible"
                ],
                "research_gaps": [
                    "What's missing across all documents",
                    "Areas that need more coverage",
                    "Potential research directions"
                ]
            }}
            
            Return ONLY the JSON object, no other text.
            """
            
            response = await self.gemini_service._make_gemini_request(prompt)
            
            if response:
                try:
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        comparative_data = json.loads(json_str)
                        
                        comparative_data["documents_analyzed"] = len(enhanced_summaries)
                        comparative_data["analysis_timestamp"] = datetime.now().isoformat()
                        
                        return comparative_data
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse comparative analysis: {e}")
            
            # Fallback comparative analysis
            return {
                "comparative_summary": f"Analysis of {len(enhanced_summaries)} documents completed",
                "common_themes": ["Multiple documents analyzed"],
                "unique_insights": ["Each document provides distinct perspective"],
                "cross_document_patterns": ["Pattern analysis requires manual review"],
                "synthesis_opportunities": ["Documents could be integrated for broader insights"],
                "research_gaps": ["Detailed gap analysis needs human review"],
                "documents_analyzed": len(enhanced_summaries),
                "analysis_timestamp": datetime.now().isoformat(),
                "note": "Simplified analysis provided"
            }
            
        except Exception as e:
            print(f"Comparative analysis failed: {e}")
            return {"error": str(e)}
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about the enhanced summary service."""
        return {
            "service_name": "EnhancedSummaryService",
            "workflow_steps": 5,
            "services_integrated": [
                "DocumentConverterService",
                "GeminiRAGService", 
                "WebSearchService",
                "GeminiService"
            ],
            "supported_formats": self.document_converter.get_supported_formats(),
            "capabilities": [
                "Document to JSON conversion",
                "Gemini RAG summarization",
                "Web search integration",
                "Enhanced summary generation",
                "Batch processing",
                "Comparative analysis"
            ],
            "timestamp": datetime.now().isoformat()
        }
