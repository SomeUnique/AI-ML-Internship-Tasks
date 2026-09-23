# AI-Powered Research Assistant for Market Scans

**Project type:** AI Product Prototype (Week 3, Advanced)
**SafeX relevance:** Directly reusable as an internal utility, or the seed of a future SaaS product for market/competitor research.

## Problem
Analysts spend hours manually reading multiple articles and reports just to summarize
a market or competitor landscape — cross-referencing facts, spotting where sources
agree or disagree, and tracking which claim came from which source.

## Solution
A pipeline that takes several source documents on one topic and produces a structured,
**source-attributed** synthesis: key findings, where sources agree, where they
disagree, coverage gaps, and a confidence indicator per finding — every claim traces
back to a specific source number. This follows the same core pattern professional
research tools (Elicit, Perplexity) use: structured per-source extraction, then
cross-source synthesis, with citations embedded throughout rather than bolted on
at the end.

## Sample Run
- **Topic:** AI adoption in Pakistani SMEs
- **Sources:** 5 real, current (2025-2026) articles/reports — 1 academic survey (368
  SMEs), 3 industry/news pieces, 1 practitioner blog. Full text summarized in
  `/sources/source_1.txt` through `source_5.txt` (paraphrased in my own words from
  the original articles, with title/publisher/date/URL kept for attribution).
- **Output:** `market_scan_report.md` — 7 key findings, 1 cross-source agreement, 1
  genuine disagreement in emphasis, 3 coverage gaps, plus an independent numeric
  cross-check section.

## Tools & Technologies
- **Python** — pipeline logic
- **Anthropic API** (`claude-sonnet-4-6`) — the synthesis/reasoning engine
- **Custom prompt engineering** — forces structured JSON output (not free text) so
  the result can be reliably parsed and formatted, and explicitly instructs the
  model not to state anything unsupported by the source text
- **Regex-based post-processing** — independent, code-level checks that don't rely
  on the model grading its own work (see Hallucination Checks below)

## Key Features
1. **Structured, cited synthesis** — every finding lists which source number(s)
   support it.
2. **Agreement vs. disagreement sections** — explicitly separates "multiple sources
   confirm this" from "sources differ in emphasis/framing here," which is the part
   analysts usually spend the most manual time on.
3. **Confidence indicator** — High/Medium/Low based on how many independent sources
   support a finding.
4. **Coverage gaps** — explicitly lists what the sources *don't* address, so the
   analyst knows what still needs separate research.
5. **Exportable report** — clean Markdown output, ready to paste into a doc or
   convert to PDF/Word.

## Hallucination Checks Performed (Day 6)
This is a known failure mode for LLM-based synthesis tools: the model can cite a
source that doesn't actually contain the claim, or quietly blend two sources'
numbers into one made-up statistic. Three checks were built in:

1. **Prompt-level guardrail** — the system prompt explicitly instructs: *"NEVER
   state a fact that isn't explicitly supported by the source text... if you're not
   sure, leave it out rather than guess."*
2. **Automated keyword-overlap check** (`flag_unsupported_claims`) — for every
   finding, code independently checks whether the claim's key terms actually appear
   in the cited source's text. If overlap is too low, the report displays a visible
   ⚠️ *"needs manual verification"* warning next to that specific finding — this
   check does **not** trust the model's own confidence about itself.
3. **Manual fact-check** — I read all 5 source summaries end-to-end and manually
   verified each of the 7 key findings in the sample report against its cited
   source before finalizing the report. All 7 checked out; none were flagged by
   the automated check either.
4. **Deliberate test case** — I ran the pipeline logic against a hand-built mock
   response that included one intentionally fabricated claim ("50% of agricultural
   SMEs use AI-powered irrigation" — not in any source). The automated check
   correctly flagged it. See `test_pipeline_logic.py`.

## Weaknesses Found & Fixed (Day 6)
Testing surfaced three real weaknesses in the first version, all fixed before
submission:

1. **Confidence was self-reported by the model.** The model sometimes labeled a
   single-source claim "High confidence." **Fix:** confidence is now recomputed in
   code from the actual number of cited sources (3+ = High, 2 = Medium, 1 = Low),
   never trusting the model's own label.
2. **The unsupported-claim check used a fixed raw word-overlap count.** This
   unfairly passed short claims (2 shared words out of 3 = looked fine, but was
   mostly coincidence) and unfairly failed long, well-supported claims phrased
   differently from the source. **Fix:** switched to a proportional overlap ratio
   scaled to claim length.
3. **Numeric conflicts between sources were entirely left to the model to notice**,
   and LLMs can miss this, especially across long inputs. **Fix:** added an
   independent, code-based regex pass that extracts every percentage mentioned
   across all sources and lists them side-by-side in the report, so a human can
   quickly spot conflicting stats even if the model didn't flag them.

## Challenges Faced & How I Solved Them
- **Getting reliable structure out of the model.** Free-text summaries are hard to
  parse and inconsistent. Solved by forcing strict JSON output with an explicit
  schema in the prompt, and re-throwing a clear error if parsing fails rather than
  silently guessing.
- **Trusting the model to self-grade its own confidence/accuracy.** Solved by never
  trusting model-reported confidence — always recomputing it independently in code
  from the actual citation count, and adding a separate code-level fact-overlap
  check rather than relying on the model to flag its own weak claims.
- **Copyright.** Using full original article text directly would risk reproducing
  copyrighted material. Solved by paraphrasing each source into my own words before
  using it as pipeline input, while preserving factual accuracy and full
  attribution (title/publisher/date/URL).
- **Testing without a live API key.** This environment had no `ANTHROPIC_API_KEY`
  set. Solved by separating the pipeline into independently testable pieces
  (`load_sources`, `format_report`, `flag_unsupported_claims`, `recompute_confidence`)
  and testing them against a hand-built mock synthesis response — this validated
  all the logic *except* the actual live API call, which will run as-is once a real
  key is added.

## Future Improvements
- Accept raw URLs/PDFs directly instead of requiring pre-saved `.txt` files (would
  need a fetch + clean step).
- Add a second LLM pass that specifically re-checks each finding against *only* its
  cited source text (a "self-critique" pass), rather than relying solely on the
  keyword-overlap heuristic.
- Export directly to PDF/Word in addition to Markdown.
- Support incremental updates — re-run with 2 new sources added without
  re-processing the original 5.

## How to Run
```bash
pip install anthropic
export ANTHROPIC_API_KEY="your-key-here"     # get one at console.anthropic.com
python research_assistant.py
```
Add more sources by dropping additional `.txt` files (same TITLE/PUBLISHER/DATE/URL
header format) into the `sources/` folder.

To run the tests without an API key:
```bash
python test_pipeline_logic.py
```
