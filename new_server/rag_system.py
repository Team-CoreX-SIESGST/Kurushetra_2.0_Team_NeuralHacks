import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from web_search import WebSearchEngine

class RAGSystem:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        self.web_search_engine = WebSearchEngine()
        
        if not self.api_key:
            print("Warning: GEMINI_API_KEY not found. Set it as environment variable or pass it to the constructor.")
    
    def check_api_status(self) -> str:
        """Check if API key is configured"""
        return "configured" if self.api_key else "not_configured"
    
    def get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        return datetime.now().isoformat()
    
    async def generate_summary(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary using Gemini API with RAG-style processing"""
        if not self.api_key:
            return {
                "error": "API key not configured",
                "fallback_summary": self._generate_fallback_summary(extracted_data)
            }
        
        try:
            # Prepare context from extracted data
            context = self._prepare_context(extracted_data)
            
            # Generate different types of summaries
            summaries = {}
            
            # 1. General Summary
            summaries["general"] = await self._call_gemini_api(
                self._create_general_summary_prompt(context)
            )
            
            # 2. Key Points Summary
            summaries["key_points"] = await self._call_gemini_api(
                self._create_key_points_prompt(context)
            )
            
            # 3. Technical Summary (if applicable)
            if self._is_technical_content(extracted_data):
                summaries["technical"] = await self._call_gemini_api(
                    self._create_technical_summary_prompt(context)
                )
            
            # 4. Executive Summary
            summaries["executive"] = await self._call_gemini_api(
                self._create_executive_summary_prompt(context)
            )
            
            # 5. Content Analysis
            summaries["analysis"] = await self._call_gemini_api(
                self._create_analysis_prompt(context)
            )
            
            # 6. Content Categorization for Web Search
            content_categories = await self._call_gemini_api(
                self._create_categorization_prompt(context)
            )
            
            return {
                "summaries": summaries,
                "metadata": {
                    "generated_at": self.get_current_timestamp(),
                    "content_type": extracted_data.get("content_type", "unknown"),
                    "content_hash": self._generate_content_hash(context),
                    "source_file": extracted_data.get("file_metadata", {}).get("original_filename", "unknown")
                },
                "content_stats": self._generate_content_stats(context)
            }
        
        except Exception as e:
            return {
                "error": f"Failed to generate summary: {str(e)}",
                "fallback_summary": self._generate_fallback_summary(extracted_data)
            }
    
    async def generate_summary_with_urls(self, extracted_data: Dict[str, Any], include_urls: bool = True) -> Dict[str, Any]:
        """Generate comprehensive summary with related web URLs"""
        # First generate the standard summary
        summary_result = await self.generate_summary(extracted_data)
        
        if not include_urls or "error" in summary_result:
            return summary_result
        
        try:
            # Get context for web search
            context = self._prepare_context(extracted_data)
            
            # Generate content categorization for better web search
            ai_categories = None
            try:
                content_categories_response = await self._call_gemini_api(
                    self._create_categorization_prompt(context)
                )
                # Parse AI categories from JSON response
                ai_categories = json.loads(content_categories_response)
            except Exception as e:
                print(f"Failed to get AI categories: {str(e)}")
            
            # Find related web URLs using AI categories
            web_search_result = await self.web_search_engine.find_relevant_urls(
                context, extracted_data, max_urls=10, ai_categories=ai_categories
            )
            
            # Add web search results to the summary
            summary_result["related_web_resources"] = web_search_result
            
            # Update metadata to indicate URLs were included
            summary_result["metadata"]["includes_web_resources"] = True
            summary_result["metadata"]["web_search_timestamp"] = web_search_result.get("search_metadata", {}).get("search_timestamp")
            
            return summary_result
            
        except Exception as e:
            # If web search fails, return the original summary with error info
            summary_result["web_search_error"] = f"Failed to fetch related URLs: {str(e)}"
            summary_result["metadata"]["includes_web_resources"] = False
            return summary_result
    
    def _prepare_context(self, extracted_data: Dict[str, Any]) -> str:
        """Prepare context string from extracted data"""
        context_parts = []
        content_type = extracted_data.get("content_type", "")
        
        if content_type == "pdf":
            for page in extracted_data.get("text_content", []):
                context_parts.append(f"Page {page['page']}: {page['content']}")
        
        elif content_type == "docx":
            for para in extracted_data.get("paragraphs", []):
                context_parts.append(para["text"])
            
            # Add tables if present
            for i, table in enumerate(extracted_data.get("tables", [])):
                context_parts.append(f"Table {i+1}: {str(table)}")
        
        elif content_type == "excel":
            for sheet_name, sheet_data in extracted_data.get("sheets", {}).items():
                context_parts.append(f"Sheet '{sheet_name}': {len(sheet_data.get('data', []))} rows")
                # Add sample data
                sample_data = sheet_data.get("data", [])[:5]  # First 5 rows
                context_parts.append(f"Sample data: {json.dumps(sample_data, indent=2)}")
        
        elif content_type == "csv":
            context_parts.append(f"CSV with {extracted_data.get('total_rows', 0)} rows and {extracted_data.get('total_columns', 0)} columns")
            sample_data = extracted_data.get("data", [])[:10]  # First 10 rows
            context_parts.append(f"Sample data: {json.dumps(sample_data, indent=2)}")
        
        elif content_type == "text":
            context_parts.append(extracted_data.get("content", ""))
        
        elif content_type == "json":
            context_parts.append(f"JSON Data: {json.dumps(extracted_data.get('data', {}), indent=2)}")
        
        elif content_type == "xml":
            context_parts.append(f"XML Data: {json.dumps(extracted_data.get('data', {}), indent=2)}")
        
        elif content_type == "html":
            context_parts.append(f"Title: {extracted_data.get('title', 'No title')}")
            context_parts.append(f"Content: {extracted_data.get('text_content', '')}")
            context_parts.append(f"Links: {len(extracted_data.get('links', []))} links found")
        
        elif content_type == "markdown":
            context_parts.append(extracted_data.get("text_content", ""))
        
        elif content_type == "pptx":
            for slide in extracted_data.get("slides", []):
                context_parts.append(f"Slide {slide['slide_number']}: {slide['title']}")
                for content in slide.get("content", []):
                    context_parts.append(content)
        
        elif content_type == "image_ocr":
            context_parts.append(f"Extracted text from image: {extracted_data.get('extracted_text', '')}")
        
        return "\n\n".join(context_parts)
    
    def _create_general_summary_prompt(self, context: str) -> str:
        """Create prompt for general summary"""
        return f"""
        Please provide a comprehensive summary of the following document content:
        
        {context}
        
        Please include:
        1. Main topic and purpose
        2. Key information and findings
        3. Important details and context
        4. Overall conclusion or takeaways
        
        Keep the summary informative but concise.
        """
    
    def _create_key_points_prompt(self, context: str) -> str:
        """Create prompt for key points extraction"""
        return f"""
        Extract and list the key points from the following content:
        
        {context}
        
        Format the response as a bulleted list of the most important points, insights, or findings.
        Focus on actionable information and critical details.
        """
    
    def _create_technical_summary_prompt(self, context: str) -> str:
        """Create prompt for technical summary"""
        return f"""
        Analyze the following content and provide a technical summary:
        
        {context}
        
        Focus on:
        1. Technical concepts and terminology
        2. Data structures and formats
        3. Technical specifications or requirements
        4. Implementation details
        5. Technical recommendations or conclusions
        """
    
    def _create_executive_summary_prompt(self, context: str) -> str:
        """Create prompt for executive summary"""
        return f"""
        Create an executive summary of the following content:
        
        {context}
        
        The summary should be suitable for senior management and include:
        1. High-level overview
        2. Key business implications
        3. Important decisions or recommendations
        4. Strategic insights
        5. Bottom-line impact
        
        Keep it concise and business-focused.
        """
    
    def _create_analysis_prompt(self, context: str) -> str:
        """Create prompt for content analysis"""
        return f"""
        Analyze the following content and provide insights:
        
        {context}
        
        Please provide:
        1. Content type and structure analysis
        2. Quality and completeness assessment
        3. Key themes or patterns identified
        4. Potential use cases or applications
        5. Recommendations for further action
        """
    
    def _create_categorization_prompt(self, context: str) -> str:
        """Create prompt for content categorization for web search"""
        return f"""
        Analyze the following content and categorize it for web resource discovery. 
        Respond ONLY with a JSON object containing relevant domains, topics, and search terms.
        
        {context}
        
        Return a JSON object with this exact structure:
        {{
            "primary_domains": ["domain1", "domain2", "domain3"],
            "topics": ["topic1", "topic2", "topic3", "topic4", "topic5"],
            "search_terms": ["search_term1", "search_term2", "search_term3"],
            "academic_fields": ["field1", "field2"],
            "tools_technologies": ["tool1", "tool2", "tool3"]
        }}
        
        Guidelines:
        - primary_domains: Broad categories like "artificial_intelligence", "data_science", "finance", "healthcare", "marketing", "software_engineering", "research", etc.
        - topics: Specific topics within those domains
        - search_terms: Key terms that would yield good web search results
        - academic_fields: Related academic disciplines
        - tools_technologies: Specific tools, libraries, platforms, or technologies mentioned or relevant
        
        Example domains: artificial_intelligence, machine_learning, data_science, natural_language_processing, computer_vision, cybersecurity, blockchain, cloud_computing, software_engineering, web_development, mobile_development, database_management, business_analytics, finance, healthcare, education, marketing, psychology, biology, chemistry, physics, mathematics, statistics, economics, management, etc.
        """
    
    def _is_technical_content(self, extracted_data: Dict[str, Any]) -> bool:
        """Determine if content is technical in nature"""
        content_type = extracted_data.get("content_type", "")
        
        # Technical file types
        if content_type in ["json", "xml", "csv", "excel"]:
            return True
        
        # Check for technical keywords in text content
        technical_keywords = [
            "API", "database", "algorithm", "code", "programming", 
            "software", "system", "architecture", "framework", 
            "configuration", "deployment", "technical", "specification"
        ]
        
        context = self._prepare_context(extracted_data).lower()
        return any(keyword.lower() in context for keyword in technical_keywords)
    
    async def _call_gemini_api(self, prompt: str) -> str:
        """Make API call to Gemini"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "topK": 40,
                        "topP": 0.95,
                        "maxOutputTokens": 1024,
                    }
                }
                
                headers = {
                    "Content-Type": "application/json",
                }
                
                url = f"{self.base_url}?key={self.api_key}"
                
                async with session.post(url, json=payload, headers=headers) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"API request failed: {response.status} - {error_text}")
        
        except Exception as e:
            raise Exception(f"Gemini API call failed: {str(e)}")
    
    def _generate_fallback_summary(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic summary without AI when API is unavailable"""
        content_type = extracted_data.get("content_type", "unknown")
        
        summary = {
            "type": "fallback_summary",
            "content_type": content_type,
            "basic_info": {}
        }
        
        if content_type == "pdf":
            summary["basic_info"] = {
                "total_pages": extracted_data.get("total_pages", 0),
                "has_content": len(extracted_data.get("text_content", [])) > 0
            }
        
        elif content_type == "docx":
            summary["basic_info"] = {
                "total_paragraphs": extracted_data.get("total_paragraphs", 0),
                "total_tables": extracted_data.get("total_tables", 0),
                "author": extracted_data.get("document_metadata", {}).get("author")
            }
        
        elif content_type == "excel":
            summary["basic_info"] = {
                "total_sheets": extracted_data.get("total_sheets", 0),
                "sheet_names": extracted_data.get("sheet_names", [])
            }
        
        elif content_type == "csv":
            summary["basic_info"] = {
                "total_rows": extracted_data.get("total_rows", 0),
                "total_columns": extracted_data.get("total_columns", 0),
                "columns": extracted_data.get("columns", [])
            }
        
        elif content_type == "text":
            summary["basic_info"] = {
                "total_lines": extracted_data.get("total_lines", 0),
                "total_words": extracted_data.get("total_words", 0),
                "total_characters": extracted_data.get("total_characters", 0)
            }
        
        return summary
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_content_stats(self, context: str) -> Dict[str, Any]:
        """Generate basic content statistics"""
        words = context.split()
        sentences = context.split('.')
        
        return {
            "word_count": len(words),
            "character_count": len(context),
            "sentence_count": len(sentences),
            "average_sentence_length": len(words) / len(sentences) if sentences else 0,
            "unique_words": len(set(word.lower().strip('.,!?";') for word in words))
        }
