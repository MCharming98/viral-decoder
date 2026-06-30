# ViralDecoder

Decode viral X content — analyze profiles, reverse-engineer viral playbooks, and generate structured account reports with any AI assistant.

ViralDecoder is an **AI skill**: a repo with instructions, report templates, and Python tools that connect to the X API, cache tweet data, and produce markdown and HTML reports. You describe what you want in plain language; your AI reads `SKILL.md` and handles the rest.

## What you get

| Report | What it covers |
|--------|----------------|
| **Profile** | Bio, metadata, follower metrics, account signals |
| **Activity** | Posting cadence and content patterns |
| **Engagement** | Likes, retweets, impressions, top posts |
| **Content insights** | Audience, themes, format performance, voice |
| **Viral playbook** | Reverse-engineered SOP for what makes posts spread |
| **Complete report** | All of the above merged into one document |
| **HTML report** | Visual infographic page built from the complete report |

By default, asking for a report without specifying a type produces the full analysis as an HTML page at `reports/{username}/complete-report.html`.

## Setup

Tell your AI:

> Set up this skill: https://github.com/MCharming98/viral-decoder/blob/main/viral-decoder-skill/SKILL.md

## Usage

Ask your AI to analyze an X account. You don't need to run scripts yourself — describe the account and the report you want.

### Example prompts

| Goal | Try saying… |
|------|-------------|
| Full analysis (default) | *Analyze @naval on X and generate a report.* |
| Full analysis (explicit) | *Run ViralDecoder on @levelsio — I want the complete HTML report.* |
| Profile only | *Generate a profile report for @paulg.* |
| Activity & cadence | *How often does @sama post? Give me an activity report.* |
| Engagement metrics | *Create an engagement report for @elonmusk — top posts, likes, and retweets.* |
| Content themes | *Analyze @balajis's content and write a content-insights report.* |
| Viral playbook | *Reverse-engineer the viral playbook for @dhh — what makes their posts spread?* |
| Markdown only | *Generate the complete markdown report for @shl — skip the HTML for now.* |
| HTML from existing data | *Turn the complete markdown report for @shl into the infographic HTML.* |

Reports are saved under `reports/{username}/`. Tweet data is cached in `tweets/{username}.json` so repeat runs don't re-fetch unnecessarily.

## Project layout

```
viral-decoder-skill/
  SKILL.md              Instructions for your AI assistant
  references/           Report templates
  scripts/              X API client and data tools
reports/                Generated reports
tweets/                 Cached tweet datasets
```

## License

See [LICENSE](LICENSE).
