from typing import Any

import httpx

from scripts.client import XClient

DEFAULT_USER_FIELDS = (
    "created_at,description,entities,id,location,name,"
    "pinned_tweet_id,profile_image_url,protected,public_metrics,"
    "url,username,verified,verified_type"
)

PROFILE_IMAGE_SIZES = ("mini", "normal", "bigger", "400x400")


def resolve_profile_image_url(url: str, size: str = "400x400") -> str:
    """Return a profile image URL for the requested X CDN size variant."""
    if size not in PROFILE_IMAGE_SIZES:
        raise ValueError(f"size must be one of {PROFILE_IMAGE_SIZES}")
    for variant in PROFILE_IMAGE_SIZES:
        suffix = f"_{variant}"
        if suffix in url:
            return url.replace(suffix, f"_{size}")
    return url


def get_user_by_username(client: XClient, username: str) -> dict[str, Any]:
    """Fetch a user profile by @username."""
    payload = client.get(
        f"/users/by/username/{username.lstrip('@')}",
        params={"user.fields": DEFAULT_USER_FIELDS},
    )
    return payload.get("data", {})


def fetch_profile_image(
    client: XClient,
    username: str,
    *,
    size: str = "400x400",
    timeout: float = 30.0,
) -> dict[str, Any]:
    """Fetch profile image bytes and metadata for @username."""
    user = get_user_by_username(client, username)
    raw_url = user.get("profile_image_url")
    if not raw_url:
        raise ValueError(f"No profile image for @{username.lstrip('@')}")

    url = resolve_profile_image_url(raw_url, size=size)
    response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()

    return {
        "username": user.get("username", username.lstrip("@")),
        "url": url,
        "content": response.content,
        "content_type": response.headers.get("content-type", "image/jpeg"),
        "size": size,
    }
