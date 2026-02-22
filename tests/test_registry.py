from src.prompt_engine.template import PromptTemplate
from src.prompt_engine.registry import PromptRegistry


def test_render_and_log(tmp_path):
    test = PromptTemplate("gpt-4o-mini", "src/prompts")
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    record = PromptRegistry(
        test, str(tmp_path / "manifest.json"), str(tmp_path / "audit.json")
    )
    record.render_and_log(role, "code_review.j2")
    assert len(record.audit_logs) == 1
    assert record.audit_logs[0].template_name == "code_review.j2"


def test_version_hash_stability(tmp_path):
    test = PromptTemplate("gpt-4o-mini", "src/prompts")
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }
    role1 = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    record = PromptRegistry(
        test, str(tmp_path / "manifest.json"), str(tmp_path / "audit.json")
    )
    record.render_and_log(role, "code_review.j2")
    record.render_and_log(role1, "code_review.j2")
    assert record.audit_logs[0].version_hash == record.audit_logs[1].version_hash


def test_get_version(tmp_path):
    test = PromptTemplate("gpt-4o-mini", "src/prompts")
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    record = PromptRegistry(
        test, str(tmp_path / "manifest.json"), str(tmp_path / "audit.json")
    )
    record.render_and_log(role, "code_review.j2")
    number = record.get("code_review.j2", record.data["code_review.j2"][0].version_hash)
    assert number.version_hash == record.data["code_review.j2"][0].version_hash


def test_diff_versions(tmp_path):
    test = PromptTemplate("gpt-4o-mini", "src/prompts")
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }
    role1 = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love ydou",
        "output_schema": "{}",
    }

    record = PromptRegistry(
        test, str(tmp_path / "manifest.json"), str(tmp_path / "audit.json")
    )
    record.render_and_log(role, "code_review.j2")
    record.render_and_log(role1, "code_review.j2")

    assert (
        record.diff(
            "code_review.j2",
            record.data["code_review.j2"][0].version_hash,
            record.data["code_review.j2"][1].version_hash,
        )
        is not None
    )
