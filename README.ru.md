# unroll

[English](README.md) | Русский

Скилл для ИИ-агентов, который достаёт тред из X/Twitter в виде Markdown: агент может его прочитать, пересказать или сохранить в файл. Подходит и для обычного треда (пост и ответы автора под ним), и для ветки, где автор переписывается с другими людьми.

Написан по открытому формату [Agent Skills](https://agentskills.io/specification). Проверен в Claude Code и oh-my-pi; Codex и другие агенты, которые читают `SKILL.md`, тоже должны подойти, см. [Другие агенты](#другие-агенты).

Данные берутся из публичного [FxTwitter API](https://docs.fxembed.com/api/introduction/), поэтому аккаунт X, ключ API и браузер не нужны.

## Установка в Claude Code

```
/plugin marketplace add fwx/unroll
/plugin install unroll@unroll
```

Или скопируйте `skills/unroll` в `~/.claude/skills/unroll` вручную.

## Использование

Дайте агенту ссылку и попросите своими словами, волшебная фраза не нужна:

> прочитай тред и скажи, о чём он https://x.com/user/status/123

> сохрани тред https://x.com/user/status/123

Если просите прочитать, пересказать или перевести, агент получает тред текстом и файл не создаётся. Если просите сохранить, появится `<автор>-<id>.md`.

Или вызовите скилл напрямую:

```
/unroll:unroll https://x.com/user/status/123   # Claude Code
/skill:unroll https://x.com/user/status/123    # oh-my-pi
$unroll https://x.com/user/status/123          # Codex
```

Подойдёт ссылка на любой твит треда: первый, последний или из середины.

Скрипт работает и без агента. Нужен Node.js 18+, зависимостей нет:

```bash
node skills/unroll/scripts/unroll.mjs https://x.com/user/status/123 -o thread.md
node skills/unroll/scripts/unroll.mjs https://x.com/user/status/123 -o -   # вывод в stdout
```

## Другие агенты

Склонируйте репозиторий и сделайте ссылку (или скопируйте) `skills/unroll` в папку скиллов агента:

```bash
git clone https://github.com/fwx/unroll.git
ln -s "$PWD/unroll/skills/unroll" ~/.omp/agent/skills/unroll   # oh-my-pi
ln -s "$PWD/unroll/skills/unroll" ~/.codex/skills/unroll       # Codex
```

Для одного проекта подойдёт `.omp/skills/` или `.agents/skills/` внутри репозитория. Проверено на omp 18.12, путь для Codex взят из его документации и пока не проверялся.

## Что получается

```markdown
---
author: "@user"
name: "User Name"
date: 2026-11-04
source: https://x.com/user/status/123
tweets: 19
---

# Первая строка треда

*[@user](https://x.com/user) · 2026-11-04*

Текст первого твита...

---

Текст второго твита...
```

Картинки вставляются как `![](url)`. Видео и GIF превращаются в превью со ссылкой на mp4. Цитируемые твиты попадают в блок `>` со ссылкой на источник.

## Ограничения

- Сохраняется одна ветка: цепочка, которая ведёт к твиту по ссылке и продолжается после него. Остальные ответы под постом не попадают. Если в ветке пишут несколько человек, у каждого твита подписан автор.
- Если `api.fxtwitter.com` лежит, скрипт ничего не скачает. Лимит 1000 запросов в минуту с одного IP, один тред стоит один запрос.
- Удалённые и закрытые твиты получить нельзя.

## Лицензия

[MIT](LICENSE)
