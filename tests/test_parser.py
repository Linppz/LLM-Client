from src.parser.output_parser import OutputParser
from src.schemas.code_review import CodeReviewResult, ErrorResult, CodeReviewResponse
import pytest


def test_clean_markdown():
    obj = OutputParser()
    text = '```json\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}\n```'
    assert (
        obj._clean_markdown(text)
        == '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    )
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8
    assert result.issues == []
    assert result.summary == "This is a well written code review result"


def test_extract_prefix_garbage():
    text = 'Here is my review:\n{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"}'
    obj = OutputParser()
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8


def test_truncated_json():
    text = '{"overall_score": 8, "issues": [], "summary": "This is a well written code review result"'
    obj = OutputParser()
    result = obj.parse(text, CodeReviewResult)
    assert result.overall_score == 8


# def test_union_error_result4():
#     raw_text = "I'm sorry, I cannot help with that."
#     with pytest.raises(OutputParseError):
#         result = OutputParser().parse(raw_text, CodeReviewResponse)


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
def test_union_error_result_param(raw_text, schema, expected_type):
    result = OutputParser().parse(raw_text, schema)
    assert isinstance(result, expected_type)
