---
name: codex-images
description: Generate or edit images from inside Claude Code with OpenAI Codex CLI and the user's ChatGPT subscription (GPT image model, no API key, no per-image cost). Use when the user asks to "make an image", "generate a picture/thumbnail/illustration", "use GPT images / Codex", wants the same character in a new scene from reference images, or wants a batch of images from a list of prompts.
---

# Codex images: GPT image generation from Claude Code

Codex CLI (OpenAI's coding agent) has a built-in image generation tool. When Codex is signed in with a ChatGPT
account that has a paid plan (Plus, Pro, Business...), images come out of the subscription quota. There is no API key
and no per-image cost. This skill drives Codex from Claude Code through `scripts/codex_images.py`.

## Before the first image (check once per session)
1. `codex --version`. If it is missing: `npm install -g @openai/codex` (needs Node.js 22+).
2. `codex login status`. It must say **Logged in using ChatGPT**. "API key" will not work (no image tool), and
   "Not logged in" means you must log in first:
   - computer with a browser: `codex login` (the browser opens, sign in with the ChatGPT account that has the plan);
   - server / container / cloud session without a browser: `codex login --device-auth`. It prints a URL and a
     one-time code. The USER opens the URL on any device and types the code. Show them the URL and code; never ask
     them to paste a password, token or `auth.json` into the chat.
3. If images fail with "no image generation tool", the account has no paid plan (a free account never gets the
   tool). Run `codex`, type `/status`, and check that the plan shows (Plus/Pro). If not, `codex logout` and log in
   with the right account.

## One image
```
python3 <skill_dir>/scripts/codex_images.py one "<prompt>" --aspect 9:16 --out out/fox.png
python3 <skill_dir>/scripts/codex_images.py one "<prompt>" --aspect 1:1 --out out/fox2.png --ref out/fox.png
```
About 40–80 seconds per image. Run it in the background if the session should stay responsive. Then show the
image to the user (open/read the PNG).

## A batch (job file)
```json
{"job": "my_batch", "aspect": "9:16",
 "jobs": [{"id": "fox_cafe", "prompt": "...", "refs": []},
          {"id": "fox_park", "prompt": "...", "refs": ["results/my_batch/fox_cafe.png"]}]}
```
`python3 <skill_dir>/scripts/codex_images.py job my_batch.json --par 3` writes `results/my_batch/<id>.png`,
`<id>.log` and `log.json`. Reference paths are relative to the job file. Existing outputs are skipped, so a rerun
continues where it stopped. Optional `"model"` and `"effort"` at the top select the Codex chat model (not the image
model).

## Writing prompts that keep a character or a place
- At most **5 reference images** per image. With 6 the image tool refuses. Pick the 5 that matter.
- Open with one line per image: "Image 1: the character sheet of Mia (face, hair, outfit). Image 2: the approved
  wide shot of the room (light, layout)." Then say exactly what goes where, and in words where things stand
  ("Mia in the left third, facing right").
- List what must NOT change (identity, face, hair, outfit, room layout, proportions, perspective) and repeat that
  list in every fix.
- For a consistent series look, never ask for "as realistic as possible": the model drifts to photo style and the
  faces change. Say "keep exactly the rendering style of Image 1".
- To fix part of an existing image, attach the image itself and say "change ONLY ...; everything else stays
  pixel-identical". Small crops edit better than whole frames.
- If references seem ignored (the result looks like someone else), set a stronger Codex model and
  `"effort": "medium"` in the job. The fast default model sometimes generates from text only.

## Limits to tell the user (measured, late 2026)
- The image model, size and quality are chosen by Codex (`gpt-image-2` family, "auto"). They cannot be set. 16:9
  comes out about 1672×941. Ask for the aspect ratio in the prompt.
- The account makes one image at a time. Parallel runs (`--par 3`) only save the gaps between runs, about 47 s per image either way.
- There is a usage window and a daily image limit (a heavy day on Plus hit it at about 280 images). The error says
  "usage limit". Stop and continue after the reset.
- Disk: Codex keeps every image twice (`~/.codex/generated_images` and the session file). The script deletes both after copying.

## Never
- Never print, commit or paste `~/.codex/auth.json`. It is the login, like a password. Add `.codex/` to `.gitignore`.
- Never generate real people's likeness, logos or copyrighted characters. Follow OpenAI's usage policies.
