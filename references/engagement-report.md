---
name: engagement-report
description: >-
  Generate an engagement analysis for an X user's posts — likes, retweets,
  replies, and impressions relative to audience size. Use when analyzing
  influence, reach, or how well content performs on X.
---

# Engagement Report

Measure engagement using `get_and_store_user_tweets`, `load_stored_tweets`, and `get_user_by_username`.

## Tools

| Tool | Module | Purpose |
|------|--------|---------|
| `get_user_by_username` | `scripts/profile.py` | Follower count and account context |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch, dedupe, and store timeline |
| `load_stored_tweets` | `scripts/store.py` | Read full saved dataset for analysis |

## Workflow

1. Fetch the user profile for follower count and context.
2. Fetch tweets with `get_and_store_user_tweets` (paginate if needed).
3. Load the full dataset with `load_stored_tweets(username)`.
4. Aggregate `public_metrics` across the sample.
5. Write the report using the template below.
6. Save the report to `reports/{username}/engagement.md`.

### Fetching tweets

```python
user = get_user_by_username(client, username)
result = get_and_store_user_tweets(
    client,
    user["id"],
    username=user["username"],
    start_time="2024-01-01T00:00:00Z",
    end_time="2024-06-01T00:00:00Z",
)

tweets = load_stored_tweets(user["username"])
```

## Metrics to compute

Per tweet (from `public_metrics`):

- `like_count`, `retweet_count`, `reply_count`, `quote_count`, `impression_count` (if available)

Aggregates:

- Mean and median for each metric
- Engagement rate: `(likes + retweets + replies + quotes) / followers`
- Top 5 posts by total engagement
- Bottom 5 posts (if sample ≥ 10)
- Media vs text-only engagement split (using `media` field)

## Linking

Always link to X when referencing the account or a specific post:

- **Profile:** link the handle as `[@{username}](https://x.com/{username})` on first mention.
- **Any tweet cited:** use the stored `url` field — e.g. `[truncated text…]({url})` with engagement stats inline.
- **Fallback:** if `url` is missing, use `https://x.com/{username}/status/{id}`.

Never list a top or underperforming post without its link.

## Report template

```markdown
# Engagement Report: [@{username}](https://x.com/{username})

## Context
- **Followers:** {followers}
- **Posts analyzed:** {count}
- **Date range:** {oldest} → {newest}
- **Data source:** {stored / API / mixed}

## Averages per post
| Metric      | Mean  | Median |
|-------------|-------|--------|
| Likes       | {avg} | {med}  |
| Retweets    | {avg} | {med}  |
| Replies     | {avg} | {med}  |
| Quotes      | {avg} | {med}  |
| Impressions | {avg} | {med}  |

## Engagement rate
- **Avg engagement rate:** {rate}% of followers

## Top posts
{Numbered list: [truncated text…](url), engagement total, date, media type if any}

## Underperformers
{If applicable — [truncated text…](url), lowest engagement posts}

## Summary
{2-3 sentences on typical reach, what content resonates, audience responsiveness}
```

## Save report

- **Path:** `reports/{username}/engagement.md` (strip leading `@` from username)
- **Format:** markdown file containing the filled template above
- Create `reports/{username}/` if it does not exist

## Notes

- Analyze from `load_stored_tweets`, not just the last page returned by fetch.
- Impression counts require appropriate API access tier.
- Compare engagement rate to follower count, not absolute numbers alone.
- Stored tweets include inline `media` metadata for correlating format with performance.
- If `get_and_store_user_tweets` returns `source == "stored"`, note that metrics are from cached data.
- Highlight outliers and possible viral posts.
- When citing any tweet, always include its permalink as a markdown link.
