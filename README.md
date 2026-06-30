# ViralDecoder

Decode viral X content — analyze profiles, reverse-engineer viral playbooks, and generate structured account reports. Agent skills produce reports; Python scripts connect to the X API and expose tools.

## Layout

```
viral-decoder-skill/
  SKILL.md              Entry point for agents — setup, tools, pipeline
  references/           Report templates (one .md per report type)
  scripts/              Flat Python package — client, config, and tools
    client.py
    config.py
    profile.py
    timeline.py
    store.py
    .env.example
reports/                Generated account reports
tweets/                 Cached tweet datasets (default storage location)
```

## Setup

1. Copy `viral-decoder-skill/scripts/.env.example` to `.env` at the repo root.
2. Set `X_BEARER_TOKEN` for read-only API access (profile lookup, timelines). Create an app and generate credentials at the [X Developer Platform](https://developer.x.com/).
3. Install dependencies:

```bash
pip install -e .
```

Verify credentials:

```bash
python -c "from scripts.config import XConfig; c=XConfig.from_env(); exit(0 if c.bearer_token else 1)"
```

OAuth 1.0a variables (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`) are only needed for posting — not for report generation.

## Usage

```python
from scripts.client import XClient
from scripts.profile import get_user_by_username
from scripts.timeline import get_tweets, get_and_store_user_tweets
from scripts.store import load_stored_tweets

client = XClient()
user = get_user_by_username(client, "username")

# Fetch without storing
payload = get_tweets(client, user["id"], max_results=100)

# Fetch, dedupe, and cache locally (default: tweets/{username}.json)
get_and_store_user_tweets(client, user["id"], username=user["username"])
tweets = load_stored_tweets(user["username"])
```

### Custom tweet storage

`get_and_store_user_tweets`, `store_tweets`, and `load_stored_tweets` accept an optional `path`:

- **Omitted** — `tweets/{username}.json`
- **Directory** — `path="data/tweets"` → `data/tweets/{username}.json`
- **File** — `path="cache/alice.json"` → that exact file

```python
get_and_store_user_tweets(
    client, user["id"], username="alice", path="cache/alice.json"
)
tweets = load_stored_tweets("alice", path="cache/alice.json")
```

## Reports

Use `viral-decoder-skill/SKILL.md` to drive report generation. Reference templates live in `viral-decoder-skill/references/`:

| Reference | Output |
|-----------|--------|
| profile-report | `reports/{username}/profile.md` |
| activity-report | `reports/{username}/activity.md` |
| engagement-report | `reports/{username}/engagement.md` |
| content-insights | `reports/{username}/content-insights.md` |
| viral-playbook | `reports/{username}/viral-playbook.md` |
| complete-report | `reports/{username}/complete-report.md` |
| html-report | `reports/{username}/complete-report.html` |

For a full account analysis, follow **complete-report** — it orchestrates the sub-reports and merges them into one document.
