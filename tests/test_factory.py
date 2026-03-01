from src.llm.factory import LLMFactory
from unittest.mock import patch
import pytest


async def test_get_client_returns_openai():
    with patch("src.llm.factory.OpenAIClient") as Mock_openai:
        client = LLMFactory.get_client("openai")
        Mock_openai.assert_called_once()
        assert client is Mock_openai.return_value
    LLMFactory._instances.clear()


async def test_get_client_returns_anthropic():
    with patch("src.llm.factory.AnthropicClient") as Mock_Anthropic:
        client = LLMFactory.get_client("anthropic")
        Mock_Anthropic.assert_called_once()
        assert client is Mock_Anthropic.return_value
    LLMFactory._instances.clear()


async def test_singleton_same_instance():
    with patch("src.llm.factory.OpenAIClient") as Mock_openai:
        client1 = LLMFactory.get_client("openai")
        client2 = LLMFactory.get_client("openai")
        assert client1 is client2
    LLMFactory._instances.clear()


async def test_different_providers_different_instances():
    with (
        patch("src.llm.factory.OpenAIClient") as Mock_openai,
        patch("src.llm.factory.AnthropicClient") as Mock_Anthropic,
    ):
        client1 = LLMFactory.get_client("openai")
        client2 = LLMFactory.get_client("anthropic")
        assert client1 is not client2
    LLMFactory._instances.clear()


async def test_invalid_provider_raises():
    with pytest.raises(ValueError):
        with patch("src.llm.factory.AnthropicClient") as Mock_Anthropic:
            client = LLMFactory.get_client("anthropidc")
    LLMFactory._instances.clear()


async def test_default_provider_from_settings():
    with patch("src.llm.factory.OpenAIClient") as Mock_openai:
        client = LLMFactory.get_client()
        Mock_openai.assert_called_once()
        assert client is Mock_openai.return_value
    LLMFactory._instances.clear()
