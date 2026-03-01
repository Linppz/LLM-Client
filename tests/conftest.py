from typing import List, AsyncIterator
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.parser.output_parser import OutputParser
from unittest.mock import AsyncMock
import pytest


@pytest.fixture
def fake_llm():
    class FakeLLM(BaseLLM):
        def __init__(self):
            pass

        async def generate(
            self, messages: List[Message], config: GenerationConfig
        ) -> LLMResponse:
            return LLMResponse(
                content='{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}',
                raw_response={"哥哥": "鸡你太美"},
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                model_name="林鹏蓁的大脑",
                finish_reason=None,
            )

        async def stream(
            self, messages: List[Message], config: GenerationConfig
        ) -> AsyncIterator[str]:
            yield "鸡你太美"

    return FakeLLM()



@pytest.fixture
def output_parser():
    return OutputParser()


@pytest.fixture
def prompt_template():
    return PromptTemplate("gpt-4o-mini", "src/prompts")


@pytest.fixture
def prompt_registry(prompt_template, tmp_path):
    template = prompt_template
    record = PromptRegistry(
        template, str(tmp_path / "manifest_path"), str(tmp_path / "audit_log_path")
    )
    return record


@pytest.fixture
def sample_messages():
    return [
        Message(role="system", content="You are a helpful assistant for code review."),
        Message(
            role="user",
            content="Please review the following code and provide feedback.",
        ),
    ]


@pytest.fixture
def generation_config():
    return GenerationConfig(temperature=1, max_token=500, top_p=0.9)


@pytest.fixture
def mock_llm():
    return AsyncMock(spec = BaseLLM)