<p align="center"><img src=".claude-plugin/icon.svg" width="88" alt=""></p>

# unroll

Тред из Twitter/X в Markdown прямо из вашего ИИ-агента.

[English](README.md) | Русский

Скилл для ИИ-агентов, который достаёт тред из X/Twitter в виде Markdown: агент может его прочитать, пересказать или сохранить в файл. Подходит и для обычного треда (пост и ответы автора под ним), и для ветки, где автор переписывается с другими людьми.

Написан по открытому формату [Agent Skills](https://agentskills.io/specification). Проверен в Claude Code, oh-my-pi и Codex. Другие агенты, которые читают `SKILL.md`, тоже должны подойти, см. [Другие агенты](#другие-агенты).

Данные берутся из публичного [FxTwitter API](https://docs.fxembed.com/api/introduction/), поэтому аккаунт X, ключ API и браузер не нужны.

![демо unroll: агент пересказывает тред из X](assets/demo.gif)

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

Скрипт работает и без агента. Нужен Python 3.8+, сторонних библиотек нет:

```bash
python3 skills/unroll/scripts/unroll.py https://x.com/user/status/123 -o thread.md
python3 skills/unroll/scripts/unroll.py https://x.com/user/status/123 -o -   # вывод в stdout
```

## Другие агенты

Быстрее всего через CLI [`skills`](https://skills.sh). Он спросит, в какие агенты ставить (Codex, Cursor, omp и другие):

```bash
npx skills add fwx/unroll
```

Или вручную: склонируйте репозиторий и сделайте ссылку (или скопируйте) `skills/unroll` в папку скиллов агента:

```bash
git clone https://github.com/fwx/unroll.git
ln -s "$PWD/unroll/skills/unroll" ~/.omp/agent/skills/unroll   # oh-my-pi
ln -s "$PWD/unroll/skills/unroll" ~/.codex/skills/unroll       # Codex
```

Для одного проекта подойдёт `.omp/skills/` или `.agents/skills/` внутри репозитория. Проверено на omp 18.12 и Codex 0.153.

В песочнице Codex по умолчанию нет сети, и скрипт не достучится до `api.fxtwitter.com`. Если он падает с сетевой ошибкой, добавьте в `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
network_access = true
```

## Что получается

Настоящий запуск на ответе Сэма Альтмана, обрезан после пяти твитов. Ссылка ведёт глубоко в ответы, поэтому файл начинается с исходного поста и спускается к ней:

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

В треде с одним автором подписей `@ник` и поля `participants` нет. Картинки вставляются как `![](url)`. Видео и GIF превращаются в превью со ссылкой на mp4. Цитируемые твиты попадают в блок `>` со ссылкой на источник. Если цитата сама цитирует другой твит, скрипт проходит всю цепочку и вкладывает её как `> >`, до 8 уровней. У X Articles показываются заголовок и первые строки.

## Ограничения

- Сохраняется одна ветка: цепочка, которая ведёт к твиту по ссылке и продолжается после него. Остальные ответы под постом не попадают. Если в ветке пишут несколько человек, у каждого твита подписан автор.
- Если `api.fxtwitter.com` лежит, скрипт ничего не скачает. Лимит 1000 запросов в минуту с одного IP, один тред стоит один запрос.
- Удалённые и закрытые твиты получить нельзя.

## Лицензия

[MIT](LICENSE)
