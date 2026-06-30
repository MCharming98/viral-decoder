---
name: viral-decoder
description: >-
  Decode viral X content — analyze profiles, reverse-engineer viral playbooks,
  and generate structured account reports. Use when analyzing someone on X,
  generating account reports, or reverse-engineering what makes their content go viral.
---

# ViralDecoder

Analyze X accounts and produce structured reports: profile, viral playbook, activity, engagement, content insights, and visual HTML output.

## Setup

1. Copy `scripts/.env.example` to `.env` at the repo root and add X API credentials.
2. Install dependencies from the repo root:

```bash
pip install -e .
```

## Check API credentials

Before calling any X API tools, verify credentials are configured. ViralDecoder needs `X_BEARER_TOKEN` for read-only access (profile lookup, timelines).

```python
from scripts.config import XConfig

config = XConfig.from_env()
if not config.bearer_token:
    # Stop — do not call the API without credentials
    ...
```

Or from the shell:

```bash
python -c "from scripts.config import XConfig; c=XConfig.from_env(); exit(0 if c.bearer_token else 1)"
```

If `X_BEARER_TOKEN` is missing or empty:

1. Tell the user that API access is not configured.
2. Remind them to create an app and generate credentials at the [X Developer Platform](https://developer.x.com/).
3. Copy `scripts/.env.example` to `.env` at the repo root and set `X_BEARER_TOKEN` (and OAuth keys if they need write access later).
4. Do not proceed with API calls until credentials are in place.

Optional OAuth 1.0a variables (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`) are only needed for posting or user-context writes — not required for report generation.

## Tools

Python modules live under `scripts/`. Import after install:

```python
from scripts.client import XClient
from scripts.profile import get_user_by_username
from scripts.timeline import get_tweets, get_and_store_user_tweets
from scripts.store import load_stored_tweets, store_tweets, tweet_store_path
```

| Tool | Module | Purpose |
|------|--------|---------|
| `XClient` | `scripts/client.py` | HTTP client for X API v2 |
| `XConfig` | `scripts/config.py` | Load credentials from environment |
| `get_user_by_username` | `scripts/profile.py` | Profile lookup by @handle |
| `fetch_profile_image` | `scripts/profile.py` | Download profile image bytes |
| `get_tweets` | `scripts/timeline.py` | Fetch timeline from API (no storage) |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch, dedupe, and store timeline |
| `load_stored_tweets` | `scripts/store.py` | Read saved tweet dataset for analysis |
| `store_tweets` | `scripts/store.py` | Persist tweets to a JSON file |
| `tweet_store_path` | `scripts/store.py` | Resolve storage path for a username |

### Tweet storage

`store_tweets`, `get_and_store_user_tweets`, and `load_stored_tweets` accept an optional `path`:

- **Omitted** — defaults to `tweets/{username}.json`
- **Directory** — e.g. `path="data/tweets"` → `data/tweets/{username}.json`
- **File** — e.g. `path="data/tweets/alice.json"` → that exact file

```python
# Fetch without writing to disk
payload = get_tweets(client, user["id"], start_time=start, end_time=end)

# Fetch and store to default location
get_and_store_user_tweets(client, user["id"], username=user["username"])

# Fetch and store to a custom path
get_and_store_user_tweets(
    client, user["id"], username=user["username"], path="cache/alice.json"
)
tweets = load_stored_tweets(user["username"], path="cache/alice.json")
```

Use `get_tweets` for one-off API reads. Use `get_and_store_user_tweets` for report workflows — it deduplicates, merges, and skips refetch when the time range is already cached.

### Fetching tweets

**Default count:** Timeline fetches return the latest **100 tweets** by default (`max_results=100` in `get_tweets` and `get_and_store_user_tweets`). Do not change this without asking the user first — confirm whether they want more or fewer tweets before passing a different `max_results`.

**Check storage before the API:** Before calling `get_tweets` or `get_and_store_user_tweets`, always check whether tweets are already stored locally:

```python
from scripts.store import load_stored_tweets

username = user["username"]
stored = load_stored_tweets(username)  # or pass the same `path` you will use for fetch/store
if stored:
    # Use stored data when it covers the analysis window; only fetch gaps or new data
    ...
```

- Prefer `load_stored_tweets` when existing data is sufficient for the report or time range.
- Use `get_and_store_user_tweets` with `start_time` / `end_time` when you need a specific window — it skips the API if that range is fully cached and only fetches uncovered gaps.
- Call the API only when stored tweets are missing, incomplete for the requested window, or the user explicitly wants a fresh fetch.

### Data storage

- **Tweets:** `tweets/{username}.json` by default (override with `path`)
- **Reports:** `reports/{username}/` (one markdown file per report type)

## References

Read the reference file for the report type you need:

| Reference | When to use |
|-----------|-------------|
| [complete-report](references/complete-report.md) | Full account breakdown — profile, playbook, and statistics |
| [profile-report](references/profile-report.md) | Bio, metadata, follower metrics, account signals |
| [viral-playbook](references/viral-playbook.md) | Reverse-engineered SOP for viral posts |
| [activity-report](references/activity-report.md) | Posting cadence and content patterns |
| [engagement-report](references/engagement-report.md) | Likes, retweets, impressions, top posts |
| [content-insights](references/content-insights.md) | Audience, themes, format performance, voice |
| [html-report](references/html-report.md) | Infographic HTML page from markdown reports |

## Report pipeline

**Default report:** If the user does not specify which report they want, run the full **complete-report** pipeline and generate the HTML output — follow steps 1–7 below through `reports/{username}/complete-report.html`.

For a full analysis, follow **complete-report** — it orchestrates the sub-reports in order:

1. **profile-report** → `reports/{username}/profile.md`
2. **activity-report** → `reports/{username}/activity.md`
3. **engagement-report** → `reports/{username}/engagement.md`
4. **content-insights** → `reports/{username}/content-insights.md`
5. **viral-playbook** → `reports/{username}/viral-playbook.md`
6. Merge into `reports/{username}/complete-report.md`
7. **html-report** → `reports/{username}/complete-report.html`

Each sub-report can also run standalone. All reports link to X when citing profiles or posts.

## Notes

- `get_and_store_user_tweets` handles fetch, deduplication, and storage — use `get_tweets` when you only need the API response without writing to disk.
- Pass `path` to `get_and_store_user_tweets`, `store_tweets`, and `load_stored_tweets` to override the default `tweets/{username}.json` location.
- Use `load_stored_tweets` for analysis, not individual API pages.
- Flag data limitations (protected account, small sample, missing impressions, cached-only data).
- Stay factual — this is analysis, not judgment.
