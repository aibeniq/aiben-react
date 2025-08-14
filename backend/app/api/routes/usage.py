import os
from datetime import datetime, timedelta
from calendar import monthrange
from typing_extensions import TypedDict
import httpx
from fastapi import APIRouter, HTTPException
from app.api.deps import CurrentUser
from app.core.config import settings


class QuotaPeriod(TypedDict):
    start_time: int
    end_time: int
    start_date: str
    end_date: str
    max_tokens: int


class TokenUsageResponse(TypedDict):
    total_tokens: int
    quota_period: QuotaPeriod


router = APIRouter(prefix="/usage", tags=["usage"])


def calculate_quota_period() -> QuotaPeriod:
    """
    Calculate the current quota period based on configuration.

    Returns:
        QuotaPeriod: Contains start_time, end_time, start_date, end_date, and max_tokens
    """
    today = datetime.now()
    current_day = today.day
    current_month = today.month
    current_year = today.year

    start_day = settings.QUOTA_PERIOD_START_DAY

    if current_day >= start_day:
        # Current period: this month's start_day to next month's (start_day - 1)
        start_date = datetime(current_year, current_month, start_day)

        # Calculate next month
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year

        # Calculate the last day of the period
        if start_day == 1:
            # If start_day is 1, end on the last day of current month
            _, last_day = monthrange(current_year, current_month)
            end_date = datetime(current_year, current_month, last_day, 23, 59, 59)
        else:
            # End on (start_day - 1) of next month
            end_date = datetime(next_year, next_month, start_day - 1, 23, 59, 59)
    else:
        # Current period: last month's start_day to this month's (start_day - 1)
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year

        start_date = datetime(prev_year, prev_month, start_day)

        if start_day == 1:
            # If start_day is 1, end on the last day of previous month
            _, last_day = monthrange(prev_year, prev_month)
            end_date = datetime(prev_year, prev_month, last_day, 23, 59, 59)
        else:
            # End on (start_day - 1) of current month
            end_date = datetime(current_year, current_month, start_day - 1, 23, 59, 59)

    return {
        "start_time": int(start_date.timestamp()),
        "end_time": int(end_date.timestamp()),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "max_tokens": settings.QUOTA_PERIOD_MAX_TOKENS,
    }


@router.get("/token-usage")
async def get_token_usage(
    current_user: CurrentUser,
) -> TokenUsageResponse:
    """
    Get total OpenAI API token usage and current quota period information.

    Returns the total number of tokens consumed by the configured API key
    along with the current quota period details.
    """

    openai_admin_key = os.getenv("OPENAI_ADMIN_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_admin_key:
        raise HTTPException(
            status_code=500, detail="OpenAI admin access is not configured"
        )

    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")

    quota_period = calculate_quota_period()

    params = [
        ("start_time", quota_period["start_time"]),
        ("bucket_width", "1d"),
        ("api_key_ids[]", openai_api_key),
        ("group_by[]", "api_key_id"),
        ("group_by[]", "model"),
        ("group_by[]", "bucket"),
    ]

    url = "https://api.openai.com/v1/organization/usage/completions"
    headers = {
        "Authorization": f"Bearer {openai_admin_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)

            if response.status_code == 200:
                data = response.json()

                total_tokens: int = 0

                if data and "data" in data and isinstance(data["data"], list):
                    for bucket in data["data"]:
                        if "results" in bucket and isinstance(bucket["results"], list):
                            for result in bucket["results"]:
                                total_tokens += result.get("input_tokens", 0)
                                total_tokens += result.get("output_tokens", 0)

                return TokenUsageResponse(
                    total_tokens=total_tokens, quota_period=quota_period
                )

            elif response.status_code == 401:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid OpenAI admin credentials or insufficient permissions",
                )
            elif response.status_code == 429:
                raise HTTPException(
                    status_code=429, detail="Rate limit exceeded for OpenAI Admin API"
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"OpenAI API returned status {response.status_code}",
                )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="Failed to connect to OpenAI API")
