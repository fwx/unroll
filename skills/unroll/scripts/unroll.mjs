#!/usr/bin/env node
// unroll: fetches an X/Twitter thread as Markdown, to a file or stdout.
// Usage: node unroll.mjs <url of any tweet in the thread> [-o out.md | -o - for stdout]

import { writeFileSync } from "node:fs";

const API = "https://api.fxtwitter.com/2/thread/";

function parseId(input) {
  const m = String(input).match(/(?:status(?:es)?\/)?(\d{5,})/);
  if (!m) throw new Error(`Could not extract a tweet ID from: ${input}`);
  return m[1];
}

// fxtwitter /2/thread/<id> returns the author's whole self-reply chain,
// no matter which tweet of the thread you start from.
async function collectThread(id) {
  const res = await fetch(API + id, { headers: { "User-Agent": "unroll" } });
  const data = await res.json().catch(() => null);
  if (!res.ok || !data?.status) {
    throw new Error(`Failed to fetch thread ${id}: ${data?.message ?? res.status}`);
  }
  const author = data.status.author.screen_name.toLowerCase();
  const thread = data.thread?.length ? data.thread : [data.status];
  return thread
    .filter((t) => t.author.screen_name.toLowerCase() === author)
    .sort((a, b) => a.created_timestamp - b.created_timestamp);
}

function mediaMd(media) {
  if (!media?.all?.length) return "";
  return media.all
    .map((m) => {
      if (m.type === "photo") return `![](${m.url})`;
      // Videos and GIFs: thumbnail image linking to the mp4.
      const thumb = m.thumbnail_url ? `![](${m.thumbnail_url})` : "▶ video";
      return `[${thumb}](${m.url})`;
    })
    .join("\n\n");
}

function quoteMd(q) {
  if (!q) return "";
  const body = [`**@${q.author.screen_name}**: ${q.text}`, mediaMd(q.media)]
    .filter(Boolean)
    .join("\n\n");
  return body
    .split("\n")
    .map((l) => `> ${l}`)
    .concat(`> — [source](${q.url})`)
    .join("\n");
}

function tweetMd(t) {
  return [t.text, mediaMd(t.media), quoteMd(t.quote)].filter(Boolean).join("\n\n");
}

function toMarkdown(tweets) {
  const first = tweets[0];
  const a = first.author;
  const date = new Date(first.created_timestamp * 1000).toISOString().slice(0, 10);
  const title = first.text.split("\n")[0].slice(0, 80).trim().replace(/"/g, "'");

  const front = [
    "---",
    `author: "@${a.screen_name}"`,
    `name: "${a.name.replace(/"/g, "'")}"`,
    `date: ${date}`,
    `source: ${first.url}`,
    `tweets: ${tweets.length}`,
    "---",
  ].join("\n");

  const header = `# ${title}\n\n*[@${a.screen_name}](${a.url}) · ${date}*`;
  const body = tweets.map(tweetMd).join("\n\n---\n\n");
  return `${front}\n\n${header}\n\n${body}\n`;
}

async function main() {
  const args = process.argv.slice(2);
  const oIdx = args.indexOf("-o");
  const out = oIdx >= 0 ? args.splice(oIdx, 2)[1] : null;
  if (!args[0]) {
    console.error("Usage: node unroll.mjs <tweet url> [-o out.md | -o -]");
    process.exit(1);
  }

  const tweets = await collectThread(parseId(args[0]));
  const md = toMarkdown(tweets);
  if (out === "-") {
    process.stdout.write(md);
    return;
  }
  const file = out ?? `${tweets[0].author.screen_name}-${tweets[0].id}.md`;
  writeFileSync(file, md);
  console.error(`✓ ${tweets.length} tweets → ${file}`);
}

main().catch((e) => {
  console.error("✗", e.message);
  process.exit(1);
});
