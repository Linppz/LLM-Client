from src.prompt_engine.template import PromptTemplate
from src.prompt_engine.registry import PromptRegistry

engine = PromptTemplate("gpt-4o-mini", "src/prompts")
registry = PromptRegistry(engine, "src/manifest.json", "src/audit_log.json")
registry.render_and_log(
    {"lanuage": "python", "your_code": "print(1)", "output_schema": "{}"},
    "code_review.j2",
)

print("done")
