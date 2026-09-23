import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()

AUDIT_PROMPT = """\
You are an expert retail website auditor. You evaluate how professional, \
complete, and business-ready a retail-sector website is based ONLY on the \
factual data provided below. Do NOT assume any information not present in \
the facts.

Here are the scraped facts about the website:

{facts_json}

Based on these facts ONLY, return a STRICT JSON object (no extra text, no \
markdown fences) with the following fields:

{{
  "score": <integer 0-100>,
  "missing_features": [<list of specific missing features for THIS site>],
  "problems": [<list of specific problems found for THIS site>],
  "recommendations": [<list of actionable recommendations for THIS site>],
  "priority": "<High | Medium | Low>"
}}

Scoring guidelines:
- 90-100: Excellent, fully professional retail site
- 70-89:  Good, minor improvements needed
- 50-69:  Average, several gaps to address
- Below 50: Significant issues, major work needed

Priority guidelines:
- High:   Score below 50 or critical features missing (no CTA, no contact)
- Medium: Score 50-69 or moderate issues
- Low:    Score 70+ with only minor improvements

IMPORTANT: Return ONLY the raw JSON object. No markdown, no explanation.
"""

MAX_SCORE = 100


def _add(problems, missing, recommendations, problem, feature, recommendation):
    if feature:
        missing.append(feature)
    if problem:
        problems.append(problem)
    if recommendation:
        recommendations.append(recommendation)


