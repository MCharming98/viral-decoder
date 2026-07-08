---
name: viral-playbook
description: >-
  Reverse-engineer an X account's repeatable SOP for creating viral posts —
  hooks, post anatomy, distribution tactics, and anti-patterns backed by data.
  Use when the user wants a viral playbook, content SOP, or growth formula
  for someone on X.
---

# Viral Playbook

Synthesize a step-by-step playbook for how an account creates posts that go viral — not generic X advice, but a data-backed SOP specific to this account.

## Tools

| Tool | Module | Purpose |
|------|--------|---------|
| `get_user_by_username` | `scripts/profile.py` | Bio, pinned post, follower context |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch, dedupe, and store timeline |
| `load_stored_tweets` | `scripts/store.py` | Read full saved dataset for analysis |

## Workflow

1. Fetch profile with `get_user_by_username` for bio, metrics, and pinned post.
2. Ensure tweets are stored via `get_and_store_user_tweets` (paginate if needed).
3. Load `load_stored_tweets(username)` as the analysis dataset.
4. Follow [engagement-report](engagement-report.md) and [content-insights](content-insights.md) if their saved reports are missing or stale; otherwise read `reports/{username}/engagement.md` and `reports/{username}/content-insights.md`.
5. Read the full text of top 10–15 posts to extract hook patterns, post anatomy, and distribution tactics.
6. Synthesize the playbook using the template below.
7. Save to `reports/{username}/viral-playbook.md`.

### Data collection

```python
user = get_user_by_username(client, username)
result = get_and_store_user_tweets(
    client,
    user["id"],
    username=user["username"],
    start_time=start_time,   # optional
    end_time=end_time,
)

tweets = load_stored_tweets(user["username"])
```

Pull from engagement-report and content-insights outputs plus profile signals (pinned post, bio positioning, follower ratio).

## What to cover

Answer: *What is this account's repeatable SOP for creating posts that go viral?*

| Angle | What to look for |
|-------|------------------|
| **Core formula** | The 1-sentence thesis behind their content strategy |
| **The SOP** | Step-by-step workflow: trigger → hook → format → proof → distribution → follow-up |
| **Hook library** | Named hook templates with linked examples (provocative opener, milestone counter, builder reveal, etc.) |
| **Post anatomy** | Structure of top posts: line count, char length, media type, CTA placement |
| **Winning format** | Content type with highest avg engagement — cite multiplier vs baseline |
| **Distribution levers** | Ecosystem tagging, pinning, reply-thread CTAs, launch-day exceptions |
| **Content arc** | How posts build on each other chronologically (community → win → demo → milestone) |
| **Timing** | Day/hour patterns for top performers vs account average |
| **Anti-patterns** | What they do that *doesn't* work — contrast with top posts |

## Rules

- Every claim needs a number or linked example post.
- Extract 3–5 named hook templates from top performers, not vague traits.
- Document the SOP as numbered steps a reader could follow.
- Compare top performers to account averages (e.g. "video posts average 3× overall mean").
- Note top-post avg length vs underperformers when the gap is meaningful.
- If follower history is unavailable (API limitation), infer growth strategy from content that over-indexes on engagement rate — do not invent follower growth numbers.
- If sample is too small (<30 posts), note low confidence and keep claims narrow.

## Linking

Always link to X when referencing the account or a specific post:

- **Profile:** link the handle as `[@{username}](https://x.com/{username})` on first mention.
- **Any tweet cited:** use the stored `url` field — e.g. `[truncated text…]({url})`.
- **Fallback:** if `url` is missing, use `https://x.com/{username}/status/{id}`.

Never mention a tweet anywhere in the playbook without its link.

## Report template

```markdown
# Viral Playbook: [@{username}](https://x.com/{username})

## Sample
- **Posts analyzed:** {count}
- **Date range:** {oldest} → {newest}
- **Followers:** {followers}
- **Data source:** {stored / API / mixed}

## Core formula
{2-3 sentences: the thesis behind their viral content — what they repeat and why it works for their niche}

## The SOP
How @{username} creates a viral post, step by step:

1. **{Step name}** — {what they do}. Evidence: {metric or linked example}
2. **{Step name}** — {what they do}. Evidence: {metric or linked example}
3. **{Step name}** — {what they do}. Evidence: {metric or linked example}
4. **{Step name}** — {what they do}. Evidence: {metric or linked example}
5. **{Step name}** — {what they do}. Evidence: {metric or linked example}

## Hook library
| Hook type | Template | Avg engagement | Example |
|-----------|----------|----------------|---------|
| {name} | "{opening pattern…}" | {N} ({multiplier}×) | [{truncated…}](url) |
| {name} | "{opening pattern…}" | {N} | [{truncated…}](url) |
| {name} | "{opening pattern…}" | {N} | [{truncated…}](url) |

## Post anatomy (top performers)
- **Length:** {avg chars for top 20 vs bottom 20}
- **Structure:** {typical line pattern — hook → proof → CTA}
- **Media:** {format split in top 20 with avg engagement per format}
- **CTA placement:** {where links/sign-ups go — in-post vs reply thread}

## Distribution playbook
- {pinned post strategy with engagement number}
- {ecosystem tags — who they @ and how often in top posts}
- {reply-thread pattern for CTAs after viral main post}
- {launch-day exceptions if any}

## Content arc
{Chronological narrative of how their top posts build on each other — e.g. community post → accelerator win → product demo → milestone → pin}

## What to skip
- {anti-pattern 1 with linked low-performer and contrast metric}
- {anti-pattern 2 with linked low-performer and contrast metric}

## Bottom line
{1-2 sentences: the single most important SOP step to copy for similar results}
```

## Save report

- **Path:** `reports/{username}/viral-playbook.md` (strip leading `@` from username)
- **Format:** markdown file containing the filled template above
- Create `reports/{username}/` if it does not exist

## Notes

- Cross-reference [engagement-report](engagement-report.md) for top/underperforming posts and [content-insights](content-insights.md) for themes, format mix, and voice.
- Analyze from `load_stored_tweets`, not just the last page returned by fetch.
- Each stored tweet includes `url` (permalink), `media` metadata, and `entities.urls` for content analysis.
- Flag data limitations (protected account, small sample, missing impressions, cached-only data).
- Stay factual — this is analysis, not judgment.
- When citing any tweet, always include its permalink as a markdown link.
