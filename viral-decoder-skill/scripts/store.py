import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DEFAULT_TWEETS_DIR = Path("tweets")


def tweet_store_path(username: str, path: Path | str | None = None) -> Path:
    """Resolve the JSON file path for a user's stored tweets."""
    clean_username = username.lstrip("@")
    if path is None:
        return DEFAULT_TWEETS_DIR / f"{clean_username}.json"
    resolved = Path(path)
    if resolved.suffix == ".json":
        return resolved
    return resolved / f"{clean_username}.json"


def _extract_tweets(payload: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return payload
    return payload.get("data") or []


def _extract_media(payload: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return []
    includes = payload.get("includes") or {}
    return includes.get("media") or []


def _media_by_key(media_items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        item["media_key"]: item
        for item in media_items
        if item.get("media_key")
    }


def tweet_url(username: str, tweet_id: str) -> str:
    """Build the permalink for a tweet."""
    return f"https://x.com/{username.lstrip('@')}/status/{tweet_id}"


def _attach_urls(
    tweets: list[dict[str, Any]],
    username: str,
) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for tweet in tweets:
        tweet = dict(tweet)
        tweet_id = tweet.get("id")
        if tweet_id:
            tweet["url"] = tweet_url(username, tweet_id)
        enriched.append(tweet)
    return enriched


def _attach_media(
    tweets: list[dict[str, Any]],
    media_items: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if not media_items:
        return tweets

    lookup = _media_by_key(media_items)
    enriched: list[dict[str, Any]] = []
    for tweet in tweets:
        tweet = dict(tweet)
        media_keys = (tweet.get("attachments") or {}).get("media_keys") or []
        if media_keys:
            tweet["media"] = [
                lookup[key] for key in media_keys if key in lookup
            ]
        enriched.append(tweet)
    return enriched


def _sort_tweets_desc(tweets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        tweets,
        key=lambda tweet: tweet.get("created_at") or "",
        reverse=True,
    )


def _merge_tweets(
    existing: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    without_id: list[dict[str, Any]] = []
    by_id: dict[str, dict[str, Any]] = {}

    for tweet in existing:
        tweet_id = tweet.get("id")
        if tweet_id is None:
            without_id.append(tweet)
            continue
        by_id[tweet_id] = tweet

    for tweet in incoming:
        tweet_id = tweet.get("id")
        if tweet_id is None:
            without_id.append(tweet)
            continue
        by_id[tweet_id] = tweet

    return without_id + list(by_id.values())


def load_stored_tweets(
    username: str,
    *,
    path: Path | str | None = None,
) -> list[dict[str, Any]]:
    """Load stored tweets for a user, or an empty list if none exist."""
    output_path = tweet_store_path(username, path)
    if not output_path.exists():
        return []
    return json.loads(output_path.read_text())


def _parse_created_at(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return datetime.strptime(value, "%a %b %d %H:%M:%S %z %Y")


def stored_time_range(
    tweets: list[dict[str, Any]],
) -> tuple[datetime, datetime] | None:
    """Return (oldest, newest) created_at from stored tweets."""
    timestamps = [
        _parse_created_at(tweet["created_at"])
        for tweet in tweets
        if tweet.get("created_at")
    ]
    if not timestamps:
        return None
    return min(timestamps), max(timestamps)


def filter_tweets_by_time(
    tweets: list[dict[str, Any]],
    *,
    start_time: str,
    end_time: str,
) -> list[dict[str, Any]]:
    """Return tweets whose created_at falls within [start_time, end_time]."""
    start = _parse_created_at(start_time)
    end = _parse_created_at(end_time)
    return [
        tweet
        for tweet in tweets
        if tweet.get("created_at")
        and start <= _parse_created_at(tweet["created_at"]) <= end
    ]


def is_time_range_fully_stored(
    tweets: list[dict[str, Any]],
    *,
    start_time: str,
    end_time: str,
) -> bool:
    """True when stored tweets fully cover the requested time window."""
    stored_range = stored_time_range(tweets)
    if stored_range is None:
        return False

    oldest_stored, newest_stored = stored_range
    start = _parse_created_at(start_time)
    end = _parse_created_at(end_time)
    return oldest_stored <= start and end <= newest_stored


def _format_ts(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return (
        value.astimezone(timezone.utc)
        .replace(microsecond=0)
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    )


def uncovered_time_ranges(
    tweets: list[dict[str, Any]],
    *,
    start_time: str,
    end_time: str,
) -> list[tuple[str, str]]:
    """Return uncovered [start, end] ranges within the requested window."""
    start = _parse_created_at(start_time)
    end = _parse_created_at(end_time)
    if start > end:
        return []

    if is_time_range_fully_stored(
        tweets,
        start_time=start_time,
        end_time=end_time,
    ):
        return []

    stored_range = stored_time_range(tweets)
    if stored_range is None:
        return [(start_time, end_time)]

    oldest_stored, newest_stored = stored_range
    gaps: list[tuple[str, str]] = []

    if start < oldest_stored:
        gap_end = min(end, oldest_stored - timedelta(seconds=1))
        if start <= gap_end:
            gaps.append((_format_ts(start), _format_ts(gap_end)))

    if end > newest_stored:
        gap_start = max(start, newest_stored + timedelta(seconds=1))
        if gap_start <= end:
            gaps.append((_format_ts(gap_start), _format_ts(end)))

    if not gaps:
        return [(start_time, end_time)]

    return gaps


def store_tweets(
    username: str,
    payload: dict[str, Any] | list[dict[str, Any]],
    *,
    path: Path | str | None = None,
    merge: bool = True,
) -> Path:
    """Store tweets in a JSON file, sorted by created_at descending."""
    clean_username = username.lstrip("@")
    output_path = tweet_store_path(clean_username, path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    incoming = _attach_media(_extract_tweets(payload), _extract_media(payload))
    existing: list[dict[str, Any]] = []
    if merge and output_path.exists():
        existing = json.loads(output_path.read_text())

    tweets = _attach_urls(
        _sort_tweets_desc(_merge_tweets(existing, incoming)),
        clean_username,
    )

    output_path.write_text(json.dumps(tweets, indent=2) + "\n")
    return output_path
