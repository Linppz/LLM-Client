# src/llm/openai_client.py
from typing import List, AsyncIterator
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage
from src.core.structured_call import StructuredCall
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.core.cli_config import cli_config
from src.parser.output_parser import OutputParser
import asyncio
from src.schemas.code_review import CodeReviewResult


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


def test_pipeline_integration():
    llm_client = FakeLLM()
    prompt_template = PromptTemplate("dfdfd", cli_config.paths.template_dir)
    output_parser = OutputParser()
    prompt_registry = PromptRegistry(
        prompt_template, cli_config.paths.manifest_path, cli_config.paths.audit_log_path
    )
    prompts = {
        "role": "Professor",
        "lanuage": "Python",
        "your_code": "print('hello')",
        "output_schema": "{}",
    }
    result = asyncio.run(
        StructuredCall(llm_client, prompt_registry, output_parser).call(
            prompts, "code_review.j2", CodeReviewResult
        )
    )

    assert result[0].overall_score == 8
    assert result[0].summary == "This is a well written code review result"
    assert result[0].issues == []
