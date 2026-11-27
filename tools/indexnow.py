#!/usr/bin/env python3
"""Tell Bing (and other IndexNow search engines) which pages just changed.

Usage:  python3 tools/indexnow.py --base HEAD~1 --head HEAD [--dry-run]
        python3 tools/indexnow.py --all [--dry-run]     (every indexable page)

Looks at the .html files that changed between two commits, skips pages that
are not meant for search (noindex or no title), and sends their public URLs to
the IndexNow endpoint. The key file in the site root (<key>.txt) proves the
site is ours. The key is public by design; it is not a secret.
It never fails the build: a problem is printed and the script exits normally.
"""
import argparse
import glob
import json
import re
import subprocess
import sys
import urllib.request

HOST = "galaxyestatesproperties.co.in"
BASE = "https://" + HOST + "/"
ENDPOINT = "https://api.indexnow.org/indexnow"


def key():
    for f in glob.glob("[0-9a-f]" * 32 + ".txt"):
        k = open(f, encoding="utf-8").read().strip()
        if f == k + ".txt":
            return k
    return None


def changed_pages(base, head, everything=False):
    if everything:
        out = sorted(glob.glob("*.html"))
    else:
        out = subprocess.run(["git", "diff", "--name-only", "--diff-filter=AM", base, head],
                             capture_output=True, text=True, check=True).stdout.split()
    urls = []
    for f in out:
        if "/" in f or not f.endswith(".html"):
            continue
        try:
            s = open(f, encoding="utf-8").read()
        except OSError:
            continue
        if "noindex" in s[:4000] or "<title>" not in s or 'http-equiv="refresh"' in s[:4000]:
            continue  # not for search: noindex, no title, or a redirect stub
        urls.append(BASE if f == "index.html" else BASE + f)
    return sorted(set(urls))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD~1")
    ap.add_argument("--head", default="HEAD")
    ap.add_argument("--all", action="store_true", help="send every indexable page")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    k = key()
    if not k:
        print("IndexNow: no key file in the site root; nothing sent.")
        return 0
    try:
        urls = changed_pages(a.base, a.head, a.all)
    except subprocess.CalledProcessError as e:
        print("IndexNow: could not compare commits:", e)
        return 0
    if not urls:
        print("IndexNow: no changed pages to send.")
        return 0
    body = {"host": HOST, "key": k, "keyLocation": BASE + k + ".txt", "urlList": urls[:10000]}
    if a.dry_run:
        print("IndexNow (dry run): would send", len(urls), "URLs")
        for u in urls[:10]:
            print("  ", u)
        return 0
    req = urllib.request.Request(ENDPOINT, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("IndexNow: sent", len(urls), "URLs, response", r.status)
    except Exception as e:  # keep the deploy green whatever happens
        print("IndexNow: not accepted:", e)
    return 0


if __name__ == "__main__":
    sys.exit(main())
