# AI-Assisted Website Quality Auditor - Retail Sector

A tool that audits retail-sector websites and produces a report scoring how
professional, complete, and business-ready each site is. It combines a
rule-based scraper (extracts factual data) with a scoring engine that works
**with or without an API key**:

- **Offline mode (no API key needed):** a built-in rule-based engine scores
  the site by checking facts like page title, meta description, navigation,
  contact form, CTAs, social links, alt-text coverage, load time, and the
  mobile viewport tag.
- **AI mode (optional):** if an `ANTHROPIC_API_KEY` is set, the facts are
  sent to Anthropic Claude for a deeper judgment-based score and tailored
  recommendations.

## What It Does

1. Reads a list of website URLs from `sites.txt`
2. Scrapes each site to extract factual data (status code, title, images,
   CTAs, social links, mobile viewport, load time, and more)
3. Scores each site out of 100 — automatically, with no API needed — and
   lists missing features, problems, recommendations, and a priority level
4. Combines everything into a Markdown report saved at `output/audit_report.md`

## Setup & Installation

```bash
# 1. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS/Linux

# 2. Install dependencies
pip install -r requirements.txt
```

## Setting the API Key (Optional)

The tool runs fully offline without any API key. Setting a key is only needed
if you want Claude's AI-based judgment instead of the built-in rule-based
scoring.

### Option A: .env file (recommended)

1. Copy `.env.example` to `.env`:

```bash
copy .env.example .env         # Windows
cp .env.example .env           # macOS/Linux
```

2. Open `.env` and paste your key:

```
ANTHROPIC_API_KEY=sk-ant-...
```

The `.env` file is loaded automatically by the script via `python-dotenv`.

### Option B: Environment variable

```bash
# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-..."
```

```bash
# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-..."
```

Get a key at [console.anthropic.com](https://console.anthropic.com/).

## Configuring Sites

Edit `sites.txt` and add one retail website URL per line
(blank lines and lines starting with `#` are ignored):

```
https://www.apple.com
https://www.zara.com
https://www.nike.com
```

## Running the Project

No API key needed — it works out of the box:

```bash
python main.py
```

Progress is printed to the console as each site is scraped and scored.
The final report is written to `output/audit_report.md`.

### Offline vs AI mode

- **By default** the tool runs in offline mode (rule-based scoring) whenever
  no `ANTHROPIC_API_KEY` is present.
- If an `ANTHROPIC_API_KEY` is set in `.env`, it automatically uses Claude
  for the AI judgment.
- To force offline mode even with a key set:

```bash
python main.py --offline
```

Each site's console output and report section shows which mode was used
(`Mode: rule-based scoring` vs `Mode: Claude AI`).

## Detected Facts (Script) vs Score (Offline Engine / Claude)

The report separates each site's results into two sections. Only the facts
on the left are scraped; everything on the right is the judgment — produced
either by the built-in offline rules engine or by Claude when a key is set.

| Automatically Detected Facts (Script) | Generated Judgment (Score) |
|---|---|
| HTTP status code | Overall score (0-100) |
| Page title | Missing features list |
| Meta description | Problems list |
| Navigation link count | Recommendations list |
| Contact form presence (`<form>` tag) | Priority level (High/Medium/Low) |
| CTA buttons (text matching buy/shop/sign up/etc.) | |
| Social media links (FB, IG, X, LinkedIn, TikTok, etc.) | |
| Total images & images with alt text | |
| Page load time (measured in seconds) | |
| Viewport meta tag presence (mobile signal) | |
| robots.txt allow/block status | |

### How the offline score is calculated

100 points are distributed across 9 checks:

| Check | Max Points |
|---|---|
| Page title present | 10 |
| Meta description present | 10 |
| Navigation links (5+) | 10 |
| Contact form present | 10 |
| CTA buttons found | 15 |
| Social media links (1-5 platforms) | 5-10 |
| Alt-text coverage on images (0-100%) | 5-15 |
| Fast page load time (<2s / <4s / slower) | 10 / 6 / 2 |
| Viewport meta tag present | 10 |

Priority: High (score < 50), Medium (50-69), Low (70+).

## Limitations

Be aware of the following gaps:

1. **No JavaScript rendering.** The scraper uses `requests` + `BeautifulSoup`
   and only parses the raw HTML. Content loaded dynamically with JavaScript
   (e.g. React/Vue single-page apps, lazy-loaded images, popup CTAs) will be
   missed and reported as absent.
2. **Scores are heuristics/judgment, not truth.** The offline score is a
   fixed weighted formula over 9 basic checks, and Claude's AI score is a
   model judgment. Both are directional guides — the offline score can't
   understand design quality, and different AI models/prompts can produce
   different scores. Sanity-check results by hand.
3. **Mobile responsiveness is not really tested.** The script only checks
   for a `<meta name="viewport">` tag. It does **not** run a headless browser
   or test actual rendering at mobile widths.
4. **Social/CTA detection is text-based.** Links are matched by domain
   (`facebook.com`, etc.) and button text against keywords. Oddly branded
   links or icon-only buttons may be missed.
5. **Blocked/bot-protected sites may fail.** Sites using Cloudflare or heavy
   bot protection can return 403 even with a browser User-Agent.
6. **Load time is approximate.** Measured as full-response time, not
   render/time-to-interactive. Slower on mobile networks.
7. **Only the homepage is audited.** Content on sub-pages is not inspected.

## What a Human Reviewer Should Still Check Manually

- Open each site in a real browser and verify the score feels right.
- Click through to product pages, checkout flow, and contact page — the
  homepage alone doesn't prove the site is business-ready.
- Test the site on an actual phone or tablet at multiple widths.
- Run page-speed tools (Google PageSpeed Insights, Lighthouse) for true
  performance numbers.
- Check broken links, form submissions, and purchase flow manually.
- Verify business details the script can't see: shipping policy, returns,
  privacy policy, tax/legal pages.

## Project Structure

```
├── main.py              # End-to-end pipeline (entry point, supports --offline)
├── scraper.py           # Extracts facts from each website
├── ai_auditor.py        # Scores sites (offline rules engine or Claude API)
├── report_generator.py  # Builds the Markdown report
├── sites.txt            # List of URLs to audit (one per line)
├── output/
│   └── audit_report.md  # Generated report
├── requirements.txt     # Python dependencies
├── .env.example         # Template for the API key file
└── README.md            # This file
```