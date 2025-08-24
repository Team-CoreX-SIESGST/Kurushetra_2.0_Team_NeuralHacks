"""
Summarizer service for OmniSearch AI.
Generates final answers with source citations using LLM models.
"""

import json
import aiohttp
from typing import List, Dict, Any, Optional
from app.prompts.templates import format_summarizer_prompt
from app.settings import settings

class SummarizerService:
    """Service for generating final summaries with source citations."""
    
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.default_model = "llama2:7b-chat"  # Good for summarization
    
    async def generate_summary(self, user_query: str, sources: List[Dict[str, Any]], model_path: str = None) -> Dict[str, Any]:
        """Generate a final summary with source citations."""
        try:
            if not sources:
                return {
                    "answer": "INSUFFICIENT_EVIDENCE",
                    "confidence": 0.0,
                    "sources": [],
                    "code": None
                }
            
            # Prepare sources for summarization
            formatted_sources = []
            for i, source in enumerate(sources):
                formatted_source = {
                    'src_id': f"SRC_{i+1}",
                    'text': source.get('text', source.get('content', '')),
                    'file_id': source.get('file_id', ''),
                    'filename': source.get('filename', ''),
                    'page': source.get('page', ''),
                    'url': source.get('url', ''),
                    'score': source.get('score', 0)
                }
                formatted_sources.append(formatted_source)
            
            # Format prompt for summarization
            prompt = format_summarizer_prompt(user_query, formatted_sources)
            
            # Use specified model or default
            model_to_use = model_path or self.default_model
            
            # Use Ollama API for summarization
            async with aiohttp.ClientSession() as session:
                try:
                    payload = {
                        "model": model_to_use,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 2000
                        }
                    }
                    
                    async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                        if response.status == 200:
                            result = await response.json()
                            response_text = result.get("response", "")
                            
                            # Parse JSON response
                            summary = self._parse_summary_response(response_text, formatted_sources)
                            
                            # Validate summary structure
                            if self._validate_summary(summary):
                                return summary
                finally:
                    await session.close()
                    
            # Fallback: generate basic summary if parsing fails
            return self._generate_fallback_summary(user_query, formatted_sources)
            
        except Exception as e:
            print(f"Summarization failed: {e}")
            return {
                "answer": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.0,
                "sources": [],
                "code": None
            }
    
    def _parse_summary_response(self, response_text: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse the summarizer model response."""
        try:
            # Check if response is empty
            if not response_text or response_text.strip() == "":
                print("Empty response from summarizer")
                return {}
            
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                print(f"No JSON found in response: {response_text[:100]}...")
                return {}
            
            json_str = response_text[json_start:json_end]
            
            # Validate JSON string is not empty
            if not json_str.strip():
                print("Empty JSON string extracted")
                return {}
            
            summary_data = json.loads(json_str)
            
            # Ensure required fields exist
            required_fields = ['answer', 'confidence', 'sources']
            for field in required_fields:
                if field not in summary_data:
                    summary_data[field] = self._get_default_value(field)
            
            # Process sources to include metadata
            processed_sources = []
            for source in summary_data.get('sources', []):
                processed_source = {
                    'src_id': source.get('src_id', ''),
                    'quote': source.get('quote', ''),
                    'url_or_file': source.get('url_or_file', ''),
                    'file_id': '',
                    'filename': '',
                    'page': '',
                    'score': 0
                }
                
                # Try to match with original sources
                for orig_source in sources:
                    if orig_source['src_id'] == source['src_id']:
                        processed_source.update({
                            'file_id': orig_source.get('file_id', ''),
                            'filename': orig_source.get('filename', ''),
                            'page': orig_source.get('page', ''),
                            'score': orig_source.get('score', 0)
                        })
                        break
                
                processed_sources.append(processed_source)
            
            summary_data['sources'] = processed_sources
            
            return summary_data
            
        except Exception as e:
            print(f"Failed to parse summary response: {e}")
            return {}
    
    def _validate_summary(self, summary: Dict[str, Any]) -> bool:
        """Validate summary structure and content."""
        try:
            # Check required fields
            if 'answer' not in summary or 'confidence' not in summary or 'sources' not in summary:
                return False
            
            # Validate confidence score
            confidence = summary.get('confidence', 0)
            if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
                return False
            
            # Validate answer
            answer = summary.get('answer', '')
            if not isinstance(answer, str) or len(answer.strip()) == 0:
                return False
            
            # Check for INSUFFICIENT_EVIDENCE case
            if answer == "INSUFFICIENT_EVIDENCE":
                return confidence == 0.0 and len(summary.get('sources', [])) == 0
            
            return True
            
        except Exception:
            return False
    
    def _get_default_value(self, field: str) -> Any:
        """Get default value for a field."""
        defaults = {
            'answer': 'INSUFFICIENT_EVIDENCE',
            'confidence': 0.0,
            'sources': [],
            'code': None
        }
        return defaults.get(field, None)
    
    def _generate_fallback_summary(self, user_query: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a basic fallback summary when LLM fails."""
        try:
            if not sources:
                return {
                    "answer": "INSUFFICIENT_EVIDENCE",
                    "confidence": 0.0,
                    "sources": [],
                    "code": None
                }
            
            # Create basic summary from top sources
            top_sources = sorted(sources, key=lambda x: x.get('score', 0), reverse=True)[:3]
            
            # Generate simple answer
            answer_parts = []
            for i, source in enumerate(top_sources):
                answer_parts.append(f"[{source['src_id']}] {source['text'][:100]}...")
            
            answer = f"Based on the available sources: {' '.join(answer_parts)}"
            
            # Process sources for output
            processed_sources = []
            for source in top_sources:
                processed_sources.append({
                    'src_id': source['src_id'],
                    'quote': source['text'][:200] + "..." if len(source['text']) > 200 else source['text'],
                    'url_or_file': source.get('filename', '') or source.get('url', ''),
                    'file_id': source.get('file_id', ''),
                    'filename': source.get('filename', ''),
                    'page': source.get('page', ''),
                    'score': source.get('score', 0)
                })
            
            return {
                "answer": answer,
                "confidence": 0.6,  # Lower confidence for fallback
                "sources": processed_sources,
                "code": None
            }
            
        except Exception as e:
            print(f"Fallback summary generation failed: {e}")
            return {
                "answer": "INSUFFICIENT_EVIDENCE",
                "confidence": 0.0,
                "sources": [],
                "code": None
            }
    
    async def batch_summarize(self, queries: List[str], sources_list: List[List[Dict[str, Any]]], model_path: str = None) -> List[Dict[str, Any]]:
        """Generate summaries for multiple queries in batch."""
        try:
            results = []
            for query, sources in zip(queries, sources_list):
                summary = await self.generate_summary(query, sources, model_path)
                results.append(summary)
            return results
        except Exception as e:
            print(f"Batch summarization failed: {e}")
            return []
