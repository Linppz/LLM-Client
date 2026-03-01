from src.core.config import Settings
import pytest
from pydantic import ValidationError

def test_set_environment(monkeypatch):
    monkeypatch.setenv("LLM_DEFAULT_MODEL", "林鹏蓁的大脑")
    monkeypatch.setenv("LLM_TIMEOUT", "80")
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")
    obj = Settings()
    assert obj.LLM_DEFAULT_MODEL == "林鹏蓁的大脑"
    assert obj.LLM_TIMEOUT == 80
    assert obj.LLM_PROVIDER == "anthropic"

def test_original_settings(monkeypatch, tmp_path):
    # here which means we cut off the hand and the feet for the class, let it be alone to test
    monkeypatch.chdir(tmp_path)
    obj = Settings()
    assert obj.LLM_DEFAULT_MODEL == "gpt-4o-mini"
    assert obj.LLM_TIMEOUT == 30
    assert obj.LLM_PROVIDER == "openai"

def test_validation_error_setting(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "invalid")
    with pytest.raises(ValidationError):
        obj = Settings()

def test_get_correct_value(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "888")
    obj = Settings()
    assert obj.OPENAI_API_KEY.get_secret_value() == "888"