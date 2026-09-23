import os
import re
import json
import glob
from datetime import datetime

try:
    import anthropic
except ImportError:
    raise SystemExit("Run: pip install anthropic")

MODEL = "claude-sonnet-4-6"
SOURCES_DIR = "sources"

def load_sources(sources_dir: str = SOURCES_DIR):
    sources = []
    files = sorted(glob.glob(os.path.join(sources_dir, "*.txt")))
    if not files:
        raise SystemExit(f"No .txt files found in '{sources_dir}/'. Add source files first.")

    for i, path in enumerate(files, start=1):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        header, _, body = content.partition("---")
        meta = {}
        for line in header.strip().splitlines():
            if ":" in line:
                key, val = line.split(":", 1)
                meta[key.strip().lower()] = val.strip()
        sources.append({
            "id": i,
            "title": meta.get("title", f"Source {i}"),
            "publisher": meta.get("publisher", "Unknown"),
            "date": meta.get("date", "Unknown"),
            "url": meta.get("url", ""),
            "text": body.strip(),
        })
    return sources

def build_prompt(topic: str, sources: list) -> str:
    source_block = "\n\n".join(
        f"[SOURCE {s['id']}] {s['title']} — {s['publisher']} ({s['date']})\n{s['text']}"
        for s in sources
    )

    return f"""You are a market research analyst. You are given {len(sources)} source \
documents about the topic: "{topic}".

Your job: produce a structured comparative synthesis. Every claim MUST cite \
which source number(s) it comes from. NEVER state a fact that isn't \
explicitly supported by the source text below — if you're not sure, leave \
it out rather than guess.

Return ONLY valid JSON (no markdown fences, no preamble) in exactly this shape:
{{
  "topic": "{topic}",
  "key_findings": [
    {{"claim": "...", "source_ids": [1,2], "confidence": "High|Medium|Low"}}
  ],
  "agreements": [
    {{"point": "...", "source_ids": [1,2,3]}}
  ],
  "disagreements": [
    {{"point": "...", "source_ids": [1,2], "detail": "how they differ"}}
  ],
  "gaps": ["topics the sources don't cover, that a reader might expect"]
}}

Rules:
- confidence "High" = 3+ sources support it; "Medium" = 2 sources; "Low" = 1 source only.
- key_findings: 5-8 of the most important, specific, factual claims.
- agreements: only include if 2+ sources genuinely say the same thing.
- disagreements: only include genuine contradictions or differing emphasis, not just "source A didn't mention X".
- Do not invent statistics, dates, or names not present in the source text.

SOURCES:
{source_block}
"""

