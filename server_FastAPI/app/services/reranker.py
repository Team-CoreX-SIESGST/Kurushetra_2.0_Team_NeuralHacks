"""
Reranker service for OmniSearch AI.
Uses cross-encoder models to improve search relevance.
"""

import json
import aiohttp
from typing import List, Dict, Any, Optional
from app.prompts.templates import format_reranker_prompt
from app.settings import settings

class RerankerService:
    """Service for reranking search results using cross-encoder models."""
    
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.fallback_model = "phi3:3.8b"  # Fallback model for reranking
    
    async def rerank_results(self, query: str, candidates: List[Dict[str, Any]], top_k: int = 10) -> List[Dict[str, Any]]:
        """Rerank search candidates based on query relevance."""
        try:
            if not candidates:
                return []
            
            # Prepare snippets for reranking
            snippets = []
            for candidate in candidates:
                snippet = {
                    'id': candidate.get('id', candidate.get('vector_id', 'unknown')),
                    'text': candidate.get('text', candidate.get('content', ''))[:500]  # Limit text length
                }
                snippets.append(snippet)
            
            # Format prompt for reranking
            prompt = format_reranker_prompt(query, snippets)
            
            # Use Ollama API for reranking
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.fallback_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 1000
                    }
                }
                
                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get("response", "")
                        
                        # Parse JSON response
                        reranked_results = self._parse_reranker_response(response_text, candidates)
                        
                        # Sort by score and return top_k
                        reranked_results.sort(key=lambda x: x.get('score', 0), reverse=True)
                        return reranked_results[:top_k]
            
            # Fallback: return original candidates if reranking fails
            return candidates[:top_k]
            
        except Exception as e:
            print(f"Reranking failed: {e}")
            # Return original candidates as fallback
            return candidates[:top_k]
    
    def _parse_reranker_response(self, response_text: str, original_candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse the reranker model response and map back to original candidates."""
        try:
            # Extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                return original_candidates
            
            json_str = response_text[json_start:json_end]
            reranked_data = json.loads(json_str)
            
            # Map reranked scores back to original candidates
            candidate_map = {}
            for candidate in original_candidates:
                candidate_id = str(candidate.get('id', candidate.get('vector_id', 'unknown')))
                candidate_map[candidate_id] = candidate
            
            reranked_results = []
            for item in reranked_data:
                if isinstance(item, dict) and 'id' in item and 'score' in item:
                    candidate_id = str(item['id'])
                    if candidate_id in candidate_map:
                        result = candidate_map[candidate_id].copy()
                        result['rerank_score'] = item.get('score', 0)
                        result['justification'] = item.get('justification', '')
                        reranked_results.append(result)
            
            # Add candidates that weren't reranked with default scores
            for candidate in original_candidates:
                candidate_id = str(candidate.get('id', candidate.get('vector_id', 'unknown')))
                if not any(r.get('id') == candidate_id or r.get('vector_id') == candidate_id for r in reranked_results):
                    result = candidate.copy()
                    result['rerank_score'] = 50  # Default score
                    result['justification'] = 'Not reranked'
                    reranked_results.append(result)
            
            return reranked_results
            
        except Exception as e:
            print(f"Failed to parse reranker response: {e}")
            return original_candidates
    
    async def batch_rerank(self, queries: List[str], candidates_list: List[List[Dict[str, Any]]], top_k: int = 10) -> List[List[Dict[str, Any]]]:
        """Rerank multiple queries and their candidates in batch."""
        try:
            results = []
            for query, candidates in zip(queries, candidates_list):
                reranked = await self.rerank_results(query, candidates, top_k)
                results.append(reranked)
            return results
        except Exception as e:
            print(f"Batch reranking failed: {e}")
            return candidates_list
    
    def calculate_rerank_metrics(self, original_ranks: List[int], reranked_ranks: List[int]) -> Dict[str, float]:
        """Calculate metrics to evaluate reranking performance."""
        try:
            if len(original_ranks) != len(reranked_ranks):
                return {}
            
            # Calculate rank correlation
            n = len(original_ranks)
            if n < 2:
                return {}
            
            # Spearman's rank correlation
            d_squared_sum = sum((original_ranks[i] - reranked_ranks[i]) ** 2 for i in range(n))
            spearman_corr = 1 - (6 * d_squared_sum) / (n * (n**2 - 1))
            
            # Mean reciprocal rank improvement
            mrr_improvement = sum(1/r - 1/original_ranks[i] for i, r in enumerate(reranked_ranks) if r > 0 and original_ranks[i] > 0)
            
            return {
                "spearman_correlation": spearman_corr,
                "mrr_improvement": mrr_improvement,
                "total_candidates": n
            }
            
        except Exception as e:
            print(f"Failed to calculate rerank metrics: {e}")
            return {}
