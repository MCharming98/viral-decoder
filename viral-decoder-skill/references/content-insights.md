---
name: content-insights
description: >-
  Analyze an X user's tweets for audience signals, content themes, format
  performance, and writing style. Use when analyzing who someone speaks to,
  what they post about, what resonates, or how they communicate on X.
---

# Content Insights

Synthesize qualitative and quantitative patterns from stored tweets — audience, content types, performance by format, and voice.

## Tools

| Tool | Module | Purpose |
|------|--------|---------|
| `get_user_by_username` | `scripts/profile.py` | Bio, niche signals, follower context |
| `get_and_store_user_tweets` | `scripts/timeline.py` | Fetch and store timeline |
| `load_stored_tweets` | `scripts/store.py` | Full tweet dataset for analysis |

## Workflow

1. Fetch profile with `get_user_by_username` for bio, metrics, and positioning context.
2. Ensure tweets are stored via `get_and_store_user_tweets` (gap detection fills missing ranges automatically).
3. Load `load_stored_tweets(username)` as the analysis dataset.
4. Cluster tweets by theme, format, and engagement tier.
5. Infer audience and style from evidence in the data.
6. Write the report using the template below.
7. Save to `reports/{username}/content-insights.md`.

### Data collection

```python
user = get_user_by_username(client, username)
get_and_store_user_tweets(
    client,
    user["id"],
    username=user["username"],
    start_time=start_time,   # optional
    end_time=end_time,
)

tweets = load_stored_tweets(user["username"])
profile = user
```

## Analysis dimensions

### Target audience (inferred)

Use profile + tweet evidence — do not guess without signals.

- **Bio and location:** stated role, industry, affiliations
- **Topic clusters:** recurring themes (e.g. startups, AI, hardware, personal)
- **Who they engage with:** `entities.mentions` frequency and types of accounts
- **Conversation style:** high `reply_count` vs `like_count` suggests dialogue-driven audience
- **Language:** `lang` field distribution
- **Implied reader:** who would find this content useful (founders, engineers, general tech, etc.)

### Content types

Classify each tweet (a tweet can have multiple tags):

| Type | Signals |
|------|---------|
| Question | Ends with `?` or invites responses; high reply ratio |
| Opinion / take | Assertive statement, low media |
| Story / personal | First-person narrative, anecdote |
| Product / promo | Brand names, launches, `@` company accounts |
| Link share | `entities.urls` with external `expanded_url` |
| Photo / visual | `media[].type == photo` |
| Video / GIF | `media[].type` in `video`, `animated_gif` |
| Mention / shoutout | `entities.mentions` present |
| Thread fragment | Numbered posts, "🧵", continuation cues |

Report share of each type and average engagement per type.

### Performance patterns

Compare engagement across content types using `public_metrics`:

- **Engagement score:** `like_count + retweet_count + reply_count + quote_count`
- **Reply rate:** `reply_count / impression_count` (if impressions available)
- **Bookmark rate:** `bookmark_count / impression_count` (if available)
- **Top performers:** highest engagement by type — what format + theme combo wins
- **Underperformers:** consistent low engagement despite similar cadence
- **Outliers:** posts with engagement > 3× median — note topic and format

### Voice and style

Analyze `text` across the sample:

- **Tone:** formal / casual / humorous / earnest / provocative
- **Length:** short (<80 chars) vs long-form; avg character count
- **Capitalization:** lowercase aesthetic vs standard
- **Emoji and punctuation:** frequency, expressive markers
- **Person:** first person ("I", "my") vs collective ("we") vs impersonal
- **Signature patterns:** recurring phrases, openers, rhetorical habits
- **Multilingual mix:** if multiple `lang` values

## Linking

Always link to X when referencing the account or a specific post:

- **Profile:** link the handle as `[@{username}](https://x.com/{username})` on first mention.
- **Any tweet cited:** use the stored `url` field — e.g. `[truncated text…]({url})`.
- **Fallback:** if `url` is missing, use `https://x.com/{username}/status/{id}`.

Never quote or reference an example post without its link.

## Report template

```markdown
# Content Insights: [@{username}](https://x.com/{username})

## Sample
- **Posts analyzed:** {count}
- **Date range:** {oldest} → {newest}
- **Followers:** {followers}
- **Data source:** {stored / API / mixed}

## Target audience
- **Primary audience:** {who they appear to speak to}
- **Secondary audience:** {if applicable}
- **Evidence:**
  - {bullet: bio/role signal}
  - {bullet: topic cluster}
  - {bullet: engagement pattern}

## Content mix
| Type | Share | Avg engagement |
|------|-------|----------------|
| {type} | {pct}% | {score} |

## Top themes
1. **{theme}** — {post count}, {avg engagement}, [{example truncated text…}](url)
2. **{theme}** — ...
3. **{theme}** — ...

## What performs best
- **Best format:** {photo / question / link / etc.}
- **Best topics:** {themes with highest avg engagement}
- **Standout posts:**
  - [{truncated text…}](url) — {date}, {engagement}, {format}

## What underperforms
- {format or theme with consistently lower engagement — link example posts}

## Voice and style
- **Tone:** {description}
- **Typical length:** {avg chars}
- **Distinctive habits:** {patterns observed}
- **Example voice:** {1-2 representative quotes as links — [truncated text…](url)}

## Strategic read
{3-5 sentences: how this account builds its audience, what content strategy is visible, what niche they own}

## Recommendations
- {Optional: content angles that fit their style and audience — evidence-based only}
```

## Save report

- **Path:** `reports/{username}/content-insights.md` (strip leading `@` from username)
- **Format:** markdown file containing the filled template above
- Create `reports/{username}/` if it does not exist

## Notes

- Ground every claim in tweet or profile evidence; label inferences clearly.
- Small samples (<30 posts) — note low confidence on theme and audience conclusions.
- Reply-heavy posts may reflect conversation starters, not necessarily audience size.
- Do not infer demographics (age, gender, income) unless explicitly stated in bio or tweets.
- Cross-reference [engagement-report](engagement-report.md) for raw metrics; this reference focuses on meaning and patterns.
- Stay factual — describe what the content does, not who the person is as a moral judgment.
- When citing any tweet, always include its permalink as a markdown link.
