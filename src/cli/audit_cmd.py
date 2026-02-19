import typer
audit_cmd = typer.Typer()
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.core.config import settings


@audit_cmd.command(name = 'show')
def show_audit(last: int = typer.Optinon(10)):
    engine = PromptTemplate(settings.LLM_DEFAULT_MODEL,"src/prompts")
    task = PromptRegistry(engine, "src/manifest.json", "src/audit_log.json")
    temp = 
    for i in task.audit_logs[-last:]:
        print(f"Template Name: {i.template_name}")
        print(f"Version Hash: {i.version_hash}")
        print(f"Rendered Prompt: {i.rendered_prompt}")
        print(f"Variables: {i.variables}")
        print("=====================================")
