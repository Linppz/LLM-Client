import typer
from src.core.structured_call import StructuredCall
from src.core.config import settings
from src.schemas.code_review import CodeReviewResult
from src.llm.base import BaseLLM
from src.llm.openai_client import OpenAIClient
from src.prompt_engine.registry import PromptRegistry
from src.prompt_engine.template import PromptTemplate
from src.parser.output_parser import OutputParser
from src.llm.factory import  LLMFactory
import asyncio
from typing import Annotated
from src.core.cli_config import cli_config
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
from rich.traceback import install
from src.cli.console import console
from src.llm.schemas import Message, Role, GenerationConfig

install(show_locals=True)

color_map = {
    "critical": "red",
    "major": "yellow",
    "minor": "green"
}

run_cmd = typer.Typer()


async def agency_stream(client: BaseLLM, chat_history: list, config: GenerationConfig):
    full_response = ""
    with Live(console = console, refresh_per_second=4) as live:
        async for word in client.stream(chat_history, config):
            full_response += word
            live.update(Panel(Markdown(full_response), title = "Code Review Result", subtitle = "streaming...", border_style="blue"))
      

@run_cmd.command(name = 'code-review')
def code_review(file_name: Annotated[str, typer.Option(help = "要审查的代码文件路径")], model_name: Annotated[str, typer.Option(help = "要用什么模型呢")] = "openai", stream :Annotated[bool, typer.Option( help = "要不要流式输出？")] = False):
    try:
        with open(file_name, 'r', encoding='utf-8') as f:
            code = f.read()

        prompts = {
            "role" : "Professor",
            "lanuage" : "Python",
            "your_code" : code
        }


    
        engine = PromptTemplate(settings.LLM_DEFAULT_MODEL,cli_config.paths.template_dir)
        output_parser = OutputParser()
        promptregistry = PromptRegistry(engine, cli_config.paths.manifest_path, cli_config.paths.audit_log_path)
        if stream:
            prompts['output_schema'] = CodeReviewResult.model_json_schema()
            client = LLMFactory.get_client(model_name)
            chat_history = []
            chat_history.append(Message(role = Role.USER,  content = promptregistry.render_and_log(prompts, "code_review.j2").rendered_text))
            config = GenerationConfig()
            asyncio.run(agency_stream(client, chat_history, config))

        else:
            llm_client = LLMFactory.get_client(model_name)
            structured_call = StructuredCall(llm_client,promptregistry,output_parser)
            with console.status("正在调用 LLM..."):
                result =  asyncio.run(structured_call.call(prompts, "code_review.j2", CodeReviewResult))

            content = f'Overall Score : {result.overall_score}\n summary : {result.summary}\n'
            table = Table(title="Code Issues")
            table.add_column("Line")
            table.add_column("Severity")
            table.add_column("Description")
            table.add_column("Suggested Fix")

            for issue in result.issues:
                table.add_row(str(issue.line), f"[{color_map[issue.severity]}]{issue.severity.value}[/{color_map[issue.severity]}]", issue.description, issue.suggested_fix or "N/A")
            console.print(Panel(content, title = "Code Review Result"))
            console.print(table)
    except Exception as e:
        console.print_exception(show_locals=True)
        raise typer.Exit(code=1)


