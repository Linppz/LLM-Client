from src.core.structured_call import StructuredCall
import asyncio
from src.schemas.code_review import CodeReviewResult
from unittest.mock import Mock, AsyncMock
from src.core.pipeline import Pipeline
from src.llm.schemas import LLMResponse, TokenUsage
import pytest



def test_pipeline_integration(fake_llm, output_parser, prompt_registry):
    prompts = {
        "role": "Professor",
        "lanuage": "Python",
        "your_code": "print('hello')",
        "output_schema": "{}",
    }
    result = asyncio.run(
        StructuredCall(fake_llm, prompt_registry, output_parser).call(
            prompts, "code_review.j2", CodeReviewResult
        )
    )

    assert result[0].overall_score == 8
    assert result[0].summary == "This is a well written code review result"
    assert result[0].issues == []

def test_pipeline_integration_end_to_end(fake_llm, monkeypatch):
    prompts = {
        "role": "Professor",
        "lanuage": "Python",
        "your_code": "print('hello')",
        "output_schema": "{}",
    }
    fake_temp = Mock()
    monkeypatch.setattr("src.core.pipeline.LLMFactory", fake_temp)
    fake_temp.get_client.return_value = fake_llm
    result = asyncio.run(Pipeline("Nothing", "openai").run(prompts,"code_review.j2", CodeReviewResult))

    assert result.template_name["user_template"] == "code_review.j2"
    assert result.main_information.overall_score == 8
    assert result.token_usage.prompt_tokens == 0
    assert result.retry_time == 0

def test_pipeline_retry_then_success(mock_llm, monkeypatch):
    prompts = {
        "role": "Professor",
        "lanuage": "Python",
        "your_code": "print('hello')",
        "output_schema": "{}",
    }
    llmresponse1 = LLMResponse(
                content='"overall_score": 8, "issues": [], "summary": "This is a well written code review result"',
                raw_response={"哥哥": "鸡你太美"},
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                model_name="林鹏蓁的大脑",
                finish_reason=None,
            )
    llmresponse2 = LLMResponse(
                content='{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}',
                raw_response={"哥哥": "鸡你太美"},
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                model_name="林鹏蓁的大脑",
                finish_reason=None,
            )
    fake_temp = Mock()
    monkeypatch.setattr("src.core.pipeline.LLMFactory", fake_temp)
    mock_llm.generate = AsyncMock(side_effect = [llmresponse1, llmresponse2])
    fake_temp.get_client.return_value = mock_llm
    result = asyncio.run(Pipeline("Nothing", "openai").run(prompts,"code_review.j2", CodeReviewResult))

    assert result.template_name["user_template"] == "code_review.j2"
    assert result.main_information.overall_score == 8
    assert result.token_usage.prompt_tokens == 0
    assert result.retry_time == 1

def test_pipeline_fail(mock_llm, monkeypatch):
    prompts = {
        "role": "Professor",
        "lanuage": "Python",
        "your_code": "print('hello')",
        "output_schema": "{}",
    }
    llmresponse1 = LLMResponse(
                content='"overall_score": 8, "issues": [], "summary": "This is a well written code review result"',
                raw_response={"哥哥": "鸡你太美"},
                usage=TokenUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                model_name="林鹏蓁的大脑",
                finish_reason=None,
            )
    
    response_box = [llmresponse1 for _ in range(4)]
    fake_temp = Mock()
    monkeypatch.setattr("src.core.pipeline.LLMFactory", fake_temp)
    mock_llm.generate = AsyncMock(side_effect = response_box)
    fake_temp.get_client.return_value = mock_llm
    with pytest.raises(Exception):
        result = asyncio.run(Pipeline("Nothing", "openai").run(prompts,"code_review.j2", CodeReviewResult))
