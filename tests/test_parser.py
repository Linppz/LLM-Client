from src.schemas.code_review import CodeReviewResult, ErrorResult, CodeReviewResponse
import pytest
from src.core.exceptions import OutputParseError


def test_clean_markdown(output_parser):
    text = '```json\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}\n```'
    assert (
        output_parser._clean_markdown(text)
        == '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    )
    result = output_parser.parse(text, CodeReviewResult)
    assert result.overall_score == 8
    assert result.issues == []
    assert result.summary == "This is a well written code review result"


def test_extract_prefix_garbage(output_parser):
    text = 'Here is my review:\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    result = output_parser.parse(text, CodeReviewResult)
    assert result.overall_score == 8


def test_truncated_json(output_parser):
    text = '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"'
    result = output_parser.parse(text, CodeReviewResult)
    assert result.overall_score == 8


def test_parse_empty_string(output_parser):
    with pytest.raises(OutputParseError):
        result = output_parser.parse("", CodeReviewResult)    

def test_parse_completely_invalid(output_parser):
    with pytest.raises(OutputParseError):
        result = output_parser.parse("hello world no json here", CodeReviewResult)  

@pytest.mark.parametrize(
    "raw_text, schema, expected_type",
    [
        (
            '```json{"error_code": "INVALID_INPUT", "message": "The input code has syntax errors."}```',
            CodeReviewResponse,
            ErrorResult,
        ),
        (
            'Here is my analysis of your code:{"overall_score": 6, "issues": [], "summary": "...至少20字的sumdddddddddddddddddddddddddddddddddmary..."}',
            CodeReviewResponse,
            CodeReviewResult,
        ),
        (
            '```json{"error_code": "INVALID_INPUT", "message": "The input code has syntax errors."```',
            CodeReviewResponse,
            ErrorResult,
        ),
        (
            '  \n\n  {"error_code": "REFUSED", "message": "Cannot review this code"}  \n  ',
            CodeReviewResponse,
            ErrorResult,
        ),
    ],
)
def test_union_error_result_param(output_parser, raw_text, schema, expected_type):
    result = output_parser.parse(raw_text, schema)
    assert isinstance(result, expected_type)
