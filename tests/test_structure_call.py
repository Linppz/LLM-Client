from unittest.mock import patch, Mock, AsyncMock
from src.core.structured_call import StructuredCall
from src.core.exceptions import OutputParseError, LLMResponseError
from pydantic import ValidationError
from pydantic import BaseModel
import pytest


async def test_call_success_first_try():
    llm = Mock()
    Mock_Response = Mock()
    llm.generate = AsyncMock(return_value=Mock_Response)
    Mock_Response.content = "Dear Lin"
    prompt_registry = Mock()
    output_parser = Mock()
    output_parser.parse = Mock(return_value="hello I am rabbit")
    prompt_registry.render_and_log.return_value.rendered_text = "Hello world"
    obj = StructuredCall(llm, prompt_registry, output_parser)
    prompts = {"word": "Hello world"}
    user_template = "Hello, world"

    class format(BaseModel):
        food: str
        price: int

    result = await obj.call(prompts, user_template, format)
    assert result[0] == "hello I am rabbit"
    assert result[1].content == "Dear Lin"
    assert result[2] == 0


async def test_call_retries_on_parse_error():
    llm = Mock()
    Mock_Response = Mock()
    llm.generate = AsyncMock(return_value=Mock_Response)
    Mock_Response.content = "Dear Lin"
    prompt_registry = Mock()
    output_parser = Mock()
    output_parser.parse = Mock(side_effect=[OutputParseError("df", "dff"), "hello I am rabbit"])
    prompt_registry.render_and_log.return_value.rendered_text = "Hello world"
    obj = StructuredCall(llm, prompt_registry, output_parser)
    prompts = {"word": "Hello world"}
    user_template = "Hello, world"

    class format(BaseModel):
        food: str
        price: int

    result = await obj.call(prompts, user_template, format)
    assert result[0] == "hello I am rabbit"
    assert result[1].content == "Dear Lin"
    assert result[2] == 1
    assert llm.generate.call_count == 2


async def test_call_retries_on_validation_error():
    llm = Mock()
    Mock_Response = Mock()
    llm.generate = AsyncMock(return_value=Mock_Response)
    Mock_Response.content = "Dear Lin"
    prompt_registry = Mock()
    output_parser = Mock()

    class format(BaseModel):
        food: int
        price: int

    try:
        format(food="df", price="df")
    except ValidationError as e:
        Validation_error = e
    output_parser.parse = Mock(side_effect=[Validation_error, "hello I am rabbit"])
    prompt_registry.render_and_log.return_value.rendered_text = "Hello world"
    obj = StructuredCall(llm, prompt_registry, output_parser)
    prompts = {"word": "Hello world"}
    user_template = "Hello, world"
    result = await obj.call(prompts, user_template, format)
    assert result[0] == "hello I am rabbit"
    assert result[1].content == "Dear Lin"
    assert result[2] == 1
    assert llm.generate.call_count == 2


async def test_call_raises_on_llm_error():
    llm = Mock()
    error1 = LLMResponseError("df", "dd", "dd")
    llm.generate = AsyncMock(side_effect = error1)
    prompt_registry = Mock()
    output_parser = Mock()
    

    prompt_registry.render_and_log.return_value.rendered_text = "Hello world"
    obj = StructuredCall(llm, prompt_registry, output_parser)
    prompts = {"word": "Hello world"}
    user_template = "Hello, world"

    class format(BaseModel):
        food: str
        price: int

    with pytest.raises(LLMResponseError):
        result = await obj.call(prompts, user_template, format)


async def test_call_exhausts_retries():
    llm = Mock()
    Mock_Response = Mock()
    llm.generate = AsyncMock(return_value=Mock_Response)
    Mock_Response.content = "Dear Lin"
    prompt_registry = Mock()
    output_parser = Mock()
    queue = [OutputParseError("df", "dff") for _ in range(4)]
    output_parser.parse = Mock(side_effect=queue)
    prompt_registry.render_and_log.return_value.rendered_text = "Hello world"
    obj = StructuredCall(llm, prompt_registry, output_parser)
    prompts = {"word": "Hello world"}
    user_template = "Hello, world"

    class format(BaseModel):
        food: str
        price: int


    with pytest.raises(OutputParseError):
        result = await obj.call(prompts, user_template, format)