---
name: codex-images
description: Generate or edit images from inside Claude Code with OpenAI Codex CLI and the user's ChatGPT subscription (GPT image tool, no API key, no per-image cost). Claude installs and signs in Codex in its own environment (cloud session or local) with a one-time code the user approves on their phone. Use when the user asks to "make an image", "generate a picture/thumbnail/illustration", "use GPT images / Codex", wants the same character in a new scene from reference images, or wants a batch of images from a list of prompts.
---

# Codex images: GPT image generation from Claude Code

Codex CLI (OpenAI's coding agent) has a built-in image generation tool. Signed in with a ChatGPT account that has a
paid plan (Plus, Pro, Business...), images come out of that plan's quota: no API key, no per-image cost.
**You (Claude) install and run Codex in your own environment**: the cloud container of a Claude Code web/app session,
or the user's computer when Claude Code runs locally. The user never opens a terminal; they only approve a one-time
code on their phone. Scripts: `scripts/codex_login.py` (sign-in) and `scripts/codex_images.py` (images).

## First time in a session: sign in (you do it, the user approves)
1. `python3 <skill_dir>/scripts/codex_login.py start`
   - installs Codex if missing (`npm install -g @openai/codex`, Node 22+),
   - starts `codex login --device-auth` in the background (it blocks until approval),
   - prints `URL: https://auth.openai.com/codex/device` and `CODE: XXXX-XXXXX` (valid 15 minutes).
   If it prints `ALREADY_LOGGED_IN`, skip to the images.
2. Tell the user, in one short message: open the URL on any device (their phone is fine), sign in with the ChatGPT
   account that HAS the paid plan, and type the code. Say what it grants (this environment can generate images on
   their ChatGPT quota) and that they should continue only because they asked for it. Give the code exactly.
3. `python3 <skill_dir>/scripts/codex_login.py wait`, which returns `LOGGED_IN: Logged in using ChatGPT` once they approved.
   If it times out, run `start` again for a fresh code.
4. Never print, copy or commit `~/.codex/auth.json` (it is the login). In a cloud session the login lasts for the
   whole session, and every new cloud session needs a new code (same steps). Locally the login is saved on the
   computer and carries over between sessions, so check `codex_login.py status` first.
5. "No image generation tool" on the first image means the account has no paid plan: `codex logout`, ask the user to
   sign out on chatgpt.com, and run `start` again with the right account. (`codex` then `/status` shows the plan.)

## One image
```
python3 <skill_dir>/scripts/codex_images.py one "<prompt>" --aspect 9:16 --out out/fox.png
python3 <skill_dir>/scripts/codex_images.py one "<prompt>" --aspect 1:1 --out out/fox2.png --ref out/fox.png
```
About 40–80 s per image (up to ~2 min with references). Tell the user one line ("making the image in Codex, about a
minute"); run longer batches in the background. Then show the PNG (open/read it, or send the file).

## A batch (job file)
```json
{"job": "my_batch", "aspect": "9:16", "model": "<strong Codex model>", "effort": "medium",
 "jobs": [{"id": "fox_cafe", "prompt": "...", "refs": []},
          {"id": "fox_park", "prompt": "...", "refs": ["results/my_batch/fox_cafe.png"]}]}
```
`python3 <skill_dir>/scripts/codex_images.py job my_batch.json --par 3` writes `results/my_batch/<id>.png`, `<id>.log`
and `log.json`. Reference paths are relative to the job file; finished images are skipped on rerun; a job whose
reference is another job's output waits for it. `model`/`effort` select the Codex chat model (not the image model).

## Prompts that keep a character or a place
- At most **5 reference images** per image (6 makes the image tool refuse).
- Open with one line per image ("Image 1: the character sheet. Image 2: the room."), say in words where things are,
  and list what must NOT change (identity, face, outfit, layout, proportions). Repeat that list in every fix.
- For a consistent animated look never ask for "as realistic as possible"; say "keep the rendering style of Image 1".
- To fix one detail, attach the image itself: "change ONLY ...; everything else stays identical".
- If references are ignored (someone else comes out), use a stronger Codex model and `"effort": "medium"`.

## Limits to tell the user
- Codex decides the image model, size and quality; they cannot be set. Ask for the aspect ratio in the prompt.
- One image at a time per account; `--par` only saves the gaps between runs.
- A usage window plus a daily image limit. The error says "usage limit": stop and continue after the reset.
- Disk: `codex_images.py` deletes Codex's copies after saving; also clean `~/.codex/generated_images` and a large
  `~/.codex/*.sqlite` history now and then.

## Never
- Print or commit `~/.codex/auth.json`, or ask the user to paste passwords or tokens into the chat.
- Generate real people's likeness, logos or copyrighted characters. Follow OpenAI's usage policies.
