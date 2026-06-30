---
name: profile-report
description: >-
  Generate a structured profile report for an X (Twitter) user. Covers bio,
  account metadata, follower metrics, and account signals. Use when analyzing
  a user profile, summarizing who someone is on X, or producing a ViralDecoder
  profile section.
---

# Profile Report

Generate a profile report for an X user using `get_user_by_username` from `scripts/profile.py`.

## Tools

| Tool | Module | Purpose |
|------|--------|---------|
| `get_user_by_username` | `scripts/profile.py` | Fetch profile by @handle |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch and store timeline (optional, for pinned post) |
| `load_stored_tweets` | `scripts/store.py` | Read saved tweets |

## Workflow

1. Resolve the target username (strip leading `@`).
2. Fetch profile data with `get_user_by_username`.
3. Write the report using the template below.
4. Save the report to `reports/{username}/profile.md`.

## Data to collect

From the user object, extract:

- `username`, `name`, `description`, `location`, `url`
- `created_at`, `verified`, `verified_type`, `protected`
- `public_metrics`: followers, following, tweet count, listed count
- `profile_image_url`, `pinned_tweet_id` (note if present)

## Linking

Always link to X when referencing the account or a specific post:

- **Profile:** link the handle as `[@{username}](https://x.com/{username})` on first mention in the report title and overview.
- **Pinned post:** if discussed, link using `https://x.com/{username}/status/{pinned_tweet_id}`.
- **Any tweet cited:** use the stored `url` field, or build `https://x.com/{username}/status/{id}` if missing.

## Report template

```markdown
# Profile Report: [@{username}](https://x.com/{username})

## Overview
- **Display name:** {name}
- **Handle:** [@{username}](https://x.com/{username})
- **Bio:** {description}
- **Location:** {location or "Not set"}
- **Website:** {url or "Not set"}
- **Joined:** {created_at}
- **Verified:** {verified} ({verified_type})
- **Protected:** {protected}

## Reach
| Metric    | Count |
|-----------|-------|
| Followers | {followers} |
| Following | {following} |
| Posts     | {tweet_count} |
| Listed    | {listed_count} |

## Signals
- Follower/following ratio: {ratio}
- Account age: {age}
- Pinned post: {yes/no — link to post if yes: [view](https://x.com/{username}/status/{pinned_tweet_id})}

## Summary
{2-3 sentences: who this account presents as, scale of audience, notable flags}
```

## Save report

- **Path:** `reports/{username}/profile.md` (strip leading `@` from username)
- **Format:** markdown file containing the filled template above
- Create `reports/{username}/` if it does not exist

## Notes

- Flag protected accounts — timeline tools may be limited.
- Follower count is current snapshot only; the X API has no follower history endpoint.
- Compute follower/following ratio; flag unusually high or low values.
- Keep tone factual and evidence-based.
- When citing any tweet, always include its permalink as a markdown link.
