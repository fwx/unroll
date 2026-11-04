# unroll

English | [Русский](README.ru.md)

An agent skill that pulls an X/Twitter thread into clean Markdown, so your agent can read it, summarize it, or save it to a file. A thread here means a post plus the author's own replies under it.

It uses the open [Agent Skills](https://agentskills.io/specification) format. Tested in Claude Code and oh-my-pi; Codex and other agents that read `SKILL.md` should work too, see [Other agents](#other-agents).

It pulls data from the public [FxTwitter API](https://docs.fxembed.com/api/introduction/), so you don't need an X account, an API key, or a headless browser.

## Install in Claude Code

```
/plugin marketplace add fwx/unroll
/plugin install unroll@unroll
```

Or copy `skills/unroll` to `~/.claude/skills/unroll` by hand.

## Use

Give your agent a link and ask in your own words. No magic phrase needed:

> read this thread and tell me what it's about https://x.com/user/status/123

> save this thread https://x.com/user/status/123

If you ask to read, summarize, or translate, the agent gets the thread as text and no file is created. If you ask to save, it writes `<author>-<id>.md`.

Or call the skill directly:

```
/unroll:unroll https://x.com/user/status/123   # Claude Code
/skill:unroll https://x.com/user/status/123    # oh-my-pi
$unroll https://x.com/user/status/123          # Codex
```

Any tweet from the thread works: the first one, the last one, or one in the middle.

The script runs fine without any agent too. It needs Node.js 18+ and has no dependencies:

```bash
node skills/unroll/scripts/unroll.mjs https://x.com/user/status/123 -o thread.md
node skills/unroll/scripts/unroll.mjs https://x.com/user/status/123 -o -   # print to stdout
```

## Other agents

Clone the repo and link (or copy) `skills/unroll` into the agent's skills directory:

```bash
git clone https://github.com/fwx/unroll.git
ln -s "$PWD/unroll/skills/unroll" ~/.omp/agent/skills/unroll   # oh-my-pi
ln -s "$PWD/unroll/skills/unroll" ~/.codex/skills/unroll       # Codex
```

For a single project, use `.omp/skills/` or `.agents/skills/` inside the repo instead. Checked with omp 18.12; the Codex path comes from its docs and hasn't been tested yet.

## Output

```markdown
---
author: "@user"
name: "User Name"
date: 2026-11-04
source: https://x.com/user/status/123
tweets: 19
---

# First line of the thread

*[@user](https://x.com/user) · 2026-11-04*

Text of the first tweet...

---

Text of the second tweet...
```

Photos become `![](url)`. Videos and GIFs become a thumbnail that links to the mp4. Quoted tweets go into a `>` blockquote with a link back to the source.

## Limits

- Only the author's tweets are kept. Replies from other people are dropped.
- If `api.fxtwitter.com` is down, the script can't fetch anything. The limit is 1000 requests per minute per IP, and one thread costs one request.
- Deleted and protected tweets are out of reach.

## License

[MIT](LICENSE)
