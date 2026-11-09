#!/usr/bin/env python3
"""Sign Codex in with ChatGPT from inside a Claude Code chat (cloud session or local), with no browser on this machine.

    python3 codex_login.py start    # installs Codex if missing, starts device auth in the background,
                                    # prints the URL and the one-time code for the user
    python3 codex_login.py wait     # waits (up to 15 min) until the user approved; prints the result
    python3 codex_login.py status   # one check

The user opens https://auth.openai.com/codex/device on any device (a phone is fine), signs in with the ChatGPT
account that has the paid plan, and types the code. The code expires in 15 minutes. The login is stored in
~/.codex/auth.json on THIS machine: in the cloud it lasts for the session (a new cloud session needs a new code);
locally it carries over between sessions. Never print that file.
"""
import os, re, shutil, subprocess, sys, time
from pathlib import Path

LOG = Path(os.environ.get("TMPDIR", "/tmp")) / "codex_login.log"
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


def sh(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def status():
    if not shutil.which("codex"):
        return "codex not installed"
    r = sh(["codex", "login", "status"])
    return (r.stdout + r.stderr).strip()


def ensure_codex():
    if shutil.which("codex"):
        return
    print("Installing Codex CLI (npm install -g @openai/codex)...", flush=True)
    r = sh(["npm", "install", "-g", "@openai/codex"])
    if r.returncode != 0 or not shutil.which("codex"):
        sys.exit("Could not install Codex: " + (r.stderr or r.stdout)[-600:])


def start():
    ensure_codex()
    s = status()
    if "Logged in using ChatGPT" in s:
        print("ALREADY_LOGGED_IN: " + s)
        return
    LOG.write_text("")
    # device auth blocks until the user approves, so it runs in the background and we read its output
    with open(LOG, "w") as f:
        subprocess.Popen(["codex", "login", "--device-auth"], stdout=f, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, start_new_session=True)
    url = code = None
    for _ in range(60):
        time.sleep(0.5)
        text = ANSI.sub("", LOG.read_text(errors="ignore"))
        u = re.search(r"https://\S+/device\S*", text)
        c = re.search(r"\b([A-Z0-9]{4}-[A-Z0-9]{4,6})\b", text)
        if u and c:
            url, code = u.group(0), c.group(1)
            break
    if not code:
        sys.exit("No device code yet. Log:\n" + ANSI.sub("", LOG.read_text(errors="ignore"))[-1500:])
    print(f"URL: {url}\nCODE: {code}\nEXPIRES: 15 minutes")
    print("Tell the user: open the URL on any device, sign in with the ChatGPT account that has the paid plan, "
          "type the code. Continue only if they started this login. Then run: codex_login.py wait")


def wait(timeout=900):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = status()
        if "Logged in using ChatGPT" in s:
            print("LOGGED_IN: " + s)
            return
        time.sleep(5)
    sys.exit("Timed out (the code lasts 15 minutes). Run codex_login.py start again for a new code.")


if __name__ == "__main__":
    {"start": start, "wait": wait, "status": lambda: print(status())}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
