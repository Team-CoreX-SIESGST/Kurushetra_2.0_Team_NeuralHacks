"""
Gemini AI service for OmniSearch AI.
Handles content analysis, tag generation, and intent classification using Google's Gemini API.
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from app.settings import settings

class GeminiService:
    """Service for interacting with Google's Gemini API."""
    
    def __init__(self):
        self.api_key = settings.gemini_api_key
        self.model = None
        self.initialized = False
        
        # Configure safety settings to be more permissive for research content
        self.safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
    
    async def initialize(self):
        """Initialize the Gemini API."""
        if self.initialized:
            return
            
        try:
            if not self.api_key:
                raise ValueError("Gemini API key not found in environment variables")
            
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.initialized = True
            print("✅ Gemini service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize Gemini service: {e}")
            raise
    
    async def generate_content_tags(self, content: str, max_tags: int = 10) -> List[str]:
        """
        Generate searchable tags from content using Gemini.
        
        Args:
            content: Text content to analyze
            max_tags: Maximum number of tags to generate
            
        Returns:
            List of tags suitable for web search
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            prompt = f"""
            Analyze the following content and generate {max_tags} specific, searchable tags that could be used to find relevant websites and resources on the internet. 

            Focus on:
            - Key topics, concepts, and themes
            - Technical terms and jargon
            - Important entities (people, places, organizations)
            - Subject areas and domains
            - Actionable keywords for web search

            Content to analyze:
            {content[:2000]}  # Limit content to avoid token limits

            Return ONLY a JSON array of strings, no other text:
            ["tag1", "tag2", "tag3", ...]
            """
            
            response = await self._make_gemini_request(prompt)
            
            if response:
                # Try to parse JSON response
                try:
                    # Extract JSON array from response
                    response_text = response.strip()
                    if response_text.startswith('[') and response_text.endswith(']'):
                        tags = json.loads(response_text)
                        return [tag.strip() for tag in tags if isinstance(tag, str)][:max_tags]
                    else:
                        # Fallback: extract tags from text response
                        lines = response_text.split('\n')
                        tags = []
                        for line in lines:
                            line = line.strip()
                            if line and not line.startswith('Here') and not line.startswith('Based'):
                                # Remove quotes, bullets, and numbers
                                clean_tag = line.replace('"', '').replace("'", '').replace('- ', '').replace('* ', '')
                                if clean_tag and len(clean_tag) < 50:  # Reasonable tag length
                                    tags.append(clean_tag)
                        return tags[:max_tags]
                except json.JSONDecodeError:
                    print(f"Failed to parse Gemini tags response: {response}")
                    return self._fallback_tags(content, max_tags)
            
            return self._fallback_tags(content, max_tags)
            
        except Exception as e:
            print(f"Tag generation failed: {e}")
            return self._fallback_tags(content, max_tags)
    
    async def classify_intent(self, query: str) -> str:
        """
        Classify the intent of a user query using Gemini.
        
        Args:
            query: User query to classify
            
        Returns:
            Intent classification string
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            prompt = f"""
            Classify the intent of this user query into ONE of these categories:

            1. "code_generation" - User wants code, programming help, or implementation
            2. "summarize" - User wants a summary, main points, or overview
            3. "table_query" - User wants data analysis, statistics, or tabular information
            4. "factual_short_answer" - User wants a brief factual answer or definition
            5. "image_analysis" - User wants to analyze visual content or images
            6. "research_longform" - User wants detailed research, analysis, or comprehensive information

            Query: "{query}"

            Respond with ONLY the category name (e.g., "code_generation"), no other text.
            """
            
            response = await self._make_gemini_request(prompt)
            
            if response:
                intent = response.strip().lower().replace('"', '').replace("'", '')
                valid_intents = [
                    "code_generation", "summarize", "table_query", 
                    "factual_short_answer", "image_analysis", "research_longform"
                ]
                
                if intent in valid_intents:
                    return intent
            
            # Fallback to heuristic classification
            return self._classify_intent_heuristic(query)
            
        except Exception as e:
            print(f"Intent classification failed: {e}")
            return self._classify_intent_heuristic(query)
    
    async def recommend_model(self, content: str, query: str, search_results: List[Dict]) -> Dict[str, Any]:
        """
        Recommend the best model for processing given content and query.
        
        Args:
            content: Content to analyze
            query: User query
            search_results: Search results from web/vector DB
            
        Returns:
            Model recommendation with reasoning
        """
        if not self.initialized:
            await self.initialize()
        
        try:
            # Analyze the complexity and type of content
            complexity_info = {
                "content_length": len(content),
                "num_search_results": len(search_results),
                "query_length": len(query),
                "query_type": await self.classify_intent(query)
            }
            
            prompt = f"""
            Based on the following information, recommend the best AI model configuration:

            Query Type: {complexity_info['query_type']}
            Content Length: {complexity_info['content_length']} characters
            Number of Search Results: {complexity_info['num_search_results']}
            Query: "{query[:200]}..."

            Available model categories:
            1. "lightweight" - Fast, efficient for simple tasks (summaries, factual answers)
            2. "medium" - Balanced performance for moderate complexity
            3. "heavy" - Most capable for complex analysis, research, and generation

            Respond in JSON format:
            {{
                "recommended_model": "lightweight|medium|heavy",
                "reasoning": "Brief explanation of why this model is best",
                "estimated_processing_time": "fast|moderate|slow",
                "confidence": 0.8
            }}
            """
            
            response = await self._make_gemini_request(prompt)
            
            if response:
                try:
                    recommendation = json.loads(response.strip())
                    return {
                        "recommended_model": recommendation.get("recommended_model", "medium"),
                        "reasoning": recommendation.get("reasoning", "Default recommendation"),
                        "estimated_processing_time": recommendation.get("estimated_processing_time", "moderate"),
                        "confidence": float(recommendation.get("confidence", 0.7))
                    }
                except json.JSONDecodeError:
                    pass
            
            # Fallback recommendation based on heuristics
            return self._fallback_model_recommendation(complexity_info)
            
        except Exception as e:
            print(f"Model recommendation failed: {e}")
            return self._fallback_model_recommendation({"query_type": "research_longform"})
    
    async def _make_gemini_request(self, prompt: str, max_retries: int = 3) -> Optional[str]:
        """Make a request to Gemini API with retry logic."""
        
        for attempt in range(max_retries):
            try:
                response = self.model.generate_content(
                    prompt,
                    safety_settings=self.safety_settings,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.3,
                        top_k=20,
                        top_p=0.8,
                        max_output_tokens=1000
                    )
                )
                
                if response.text:
                    return response.text.strip()
                else:
                    print(f"Gemini returned empty response on attempt {attempt + 1}")
                    
            except Exception as e:
                print(f"Gemini API error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def _fallback_tags(self, content: str, max_tags: int) -> List[str]:
        """Generate fallback tags using simple text analysis."""
        words = content.lower().split()
        
        # Filter common words and create basic tags
        common_words = {
            'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
            'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
            'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an'
        }
        
        # Extract potential tags
        word_freq = {}
        for word in words:
            clean_word = ''.join(c for c in word if c.isalnum()).lower()
            if len(clean_word) > 3 and clean_word not in common_words:
                word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
        
        # Sort by frequency and return top tags
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:max_tags]]
    
    def _classify_intent_heuristic(self, query: str) -> str:
        """Fallback heuristic-based intent classification."""
        query_lower = query.lower()
        
        # Code generation keywords
        code_keywords = ['code', 'function', 'programming', 'script', 'algorithm', 'implement']
        if any(keyword in query_lower for keyword in code_keywords):
            return 'code_generation'
        
        # Summarization keywords
        summary_keywords = ['summarize', 'summary', 'main points', 'overview', 'brief']
        if any(keyword in query_lower for keyword in summary_keywords):
            return 'summarize'
        
        # Data/table keywords
        table_keywords = ['table', 'data', 'statistics', 'numbers', 'chart', 'analyze data']
        if any(keyword in query_lower for keyword in table_keywords):
            return 'table_query'
        
        # Short answer keywords
        factual_keywords = ['what is', 'who is', 'when', 'where', 'define', 'definition']
        if any(keyword in query_lower for keyword in factual_keywords):
            return 'factual_short_answer'
        
        # Image keywords
        image_keywords = ['image', 'picture', 'photo', 'visual', 'diagram']
        if any(keyword in query_lower for keyword in image_keywords):
            return 'image_analysis'
        
        # Default to research
        return 'research_longform'
    
    def _fallback_model_recommendation(self, complexity_info: Dict) -> Dict[str, Any]:
        """Provide fallback model recommendation based on heuristics."""
        
        query_type = complexity_info.get('query_type', 'research_longform')
        content_length = complexity_info.get('content_length', 0)
        
        if query_type in ['factual_short_answer', 'summarize'] or content_length < 1000:
            return {
                "recommended_model": "lightweight",
                "reasoning": "Simple query or short content, lightweight model is sufficient",
                "estimated_processing_time": "fast",
                "confidence": 0.8
            }
        elif query_type == 'code_generation' or content_length > 5000:
            return {
                "recommended_model": "heavy",
                "reasoning": "Complex task or large content requires most capable model",
                "estimated_processing_time": "slow",
                "confidence": 0.7
            }
        else:
            return {
                "recommended_model": "medium",
                "reasoning": "Moderate complexity task, balanced model recommended",
                "estimated_processing_time": "moderate",
                "confidence": 0.75
            }
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get statistics about the Gemini service."""
        return {
            "initialized": self.initialized,
            "api_key_configured": bool(self.api_key),
            "model_name": "gemini-2.0-flash-exp" if self.model else None
        }
