# claude-codex-images

**Generate GPT images from inside Claude Code, using the ChatGPT subscription you already pay for. No API key, no per-image cost.**

[עברית למטה ⬇](#עברית)

<p align="center"><img src="docs/fox_barista.jpg" width="300" alt="Generated from text only"> <img src="docs/fox_reading.jpg" width="300" alt="Same character from a reference image"></p>
<p align="center"><sub>Left: from a text prompt (36 s). Right: the same fox, made with the left image as a reference (76 s). Both from <code>examples/job_example.json</code>.</sub></p>

Claude Code is great at planning and writing, but it has no image model. OpenAI's **Codex CLI** has a built-in image
generation tool (the `gpt-image-2` family), and when Codex is signed in with a ChatGPT account that has a paid plan,
the images come out of your plan's quota. This repo is a Claude Code **skill** plus one small Python script. Together
they let Claude call Codex for you: you ask for a picture in the chat, and a PNG lands in your folder.

This setup came out of a real production pipeline (an animated YouTube series that makes hundreds of frames a week).
Every rule below was paid for with a failed image.

---

## What you need
- A **ChatGPT paid plan** (Plus, Pro, Business, Edu, Enterprise). A free account never gets the image tool.
- **Claude Code** (CLI, desktop, or claude.ai/code).
- **Node.js 22+** (for Codex CLI) and **Python 3.9+** (for the script, standard library only).

## 1. Install Codex CLI
```bash
npm install -g @openai/codex
codex --version
```

## 2. Sign in with your ChatGPT account
**On a computer with a browser:**
```bash
codex login          # the browser opens -> sign in with the ChatGPT account that HAS the plan
codex login status   # must print: Logged in using ChatGPT
```
**On a server, container or Claude Code in the cloud (no browser):**
```bash
codex login --device-auth
```
It prints a URL and a one-time code. Open the URL on your phone or laptop, sign in, and type the code. The machine is
now logged in. No password or token ever goes into a chat. In a cloud session the login lasts until the container is
reset. Run it again in a new session.

**Check the plan:** run `codex`, type `/status`. It should show your plan (e.g. `Plus`) and the usage limits. If it
does not, you are logged in with the wrong account: `codex logout`, sign out on chatgpt.com, and log in again.

> The login is stored in `~/.codex/auth.json`. Treat it like a password. Never commit it, never paste it into a chat.
> Copying that file to another machine you own also works, but device auth is safer.

## 3. Install the skill in Claude Code
```bash
git clone https://github.com/codex-images/claude-codex-images
mkdir -p ~/.claude/skills
cp -r claude-codex-images/skill/codex-images ~/.claude/skills/
```
(For one project only, copy it to `<project>/.claude/skills/` instead.) Restart Claude Code. The skill is now listed.

## 4. Your first image
In Claude Code just ask:

> Make me a 9:16 image of a cartoon fox barista pouring latte art in a cozy cafe.

Claude checks the Codex login, runs the script, waits ~45 seconds, and shows you the PNG. Or run it yourself:
```bash
python3 ~/.claude/skills/codex-images/scripts/codex_images.py one \
  "a cartoon fox barista pouring latte art in a cozy cafe" --aspect 9:16 --out fox.png
```

## 5. Batches from a job file
```bash
python3 ~/.claude/skills/codex-images/scripts/codex_images.py job examples/job_example.json --par 3
```
See [`examples/job_example.json`](examples/job_example.json): a list of `{id, prompt, refs}` with an `aspect`. Results
go to `examples/results/<job>/<id>.png` with a `.log` per image and a `log.json`. Existing images are skipped, so a
rerun continues. A job whose reference is another job's output waits for it automatically.

## 6. Reference images (same character, new scene)
- **Up to 5 reference images per image.** With 6 the image tool refuses.
- Start the prompt with a line per image: *"Image 1: the character sheet (face, hair, outfit). Image 2: the room."*
- Say where things are in words (*"in the left third, facing right"*), and list what must **not** change (identity,
  face, outfit, layout, proportions). Repeat that list in every fix.
- Don't ask for "as realistic as possible" if you want a consistent cartoon/3D look. The faces drift.
- To fix one detail, attach the image itself: *"change ONLY the cup; everything else stays identical"*.
- If references are ignored, set a stronger Codex model and `"effort": "medium"` in the job file. The fast default
  model sometimes generates from text only.

## 7. Known limits (measured)
| | |
|---|---|
| Image model | fixed by Codex (`gpt-image-2` family). You can't choose it, the size or the quality |
| Size | auto. 16:9 ≈ 1672×941. Ask for the aspect ratio in the prompt |
| Speed | ~40–80 s per image. The account makes one image at a time, so `--par 3` only saves the gaps |
| Quota | your ChatGPT usage window plus a daily image limit (a heavy Plus day hit it at ~280 images). Error: "usage limit" |
| References | max 5 per image |

## 8. Troubleshooting
| Symptom | Fix |
|---|---|
| `codex: command not found` | reopen the terminal after `npm install -g`, or use the full path from `npm prefix -g` |
| "no image generation tool" / no PNG | the account has no paid plan, or it is logged in with an API key. Check `/status`, then `codex logout` + `codex login` |
| the image tool "rejected" the references | more than 5 references. Merge two into one sheet |
| the result is "someone else" | references were not passed. Use a stronger model + `effort: medium`, and keep the "Image 1: ..." lines |
| "usage limit has been reached" | wait for the reset time. The script skips finished images on rerun |
| disk filling up | old Codex versions keep images in `~/.codex/generated_images` and `~/.codex/sessions`. The script deletes them after copying |
| Windows: `CreateProcessAsUserW failed: 5` | keep the read-only sandbox (the script does). Never `workspace-write` |

## 9. Privacy and terms
- Everything runs on your machine with your own account. Prompts and reference images go to OpenAI under your
  ChatGPT terms.
- `auth.json` = your login. It is in `.gitignore`. Keep it that way.
- Use this within the [OpenAI usage policies](https://openai.com/policies/usage-policies) and the terms of your
  plan: no real people's likeness without consent, no copyrighted characters or logos. This is an unofficial
  community tool, not affiliated with OpenAI or Anthropic.

## License
MIT. See [LICENSE](LICENSE).

---

<div dir="rtl">

## עברית

**יוצרים תמונות במודל של צ'אט ג'י־פי־טי ישירות מתוך קלוד קוד, עם המנוי שכבר משלמים עליו. בלי מפתח ובלי תשלום לתמונה.**

לקלוד קוד אין מודל תמונות. לכלי קודקס של אופן איי־איי יש כלי מובנה ליצירת תמונות, וכשמתחברים אליו עם חשבון
צ'אט ג'י־פי־טי בתשלום, התמונות יורדות מהמכסה של המנוי. בפרויקט הזה יש סקיל לקלוד קוד וסקריפט קטן. אתם מבקשים תמונה
בצ'אט, וקלוד מפעיל את קודקס בשבילכם, והתמונה נשמרת בתיקייה.

### מה צריך
- מנוי בתשלום לצ'אט ג'י־פי־טי (פלוס, פרו או עסקי). לחשבון חינמי אין כלי תמונות.
- קלוד קוד.
- נוד בגרסה 22 ומעלה, ופייתון 3.9 ומעלה.

### שלב 1: מתקינים את קודקס
```bash
npm install -g @openai/codex
```

### שלב 2: מתחברים עם החשבון של צ'אט ג'י־פי־טי
- **במחשב רגיל:** מריצים `codex login`, הדפדפן נפתח, ומתחברים עם החשבון שיש בו מנוי. בודקים עם `codex login status`
  שכתוב שם שאתם מחוברים עם צ'אט ג'י־פי־טי.
- **בשרת או בקלוד קוד בענן (בלי דפדפן):** מריצים `codex login --device-auth`. מופיעים כתובת וקוד חד־פעמי. פותחים את
  הכתובת בטלפון, מתחברים ומקלידים את הקוד. אף סיסמה לא עוברת בצ'אט. בענן ההתחברות מחזיקה עד שהמכונה מתאפסת.
- **לוודא שהמנוי מחובר:** מריצים `codex`, כותבים `/status`, וצריך לראות שם את המנוי (למשל פלוס).
- ההתחברות נשמרת בקובץ `~/.codex/auth.json`. זה כמו סיסמה: לא מעלים אותו לגיט ולא מדביקים אותו בשום צ'אט.

### שלב 3: מתקינים את הסקיל
```bash
git clone https://github.com/codex-images/claude-codex-images
mkdir -p ~/.claude/skills
cp -r claude-codex-images/skill/codex-images ~/.claude/skills/
```
ומפעילים מחדש את קלוד קוד.

### שלב 4: התמונה הראשונה
כותבים לקלוד בצ'אט, למשל: "תיצור לי תמונה לאורך של שועל ברמן שמצייר לב בקפה". אחרי כ־45 שניות התמונה מוכנה.

### תמונות ייחוס
- עד 5 תמונות ייחוס לכל תמונה. עם 6 הכלי מסרב.
- פותחים את ההנחיה בשורה לכל תמונה ("תמונה 1 היא הדמות, תמונה 2 היא החדר"), אומרים במילים מי עומד איפה, ומפרטים
  מה אסור לשנות (פנים, בגדים, סידור החדר).
- לא כותבים "הכי מציאותי שאפשר" אם רוצים סגנון מונפש אחיד, כי אז הפנים משתנות.
- אם הייחוסים לא נקלטים (יוצאת "מישהי אחרת"), בוחרים בקובץ העבודה מודל חזק יותר ורמת חשיבה בינונית.

### מגבלות
- אי אפשר לבחור מודל תמונות, גודל או איכות. קודקס קובע.
- בערך 40 עד 80 שניות לתמונה, תמונה אחת בכל רגע לכל חשבון.
- יש מכסה יומית. כשהיא נגמרת מופיעה הודעה, וממשיכים אחרי האיפוס.

### פרטיות ותנאי שימוש
הכל רץ אצלכם, עם החשבון שלכם. ההנחיות והתמונות נשלחות לאופן איי־איי לפי תנאי המנוי שלכם. לא יוצרים דמויות של
אנשים אמיתיים בלי הסכמה, ולא דמויות או סמלים מוגנים. זה כלי קהילתי לא רשמי, בלי קשר לאופן איי־איי או לאנתרופיק.

</div>