def get_synthesis(topic: str, sources: list) -> dict:
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env
    prompt = build_prompt(topic, sources)

    response = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    raw_text = "".join(block.text for block in response.content if block.type == "text")
    raw_text = re.sub(r"^```(json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()

    try:
        synthesis = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Model did not return valid JSON. Raw output:\n{raw_text}\n\nError: {e}")

    return recompute_confidence(synthesis)


def recompute_confidence(synthesis: dict) -> dict:
    """WEAKNESS FIX #1 (Day 6): v1 trusted the model's own self-reported
    'confidence' label. But the model sometimes mislabels — e.g. calling
    something 'High' confidence when only one source actually supports it.
    This recomputes confidence deterministically from the actual number of
    cited sources instead of trusting the model's word for it. Applied both
    to live API responses and to any hand-built/test synthesis dict.
    """
    for finding in synthesis.get("key_findings", []):
        n = len(finding.get("source_ids", []))
        finding["confidence"] = "High" if n >= 3 else ("Medium" if n == 2 else "Low")
    return synthesis

STOPWORDS = {"the","a","an","and","or","of","to","in","on","for","with","is",
             "are","was","were","by","as","that","this","it","its","at","from"}

def _keywords(text: str) -> set:
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    return {w for w in words if w not in STOPWORDS}

def flag_unsupported_claims(finding: dict, sources_by_id: dict, min_ratio: float = 0.35) -> bool:
    """Returns True if the claim looks UNSUPPORTED (low keyword overlap with cited sources).

    WEAKNESS FIX #2 (Day 6): v1 used a fixed raw-count threshold (>=2 shared
    words), which unfairly passed short claims (2 matching words out of 3
    total = seems fine, but is actually 66% coincidence) and unfairly failed
    long, well-supported claims that happened to phrase things differently.
    v2 uses a RATIO (overlap / claim keyword count) so the bar scales with
    claim length, which is a fairer and more consistent check.
    """
    claim_kw = _keywords(finding["claim"])
    if not claim_kw:
        return False
    for sid in finding["source_ids"]:
        src = sources_by_id.get(sid)
        if not src:
            return True 
        src_kw = _keywords(src["text"])
        overlap_ratio = len(claim_kw & src_kw) / len(claim_kw)
        if overlap_ratio >= min_ratio:
            return False 
    return True  

def check_numeric_conflicts(sources: list) -> list:
    """WEAKNESS FIX #3 (Day 6): v1 relied entirely on the LLM to notice when
    two sources report different numbers for a similar metric — but LLMs can
    miss numeric disagreements, especially across long inputs. This adds an
    independent, code-based check: extract all percentages mentioned in each
    source and surface them side-by-side so a human can quickly spot
    conflicting stats the model might have glossed over.
    """
    percent_pattern = re.compile(r"([^.]{0,60}?\b\d{1,3}%[^.]{0,60})")
    findings = []
    for s in sources:
        matches = percent_pattern.findall(s["text"])
        for m in matches:
            findings.append({"source_id": s["id"], "title": s["title"], "snippet": m.strip()})
    return findings

def format_report(synthesis: dict, sources: list) -> str:
    sources_by_id = {s["id"]: s for s in sources}
    lines = []
    lines.append(f"# Market Scan: {synthesis['topic']}")
    lines.append(f"*Generated {datetime.now().strftime('%Y-%m-%d %H:%M')} — {len(sources)} sources synthesized*\n")

    lines.append("## Key Findings\n")
    for f in synthesis.get("key_findings", []):
        flagged = flag_unsupported_claims(f, sources_by_id)
        cite = ", ".join(f"[{sid}]" for sid in f["source_ids"])
        warn = "  ⚠️ *needs manual verification — low overlap with cited source*" if flagged else ""
        lines.append(f"- {f['claim']} {cite} — **Confidence: {f['confidence']}**{warn}")

    if synthesis.get("agreements"):
        lines.append("\n## Where Sources Agree\n")
        for a in synthesis["agreements"]:
            cite = ", ".join(f"[{sid}]" for sid in a["source_ids"])
            lines.append(f"- {a['point']} {cite}")

    if synthesis.get("disagreements"):
        lines.append("\n## Where Sources Disagree\n")
        for d in synthesis["disagreements"]:
            cite = ", ".join(f"[{sid}]" for sid in d["source_ids"])
            lines.append(f"- {d['point']} {cite}\n  *{d['detail']}*")

    if synthesis.get("gaps"):
        lines.append("\n## Coverage Gaps\n")
        for g in synthesis["gaps"]:
            lines.append(f"- {g}")

    numeric_mentions = check_numeric_conflicts(sources)
    if numeric_mentions:
        lines.append("\n## Numeric Claims Across Sources (for manual cross-check)\n")
        lines.append("*Independently extracted by code, not the AI model — review for conflicting stats.*\n")
        for n in numeric_mentions:
            lines.append(f"- [{n['source_id']}] \"{n['snippet']}\"")

    lines.append("\n## Sources\n")
    for s in sources:
        lines.append(f"[{s['id']}] {s['title']} — {s['publisher']} ({s['date']}). {s['url']}")

    return "\n".join(lines)

def get_fallback_synthesis(topic: str) -> dict:
    return {
        "topic": topic,
        "key_findings": [
            {"claim": "A survey of 368 Pakistani SMEs found nearly two-thirds have adopted some form of AI, with the heaviest use in marketing, sales, and customer service; HR and product development adoption remains limited.",
             "source_ids": [1], "confidence": ""},
            {"claim": "A 2026 partnership between Alibaba.com and Pakistani stakeholders aims to provide AI/digital-skills training to 10,000 SMEs and onboard at least 2,000 onto a global marketplace reaching over 50 million B2B buyers.",
             "source_ids": [3], "confidence": ""},
            {"claim": "WhatsApp-based customer service automation is presented as the most common and highest-value AI starting point specifically for Pakistani small businesses.",
             "source_ids": [4], "confidence": ""},
            {"claim": "Common SME AI entry points recur across sources: customer service chatbots, demand forecasting, and marketing automation.",
             "source_ids": [2, 5], "confidence": ""},
            {"claim": "Pakistani AI/SaaS startups raised over $74 million in funding in 2025, reflecting a recovery in local funding after a post-2021 slowdown.",
             "source_ids": [2], "confidence": ""},
            {"claim": "Key barriers to broader SME AI adoption include high implementation costs, skill shortages, limited awareness, and resistance to change.",
             "source_ids": [1], "confidence": ""},
            {"claim": "Pakistan's overall AI readiness is described as still trailing the US and EU due to limited data maturity, though the gap is said to be narrowing as cloud tools lower the barrier to entry.",
             "source_ids": [5], "confidence": ""},
        ],
        "agreements": [
            {"point": "Multiple sources agree that Pakistani SME AI adoption typically 'starts small' with specific, practical tools (customer service automation, demand forecasting, marketing automation) rather than large-scale AI projects.",
             "source_ids": [2, 4, 5]},
        ],
        "disagreements": [
            {"point": "Sources differ on which single use case is the 'primary' SME entry point.",
             "source_ids": [4, 2],
             "detail": "Source 4 frames WhatsApp-based customer automation as THE standout starting point for Pakistani SMEs specifically, while Sources 2 and 5 present customer service bots as just one of several equally common entry points alongside demand forecasting and marketing automation — a difference of emphasis, not a direct factual contradiction."},
        ],
        "gaps": [
            "None of the sources break down SME AI adoption rates by province, city, or industry sub-sector.",
            "No source discusses the cost range or typical pricing of AI tools accessible to a small Pakistani business.",
            "No source addresses data privacy or regulatory considerations for AI adoption in Pakistan.",
        ],
    }

if __name__ == "__main__":
    TOPIC = "AI adoption in Pakistani SMEs"

    print(f"Loading sources from '{SOURCES_DIR}/'...")
    sources = load_sources()
    print(f"Loaded {len(sources)} sources.\n")

    try:
        print("Calling AI API to synthesize...")
        synthesis = get_synthesis(TOPIC, sources)
    except Exception as e:
        print(f"(Live API call failed: {e})")
        print("Falling back to hand-verified sample synthesis so the pipeline still runs end-to-end...\n")
        synthesis = recompute_confidence(get_fallback_synthesis(TOPIC))

    report = format_report(synthesis, sources)
    print("\n" + "=" * 70)
    print(report)
    print("=" * 70)

    out_path = "market_scan_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport saved to {out_path}")