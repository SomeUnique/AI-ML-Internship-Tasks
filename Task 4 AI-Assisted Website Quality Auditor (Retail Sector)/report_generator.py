"""
report_generator.py - Combines scraped facts and AI audit results into
a single Markdown report with a summary table and per-site details.
"""

import pandas as pd
from datetime import datetime


def generate_report(scraped_data: list, audit_data: list, output_path: str = "audit_report.md"):
    """
    Generate a Markdown report combining facts and AI judgments.

    Args:
        scraped_data: List of fact dictionaries from scraper.py.
        audit_data:   List of audit dictionaries from ai_auditor.py.
        output_path:  File path for the output Markdown report.
    """
    report_lines = []

    report_lines.append("# AI-Assisted Website Quality Audit Report")
    report_lines.append("**Retail Sector**\n")
    report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append(f"**Sites Audited:** {len(scraped_data)}\n")
    report_lines.append("---\n")

    table_rows = []
    for facts, audit in zip(scraped_data, audit_data):
        url = facts.get("url", "N/A")
        score = audit.get("score", "N/A")
        priority = audit.get("priority", "N/A")
        problems = "; ".join(audit.get("problems", [])) or "None"
        missing = "; ".join(audit.get("missing_features", [])) or "None"
        recommendations = "; ".join(audit.get("recommendations", [])) or "None"

        if len(problems) > 120:
            problems = problems[:117] + "..."
        if len(missing) > 120:
            missing = missing[:117] + "..."
        if len(recommendations) > 120:
            recommendations = recommendations[:117] + "..."

        table_rows.append({
            "Website": url,
            "Score": score,
            "Priority": priority,
            "Problems": problems,
            "Missing Features": missing,
            "Recommendations": recommendations
        })

    if table_rows:
        df = pd.DataFrame(table_rows)
        report_lines.append("## Summary Table\n")
        report_lines.append(df.to_markdown(index=False))
        report_lines.append("\n---\n")

    report_lines.append("## Detailed Audit Results\n")

    for i, (facts, audit) in enumerate(zip(scraped_data, audit_data), 1):
        url = facts.get("url", "N/A")
        score = audit.get("score", "N/A")
        priority = audit.get("priority", "N/A")

        report_lines.append(f"## Site {i}: {url}")
        report_lines.append(f"**Score:** {score}/100  |  **Priority:** {priority}\n")

        report_lines.append("### Automatically Detected Facts (Script)\n")

        if "error" in facts:
            report_lines.append(f"> **Scrape Error:** {facts['error']}\n")
        else:
            report_lines.append("| Fact | Value |")
            report_lines.append("|------|-------|")
            report_lines.append(f"| Status Code | {facts.get('status_code', 'N/A')} |")
            report_lines.append(f"| Page Title | {facts.get('page_title', '(empty)')} |")
            report_lines.append(f"| Meta Description | {facts.get('meta_description', '(empty)')} |")
            report_lines.append(f"| Navigation Links | {facts.get('nav_links_count', 0)} |")
            report_lines.append(f"| Contact Form | {'Yes' if facts.get('has_contact_form') else 'No'} |")
            report_lines.append(f"| CTA Buttons | {', '.join(facts.get('cta_buttons', [])) or 'None found'} |")
            report_lines.append(f"| Social Platforms | {', '.join(facts.get('social_media_platforms', [])) or 'None found'} |")
            report_lines.append(f"| Total Images | {facts.get('total_images', 0)} |")
            report_lines.append(f"| Images with Alt Text | {facts.get('images_with_alt_text', 0)} |")
            report_lines.append(f"| Alt Text Coverage | {facts.get('alt_text_coverage_pct', 0)}% |")
            report_lines.append(f"| Page Load Time | {facts.get('page_load_time_sec', 'N/A')}s |")
            report_lines.append(f"| Viewport Meta Tag | {'Yes' if facts.get('has_viewport_tag') else 'No'} |")
            report_lines.append("")

            if facts.get("nav_links_sample"):
                report_lines.append("**Navigation Links:**\n")
                for link in facts["nav_links_sample"][:10]:
                    report_lines.append(f"- {link}")
                report_lines.append("")

        report_lines.append("### AI-Generated Judgment (Claude)\n")

        if audit.get("offline"):
            report_lines.append("> **Mode:** Rule-based scoring (no API key used)\n")
        else:
            report_lines.append("> **Mode:** Claude AI\n")

        if "error" in audit:
            report_lines.append(f"> **Audit Error:** {audit['error']}\n")

        if audit.get("problems"):
            report_lines.append("**Problems:**\n")
            for item in audit["problems"]:
                report_lines.append(f"- {item}")
            report_lines.append("")

        if audit.get("missing_features"):
            report_lines.append("**Missing Features:**\n")
            for item in audit["missing_features"]:
                report_lines.append(f"- {item}")
            report_lines.append("")

        if audit.get("recommendations"):
            report_lines.append("**Recommendations:**\n")
            for item in audit["recommendations"]:
                report_lines.append(f"- {item}")
            report_lines.append("")

        report_lines.append("---\n")

    report_lines.append("*Report generated by AI-Assisted Website Quality Auditor - Retail Sector*\n")

    report_content = "\n".join(report_lines)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"  Report saved to: {output_path}")
    return report_content


if __name__ == "__main__":
    sample_scraped = [
        {
            "url": "https://example-store.com",
            "status_code": 200,
            "page_title": "Example Store",
            "meta_description": "Great products",
            "nav_links_count": 6,
            "has_contact_form": True,
            "cta_buttons": ["Shop Now"],
            "social_media_platforms": ["facebook", "instagram"],
            "total_images": 10,
            "images_with_alt_text": 9,
            "alt_text_coverage_pct": 90.0,
            "page_load_time_sec": 1.5,
            "has_viewport_tag": True,
            "viewport_content": "width=device-width"
        }
    ]
    sample_audit = [
        {
            "score": 82,
            "missing_features": ["Live chat widget"],
            "problems": ["No TikTok presence"],
            "recommendations": ["Add TikTok link to footer"],
            "priority": "Low"
        }
    ]
    generate_report(sample_scraped, sample_audit, "test_report.md")