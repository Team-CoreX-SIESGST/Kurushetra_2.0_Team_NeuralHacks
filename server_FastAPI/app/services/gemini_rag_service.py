"""
Gemini RAG Summary service for OmniSearch AI.
Takes JSON document data and generates comprehensive summaries using Gemini's RAG approach.
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.services.gemini_service import GeminiService

class GeminiRAGService:
    """Service for generating document summaries using Gemini RAG approach."""
    
    def __init__(self):
        self.gemini_service = GeminiService()
    
    async def generate_document_summary(self, json_document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a JSON document using Gemini RAG.
        
        Args:
            json_document: JSON representation of the document
            
        Returns:
            Comprehensive summary with key insights, topics, and metadata
        """
        try:
            await self.gemini_service.initialize()
            
            # Extract relevant content for summarization
            content = self._extract_content_for_summary(json_document)
            
            if not content:
                return {
                    "document_id": json_document.get("document_id", "unknown"),
                    "summary": "No content available for summarization",
                    "key_topics": [],
                    "insights": [],
                    "confidence": 0.0,
                    "error": "No extractable content found"
                }
            
            # Generate comprehensive summary using Gemini
            summary_result = await self._generate_comprehensive_summary(content, json_document)
            
            return {
                "document_id": json_document.get("document_id", "unknown"),
                "filename": json_document.get("filename", "unknown"),
                "document_type": json_document.get("metadata", {}).get("document_type", "unknown"),
                "summary": summary_result.get("summary", ""),
                "key_topics": summary_result.get("key_topics", []),
                "insights": summary_result.get("insights", []),
                "main_concepts": summary_result.get("main_concepts", []),
                "potential_queries": summary_result.get("potential_queries", []),
                "confidence": summary_result.get("confidence", 0.7),
                "processing_timestamp": datetime.now().isoformat(),
                "content_stats": {
                    "total_characters": json_document.get("metadata", {}).get("total_characters", 0),
                    "total_words": json_document.get("metadata", {}).get("total_words", 0),
                    "document_format": json_document.get("file_extension", "unknown")
                }
            }
            
        except Exception as e:
            print(f"Document summary generation failed: {e}")
            return {
                "document_id": json_document.get("document_id", "unknown"),
                "summary": "Summary generation failed due to technical issues",
                "key_topics": [],
                "insights": [],
                "confidence": 0.0,
                "error": str(e),
                "processing_timestamp": datetime.now().isoformat()
            }
    
    def _extract_content_for_summary(self, json_document: Dict[str, Any]) -> str:
        """Extract the most relevant content from the JSON document for summarization."""
        try:
            content_data = json_document.get("content", {})
            raw_text = content_data.get("raw_text", "")
            
            if not raw_text:
                # Try to extract from structured content
                structured_content = content_data.get("structured_content", {})
                content_type = structured_content.get("type", "")
                
                if content_type == "csv":
                    # For CSV, create a descriptive text
                    headers = structured_content.get("headers", [])
                    data = structured_content.get("data", [])
                    raw_text = f"CSV dataset with columns: {', '.join(headers)}. Contains {len(data)} rows of data."
                    
                    # Add sample data if available
                    if data and len(data) > 0:
                        sample_row = data[0]
                        raw_text += f" Sample data: {json.dumps(sample_row)}"
                
                elif content_type in ["pdf", "docx", "odt", "rtf"]:
                    # Extract from paragraphs if available
                    paragraphs = structured_content.get("paragraphs", [])
                    if paragraphs:
                        if isinstance(paragraphs[0], dict):
                            raw_text = " ".join([p.get("text", "") for p in paragraphs])
                        else:
                            raw_text = " ".join(paragraphs)
                
                elif content_type == "markdown":
                    # Use the raw markdown content
                    raw_text = content_data.get("raw_text", "")
                    if not raw_text:
                        paragraphs = structured_content.get("paragraphs", [])
                        raw_text = " ".join(paragraphs)
            
            # Limit content length for Gemini processing
            max_length = 4000  # Leave room for prompt
            if len(raw_text) > max_length:
                raw_text = raw_text[:max_length] + "..."
            
            return raw_text
            
        except Exception as e:
            print(f"Content extraction failed: {e}")
            return ""
    
    async def _generate_comprehensive_summary(self, content: str, json_document: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive summary using Gemini."""
        try:
            document_type = json_document.get("metadata", {}).get("document_type", "unknown")
            filename = json_document.get("filename", "document")
            
            prompt = f"""
            Analyze the following document content and provide a comprehensive summary in JSON format.
            
            Document Information:
            - Filename: {filename}
            - Type: {document_type}
            - Format: {json_document.get("file_extension", "unknown")}
            
            Content to analyze:
            {content}
            
            Please provide a detailed analysis in the following JSON format:
            {{
                "summary": "A comprehensive 3-4 sentence summary of the main content and purpose",
                "key_topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
                "insights": [
                    "Key insight or finding 1",
                    "Key insight or finding 2", 
                    "Key insight or finding 3"
                ],
                "main_concepts": [
                    "Primary concept 1",
                    "Primary concept 2",
                    "Primary concept 3"
                ],
                "potential_queries": [
                    "What question might someone ask about this content?",
                    "Another relevant question about this document",
                    "A third potential search query"
                ],
                "confidence": 0.85
            }}
            
            Focus on:
            1. The document's main purpose and key information
            2. Important topics, themes, and concepts
            3. Actionable insights or findings
            4. What someone might want to know about this content
            5. Technical terms or specialized knowledge if present
            
            Return ONLY the JSON object, no other text.
            """
            
            response = await self.gemini_service._make_gemini_request(prompt)
            
            if response:
                # Parse the JSON response
                try:
                    # Extract JSON from response
                    json_start = response.find('{')
                    json_end = response.rfind('}') + 1
                    
                    if json_start != -1 and json_end > json_start:
                        json_str = response[json_start:json_end]
                        summary_data = json.loads(json_str)
                        
                        # Validate and ensure required fields
                        required_fields = ["summary", "key_topics", "insights", "main_concepts", "potential_queries"]
                        for field in required_fields:
                            if field not in summary_data:
                                summary_data[field] = self._get_default_field_value(field)
                        
                        # Ensure confidence is valid
                        if "confidence" not in summary_data or not isinstance(summary_data["confidence"], (int, float)):
                            summary_data["confidence"] = 0.7
                        
                        return summary_data
                        
                except json.JSONDecodeError as e:
                    print(f"Failed to parse Gemini response as JSON: {e}")
                    return self._create_fallback_summary(content, document_type)
            
            # Fallback if no valid response
            return self._create_fallback_summary(content, document_type)
            
        except Exception as e:
            print(f"Comprehensive summary generation failed: {e}")
            return self._create_fallback_summary(content, document_type)
    
    def _get_default_field_value(self, field: str):
        """Get default value for missing fields."""
        defaults = {
            "summary": "Document contains text content that requires manual review.",
            "key_topics": [],
            "insights": [],
            "main_concepts": [],
            "potential_queries": [],
            "confidence": 0.5
        }
        return defaults.get(field, [])
    
    def _create_fallback_summary(self, content: str, document_type: str) -> Dict[str, Any]:
        """Create a basic fallback summary when Gemini fails."""
        try:
            # Create basic summary from content analysis
            word_count = len(content.split())
            char_count = len(content)
            
            # Simple keyword extraction
            words = content.lower().split()
            common_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'}
            
            # Count word frequency
            word_freq = {}
            for word in words:
                clean_word = ''.join(c for c in word if c.isalnum()).lower()
                if len(clean_word) > 3 and clean_word not in common_words:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Get top keywords
            top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            key_topics = [word for word, _ in top_keywords]
            
            summary = f"This {document_type} document contains {word_count} words and {char_count} characters. "
            if key_topics:
                summary += f"Key topics appear to include: {', '.join(key_topics[:3])}."
            
            return {
                "summary": summary,
                "key_topics": key_topics,
                "insights": [f"Document contains {word_count} words", f"Content type: {document_type}"],
                "main_concepts": key_topics[:3],
                "potential_queries": [f"What is this {document_type} about?", "What are the main topics?"],
                "confidence": 0.4
            }
            
        except Exception as e:
            print(f"Fallback summary creation failed: {e}")
            return {
                "summary": "Document analysis could not be completed",
                "key_topics": [],
                "insights": [],
                "main_concepts": [],
                "potential_queries": [],
                "confidence": 0.1
            }
    
    async def batch_summarize_documents(self, json_documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate summaries for multiple documents."""
        try:
            summaries = []
            for doc in json_documents:
                summary = await self.generate_document_summary(doc)
                summaries.append(summary)
            return summaries
        except Exception as e:
            print(f"Batch document summarization failed: {e}")
            return []
    
    async def generate_search_tags(self, json_document: Dict[str, Any]) -> List[str]:
        """Generate searchable tags from document content using Gemini."""
        try:
            content = self._extract_content_for_summary(json_document)
            if not content:
                return []
            
            # Use Gemini service to generate tags
            tags = await self.gemini_service.generate_content_tags(content, max_tags=10)
            return tags
            
        except Exception as e:
            print(f"Search tag generation failed: {e}")
            return []
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG service."""
        return {
            "service_name": "GeminiRAGService",
            "gemini_initialized": self.gemini_service.initialized,
            "max_content_length": 4000,
            "supported_document_types": ["pdf", "docx", "txt", "md", "csv", "rtf", "odt"],
            "timestamp": datetime.now().isoformat()
        }
