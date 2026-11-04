---
name: unroll
description: Unroll an X/Twitter thread (an author's chain of self-replies) into a single Markdown file. Use when the user shares an x.com or twitter.com status link and wants the thread saved, exported, converted to markdown, archived, or read as one document. Triggers include "unroll this thread", "save this thread", "thread to markdown", "тред в markdown", "сохрани тред", "разверни тред".
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
2. Decide where to save. If the user named a path, pass it with `-o`. Otherwise omit `-o`;
   the script writes `<author>-<first-tweet-id>.md` into the current working directory.
3. Run the bundled script. `scripts/unroll.mjs` is relative to this skill's directory
   (the folder containing this SKILL.md); build the absolute path from it:

   ```bash
   node <skill-dir>/scripts/unroll.mjs "<url>" [-o <path.md>]
   ```

   Requires Node.js 18+. On success it prints `✓ N tweets → <file>` to stderr.
4. Tell the user the file path and the tweet count. Do not paste the whole file into the chat
   unless they ask; offer a short summary instead if it seems useful.

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
