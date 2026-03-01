from src.llm.anthropic_client import AnthropicClient
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage
from src.core.config import settings
from pydantic import SecretStr
from unittest.mock import AsyncMock, Mock
import pytest
from unittest.mock import patch


async def test_generate_success(monkeypatch, sample_messages, generation_config):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", SecretStr("fake-key"))
    llm = AnthropicClient()
    result = Mock()
    result.content = []
    content = Mock()
    content.text = "Hello, World!"
    result.content.append(content)
    result.stop_reason = "stop"
    result.usage.input_tokens = 10
    result.usage.output_tokens = 5
    result.model = "claude21(Fake)"
    result.model_dump.return_value = {"fake": "response"}

    llm.client.messages.create = AsyncMock(return_value=result)
    with patch("src.llm.anthropic_client.TextBlock", Mock):
        mock_func = llm.generate(sample_messages, generation_config)
        response = await mock_func
        assert response.content == "Hello, World!"
        assert response.usage.prompt_tokens == 10
        assert response.usage.completion_tokens == 5
        assert response.usage.total_tokens == 15
        assert response.model_name == "claude21(Fake)"
        assert response.raw_response == {"fake": "response"}
        assert response.finish_reason == "stop"
