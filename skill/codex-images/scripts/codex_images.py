#!/usr/bin/env python3
"""Generate images with OpenAI Codex CLI (ChatGPT subscription, built-in image tool) - no API key, no per-image cost.

Two modes:

  # one image
  python3 codex_images.py one "a cartoon fox barista in a cozy cafe" --aspect 9:16 --out fox.png [--ref a.png --ref b.png]

  # a batch from a job file (see examples/job_example.json)
  python3 codex_images.py job examples/job_example.json [--par 3] [--out results/]

How it works (the method that works today, learned the hard way):
  codex exec --skip-git-repo-check -s read-only --enable image_generation \
             [-m MODEL -c model_reasoning_effort=EFFORT] -C <outdir> [-i ref1,ref2,...] -- -
  * the prompt goes on stdin (`-- -`). `-i` swallows several values, so all references go in ONE
    comma-separated list and `--` closes it before the prompt.
  * the sandbox stays read-only and Codex is told NOT to save anything; we copy the PNG ourselves from
    $CODEX_HOME/generated_images/<session id>/ (never "the newest image anywhere": parallel runs would mix).
  * the image tool only uses attached images if the model passes them, so every prompt says so explicitly.
  * at most 5 reference images per image (6 makes the image tool refuse).
Requires: `codex` on PATH and `codex login` with a ChatGPT account that HAS a paid plan (Plus/Pro/...).
"""
import argparse, concurrent.futures as cf, glob, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
MAX_REFS = 5
REF_RULE = ("Use the image generation tool. Give the image tool ALL {n} attached reference images as input references "
            "and never generate without them. ")
TAIL = " Aspect ratio {aspect}. Do not save, copy or describe files. When the image is generated, answer DONE."


def run_one(prompt, refs, aspect, dst, model=None, effort=None, timeout=1200, keep_logs=True):
    """Generate one image. Returns (ok, seconds, error_tail)."""
    dst = Path(dst)
    if dst.exists() and dst.stat().st_size > 1000:
        return True, 0, "exists (skipped)"
    refs = [str(Path(r).resolve()) for r in refs or []]
    missing = [r for r in refs if not Path(r).exists()]
    if missing:
        return False, 0, f"missing reference: {missing}"
    if len(refs) > MAX_REFS:
        return False, 0, f"{len(refs)} references; the image tool accepts at most {MAX_REFS}"
    dst.parent.mkdir(parents=True, exist_ok=True)
    text = (REF_RULE.format(n=len(refs)) if refs else "Use the image generation tool. ") + prompt + TAIL.format(aspect=aspect)
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "read-only", "--enable", "image_generation", "-C", str(dst.parent)]
    if model:
        cmd += ["-m", model]
    if effort:
        cmd += ["-c", f"model_reasoning_effort={effort}"]
    if refs:
        cmd += ["-i", ",".join(refs)]
    cmd += ["--", "-"]
    t0 = time.time()
    try:
        res = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        return False, 0, "codex not found on PATH (npm install -g @openai/codex)"
    except subprocess.TimeoutExpired:
        return False, round(time.time() - t0), "timeout"
    log = res.stdout + res.stderr
    if keep_logs:
        dst.with_suffix(".log").write_text(log[-20000:], encoding="utf-8")
    m = re.search(r"session id:\S*\s+([0-9a-f-]{20,})", log)
    pngs = sorted(glob.glob(str(CODEX_HOME / "generated_images" / m.group(1) / "*.png")), key=os.path.getmtime) if m else []
    if not pngs:
        tail = log[-400:]
        if "usage limit" in log.lower():
            tail = "image usage limit reached - wait for the reset. " + tail
        return False, round(time.time() - t0), tail
    shutil.copyfile(pngs[-1], dst)
    # keep the disk free: the copy is ours now, and a session rollout holds the image again as text
    shutil.rmtree(os.path.dirname(pngs[-1]), ignore_errors=True)
    for f in glob.glob(str(CODEX_HOME / "sessions" / "*" / "*" / "*" / f"*{m.group(1)}*.jsonl")):
        try:
            os.remove(f)
        except OSError:
            pass
    return True, round(time.time() - t0), ""


def cmd_one(a):
    ok, sec, err = run_one(a.prompt, a.ref, a.aspect, a.out, a.model, a.effort)
    print(("OK" if ok else "FAILED"), a.out, f"{sec}s", err)
    sys.exit(0 if ok else 1)


def cmd_job(a):
    jf = Path(a.job).resolve()
    job = json.loads(jf.read_text(encoding="utf-8"))
    jobs = job.get("jobs") or []
    if not jobs:
        sys.exit("job file has no 'jobs' list")
    base = jf.parent  # reference paths are relative to the job file
    out = Path(a.out) if a.out else base / "results" / job.get("job", jf.stem)
    out.mkdir(parents=True, exist_ok=True)

    def go(j):
        refs = [str((base / r) if not Path(r).is_absolute() else Path(r)) for r in j.get("refs", [])]
        ok, sec, err = run_one(j["prompt"], refs, j.get("aspect", job.get("aspect", "1:1")), out / f"{j['id']}.png",
                               job.get("model"), job.get("effort"))
        print(("OK    " if ok else "FAILED"), j["id"], f"{sec}s", err[-200:] if err else "", flush=True)
        return dict(id=j["id"], ok=ok, seconds=sec, error=err)

    def refs_ready(j):
        return all(((base / r) if not Path(r).is_absolute() else Path(r)).exists() for r in j.get("refs", []))

    # jobs that use another job's output as a reference wait for it: run in waves until nothing new is possible
    done, pending = {}, list(jobs)
    while pending:
        wave = [j for j in pending if refs_ready(j)] or pending  # last wave reports the missing refs
        with cf.ThreadPoolExecutor(a.par) as ex:
            for r in ex.map(go, wave):
                done[r["id"]] = r
        pending = [j for j in pending if j not in wave]
    rs = [done[j["id"]] for j in jobs]
    (out / "log.json").write_text(json.dumps({"job": job.get("job"), "done": sum(r["ok"] for r in rs),
                                              "failed": sum(not r["ok"] for r in rs), "results": rs}, indent=1), encoding="utf-8")
    print(f"\n{sum(r['ok'] for r in rs)}/{len(rs)} images in {out}")


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="mode", required=True)
    o = sub.add_parser("one", help="generate one image")
    o.add_argument("prompt")
    o.add_argument("--out", required=True)
    o.add_argument("--aspect", default="1:1", help="e.g. 1:1, 9:16, 16:9, 4:5")
    o.add_argument("--ref", action="append", default=[], help="reference image (repeat, max 5)")
    o.add_argument("--model", default=None, help="Codex chat model, e.g. the newest full model; default = Codex default")
    o.add_argument("--effort", default=None, help="low | medium | high")
    o.set_defaults(f=cmd_one)
    j = sub.add_parser("job", help="run a job file")
    j.add_argument("job")
    j.add_argument("--par", type=int, default=3, help="parallel runs (the account still makes one image at a time)")
    j.add_argument("--out", default=None)
    j.set_defaults(f=cmd_job)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
