from src.llm.tokentracker import TokenTracker
from jinja2 import Environment, FileSystemLoader, meta
from src.core.exceptions import MissingVariableError
from src.prompt_engine.schemas import RenderResult
from typing import List
from typing import Any


class PromptTemplate:
    def __init__(self, model: str, template_dir: str):
        self.model = model
        self.env = Environment(loader=FileSystemLoader(template_dir))

    def render(self, prompts: dict[str, Any], user_template: str) -> RenderResult:
        check = self.show_missing_context(user_template)
        if check - prompts.keys():
            raise MissingVariableError(user_template, check - prompts.keys())

        template = self.env.get_template(user_template)
        text = template.render(**prompts)
        tracker = TokenTracker(self.model)
        tracker.add(text)
        usage = tracker.get_usage()
        return RenderResult(
            rendered_text=text,
            token_count=usage,
            template_name=user_template,
            variables_used=prompts,
        )

    # 看看还有哪些模板可以用
    def show_templates(self) -> List[str]:
        return self.env.list_templates()

    # 扫描某些模板需要哪些变量
    def show_missing_context(self, user_template: str) -> set[str]:
        assert self.env.loader is not None
        orig_code = self.env.loader.get_source(self.env, user_template)
        table = meta.find_undeclared_variables(self.env.parse(orig_code[0]))
        return table
