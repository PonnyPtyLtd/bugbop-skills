#!/usr/bin/env python3
"""Tiny client for the Bugbop REST API. Standard library only.

    bugbop.py GET /reports?status=new --all
    bugbop.py PATCH /reports/<id> --data '{"status": "fixed"}'
    bugbop.py POST /reports/<id>/comments --data @comment.json
    bugbop.py GET /reports?status=new --all --summary     # one line per report

Reads BUGBOP_TOKEN (required) and BUGBOP_URL (default https://bugbop.com).
"""

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

# Per-minute caps reset within a minute, so waiting those out is fine. Anything
# longer means the hourly allowance is gone, and sleeping on it would just hang.
MAX_WAIT_SECONDS = 65
MAX_RETRIES = 3


def api_url(path):
    if path.startswith("http"):
        return path
    base = os.environ.get("BUGBOP_URL", "https://bugbop.com").rstrip("/")
    if not path.startswith("/"):
        path = "/" + path
    if not path.startswith("/api/"):
        path = "/api/v1" + path
    return base + path


def request(method, url, body, token):
    for attempt in range(MAX_RETRIES + 1):
        req = urllib.request.Request(url, data=body, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        req.add_header("User-Agent", "bugbop-skill")
        if body is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, resp.headers, resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < MAX_RETRIES:
                wait = int(e.headers.get("Retry-After", "60"))
                if wait <= MAX_WAIT_SECONDS:
                    print(f"Rate limited, waiting {wait}s", file=sys.stderr)
                    time.sleep(wait)
                    continue
            return e.code, e.headers, e.read()
        except urllib.error.URLError as e:
            sys.exit(f"Couldn't reach {url}: {e.reason}")


def next_link(headers):
    for part in (headers.get("Link") or "").split(","):
        match = re.search(r'<([^>]+)>;\s*rel="next"', part)
        if match:
            return match.group(1)
    return None


def main():
    parser = argparse.ArgumentParser(description="Call the Bugbop REST API")
    parser.add_argument("method", type=str.upper, choices=["GET", "POST", "PATCH", "DELETE"])
    parser.add_argument("path", help="e.g. /reports?status=new or a full URL")
    parser.add_argument("--data", help="JSON body, or @file to read it from a file")
    parser.add_argument("--all", action="store_true", help="follow pagination and return every page")
    parser.add_argument("--summary", action="store_true", help="one line per report or comment instead of JSON")
    args = parser.parse_args()

    token = os.environ.get("BUGBOP_TOKEN")
    if not token:
        sys.exit("Set BUGBOP_TOKEN to a bugbop_pat_ token from the API Tokens tab of your Bugbop profile.")

    body = None
    if args.data:
        raw = open(args.data[1:]).read() if args.data.startswith("@") else args.data
        body = json.dumps(json.loads(raw)).encode()

    url = api_url(args.path)
    if args.all and args.method == "GET" and "per_page=" not in url:
        url += ("&" if "?" in url else "?") + "per_page=100"

    results = []
    while url:
        status, headers, raw = request(args.method, url, body, token)
        if status >= 400:
            sys.stderr.write(raw.decode() + "\n")
            sys.exit(f"HTTP {status}")
        if not raw:
            print(f"HTTP {status}")
            return
        data = json.loads(raw)
        if not (args.all and isinstance(data, list)):
            output(data, args.summary)
            return
        results.extend(data)
        url = next_link(headers)

    output(results, args.summary)


def output(data, summary):
    if summary and isinstance(data, list):
        for item in data:
            print(summarise(item))
    else:
        print(json.dumps(data, indent=2))


def summarise(item):
    user = (item.get("user") or {}).get("username", "?")
    if "report_id" in item and "content" in item:
        first_line = item["content"].strip().splitlines()[0] if item["content"].strip() else ""
        return f"{item['created_at'][:10]} {user}: {first_line[:120]}"
    if "status" in item and "title" in item:
        age = days_since(item.get("created_at"))
        return (f"{item['status']:<14} {str(item.get('severity')):<8} {age:>4}d {user:<16} "
                f"{item.get('comments_count', 0):>3}c  {item['id'][:8]}  {item['title'][:80]}")
    return json.dumps(item)


def days_since(iso):
    if not iso:
        return "?"
    from datetime import datetime, timezone
    then = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return (datetime.now(timezone.utc) - then).days


if __name__ == "__main__":
    main()
