import logging
from aiolimiter import AsyncLimiter
from src.core.config import settings
import asyncio
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    before_sleep_log,
)

logger = logging.getLogger("llm_client")


def is_retryable_error(exception: BaseException) -> bool:
    status_code = getattr(exception, "status_code", None)
    if status_code is not None:
        if status_code == 429:
            return True
        if status_code >= 500:
            return True

        return False
    return True


api_retry = retry(
    wait=wait_exponential(multiplier=1, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(is_retryable_error),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)


limiter = AsyncLimiter(max_rate=settings.LLM_RPM, time_period=60)
concurrency_limiter = asyncio.Semaphore(settings.LLM_MAX_CONCURRENT)
