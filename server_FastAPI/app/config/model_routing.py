"""
Model routing configuration for OmniSearch AI.
Maps user intents to appropriate models and provides fallback routing.
"""

from typing import Dict, List, Optional
from enum import Enum

class IntentType(str, Enum):
    """Supported intent types for model routing."""
    CODE_GENERATION = "code_generation"
    RESEARCH_LONGFORM = "research_longform"
    FACTUAL_SHORT_ANSWER = "factual_short_answer"
    TABLE_QUERY = "table_query"
    IMAGE_ANALYSIS = "image_analysis"
    SUMMARIZE = "summarize"

class ModelProfile:
    """Model profile with capabilities and configuration."""
    
    def __init__(self, name: str, model_path: str, max_tokens: int, temperature: float, capabilities: List[str]):
        self.name = name
        self.model_path = model_path
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.capabilities = capabilities

# Model routing table - maps intents to specific models
MODEL_ROUTING_TABLE = {
    IntentType.CODE_GENERATION: ModelProfile(
        name="codellama",
        model_path="codellama:7b-instruct",
        max_tokens=4096,
        temperature=0.1,
        capabilities=["code_generation", "code_explanation", "debugging"]
    ),
    IntentType.RESEARCH_LONGFORM: ModelProfile(
        name="llama2",
        model_path="llama2:13b",
        max_tokens=8192,
        temperature=0.3,
        capabilities=["research", "analysis", "long_form_writing"]
    ),
    IntentType.FACTUAL_SHORT_ANSWER: ModelProfile(
        name="llama2",
        model_path="llama2:7b",
        max_tokens=2048,
        temperature=0.1,
        capabilities=["factual_qa", "summarization", "extraction"]
    ),
    IntentType.TABLE_QUERY: ModelProfile(
        name="llama2",
        model_path="llama2:7b",
        max_tokens=4096,
        temperature=0.2,
        capabilities=["table_analysis", "data_extraction", "structured_output"]
    ),
    IntentType.IMAGE_ANALYSIS: ModelProfile(
        name="llava",
        model_path="llava:7b",
        max_tokens=2048,
        temperature=0.3,
        capabilities=["image_analysis", "visual_qa", "image_description"]
    ),
    IntentType.SUMMARIZE: ModelProfile(
        name="llama2",
        model_path="llama2:7b",
        max_tokens=2048,
        temperature=0.2,
        capabilities=["summarization", "extraction", "condensation"]
    )
}

def get_model_for_intent(intent: IntentType) -> Optional[ModelProfile]:
    """Get the appropriate model profile for a given intent."""
    return MODEL_ROUTING_TABLE.get(intent)

def get_fallback_model() -> ModelProfile:
    """Get fallback model for ambiguous or unknown intents."""
    return MODEL_ROUTING_TABLE[IntentType.RESEARCH_LONGFORM]

def get_all_intents() -> List[str]:
    """Get list of all supported intent types."""
    return [intent.value for intent in IntentType]

def validate_intent(intent: str) -> bool:
    """Validate if an intent string is supported."""
    try:
        IntentType(intent)
        return True
    except ValueError:
        return False
