---
name: unroll
description: Fetch an X/Twitter thread (a post plus the author's own replies) as clean Markdown. Use whenever the user shares an x.com or twitter.com status link and wants to read, summarize, discuss, translate, or save the thread, e.g. "read this thread", "what does this thread say", "summarize this", "save this thread", "прочитай тред", "о чём тред", "перескажи", "сохрани тред". Prefer it over web fetching, since x.com pages need login and return little to a fetcher.
compatibility: Requires Node.js 18+ and network access to api.fxtwitter.com
argument-hint: <x.com status URL> [output.md]
allowed-tools: Bash(node ${CLAUDE_SKILL_DIR}/scripts/unroll.mjs *)
---

# unroll

Converts an X/Twitter thread into one Markdown file using the public FxTwitter API
(`https://api.fxtwitter.com/2/thread/<id>`). No X account, API key, or browser automation needed.

## Steps

1. Take the tweet URL (or bare status ID) from the user's message or the skill arguments.
   Any tweet of the thread works: first, middle, or last.
2. Pick the mode from what the user wants:
   - **Read** (read, summarize, explain, translate, answer questions about the thread):
     pass `-o -`. The Markdown goes to stdout and no file is created. Work with that text.
   - **Save** (save, export, archive, "to a file"): pass `-o <path.md>` if the user named a
     path, otherwise omit `-o`; the script writes `<author>-<first-tweet-id>.md` into the
     current working directory.
3. Run the bundled script. `scripts/unroll.mjs` is relative to this skill's directory
   (the folder containing this SKILL.md); build the absolute path from it:

   ```bash
   node <skill-dir>/scripts/unroll.mjs "<url>" -o -          # read
   node <skill-dir>/scripts/unroll.mjs "<url>" [-o <path.md>] # save
   ```

   Requires Node.js 18+. In save mode it prints `✓ N tweets → <file>` to stderr.
4. Read mode: answer what the user asked, based on the thread text. Save mode: tell the user
   the file path and tweet count; don't paste the whole file into the chat unless asked.

## Output format

- YAML frontmatter: `author`, `name`, `date`, `source`, `tweets`
- `# Title` from the first line of the first tweet, then author and date
- Each tweet's text, separated by `---`
- Photos as `![](url)`, videos and GIFs as a thumbnail linking to the mp4
- Quoted tweets as a `>` blockquote with a source link

Only the thread author's own tweets are included; replies from other people are skipped.

## Errors

- `Failed to fetch thread <id>: ...`: the tweet is deleted, protected, or the ID is wrong.
  Report the message as is; do not retry in a loop.
- Network or 5xx errors: FxTwitter may be down. Say so; there is no fallback source.
- Rate limit is 1000 requests/minute per IP, one request per thread.
