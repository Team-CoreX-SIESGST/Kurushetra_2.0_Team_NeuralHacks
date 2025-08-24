"""
Model router service for OmniSearch AI.
Handles intent classification and routes tasks to appropriate models.
"""

import json
import aiohttp
from typing import Optional, Dict, Any
from app.config.model_routing import IntentType, get_model_for_intent, get_fallback_model
from app.prompts.templates import format_routing_prompt
from app.config import settings

class ModelRouter:
    """Routes user queries to appropriate models based on intent."""
    
    def __init__(self):
        self.ollama_host = settings.ollama_host
        self.fallback_model = get_fallback_model()
    
    async def classify_intent(self, task_description: str) -> str:
        """Classify the intent of a task using the fallback model."""
        try:
            prompt = format_routing_prompt(task_description)
            
            # Use Ollama API to classify intent
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.fallback_model.model_path,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 10
                    }
                }
                
                async with session.post(f"{self.ollama_host}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        intent = result.get("response", "").strip().lower()
                        
                        # Validate intent
                        if intent in [intent_type.value for intent_type in IntentType]:
                            return intent
                    
            # Fallback to research_longform if classification fails
            return IntentType.RESEARCH_LONGFORM.value
            
        except Exception as e:
            print(f"Intent classification failed: {e}")
            return IntentType.RESEARCH_LONGFORM.value
    
    def get_model_config(self, intent: str) -> Dict[str, Any]:
        """Get model configuration for a given intent."""
        try:
            intent_enum = IntentType(intent)
            model_profile = get_model_for_intent(intent_enum)
            
            if model_profile:
                return {
                    "name": model_profile.name,
                    "model_path": model_profile.model_path,
                    "max_tokens": model_profile.max_tokens,
                    "temperature": model_profile.temperature,
                    "capabilities": model_profile.capabilities
                }
        except ValueError:
            pass
        
        # Return fallback model config
        return {
            "name": self.fallback_model.name,
            "model_path": self.fallback_model.model_path,
            "max_tokens": self.fallback_model.max_tokens,
            "temperature": self.fallback_model.temperature,
            "capabilities": self.fallback_model.capabilities
        }
    
    async def route_query(self, query: str, task_description: str = None) -> Dict[str, Any]:
        """Route a query to the appropriate model."""
        if not task_description:
            task_description = query
        
        intent = await self.classify_intent(task_description)
        model_config = self.get_model_config(intent)
        
        return {
            "intent": intent,
            "model_config": model_config,
            "query": query
        }
