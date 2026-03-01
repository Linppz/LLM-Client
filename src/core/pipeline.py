from src.core.structured_call import StructuredCall
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.parser.output_parser import OutputParser
from src.llm.factory import LLMFactory
from src.core.cli_config import cli_config
from src.core.resilience import concurrency_limiter
from src.prompt_engine.schemas import PipelineResult
from typing import Any


class Pipeline:
    def __init__(self, model_name: str, model_provider: str):
        self.llm_client = LLMFactory.get_client(model_name)
        self.prompt_template = PromptTemplate(
            model_provider, cli_config.paths.template_dir
        )
        self.output_parser = OutputParser()
        self.prompt_registry = PromptRegistry(
            self.prompt_template,
            cli_config.paths.manifest_path,
            cli_config.paths.audit_log_path,
        )

    async def run(
        self, prompts: dict[str, Any], user_template: str, output_schema: Any
    ) -> PipelineResult:
        async with concurrency_limiter:
            structured_call = StructuredCall(
                self.llm_client, self.prompt_registry, self.output_parser
            )
            result = await structured_call.call(prompts, user_template, output_schema)
            # 构建 PipelineResult参数
            template_name = {}
            template_name["user_template"] = user_template
            template_name["hash_code"] = self.prompt_registry.data[user_template][
                -1
            ].version_hash
            # 拼装
            Pipline_result = PipelineResult(
                main_information=result[0],
                template_name=template_name,
                token_usage=result[1].usage,
                retry_time=result[2],  # 这里暂时不统计重试次数，后续可以加上
            )
            return Pipline_result
