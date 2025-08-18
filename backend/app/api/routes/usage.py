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
    today = datetime.utcnow()
    current_day = today.day
    current_month = today.month
    current_year = today.year

    start_day = settings.QUOTA_PERIOD_START_DAY
    
    # Debug prints for quota period calculation
    print(f"Today (UTC): {today}")
    print(f"Current day: {current_day}, Start day setting: {start_day}")
    print(f"Settings QUOTA_PERIOD_START_DAY: {settings.QUOTA_PERIOD_START_DAY}")

    if current_day >= start_day:
        # Current period: this month's start_day to next month's (start_day - 1)
        start_date = datetime(current_year, current_month, start_day)
        if current_month == 12:
            next_month = 1
            next_year = current_year + 1
        else:
            next_month = current_month + 1
            next_year = current_year
        # End date is next month's (start_day - 1), or current month's last day if start_day is 1
        if start_day > 1:
            end_day = start_day - 1
            end_date = datetime(next_year, next_month, end_day, 23, 59, 59)
        else:
            # If start_day is 1, period ends on last day of current month
            end_day = monthrange(current_year, current_month)[1]
            end_date = datetime(current_year, current_month, end_day, 23, 59, 59)
    else:
        # Current period: last month's start_day to this month's (start_day - 1)
        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year
        start_date = datetime(prev_year, prev_month, start_day)
        end_day = start_day - 1 if start_day > 1 else monthrange(current_year, current_month)[1]
        end_date = datetime(current_year, current_month, end_day, 23, 59, 59)

    # Debug prints for timestamps
    print(f"Sending start_time: {int(start_date.timestamp())} ({start_date.isoformat()} UTC)")
    print(f"Sending end_time: {int(end_date.timestamp())} ({end_date.isoformat()} UTC)")

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
        ("end_time", quota_period["end_time"]),
        ("bucket_width", "1d"),
        ("api_key_ids", "key_G3FMVaA6B071wZ5M"), #DAVID TODO - hardcoded in the key ID...
        ("group_by[]", "api_key_id"),
        #("group_by[]", "model"),
        #("group_by[]", "bucket"),
    ]
    
    # Print calculated usage period
    print(f"=== USAGE PERIOD DEBUG ===")
    print(f"Quota period start: {quota_period['start_date']}")
    print(f"Quota period end: {quota_period['end_date']}")
    print(f"Max tokens for period: {quota_period['max_tokens']:,}")
    print(f"Using API key: {openai_api_key[:10]}...{openai_api_key[-10:]}")

    url = "https://api.openai.com/v1/organization/usage/completions"
    headers = {
        "Authorization": f"Bearer {openai_admin_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            total_tokens: int = 0
            page_count = 0
            next_page = None
            
            # Handle pagination to get all usage data
            while True:
                page_count += 1
                current_params = params.copy()
                
                # Add pagination parameter if we have a next page
                if next_page:
                    current_params.append(("page", next_page))
                
                print(f"Fetching page {page_count}...")
                response = await client.get(url, headers=headers, params=current_params)

                if response.status_code == 200:
                    data = response.json()

                    # Print raw API response for debugging
                    print(f"Page {page_count} - OpenAI API response status: {response.status_code}")
                    print(f"Page {page_count} - Raw response data keys: {list(data.keys()) if data else 'None'}")
                    print(f"Page {page_count} - Raw response: {data}")

                    page_tokens = 0
                    if data and "data" in data and isinstance(data["data"], list):
                        print(f"Page {page_count} - Number of buckets: {len(data['data'])}")
                        for i, bucket in enumerate(data["data"]):
                            if "results" in bucket and isinstance(bucket["results"], list):
                                bucket_tokens = 0
                                for result in bucket["results"]:
                                    input_tokens = result.get("input_tokens", 0)
                                    output_tokens = result.get("output_tokens", 0)
                                    bucket_tokens += input_tokens + output_tokens
                                    page_tokens += input_tokens + output_tokens
                                if bucket_tokens > 0:  # Only print non-zero buckets
                                    print(f"Page {page_count}, Bucket {i}: {bucket_tokens:,} tokens")
                    
                    total_tokens += page_tokens
                    print(f"Page {page_count} total tokens: {page_tokens:,}")
                    
                    # Check if there are more pages
                    has_more = data.get("has_more", False)
                    next_page = data.get("next_page")
                    
                    if not has_more or not next_page:
                        print(f"No more pages. Total pages fetched: {page_count}")
                        break
                        
                elif response.status_code == 401:
                    print(f"OpenAI API authentication failed: {response.status_code}")
                    raise HTTPException(
                        status_code=401,
                        detail="Invalid OpenAI admin credentials or insufficient permissions",
                    )
                elif response.status_code == 429:
                    print(f"OpenAI API rate limit exceeded: {response.status_code}")
                    raise HTTPException(
                        status_code=429, detail="Rate limit exceeded for OpenAI Admin API"
                    )
                else:
                    print(f"OpenAI API error: {response.status_code} - {response.text}")
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"OpenAI API returned status {response.status_code}",
                    )

            # Print final calculated usage
            print(f"=== FINAL USAGE CALCULATION ===")
            print(f"Total tokens retrieved: {total_tokens:,}")
            print(f"Usage percentage: {(total_tokens / quota_period['max_tokens'] * 100):.2f}%")
            print(f"===========================")

            return TokenUsageResponse(
                total_tokens=total_tokens, quota_period=quota_period
            )

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail="Failed to connect to OpenAI API")
