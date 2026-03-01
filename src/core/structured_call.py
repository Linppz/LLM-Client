from src.parser.output_parser import OutputParser
from src.prompt_engine.registry import PromptRegistry
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, Role, LLMResponse
from enum import Enum
from src.core.exceptions import OutputParseError, LLMResponseError
from pydantic import ValidationError
from typing import Any


class OutputStrategy(str, Enum):
    NATIVE = "native"
    JSON_MODE = "json_mode"
    PROMPT_ONLY = "prompt_only"


class StructuredCall:
    def __init__(
        self,
        llm_client: BaseLLM,
        prompt_registry: PromptRegistry,
        output_parser: OutputParser,
        output_strategy: OutputStrategy = OutputStrategy.JSON_MODE,
    ):
        self.llm_client = llm_client
        self.prompt_registry = prompt_registry
        self.output_parser = output_parser
        self.output_strategy = output_strategy

    async def call(
        self,
        prompts: dict[str, Any],
        user_template: str,
        output_schema: Any,
        max_retries: int = 3,
    ) -> tuple[Any, LLMResponse, int]:
        # 1. 把 output_schema 的 JSON Schema 注入到 prompts 里
        prompts["output_schema"] = output_schema.model_json_schema()
        # 2. 用 prompt_registry.render_and_log() 渲染 prompt
        result = self.prompt_registry.render_and_log(prompts, user_template)
        # 3. 调用 llm_client.generate() 获取 LLM 返回
        messages = [Message(role=Role.USER, content=result.rendered_text)]
        config = GenerationConfig()
        if self.output_strategy == OutputStrategy.NATIVE:
            config.response_format = {
                "type": "json_schema",
                "json_schema": output_schema.model_json_schema(),
            }
        elif self.output_strategy == OutputStrategy.JSON_MODE:
            config.response_format = {"type": "json_object"}
        # 5. 如果 Validation Error → 格式化错误 → 追加到消息 → 重试
        for i in range(max_retries):
            try:
                response = await self.llm_client.generate(messages, config)
                raw_output = response.content
                return (
                    self.output_parser.parse(raw_output, output_schema),
                    response,
                    i,
                )
            except (OutputParseError, ValidationError) as e:
                error_message = f"parsing error: {str(e)}. The original output is decoded as: {raw_output}"
                messages.append(Message(role=Role.USER, content=error_message))
            except Exception as e:
                raise LLMResponseError(
                    raw_response=str(e),
                    provider=self.llm_client.__class__.__name__,
                    error_message=str(e),
                )

        return (
            self.output_parser.parse(raw_output, output_schema),
            response,
            max_retries,
        )
