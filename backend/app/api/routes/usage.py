import os
from datetime import datetime, timedelta
from typing import Any, Optional
import httpx
from fastapi import APIRouter, HTTPException, Query, Depends
from app.api.deps import CurrentUser

router = APIRouter(prefix="/usage", tags=["usage"])


@router.get("/token-usage")
async def get_token_usage(
    current_user: CurrentUser,
    start_time: Optional[int] = Query(
        None, description="Start time (Unix seconds) of the query time range, inclusive"
    ),
    end_time: Optional[int] = Query(
        None, description="End time (Unix seconds) of the query time range, exclusive"
    ),
    limit: Optional[int] = Query(None, description="Number of buckets to return"),
) -> dict:
    """
    Get total OpenAI API token usage.

    Returns the total number of tokens consumed by the configured API key.
    """

    # get environment variables
    openai_admin_key = os.getenv("OPENAI_ADMIN_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_admin_key:
        raise HTTPException(
            status_code=500, detail="OpenAI admin access is not configured"
        )

    if not openai_api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key is not configured")

    # if no start_time provided, default to 30 days ago
    if start_time is None:
        start_time = int((datetime.now() - timedelta(days=30)).timestamp())

    params = [
        ("start_time", start_time),
        ("bucket_width", "1d"),
        ("api_key_ids[]", openai_api_key),
        ("group_by[]", "api_key_id"),
        ("group_by[]", "model"),
        ("group_by[]", "bucket"),
    ]

    # add optional parameters if provided
    if end_time is not None:
        params.append(("end_time", end_time))
    if limit is not None:
        params.append(("limit", limit))

    # make request to OpenAI Admin API
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

                # calculate total tokens from the response
                total_tokens = 0

                if data and "data" in data and isinstance(data["data"], list):
                    for bucket in data["data"]:
                        if "results" in bucket and isinstance(bucket["results"], list):
                            for result in bucket["results"]:
                                total_tokens += result.get("input_tokens", 0)
                                total_tokens += result.get("output_tokens", 0)

                return {"total_tokens": total_tokens}

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
