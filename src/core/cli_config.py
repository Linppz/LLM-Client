import tomli
from pydantic import BaseModel


class PathsConfig(BaseModel):
    template_dir: str
    manifest_path: str
    audit_log_path: str


class LLMConfig(BaseModel):
    default_provider: str
    default_model: str


class CLIConfig(BaseModel):
    paths: PathsConfig
    llm: LLMConfig


with open("config.toml", "rb") as f:
    config = tomli.load(f)

cli_config = CLIConfig(**config)
