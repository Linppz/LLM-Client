import pytest
from pydantic import SecretStr
from src.llm.openai_client import OpenAIClient
from src.core.config import settings
from unittest.mock import AsyncMock, Mock
from tenacity import RetryError
import types
from unittest.mock import patch


async def test_openai_client(monkeypatch, sample_messages, generation_config):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", SecretStr("fake-key"))
    llm = OpenAIClient()
    result = Mock()
    result.choices = []
    ocupation = Mock()
    result.choices.append(ocupation)
    ocupation.message.content = "Hello, World!"
    ocupation.finish_reason = "stop"
    result.usage.prompt_tokens = 10
    result.usage.completion_tokens = 5
    result.usage.total_tokens = 15
    result.model = "gpt-4o-mini(Fake)"
    result.model_dump.return_value = {"fake": "response"}

    llm.client.chat.completions.create = AsyncMock(return_value=result)
    mock_func = llm.generate(sample_messages, generation_config)
    response = await mock_func
    assert response.content == "Hello, World!"
    assert response.usage.prompt_tokens == 10
    assert response.usage.completion_tokens == 5
    assert response.usage.total_tokens == 15
    assert response.model_name == "gpt-4o-mini(Fake)"
    assert response.raw_response == {"fake": "response"}
    assert response.finish_reason == "stop"


async def test_openai_client_retryable(monkeypatch, sample_messages, generation_config):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", SecretStr("fake-key"))
    llm = OpenAIClient()
    error1 = Exception("Temporary error 1")
    error2 = Exception("Temporary error 2")
    error3 = Exception("Temporary error 3")
    error1.status_code = 429
    error2.status_code = 429
    error3.status_code = 429
    box = [error1, error2, error3]
    llm.client.chat.completions.create = AsyncMock(side_effect=box)
    with pytest.raises(RetryError):
        mock_func = llm.generate(sample_messages, generation_config)
        response = await mock_func


async def test_openai_client_retryable_401(
    monkeypatch, sample_messages, generation_config
):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", SecretStr("fake-key"))
    llm = OpenAIClient()
    error1 = Exception("Temporary error 1")
    error1.status_code = 401
    llm.client.chat.completions.create = AsyncMock(side_effect=error1)
    mock_func = llm.generate(sample_messages, generation_config)
    with pytest.raises(Exception):
        response = await mock_func
    assert llm.client.chat.completions.create.call_count == 1


async def test_stream_yields_chunks(monkeypatch, sample_messages, generation_config):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", SecretStr("fake-key"))
    llm = OpenAIClient()

    async def fake_stream():
        a = Mock()
        b = Mock()
        a.choices = []
        b.choices = []
        ocuppationa = Mock()
        ocuppationb = Mock()
        ocuppationa.delta.content = "Hello, "
        ocuppationb.delta.content = "World!"
        a.choices.append(ocuppationa)
        b.choices.append(ocuppationb)
        for chunk in [a, b]:
            yield chunk

    llm.client.chat.completions.create = AsyncMock(return_value=fake_stream())

    with patch("src.llm.openai_client.AsyncStream", types.AsyncGeneratorType):
        chunks = []
        async for chunk in llm.stream(sample_messages, generation_config):
            chunks.append(chunk)
        assert chunks == ["Hello, ", "World!"]


async def test_stream_yields_chunks_whileBlank(
    monkeypatch, sample_messages, generation_config
):
    monkeypatch.setattr(settings, "OPENAI_API_KEY", SecretStr("fake-key"))
    llm = OpenAIClient()

    async def fake_stream():
        a = Mock()
        b = Mock()
        a.choices = []
        b.choices = []
        ocuppationa = Mock()
        ocuppationb = Mock()
        ocuppationa.delta.content = None
        ocuppationb.delta.content = None
        a.choices.append(ocuppationa)
        b.choices.append(ocuppationb)
        for chunk in [a, b]:
            yield chunk

    llm.client.chat.completions.create = AsyncMock(return_value=fake_stream())

    with patch("src.llm.openai_client.AsyncStream", types.AsyncGeneratorType):
        chunks = []
        async for chunk in llm.stream(sample_messages, generation_config):
            chunks.append(chunk)
        assert chunks == []
