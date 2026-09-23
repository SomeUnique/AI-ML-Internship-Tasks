import os
import sys
from scraper import scrape_sites
from ai_auditor import audit_site
from report_generator import generate_report

SITES_FILE = "sites.txt"
OUTPUT_DIR = "output"
REPORT_PATH = os.path.join(OUTPUT_DIR, "audit_report.md")

def load_urls(filename: str) -> list:
    """
    Read website URLs from a text file (one URL per line).
    Args:
        filename: Path to the sites file.
    Returns:
        List of non-empty, stripped URL strings.
    """
    urls = []
    if not os.path.exists(filename):
        print(f"[!] Sites file '{filename}' not found. Using a fallback list.")
        return []

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            url = line.strip()
            if url and not url.startswith("#"):
                urls.append(url)
    return urls

def main():
    print("=" * 60)
    print("AI-Assisted Website Quality Auditor - Retail Sector")
    print("=" * 60)

    force_offline = "--offline" in sys.argv

    if force_offline or not os.getenv("ANTHROPIC_API_KEY"):
        print("[i] Running in OFFLINE mode (no API key). Using rule-based scoring.")
    else:
        print("[i] Running in AI mode. Using Claude for judgments.")

    urls = load_urls(SITES_FILE)
    if not urls:
        print("[i] No URLs found in sites.txt. Using the following demo sites:")
        urls = [
            "https://example.com",
            "https://httpbin.org/status/403",
            "https://httpbin.org/delay/15",
            "https://www.apple.com",
            "https://www.zara.com",
        ]
        for u in urls:
            print(f"    - {u}")

    if os.path.exists(SITES_FILE):
        print(f"[i] Loaded {len(urls)} URLs from {SITES_FILE}")
    else:
        print(f"[i] Loaded {len(urls)} fallback URLs")

    print("\n[i] Scraping all sites...")
    scraped_data = scrape_sites(urls)

    print("\n[i] Scoring all sites...")
    audit_data = []
    total = len(urls)
    for index, facts in enumerate(scraped_data, 1):
        short_url = facts.get("url", "unknown").replace("https://", "").replace("http://", "")
        print(f"  Auditing site {index}/{total}: {short_url}...")

        result = audit_site(facts, offline=force_offline)
        result["url"] = facts.get("url", "unknown")
        audit_data.append(result)

        if "error" in result:
            print(f"    [!] Site {index} failed: {result['error']}")
        else:
            mode = "offline" if result.get("offline") else "AI"
            print(f"    [OK] Score: {result.get('score', 'N/A')}/100 "
                  f"| Priority: {result.get('priority', 'N/A')} | Mode: {mode}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print("\n[i] Generating report...")

    combined_scraped = []
    combined_audit = []
    for facts in scraped_data:
        url = facts.get("url")
        matching_audit = next((a for a in audit_data if a.get("url") == url), {})
        combined_scraped.append(facts)
        combined_audit.append(matching_audit)

    generate_report(combined_scraped, combined_audit, REPORT_PATH)

    print("\n" + "=" * 60)
    print("AUDIT COMPLETE")
    print("=" * 60)
    success = sum(1 for a in audit_data if "error" not in a)
    failed = total - success
    print(f"  Sites succeeded: {success}/{total}")
    print(f"  Sites failed:    {failed}/{total}")
    print(f"  Report location: {REPORT_PATH}")


if __name__ == "__main__":
    main()