#!/usr/bin/env python3
"""unroll: fetch an X/Twitter thread as Markdown, to a file or stdout.

Usage: python3 unroll.py <url of any tweet in the thread> [-o out.md | -o - for stdout]

Standard library only, Python 3.8+.
"""

import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

API = "https://api.fxtwitter.com/2/thread/"


def parse_id(value):
    m = re.search(r"(?:status(?:es)?/)?(\d{5,})", value)
    if not m:
        raise ValueError(f"Could not extract a tweet ID from: {value}")
    return m.group(1)


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "unroll"})
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.load(res)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except ValueError:
            return e.code, None


def strip_reply_mentions(t):
    """Replies start with auto-added "@user @user". display_text_range[0] marks
    where the tweet's own text begins (in code points), so cut everything before it."""
    start = ((t.get("raw_text") or {}).get("display_text_range") or [0])[0]
    return t["text"][start:].lstrip() if start > 0 else t["text"]


def collect_thread(tweet_id):
    """fxtwitter /2/thread/<id> returns the reply chain around the tweet: the author's
    whole self-reply thread, plus other people's tweets if the author was replying to them."""
    status, data = fetch_json(API + tweet_id)
    if status != 200 or not data or not data.get("status"):
        reason = (data or {}).get("message") or status
        raise RuntimeError(f"Failed to fetch thread {tweet_id}: {reason}")
    thread = data.get("thread") or [data["status"]]
    thread = [dict(t, text=strip_reply_mentions(t)) for t in thread]
    return sorted(thread, key=lambda t: t["created_timestamp"])


def media_md(media):
    items = (media or {}).get("all") or []
    out = []
    for m in items:
        if m.get("type") == "photo":
            out.append(f"![]({m['url']})")
        else:
            # Videos and GIFs: thumbnail image linking to the mp4.
            thumb = f"![]({m['thumbnail_url']})" if m.get("thumbnail_url") else "▶ video"
            out.append(f"[{thumb}]({m['url']})")
    return "\n\n".join(out)


def quote_md(q):
    if not q:
        return ""
    parts = [f"**@{q['author']['screen_name']}**: {strip_reply_mentions(q)}", media_md(q.get("media"))]
    body = "\n\n".join(p for p in parts if p)
    lines = [f"> {line}" for line in body.split("\n")]
    lines.append(f"> [source]({q['url']})")
    return "\n".join(lines)


def tweet_md(t, label_author):
    label = f"**@{t['author']['screen_name']}**" if label_author else ""
    parts = [label, t["text"], media_md(t.get("media")), quote_md(t.get("quote"))]
    return "\n\n".join(p for p in parts if p)


def to_markdown(tweets):
    first = tweets[0]
    a = first["author"]
    date = datetime.fromtimestamp(first["created_timestamp"], tz=timezone.utc).strftime("%Y-%m-%d")
    first_line, _, rest = first["text"].partition("\n")
    fits = len(first_line.strip()) <= 80
    title = (first_line if fits else first_line[:80]).strip().replace('"', "'")
    # If the whole first line became the title, don't repeat it in the body.
    if fits:
        tweets = [dict(first, text=rest.strip())] + tweets[1:]

    participants = list(dict.fromkeys(t["author"]["screen_name"] for t in tweets))
    multi = len(participants) > 1

    front = [
        "---",
        f'author: "@{a["screen_name"]}"',
        f'name: "{a["name"].replace(chr(34), chr(39))}"',
        f"date: {date}",
        f"source: {first['url']}",
        f"tweets: {len(tweets)}",
    ]
    if multi:
        front.append("participants: [" + ", ".join(f'"@{p}"' for p in participants) + "]")
    front.append("---")

    header = f"# {title}\n\n*[@{a['screen_name']}]({a['url']}) · {date}*"
    body = "\n\n---\n\n".join(tweet_md(t, multi) for t in tweets)
    return "\n".join(front) + f"\n\n{header}\n\n{body}\n"


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")  # emoji and Cyrillic on any locale
    args = list(argv)
    out = None
    if "-o" in args:
        i = args.index("-o")
        out = args[i + 1] if i + 1 < len(args) else None
        del args[i : i + 2]
    if not args:
        print("Usage: python3 unroll.py <tweet url> [-o out.md | -o -]", file=sys.stderr)
        return 1

    tweets = collect_thread(parse_id(args[0]))
    md = to_markdown(tweets)
    if out == "-":
        sys.stdout.write(md)
        return 0
    path = out or f"{tweets[0]['author']['screen_name']}-{tweets[0]['id']}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    n = len(tweets)
    print(f"✓ {n} tweet{'' if n == 1 else 's'} → {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:  # noqa: BLE001 - one-line error for the agent, no traceback
        print(f"✗ {e}", file=sys.stderr)
        sys.exit(1)
