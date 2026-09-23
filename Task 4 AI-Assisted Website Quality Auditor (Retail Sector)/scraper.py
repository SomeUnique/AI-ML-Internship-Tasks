"""
scraper.py - Extracts factual data from retail-sector websites.

This module fetches a list of URLs and extracts key facts about each website
that will later be used by the AI auditor to generate quality scores.
"""

import requests
from bs4 import BeautifulSoup
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
}

TIMEOUT = 10


def can_scrape(url: str) -> bool:
    """
    Check if we are allowed to scrape the given URL based on robots.txt.

    Args:
        url: The full URL to check.

    Returns:
        True if scraping is allowed, False otherwise.
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

    rp = RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except Exception:
        return True


def extract_facts(url: str) -> dict:
    """
    Fetch a single URL and extract key factual data from the HTML.

    Args:
        url: The full URL of the website to audit.

    Returns:
        A dictionary containing extracted facts, or an 'error' field if
        something went wrong.
    """
    if not can_scrape(url):
        return {"url": url, "error": "Blocked by robots.txt"}

    try:
        start_time = time.time()
        response = requests.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
        load_time = round(time.time() - start_time, 2)
    except requests.exceptions.Timeout:
        return {"url": url, "error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"url": url, "error": "Connection failed"}
    except requests.exceptions.RequestException as e:
        return {"url": url, "error": f"Request failed: {str(e)}"}

    if response.status_code == 403:
        return {"url": url, "error": "Access denied (HTTP 403)", "status_code": response.status_code}

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("title")
    page_title = title_tag.get_text(strip=True) if title_tag else ""

    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag["content"].strip() if meta_desc_tag and meta_desc_tag.get("content") else ""

    nav_tags = soup.find_all("nav")
    nav_links = []
    for nav in nav_tags:
        for link in nav.find_all("a", href=True):
            nav_links.append(link.get_text(strip=True))
    if not nav_links:
        nav_container = soup.find("ul", class_=lambda c: c and ("nav" in c.lower() or "menu" in c.lower()))
        if nav_container:
            nav_links = [a.get_text(strip=True) for a in nav_container.find_all("a", href=True)]

    forms = soup.find_all("form")
    has_contact_form = False
    for form in forms:
        form_text = form.get_text().lower()
        form_id = (form.get("id") or "").lower()
        form_action = (form.get("action") or "").lower()
        if any(kw in form_text + form_id + form_action for kw in ["contact", "inquiry", "message", "support"]):
            has_contact_form = True
            break
    if not has_contact_form and len(forms) > 0:
        has_contact_form = True

    cta_keywords = ["buy", "shop", "add to cart", "sign up", "register",
                    "contact", "book", "order", "subscribe", "get started", "try"]
    cta_buttons = []
    all_clickable = soup.find_all(["button", "a"])
    for elem in all_clickable:
        text = elem.get_text(strip=True).lower()
        if any(kw in text for kw in cta_keywords):
            cta_buttons.append(elem.get_text(strip=True))

    social_platforms = {
        "facebook": "facebook.com",
        "instagram": "instagram.com",
        "twitter": "twitter.com",
        "x": "x.com",
        "linkedin": "linkedin.com",
        "tiktok": "tiktok.com",
        "youtube": "youtube.com",
        "pinterest": "pinterest.com"
    }
    found_socials = set()
    all_links = soup.find_all("a", href=True)
    for link in all_links:
        href = link["href"].lower()
        for platform, domain in social_platforms.items():
            if domain in href:
                found_socials.add(platform)

    all_images = soup.find_all("img")
    total_images = len(all_images)
    images_with_alt = 0
    for img in all_images:
        alt = img.get("alt", "").strip()
        if alt and alt.lower() not in ["image", "photo", "picture", "img"]:
            images_with_alt += 1
    alt_coverage = round((images_with_alt / total_images * 100), 1) if total_images > 0 else 0.0

    viewport_tag = soup.find("meta", attrs={"name": "viewport"})
    has_viewport = viewport_tag is not None
    viewport_content = viewport_tag.get("content", "") if viewport_tag else ""

    facts = {
        "url": url,
        "status_code": response.status_code,
        "page_title": page_title,
        "meta_description": meta_description,
        "nav_links_count": len(nav_links),
        "nav_links_sample": nav_links[:10],
        "has_contact_form": has_contact_form,
        "cta_buttons": cta_buttons,
        "social_media_platforms": sorted(found_socials),
        "total_images": total_images,
        "images_with_alt_text": images_with_alt,
        "alt_text_coverage_pct": alt_coverage,
        "page_load_time_sec": load_time,
        "has_viewport_tag": has_viewport,
        "viewport_content": viewport_content
    }

    return facts


def scrape_sites(urls: list) -> list:
    """
    Scrape a list of URLs and return a list of fact dictionaries.

    Args:
        urls: A list of URL strings to scrape.

    Returns:
        A list of dictionaries, each containing extracted facts or an error.
    """
    results = []
    for url in urls:
        print(f"  Scraping: {url}")
        facts = extract_facts(url)
        results.append(facts)
    return results


if __name__ == "__main__":
    test_urls = ["https://example.com"]
    results = scrape_sites(test_urls)
    for r in results:
        print(r)