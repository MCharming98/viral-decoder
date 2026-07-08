from pathlib import Path
from typing import Any

from scripts.client import XClient
from scripts.store import (
    filter_tweets_by_time,
    is_time_range_fully_stored,
    load_stored_tweets,
    store_tweets,
    uncovered_time_ranges,
)

DEFAULT_TWEET_FIELDS = (
    "created_at,public_metrics,lang,entities,referenced_tweets,attachments"
)
DEFAULT_MEDIA_FIELDS = "type,url,preview_image_url,alt_text,height,width,duration_ms"


def _build_params(
    *,
    max_results: int = 100,
    pagination_token: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    since_id: str | None = None,
    until_id: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {
        "max_results": min(max_results, 100),
        "tweet.fields": DEFAULT_TWEET_FIELDS,
        "expansions": "attachments.media_keys",
        "media.fields": DEFAULT_MEDIA_FIELDS,
        "exclude": "retweets,replies",
    }
    if pagination_token:
        params["pagination_token"] = pagination_token
    if start_time:
        params["start_time"] = start_time
    if end_time:
        params["end_time"] = end_time
    if since_id:
        params["since_id"] = since_id
    if until_id:
        params["until_id"] = until_id
    return params


def get_tweets(
    client: XClient,
    user_id: str,
    *,
    max_results: int = 100,
    pagination_token: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    since_id: str | None = None,
    until_id: str | None = None,
) -> dict[str, Any]:
    """Fetch tweets from the API without storing locally."""
    params = _build_params(
        max_results=max_results,
        pagination_token=pagination_token,
        start_time=start_time,
        end_time=end_time,
        since_id=since_id,
        until_id=until_id,
    )
    return client.get(f"/users/{user_id}/tweets", params=params)


def _fetch_and_store_range(
    client: XClient,
    user_id: str,
    username: str,
    *,
    start_time: str,
    end_time: str,
    max_results: int,
    store_kwargs: dict[str, Any],
) -> None:
    pagination_token: str | None = None
    while True:
        params = _build_params(
            max_results=max_results,
            pagination_token=pagination_token,
            start_time=start_time,
            end_time=end_time,
        )
        payload = client.get(f"/users/{user_id}/tweets", params=params)
        store_tweets(username, payload, **store_kwargs)
        pagination_token = payload.get("meta", {}).get("next_token")
        if not pagination_token:
            break


def _store_result(*, source: str, result_count: int) -> dict[str, Any]:
    return {"source": source, "result_count": result_count}


def _result_count_in_window(
    tweets: list[dict[str, Any]],
    *,
    start_time: str,
    end_time: str,
    max_results: int,
) -> int:
    in_range = filter_tweets_by_time(
        tweets,
        start_time=start_time,
        end_time=end_time,
    )
    return min(len(in_range), min(max_results, 100))


def get_and_store_user_tweets(
    client: XClient,
    user_id: str,
    *,
    username: str,
    max_results: int = 100,
    pagination_token: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    since_id: str | None = None,
    until_id: str | None = None,
    path: Path | str | None = None,
) -> dict[str, Any]:
    """Fetch tweets, store them locally, and return fetch metadata.

    Returns ``{"source": ..., "result_count": ...}`` where ``source`` is one of
    ``"stored"``, ``"stored+api"``, or ``"api"``. Use ``load_stored_tweets`` to
    read the stored tweet data.

    Time window: use start_time/end_time (ISO 8601 UTC, e.g. 2024-01-01T00:00:00Z).
    ID window: use since_id/until_id for tweet ID bounds (both exclusive).

    If since_id or until_id is set, it takes precedence over start_time/end_time
    per the X API.

    path: file or directory for storage. A `.json` path stores to that file;
    a directory stores to `{path}/{username}.json`. Defaults to `tweets/{username}.json`.

    When start_time and end_time are set, checks stored tweets at path first:
    - Fully covered: stores nothing new and skips the API.
    - Partially covered: fetches only uncovered sub-ranges (auto-paginated).
    """
    store_kwargs: dict[str, Any] = {}
    if path is not None:
        store_kwargs["path"] = path

    if (
        start_time
        and end_time
        and pagination_token is None
        and since_id is None
        and until_id is None
    ):
        stored = load_stored_tweets(username, **store_kwargs)
        if is_time_range_fully_stored(
            stored,
            start_time=start_time,
            end_time=end_time,
        ):
            print(
                "Warning: requested time range "
                f"{start_time} to {end_time} is fully covered by stored tweets "
                f"for @{username.lstrip('@')}; skipping API request."
            )
            return _store_result(
                source="stored",
                result_count=_result_count_in_window(
                    stored,
                    start_time=start_time,
                    end_time=end_time,
                    max_results=max_results,
                ),
            )

        gaps = uncovered_time_ranges(
            stored,
            start_time=start_time,
            end_time=end_time,
        )
        if gaps:
            for gap_start, gap_end in gaps:
                print(
                    "Warning: fetching uncovered range "
                    f"{gap_start} to {gap_end} for @{username.lstrip('@')}."
                )
                _fetch_and_store_range(
                    client,
                    user_id,
                    username,
                    start_time=gap_start,
                    end_time=gap_end,
                    max_results=max_results,
                    store_kwargs=store_kwargs,
                )

            updated = load_stored_tweets(username, **store_kwargs)
            return _store_result(
                source="stored+api",
                result_count=_result_count_in_window(
                    updated,
                    start_time=start_time,
                    end_time=end_time,
                    max_results=max_results,
                ),
            )

    params = _build_params(
        max_results=max_results,
        pagination_token=pagination_token,
        start_time=start_time,
        end_time=end_time,
        since_id=since_id,
        until_id=until_id,
    )
    payload = client.get(f"/users/{user_id}/tweets", params=params)
    store_tweets(username, payload, **store_kwargs)
    data = payload.get("data") or []
    meta = payload.get("meta") or {}
    return _store_result(
        source="api",
        result_count=meta.get("result_count", len(data)),
    )
