import tiktoken
import pytest
from jinja2.exceptions import TemplateNotFound
from src.core.exceptions import MissingVariableError

def test_render_with_variables(prompt_template):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    result = prompt_template.render(role, "code_review.j2")
    assert "猪" in result.rendered_text
    assert "c++" in result.rendered_text
    assert result.token_count > 0
    assert result.template_name == "code_review.j2"


def test_token_count_accuracy(prompt_template):

    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
        "output_schema": "{}",
    }

    result = prompt_template.render(role, "code_review.j2")
    way = tiktoken.get_encoding("cl100k_base")
    expected = len(way.encode(result.rendered_text))
    assert abs(result.token_count - expected) / expected < 0.3

def test_render_nonexistent_template(prompt_template):
    with pytest.raises(TemplateNotFound):
        result = prompt_template.render({"Empty" : "None"}, "invalid input.j2")

def test_show_missing_context(prompt_template):
    role = {
        "lanuage": "c++",
        "role": "猪",
        "your_code": "cout << I Love you",
    }
    with pytest.raises(MissingVariableError):
        result = prompt_template.render(role, "code_review.j2")
