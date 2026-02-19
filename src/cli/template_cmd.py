import typer
from src.prompt_engine.template import PromptTemplate
from src.core.config import settings
from typing import List, Optional

template_cmd = typer.Typer()

@template_cmd.command(name = 'list')
def list_template():
    task = PromptTemplate(settings.LLM_DEFAULT_MODEL,"src/prompts")
    result = task.show_templates()
    for i in result:
        print(i)

@template_cmd.command(name = 'render')
def render_template(template_name: str, var: Optional[List[str]] = typer.Option(None)):
    task = PromptTemplate(settings.LLM_DEFAULT_MODEL,"src/prompts")
    my_dict = {}
    if var:
        my_dict = dict(item.split('=') for item in var)
    result = task.render(my_dict, template_name)
    print(result.rendered_text)