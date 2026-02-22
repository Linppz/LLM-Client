import typer
from src.prompt_engine.template import PromptTemplate
from src.core.config import settings
from typing import List, Optional
from typing import Annotated
from src.core.cli_config import cli_config
from src.cli.console import console

template_cmd = typer.Typer()


@template_cmd.command(name="list")
def list_template() -> None:
    task = PromptTemplate(settings.LLM_DEFAULT_MODEL, cli_config.paths.template_dir)
    result = task.show_templates()
    for i in result:
        console.print(i)


@template_cmd.command(name="render")
def render_template(
    template_name: Annotated[str, typer.Option(help="什么文件？")],
    var: Annotated[Optional[List[str]], typer.Option(help="变量列表，格式为key=value")],
) -> None:
    task = PromptTemplate(settings.LLM_DEFAULT_MODEL, cli_config.paths.template_dir)
    my_dict = {}
    if var:
        my_dict = dict(item.split("=") for item in var)
    result = task.render(my_dict, template_name)
    console.print(result.rendered_text)
