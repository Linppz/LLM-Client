# src/llm/anthropic_client.py
from typing import List, AsyncIterator, Tuple
from anthropic import AsyncAnthropic
from src.core.config import settings
from src.core.resilience import api_retry  # <--- 改这里
from src.llm.base import BaseLLM
from src.llm.schemas import Message, GenerationConfig, LLMResponse, TokenUsage, Role
from src.llm.tokentracker import TokenTracker
from anthropic import AsyncStream
from anthropic.types import TextBlock
from anthropic import NOT_GIVEN


class AnthropicClient(BaseLLM):
    def __init__(self) -> None:
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set.")

        self.client = AsyncAnthropic(
            api_key=settings.ANTHROPIC_API_KEY.get_secret_value(),
            timeout=settings.LLM_TIMEOUT,
        )

        self.model = "claude-3-5-sonnet-20240620"

    def _prepare_inputs(
        self, messages: List[Message]
    ) -> Tuple[str, List[dict[str, str]]]:
        system_prompt = ""
        anthropic_messages: list[dict[str, str]] = []
        for msg in messages:
            if msg.role == Role.SYSTEM:
                system_prompt = msg.content
            else:
                role = "assistant" if msg.role.value == "assistance" else msg.role.value
                anthropic_messages.append({"role": role, "content": msg.content})
        return system_prompt, anthropic_messages

    @api_retry
    async def generate(
        self, messages: List[Message], config: GenerationConfig
    ) -> LLMResponse:
        system_prompt, formatted_messages = self._prepare_inputs(messages)
        response = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=formatted_messages,  # type: ignore[arg-type]
            temperature=config.temperature,
            max_tokens=config.max_token or 1024,
            top_p=config.top_p if config.top_p is not None else NOT_GIVEN,  # type: ignore[arg-type]
            stream=False,
        )
        assert not isinstance(response, AsyncStream)
        content_text = ""
        if response.content and isinstance(response.content[0].type, TextBlock):
            content_text = response.content[0].text

        return LLMResponse(
            content=content_text,
            raw_response=response.model_dump(),
            usage=TokenUsage(
                prompt_tokens=response.usage.input_tokens,
                completion_tokens=response.usage.output_tokens,
                total_tokens=response.usage.input_tokens + response.usage.output_tokens,
            ),
            model_name=response.model,
            finish_reason=response.stop_reason,
        )

    @api_retry
    async def stream(
        self, messages: List[Message], config: GenerationConfig
    ) -> AsyncIterator[str]:
        self.tracker = TokenTracker(self.model)
        system_prompt, formatted_messages = self._prepare_inputs(messages)
        stream = await self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=formatted_messages,  # type: ignore[arg-type]
            temperature=config.temperature,
            max_tokens=config.max_token or 1024,
            top_p=config.top_p if config.top_p is not None else NOT_GIVEN,  # type: ignore[arg-type]
            stream=True,
        )
        assert isinstance(stream, AsyncStream)

        async for event in stream:
            if event.type == "content_block_delta" and event.delta.type == "text_delta":
                yield event.delta.text
                self.tracker.add(event.delta.text)
