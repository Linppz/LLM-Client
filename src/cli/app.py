import typer
from src.cli.audit_cmd import audit_cmd
from src.cli.template_cmd import template_cmd
app = typer.Typer()
app.add_typer(audit_cmd, name="audit")
app.add_typer(template_cmd, name="template")