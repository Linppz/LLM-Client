import typer
audit_cmd = typer.Typer()
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.core.config import settings
from typing import Annotated
from src.core.cli_config import cli_config
from src.cli.console import console
from rich.table import Table

@audit_cmd.command(name = 'show')
def show_audit(last: Annotated[int, typer.Option(help = "要显示最近多少条审计日志？")] = 5):
    engine = PromptTemplate(settings.LLM_DEFAULT_MODEL,cli_config.paths.template_dir)
    task = PromptRegistry(engine, cli_config.paths.manifest_path, cli_config.paths.audit_log_path)
    table = Table(title="Audit Logs")
    table.add_column("Template Name")
    table.add_column("Version Hash")
    table.add_column("Time stamp")
    table.add_column("Variables")
    for i in task.audit_logs[-last:]:
        table.add_row(i.template_name, i.version_hash, str(i.timestamp), str(i.variables))
    console.print(table)




@audit_cmd.command(name = 'diff')
def show_difference(usertemplate: Annotated[str, typer.Argument(help = "文件内容")], v1: Annotated[str, typer.Argument(help = '文件1')], v2: Annotated[str, typer.Option(help = '文件2')]):
    engine = PromptTemplate(settings.LLM_DEFAULT_MODEL,cli_config.paths.template_dir)
    task = PromptRegistry(engine, cli_config.paths.manifest_path, cli_config.paths.audit_log_path)
    result = task.diff(usertemplate, v1, v2)
    if result is None:
        print("No such template or versions found.")
    else:
        print("Differences between versions:")
        for line in result:
            print(line)