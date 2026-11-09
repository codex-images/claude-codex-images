# claude-codex-images

**Ask Claude Code for an image, from your phone, and get it made by GPT through the ChatGPT plan you already pay for. No API key, no per-image cost.**

[עברית למטה ⬇](#עברית)

<p align="center"><img src="docs/fox_barista.jpg" width="300" alt="Generated from text only"> <img src="docs/fox_reading.jpg" width="300" alt="Same character from a reference image"></p>
<p align="center"><sub>Left: from a text prompt (36 s). Right: the same fox, made with the left image as a reference (76 s). Both from <code>examples/job_example.json</code>.</sub></p>

Claude Code has no image model. OpenAI's **Codex CLI** has a built-in image generation tool, and when Codex is signed
in with a ChatGPT account that has a paid plan, the images come out of that plan's quota.

This repo is a Claude Code **skill** that lets Claude do the whole thing **in its own environment**:

1. Claude installs Codex where Claude runs: the cloud container of a Claude Code session on the web or in the app, or
   your computer if you run Claude Code locally.
2. Claude starts the sign-in and shows you a **one-time code in the chat**.
3. You open `https://auth.openai.com/codex/device` on your phone, sign in to ChatGPT and type the code.
4. From then on you just ask in the chat ("make me a 9:16 image of…"), and the image comes back about a minute later.

You never open a terminal. It works from the Claude app on your phone. It grew out of a real production pipeline (an
animated YouTube series that makes hundreds of frames a week), and every rule below was paid for with a failed image.

---

## What you need
- A **ChatGPT paid plan** (Plus, Pro, Business, Edu, Enterprise). A free account never gets the image tool.
- **Claude Code**: on the web (claude.ai/code), in the Claude app, or locally. Claude needs Node.js 22+ and Python 3 in
  its environment (Claude Code's cloud environment has both).

## 1. Add the skill
**For Claude Code on the web / in the app (cloud):** put the skill in the repository you work on, so every session sees it:
```bash
mkdir -p .claude/skills
cp -r skill/codex-images .claude/skills/
git add .claude/skills/codex-images && git commit -m "Add codex-images skill"
```
Or just ask Claude in a session on that repository: *"Add the codex-images skill from github.com/codex-images/claude-codex-images to this repo's .claude/skills and commit it."*

**For Claude Code on your computer:** `cp -r skill/codex-images ~/.claude/skills/` (all projects), or into
`<project>/.claude/skills/` (one project).

## 2. First image: Claude signs Codex in, you type a code
Ask in the chat:

> Make me a 9:16 image of a cartoon fox barista pouring latte art in a cozy cafe.

What happens:
1. Claude installs Codex in its environment (`npm install -g @openai/codex`), the first time only.
2. Claude runs the sign-in (`codex login --device-auth`) and writes in the chat something like:
   *Open https://auth.openai.com/codex/device and enter the code `ABCD-1234E` (valid 15 minutes).*
3. On your phone: open that page, sign in with the ChatGPT account **that has the paid plan**, type the code, approve.
4. Claude sees `Logged in using ChatGPT` and makes the image. About 40–80 seconds later it is in the chat.

> Only type a code you asked for yourself. Codex shows the same warning: if a website or another person gave you the code, cancel.

In a cloud session the sign-in lasts until the session's container is reset. Next time, Claude asks for a new code the same way.

## 3. Same character, new scene (reference images)
> Use the fox image as a reference: the same fox, now reading a book by a rainy window.

- **Up to 5 reference images per image.** With 6 the image tool refuses.
- Claude writes the prompt the way that works: a line per image (*"Image 1: the character…"*), where things are in
  words, and a list of what must **not** change (face, outfit, proportions).
- Don't ask for "as realistic as possible" if you want a consistent cartoon/3D look. The faces drift.

## 4. Many images at once
Ask for a batch ("make these 6 scenes…"), or give Claude a job file like [`examples/job_example.json`](examples/job_example.json).
Claude runs `scripts/codex_images.py job <file> --par 3`. Images land in `results/<job>/`, finished ones are skipped on a rerun,
and an image that uses another image of the batch as a reference waits for it.

## 5. Known limits (measured)
| | |
|---|---|
| Image model | chosen by Codex. You can't pick the model, the size or the quality |
| Size | auto. 16:9 ≈ 1672×941. Say the aspect ratio in the request |
| Speed | ~40–80 s per image (more with references). The account makes one image at a time |
| Quota | your ChatGPT usage window plus a daily image limit. Error: "usage limit", then wait for the reset |
| References | max 5 per image |

## 6. Troubleshooting
| Symptom | Fix |
|---|---|
| The code expired | ask Claude for a new one (it lasts 15 minutes) |
| "no image generation tool" / no image | the account has no paid plan. Claude runs `codex logout`, you sign out on chatgpt.com, then sign in again with the right account |
| The result is "someone else" | the references weren't used. Ask for a stronger Codex model with medium effort; keep the "Image 1: …" lines |
| "usage limit has been reached" | wait for the reset time. Finished images are skipped on rerun |
| Asked for a code again in a new session | expected in the cloud: the sign-in lives in that session's container |
| Disk filling up | the script deletes Codex's image copies; Claude can also clean `~/.codex/generated_images` |

### Running it yourself (optional)
The scripts work without Claude too: `python3 skill/codex-images/scripts/codex_login.py start` then `wait`, and
`python3 skill/codex-images/scripts/codex_images.py one "<prompt>" --aspect 9:16 --out fox.png`. On a computer with a
browser, plain `codex login` also works.

## 7. Privacy and terms
- Codex runs in Claude's environment, signed in with your account. Prompts and reference images go to OpenAI under your
  ChatGPT terms.
- The sign-in is stored in `~/.codex/auth.json` in that environment. It is like a password: never commit it or paste it
  anywhere. The skill tells Claude never to print it.
- Use it within the [OpenAI usage policies](https://openai.com/policies/usage-policies) and your plan's terms: no real
  people's likeness without consent, no copyrighted characters or logos. This is an unofficial community tool, not
  affiliated with OpenAI or Anthropic.

## License
MIT. See [LICENSE](LICENSE).

---

<div dir="rtl">

## עברית

**מבקשים מקלוד קוד תמונה, גם מהטלפון, והיא נוצרת בג'י־פי־טי דרך המנוי לצ'אט ג'י־פי־טי שכבר יש לכם. בלי מפתח ובלי תשלום לתמונה.**

לקלוד קוד אין מודל תמונות. לקודקס של אופן איי־איי יש כלי מובנה ליצירת תמונות, וכשהוא מחובר לחשבון צ'אט ג'י־פי־טי בתשלום, התמונות יורדות מהמכסה של המנוי.

הסקיל הזה נותן לקלוד לעשות הכל **בסביבה שלו**:
1. קלוד מתקין את קודקס איפה שהוא רץ: בסביבת הענן של סשן קלוד קוד באתר או באפליקציה, או במחשב שלכם אם קלוד קוד רץ אצלכם.
2. קלוד מפעיל את ההתחברות ומציג לכם **קוד חד־פעמי בצ'אט**.
3. אתם פותחים בטלפון את `https://auth.openai.com/codex/device`, נכנסים לחשבון צ'אט ג'י־פי־טי ומקלידים את הקוד.
4. מאז פשוט מבקשים בצ'אט ("תיצור לי תמונה לאורך של..."), ואחרי בערך דקה התמונה חוזרת.

לא פותחים טרמינל בכלל, ואפשר לעבוד מהאפליקציה בטלפון.

### מה צריך
- מנוי בתשלום לצ'אט ג'י־פי־טי (פלוס, פרו או עסקי). לחשבון חינמי אין כלי תמונות.
- קלוד קוד: באתר, באפליקציה או במחשב.

### שלב 1: מוסיפים את הסקיל
- **לקלוד קוד בענן (אתר או אפליקציה):** שמים את הסקיל בריפו שעובדים עליו, בתיקייה `.claude/skills/codex-images`, כדי שכל סשן יראה אותו. אפשר פשוט לבקש מקלוד בסשן על הריפו: "תוסיף לריפו את הסקיל codex-images מ־github.com/codex-images/claude-codex-images ותשמור".
- **לקלוד קוד במחשב:** מעתיקים את התיקייה `skill/codex-images` אל `~/.claude/skills/`.

### שלב 2: התמונה הראשונה
כותבים בצ'אט, למשל: "תיצור לי תמונה לאורך של שועל ברמן שמצייר לב בקפה".
1. בפעם הראשונה קלוד מתקין את קודקס אצלו.
2. קלוד כותב בצ'אט כתובת וקוד חד־פעמי (תקף ל־15 דקות).
3. בטלפון: פותחים את הכתובת, נכנסים עם החשבון שיש בו מנוי, מקלידים את הקוד ומאשרים.
4. קלוד רואה שההתחברות הצליחה, ואחרי 40 עד 80 שניות התמונה בצ'אט.

מקלידים רק קוד שביקשתם בעצמכם. בסשן בענן ההתחברות מחזיקה עד שהסביבה מתאפסת, ובסשן חדש קלוד יבקש קוד חדש באותה דרך.

### אותה דמות בסצנה חדשה
"תשתמש בתמונת השועל כייחוס: אותו שועל, עכשיו קורא ספר ליד חלון גשום". עד 5 תמונות ייחוס לכל תמונה. קלוד כותב את ההנחיה בשיטה שעובדת: שורה לכל תמונה, מי עומד איפה במילים, ורשימה של מה אסור לשנות.

### מגבלות
- את מודל התמונות, הגודל והאיכות קודקס קובע; אי אפשר לבחור.
- בערך 40 עד 80 שניות לתמונה, תמונה אחת בכל רגע לכל חשבון.
- יש מכסה יומית. כשהיא נגמרת מופיעה הודעה, וממשיכים אחרי האיפוס.

### פרטיות ותנאי שימוש
ההתחברות נשמרת בקובץ `~/.codex/auth.json` בסביבה של קלוד. זה כמו סיסמה: לא מעלים לגיט ולא מדביקים בשום מקום, והסקיל מורה לקלוד לעולם לא להציג אותו. ההנחיות והתמונות נשלחות לאופן איי־איי לפי תנאי המנוי שלכם. לא יוצרים דמויות של אנשים אמיתיים בלי הסכמה, ולא דמויות או סמלים מוגנים. כלי קהילתי לא רשמי, בלי קשר לאופן איי־איי או לאנתרופיק.

</div>
