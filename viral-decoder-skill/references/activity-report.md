---
name: activity-report
description: >-
  Analyze posting activity for an X user — frequency, timing patterns, and
  content volume. Use when analyzing posting behavior, cadence, or how active
  an account is on X.
---

# Activity Report

Analyze posting activity using `get_and_store_user_tweets` and `load_stored_tweets`.

## Tools

| Tool | Module | Purpose |
|------|--------|---------|
| `get_user_by_username` | `scripts/profile.py` | Resolve `user_id` and `username` |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch, dedupe, and store timeline |
| `load_stored_tweets` | `scripts/store.py` | Read full saved dataset for analysis |

## Workflow

1. Resolve the user via `get_user_by_username` to obtain `user_id` and `username`.
2. Fetch tweets with `get_and_store_user_tweets` (paginate until the window is covered).
3. Load the full dataset with `load_stored_tweets(username)` for analysis.
4. Aggregate and report using the template below.
5. Save the report to `reports/{username}/activity.md`.

### Fetching tweets

```python
user = get_user_by_username(client, username)
result = get_and_store_user_tweets(
    client,
    user["id"],
    username=user["username"],                  # required
    start_time="2024-01-01T00:00:00Z",          # optional ISO 8601 UTC window
    end_time="2024-06-01T00:00:00Z",
    max_results=100,
)

tweets = load_stored_tweets(user["username"])
```

### Behavior

- **Auto-store:** each API page is merged into `tweets/{username}.json` with deduplication by tweet `id`.
- **Cache skip:** when `start_time` and `end_time` are fully covered by stored tweets, prints a warning and returns `source == "stored"` without an API call.
- **ID bounds:** use `since_id` / `until_id` for tweet ID filters; these take precedence over time filters per the X API.
- **Exclusions:** retweets and replies are excluded by default.

### Tweet fields available

Each stored tweet includes:

- `text`, `created_at`, `lang`, `public_metrics`, `url` — permalink to the post
- `entities.urls` — link URLs in text
- `media` — attached media metadata (`type`, `url`, `preview_image_url`, `alt_text`, `height`, `width`, `duration_ms`)

## Linking

Always link to X when referencing the account or a specific post:

- **Profile:** link the handle as `[@{username}](https://x.com/{username})` on first mention.
- **Any tweet cited:** use the stored `url` field as a markdown link — e.g. `[truncated text…]({url})` or `[view post]({url})`.
- **Fallback:** if `url` is missing, use `https://x.com/{username}/status/{id}`.

Never mention a tweet in the report body without its link.

## Metrics to compute

- Total posts in sample
- Posts per day/week (based on date range in sample)
- Busiest day of week and hour (UTC)
- Average post length (characters)
- Language breakdown if `lang` is available
- Media mix: photo / video / GIF counts from `media[].type`
- Link frequency from `entities.urls`

## Report template

```markdown
# Activity Report: [@{username}](https://x.com/{username})

## Sample
- **Posts analyzed:** {count}
- **Date range:** {oldest} → {newest}
- **Data source:** {stored / API / mixed}

## Cadence
- **Posts/day:** {rate}
- **Posts/week:** {weekly_rate}
- **Busiest day:** {day}
- **Busiest hour (UTC):** {hour}

## Content
- **Avg length:** {avg_chars} chars
- **Languages:** {lang_breakdown}
- **With media:** {pct_media}%
- **With links:** {pct_links}%

## Patterns
{Bullet points on notable posting habits — link any cited example posts}

## Summary
{2-3 sentences on how actively and consistently this account posts}
```

## Save report

- **Path:** `reports/{username}/activity.md` (strip leading `@` from username)
- **Format:** markdown file containing the filled template above
- Create `reports/{username}/` if it does not exist

## Notes

- Analyze from `load_stored_tweets`, not just the last page returned by fetch.
- Stored tweets are sorted by `created_at` descending in `tweets/{username}.json`.
- Note sample size limits — the API returns paginated results (max 100 per page).
- Call out gaps in the timeline if the sample is small or the window was served from cache.
- When citing any tweet, always include its permalink as a markdown link.
