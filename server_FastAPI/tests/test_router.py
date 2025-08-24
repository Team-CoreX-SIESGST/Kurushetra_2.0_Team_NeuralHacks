"""
Tests for the model router functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.services.model_router import ModelRouter
from app.config.model_routing import IntentType, get_model_for_intent, get_fallback_model

class TestModelRouter:
    """Test cases for ModelRouter class."""
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        with patch('app.services.model_router.settings') as mock_settings:
            mock_settings.ollama_host = "http://localhost:11434"
            yield mock_settings
    
    @pytest.fixture
    def router(self, mock_settings):
        """Create ModelRouter instance for testing."""
        return ModelRouter()
    
    def test_router_initialization(self, router):
        """Test router initialization."""
        assert router.ollama_host == "http://localhost:11434"
        assert router.fallback_model is not None
    
    @pytest.mark.asyncio
    async def test_classify_intent_success(self, router):
        """Test successful intent classification."""
        mock_response = {"response": "code_generation"}
        
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.status = 200
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
            
            intent = await router.classify_intent("Write a Python function")
            assert intent == "code_generation"
    
    @pytest.mark.asyncio
    async def test_classify_intent_fallback(self, router):
        """Test intent classification fallback."""
        with patch('aiohttp.ClientSession') as mock_session:
            mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value.status = 500
            
            intent = await router.classify_intent("Write a Python function")
            assert intent == IntentType.RESEARCH_LONGFORM.value
    
    @pytest.mark.asyncio
    async def test_classify_intent_exception(self, router):
        """Test intent classification with exception."""
        with patch('aiohttp.ClientSession', side_effect=Exception("Connection failed")):
            intent = await router.classify_intent("Write a Python function")
            assert intent == IntentType.RESEARCH_LONGFORM.value
    
    def test_get_model_config_valid_intent(self, router):
        """Test getting model config for valid intent."""
        config = router.get_model_config("code_generation")
        assert config["name"] == "codellama"
        assert "code_generation" in config["capabilities"]
    
    def test_get_model_config_invalid_intent(self, router):
        """Test getting model config for invalid intent."""
        config = router.get_model_config("invalid_intent")
        assert config["name"] == router.fallback_model.name
    
    @pytest.mark.asyncio
    async def test_route_query(self, router):
        """Test complete query routing."""
        with patch.object(router, 'classify_intent', return_value="research_longform"):
            result = await router.route_query("Research topic", "Research this topic")
            
            assert result["intent"] == "research_longform"
            assert "model_config" in result
            assert result["query"] == "Research topic"
    
    @pytest.mark.asyncio
    async def test_route_query_no_task_description(self, router):
        """Test query routing without task description."""
        with patch.object(router, 'classify_intent', return_value="summarize"):
            result = await router.route_query("Summarize this")
            
            assert result["intent"] == "summarize"
            assert result["task_description"] == "Summarize this"

class TestModelRoutingConfig:
    """Test cases for model routing configuration."""
    
    def test_get_model_for_intent(self):
        """Test getting model for specific intent."""
        model = get_model_for_intent(IntentType.CODE_GENERATION)
        assert model.name == "codellama"
        assert model.model_path == "codellama:7b-instruct"
    
    def test_get_fallback_model(self):
        """Test getting fallback model."""
        model = get_fallback_model()
        assert model.name == "llama2"
        assert model.model_path == "llama2:13b"
    
    def test_get_all_intents(self):
        """Test getting all supported intents."""
        intents = get_all_intents()
        assert "code_generation" in intents
        assert "research_longform" in intents
        assert "summarize" in intents
    
    def test_validate_intent(self):
        """Test intent validation."""
        assert validate_intent("code_generation") == True
        assert validate_intent("research_longform") == True
        assert validate_intent("invalid_intent") == False
    
    def test_model_profiles(self):
        """Test model profile configurations."""
        # Test code generation model
        code_model = get_model_for_intent(IntentType.CODE_GENERATION)
        assert code_model.max_tokens == 4096
        assert code_model.temperature == 0.1
        
        # Test research model
        research_model = get_model_for_intent(IntentType.RESEARCH_LONGFORM)
        assert research_model.max_tokens == 8192
        assert research_model.temperature == 0.3
        
        # Test summarization model
        summary_model = get_model_for_intent(IntentType.SUMMARIZE)
        assert summary_model.max_tokens == 2048
        assert summary_model.temperature == 0.2

if __name__ == "__main__":
    pytest.main([__file__])
