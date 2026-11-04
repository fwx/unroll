<p align="center"><img src=".claude-plugin/icon.svg" width="88" alt=""></p>

# unroll

Unroll a Twitter/X thread to Markdown, right from your AI agent.

English | [Русский](README.ru.md)

An agent skill that pulls an X/Twitter thread into clean Markdown, so your agent can read it, summarize it, or save it to a file. That covers a classic thread (a post plus the author's replies under it) and a reply chain where the author talks to other people.

It uses the open [Agent Skills](https://agentskills.io/specification) format. Tested in Claude Code, oh-my-pi, and Codex. Other agents that read `SKILL.md` should work too, see [Other agents](#other-agents).

It pulls data from the public [FxTwitter API](https://docs.fxembed.com/api/introduction/), so you don't need an X account, an API key, or a headless browser.

![unroll demo: an agent summarizes an X thread](assets/demo.gif)

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

The script runs fine without any agent too. It needs Python 3.8+ and nothing else, only the standard library:

```bash
python3 skills/unroll/scripts/unroll.py https://x.com/user/status/123 -o thread.md
python3 skills/unroll/scripts/unroll.py https://x.com/user/status/123 -o -   # print to stdout
```

## Other agents

The quickest way is the [`skills`](https://skills.sh) CLI. It asks which agents to install to (Codex, Cursor, omp and others):

```bash
npx skills add fwx/unroll
```

Or do it by hand: clone the repo and link (or copy) `skills/unroll` into the agent's skills directory:

```bash
git clone https://github.com/fwx/unroll.git
ln -s "$PWD/unroll/skills/unroll" ~/.omp/agent/skills/unroll   # oh-my-pi
ln -s "$PWD/unroll/skills/unroll" ~/.codex/skills/unroll       # Codex
```

For a single project, use `.omp/skills/` or `.agents/skills/` inside the repo instead. Checked with omp 18.12 and Codex 0.153.

Codex's sandbox has no network by default, so the script can't reach `api.fxtwitter.com` there. If it fails with a network error, add this to `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

## Output

A real run on a reply by Sam Altman, cut after five tweets. The link points deep into the replies, so the file starts at the original post and walks down to it:

```bash
python3 skills/unroll/scripts/unroll.py https://x.com/sama/status/2117845542021808438
```

```markdown
---
author: "@sama"
name: "Sam Altman"
date: 2026-11-04
source: https://x.com/sama/status/2117794005165748448
tweets: 6
participants: ["@sama", "@HarshithLucky3", "@jestermolecule"]
---

# People should always be in control of the future.

*[@sama](https://x.com/sama) · 2026-11-04*

**@sama**

OpenAI is against the notion that it would be acceptable for people to be relegated to a role of doing things that “AI systems think makes sense to reward in humans”.

People should not cede control of the future to superintelligence, and that requirement should ultimately constrain AI progress.

---

**@HarshithLucky3**

sam come here come here

![](https://pbs.twimg.com/media/HWPwXIkbkAAMaJD.png?name=orig)

---

**@sama**

i lol'd

---

**@jestermolecule**

can u rename your x to ram altman!

---

**@sama**

ok yeah

---

...
```

In a thread with one author the `@handle` labels and `participants` are left out. Photos become `![](url)`. Videos and GIFs become a thumbnail that links to the mp4. Quoted tweets go into a `>` blockquote with a link back to the source.

## Limits

- You get one branch: the chain that leads to and continues from the linked tweet. Other replies under the post are left out. When several people post in the branch, each tweet is labeled with its author.
- If `api.fxtwitter.com` is down, the script can't fetch anything. The limit is 1000 requests per minute per IP, and one thread costs one request.
- Deleted and protected tweets are out of reach.

## License

[MIT](LICENSE)
