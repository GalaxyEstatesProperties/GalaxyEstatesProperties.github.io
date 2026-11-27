#!/usr/bin/env python3
"""Keep the site's identity and search snippets in range.

Run from the repo root before publishing:  python3 tools/check_identity.py
Exit code 1 if any key page has drifted. Titles must be 65 characters or less
and carry the brand; descriptions 120-160 characters; each page keeps the
words that say what it is. robots.txt must keep welcoming search and AI crawlers.
"""
import html
import re
import sys

BRAND = "Galaxy Estates"
PHONE = "+91 84880 62309"
PAGES = {
    "index.html": ["Ahmedabad", "GIFT City", "Dubai"],
    "projects.html": ["Projects", "Ahmedabad"],
    "land.html": ["Land", "Gujarat"],
    "industrial-land-ahmedabad-gandhinagar.html": ["Industrial", "Gandhinagar"],
    "gift-city.html": ["GIFT City"],
    "dubai-uae-property.html": ["Dubai"],
    "global.html": ["Global"],
    "about.html": ["Samir Dabhi"],
    "contact.html": ["Contact"],
    "shantigram.html": ["Shantigram"],
}
PHONE_PAGES = {"index.html", "contact.html", "industrial-land-ahmedabad-gandhinagar.html"}

problems = []
for page, words in PAGES.items():
    s = open(page, encoding="utf-8").read()
    t = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1)).strip()
    d = html.unescape(re.search(r'<meta name="description" content="([^"]*)"', s).group(1))
    if len(t) > 65:
        problems.append(f"{page}: title is {len(t)} characters (max 65)")
    if BRAND not in t:
        problems.append(f"{page}: title lost the brand name '{BRAND}'")
    for w in words:
        if w.lower() not in (t + " " + d).lower():
            problems.append(f"{page}: title and description no longer mention '{w}'")
    if not 120 <= len(d) <= 160:
        problems.append(f"{page}: description is {len(d)} characters (want 120-160)")
    if page in PHONE_PAGES and PHONE not in d:
        problems.append(f"{page}: description lost the phone number")

robots = open("robots.txt", encoding="utf-8").read()
for token in ("GPTBot", "ClaudeBot", "PerplexityBot", "Googlebot", "Bingbot"):
    if token not in robots:
        problems.append(f"robots.txt no longer names {token}")
if re.search(r"(?im)^\s*Disallow:\s*/\s*$", robots):
    problems.append("robots.txt blocks the whole site")

if problems:
    print("Identity check FAILED:")
    for p in problems:
        print(" -", p)
    sys.exit(1)
print("Identity check passed: brand, key phrases, snippet lengths and crawler access are in place.")
