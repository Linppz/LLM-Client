from unittest.mock import Mock, AsyncMock
from src.core.resilience import is_retryable_error, api_retry
import asyncio


def test_is_retryable_error_test():
    error = Mock()
    error.status_code = 500
    error.status_code = 500
    assert is_retryable_error(error) == True
    error.status_code = 429
    assert is_retryable_error(error) == True
    error.status_code = 400
    assert is_retryable_error(error) == False
    error.status_code = None
    assert is_retryable_error(error) == True


async def test_api_retry():

    # Use a list store the the behavior of the mock function across calls
    error1, error2, success = (
        Exception("Temporary Error 1"),
        Exception("Temporary Error 2"),
        "Success",
    )
    error1.status_code = 500
    error2.status_code = 429

    call_results = [error1, error2, success]

    # Create a fake async function to test the retry mechanism
    mock_func = AsyncMock(side_effect=call_results)
    decorated = api_retry(mock_func)  # Decorate the mock function with our retry logic
    result = await decorated()  # Call the decorated function, which should retry on the first two errors and succeed on the third call
    assert mock_func.call_count == 3
    assert result == success
