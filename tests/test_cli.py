from unittest.mock import Mock, AsyncMock
from typer.testing import CliRunner
from src.cli.template_cmd import list_template
from src.cli.app import app
from src.prompt_engine.schemas import PromptAuditLog

def test_template_list(monkeypatch):
    task = Mock()
    monkeypatch.setattr("src.cli.template_cmd.PromptTemplate", task) # task in here be treated as a class
    task.return_value.show_templates.return_value = ["a","b", "c"]
    runner = CliRunner()
    result = runner.invoke(app, ["template", "list"])
    assert result.exit_code == 0
    assert result.output == "a\nb\nc\n"
    assert result.exception is None

def test_template_render(monkeypatch):
    task = Mock()
    monkeypatch.setattr("src.cli.template_cmd.PromptTemplate", task)

    task.return_value.render.return_value = Mock()
    task.return_value.render.return_value.rendered_text = "Pengzhen Lin = Handsome"
    runner = CliRunner()
    result = runner.invoke(app, ["template", "render", "--template-name", "code_review.j2", "--var", "role=猪"])
    assert result.exit_code == 0
    assert result.output == "Pengzhen Lin = Handsome\n"
    task.return_value.render.assert_called_once_with({"role": "猪"}, "code_review.j2")
    assert result.exception is None

def test_audit_show(monkeypatch):
    engine,task = Mock(), Mock()
    monkeypatch.setattr("src.cli.audit_cmd.PromptTemplate", engine)
    monkeypatch.setattr("src.cli.audit_cmd.PromptRegistry", task)
    word = PromptAuditLog(
        template_name = "json",
        version_hash = "avd",
        rendered_prompt = "default",
        variables = {"ds" : 0},
    )
    task.return_value.audit_logs=[word]
    runner = CliRunner()
    result = runner.invoke(app, ["audit", "show", "--last", "5"])
    assert result.exit_code == 0
    assert "avd" in result.output
    assert result.exception is None

def test_audit_diff_with_None(monkeypatch):
    engine, task = Mock(), Mock()
    monkeypatch.setattr("src.cli.audit_cmd.PromptTemplate", engine)
    monkeypatch.setattr("src.cli.audit_cmd.PromptRegistry", task)
    task.return_value.diff.return_value = None
    runner = CliRunner()
    result = runner.invoke(app, ['audit','diff','default_value','default_value', "--v2", 'default_value'])
    assert result.exit_code == 0
    assert "No such template or versions found." in result.output
    assert result.exception is None


def test_audit_diff_with_value(monkeypatch):
    engine, task = Mock(), Mock()
    monkeypatch.setattr("src.cli.audit_cmd.PromptTemplate", engine)
    monkeypatch.setattr("src.cli.audit_cmd.PromptRegistry", task)
    task.return_value.diff.return_value = ['Hello ', "world"]
    runner = CliRunner()
    result = runner.invoke(app, ['audit','diff','default_value','default_value', "--v2", 'default_value'])
    assert result.exit_code == 0
    assert "Differences between versions:" in result.output
    assert "\nHello \nworld\n" in result.output
    assert result.exception is None

def test_code_review_without_stream(tmp_path, monkeypatch):
    f = tmp_path/ "test.py"
    f.write_text("print('hello')")
    pipeline = Mock()
    monkeypatch.setattr("src.cli.run_cmd.Pipeline", pipeline) #pipeline here is a class
    para1 = Mock() # para1 here is an integer
    para1.main_information.overall_score = 5
    para1.main_information.summary = "Good Job"
    para1.token_usage.total_tokens = 10000
    para1.main_information.issues = []
    box = [para1]
    pipeline.return_value.run = AsyncMock(side_effect = box)
    runner = CliRunner()
    result = runner.invoke(app, ['run', 'code-review', '--file-name', str(f), '--model-name', 'Grok', '--stream', '--no-stream' ])
    print(result.output)
    assert result.exit_code == 0
    assert "Totle Tokens Used" in result.output
    assert result.exception is None

def test_code_review_with_error(tmp_path, monkeypatch):
    f = tmp_path/ "test.py"
    f.write_text("print('hello')")
    pipeline = Mock()
    monkeypatch.setattr("src.cli.run_cmd.Pipeline", pipeline) #pipeline here is a class
    para1 = ValueError('GG')
    box = [para1]
    pipeline.return_value.run = AsyncMock(side_effect = box)
    runner = CliRunner()
    result = runner.invoke(app, ['run', 'code-review', '--file-name', str(f), '--model-name', 'Grok', '--stream', '--no-stream' ])
    print(result.output)
    assert result.exit_code == 1
    assert "GG" in result.output