def rule_based_audit(facts: dict) -> dict:
    """
    Score a website from scraped facts only, without calling the API.

    Uses clear heuristics: presence of a title, meta description, navigation,
    contact form, CTAs, social links, alt-text coverage, load time, and the
    viewport tag. Each healthy signal adds points up to a max of 100.

    Args:
        facts: Dictionary of facts extracted by scraper.py.

    Returns:
        Dictionary with score, missing_features, problems, recommendations,
        and priority. The 'offline' field is True to mark this as a
        rule-based judgment rather than an AI one.
    """
    if "error" in facts:
        return {
            "score": 0,
            "missing_features": ["Site could not be scraped"],
            "problems": [facts["error"]],
            "recommendations": ["Fix the accessibility issue so the site can be audited."],
            "priority": "High",
            "error": facts["error"],
            "offline": True
        }

    score = 0
    problems = []
    missing = []
    recommendations = []

    if facts.get("page_title"):
        score += 10
    else:
        _add(problems, missing, recommendations,
             "Page title is missing or empty.",
             "Page title",
             "Add a descriptive <title> tag that includes the brand and a short value offer.")

    if facts.get("meta_description"):
        score += 10
    else:
        _add(problems, missing, recommendations,
             "Meta description is missing. Sites often show badly in search results.",
             "Meta description",
             "Add a meta description of 140-160 characters summarizing the store.")

    nav_count = facts.get("nav_links_count", 0)
    if nav_count >= 5:
        score += 10
    elif nav_count > 0:
        score += 5
        _add(problems, missing, recommendations,
             f"Navigation is thin with only {nav_count} link(s).",
             "More navigation links",
             "Expand the main navigation so every store area is reachable from the homepage.")
    else:
        _add(problems, missing, recommendations,
             "No navigation links found on the homepage.",
             "Navigation menu",
             "Add a clear navigation menu with links to key store sections.")

    if facts.get("has_contact_form"):
        score += 10
    else:
        _add(problems, missing, recommendations,
             "No contact form found. Customers cannot easily reach the store.",
             "Contact form",
             "Add a contact form or at least an email/phone contact section.")

    cta_buttons = facts.get("cta_buttons", [])
    if cta_buttons:
        score += 15
    else:
        _add(problems, missing, recommendations,
             "No CTA buttons found (buy/shop/sign up/book etc.).",
             "Call-to-action buttons",
             "Add prominent CTA buttons such as Shop Now, Buy Now, or Sign Up.")

    socials = facts.get("social_media_platforms", [])
    if socials:
        score += 5 + min(2 * len(socials), 5)
        if len(socials) < 2:
            _add(problems, missing, recommendations,
                 f"Only {len(socials)} social platform(s) linked.",
                 "More social media presence",
                 "Link at least two active social profiles (e.g. Instagram and Facebook).")
    else:
        _add(problems, missing, recommendations,
             "No social media links found.",
             "Social media links",
             "Add links to your social profiles (Facebook, Instagram, TikTok, etc.) in the footer.")

    total_images = facts.get("total_images", 0)
    alt_coverage = facts.get("alt_text_coverage_pct", 0)
    if total_images == 0:
        _add(problems, missing, recommendations,
             "No images found on the homepage. Retail pages should show products.",
             "Product imagery",
             "Add product images to build confidence and visual appeal.")
    elif alt_coverage >= 90:
        score += 15
    elif alt_coverage >= 50:
        score += 10
        _add(problems, missing, recommendations,
             f"Alt text coverage is only {alt_coverage}%.",
             "Alt text on more images",
             "Add descriptive alt text to the remaining images for SEO and accessibility.")
    else:
        score += 5
        _add(problems, missing, recommendations,
             f"Alt text coverage is only {alt_coverage}%. Most images lack alt text.",
             "Alt text on images",
             "Add meaningful alt text to all product images for SEO and accessibility.")

    load_time = facts.get("page_load_time_sec", 99)
    if load_time <= 2:
        score += 10
    elif load_time <= 4:
        score += 6
    else:
        score += 2
        _add(problems, missing, recommendations,
             f"Page load time is {load_time}s which is slow for a retail site.",
             "Faster page load",
             "Optimize images, enable caching, and use a CDN to speed up the page.")

    if facts.get("has_viewport_tag"):
        score += 10
    else:
        _add(problems, missing, recommendations,
             "No viewport meta tag. Site is unlikely to render well on mobile.",
             "Mobile viewport tag",
             "Add <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"> for mobile support.")

    score = max(0, min(MAX_SCORE, score))

    if score < 50:
        priority = "High"
    elif score < 70:
        priority = "Medium"
    else:
        priority = "Low"

    return {
        "score": score,
        "missing_features": missing,
        "problems": problems,
        "recommendations": recommendations,
        "priority": priority,
        "offline": True
    }


def audit_site(facts: dict, offline: bool = False) -> dict:
    """
    Judge a website from its scraped facts.

    When offline is True, or when no ANTHROPIC_API_KEY is set, a rule-based
    scoring engine is used so no API is required. Otherwise the facts are
    sent to Claude for an AI judgment.

    Args:
        facts: Dictionary of facts extracted by scraper.py.
        offline: Force rule-based scoring even if an API key exists.

    Returns:
        Dictionary with score, missing_features, problems, recommendations,
        and priority — or an 'error' field on failure.
    """
    if "error" in facts:
        return {
            "score": 0,
            "missing_features": ["Site could not be scraped"],
            "problems": [facts["error"]],
            "recommendations": ["Fix the accessibility issue so the site can be audited."],
            "priority": "High",
            "error": facts["error"],
            "offline": True
        }

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if offline or not api_key:
        return rule_based_audit(facts)

    facts_json = json.dumps(facts, indent=2)
    prompt = AUDIT_PROMPT.format(facts_json=facts_json)

    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        raw_response = message.content[0].text.strip()
    except anthropic.APIError as e:
        return {
            "score": 0,
            "missing_features": [],
            "problems": [f"Claude API error: {str(e)}"],
            "recommendations": ["Check your API key and account billing status."],
            "priority": "High",
            "error": f"API error: {str(e)}"
        }
    except Exception as e:
        return {
            "score": 0,
            "missing_features": [],
            "problems": [f"Unexpected error: {str(e)}"],
            "recommendations": ["Retry the audit or check network connectivity."],
            "priority": "High",
            "error": str(e)
        }

    cleaned = raw_response

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines)

    try:
        audit_result = json.loads(cleaned)
    except json.JSONDecodeError:
        try:
            start = cleaned.index("{")
            end = cleaned.rindex("}") + 1
            audit_result = json.loads(cleaned[start:end])
        except (ValueError, json.JSONDecodeError):
            return {
                "score": 0,
                "missing_features": [],
                "problems": ["Claude returned a response that could not be parsed as JSON."],
                "recommendations": ["Retry the audit."],
                "priority": "High",
                "error": "JSON parse failure",
                "raw_response": raw_response[:500]
            }

    required_fields = ["score", "missing_features", "problems", "recommendations", "priority"]
    for field in required_fields:
        if field not in audit_result:
            audit_result[field] = []

    try:
        audit_result["score"] = max(0, min(100, int(audit_result["score"])))
    except (ValueError, TypeError):
        audit_result["score"] = 0

    valid_priorities = ["High", "Medium", "Low"]
    if audit_result.get("priority") not in valid_priorities:
        score = audit_result["score"]
        if score < 50:
            audit_result["priority"] = "High"
        elif score < 70:
            audit_result["priority"] = "Medium"
        else:
            audit_result["priority"] = "Low"

    return audit_result


if __name__ == "__main__":
    sample_facts = {
        "url": "https://example-store.com",
        "status_code": 200,
        "page_title": "Example Store - Shop Now",
        "meta_description": "Best products at great prices",
        "nav_links_count": 8,
        "has_contact_form": True,
        "cta_buttons": ["Shop Now", "Sign Up"],
        "social_media_platforms": ["facebook", "instagram"],
        "total_images": 20,
        "images_with_alt_text": 18,
        "alt_text_coverage_pct": 90.0,
        "page_load_time_sec": 1.2,
        "has_viewport_tag": True,
        "viewport_content": "width=device-width, initial-scale=1"
    }
    print(json.dumps(audit_site(sample_facts, offline=True), indent=2))