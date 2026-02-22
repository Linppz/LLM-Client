import typer
from src.cli.audit_cmd import audit_cmd
from src.cli.template_cmd import template_cmd
from src.cli.run_cmd import run_cmd

app = typer.Typer()
app.add_typer(audit_cmd, name="audit")
app.add_typer(template_cmd, name="template")
app.add_typer(run_cmd, name="run")

if __name__ == "__main__":
    app()
