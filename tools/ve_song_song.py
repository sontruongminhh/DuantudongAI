"""Render các cảnh motion song song (thay cho ve-canh chạy lần lượt). Cảnh đã có clip thì bỏ qua.

  python tools/ve_song_song.py runs/<run> [--so-luong 8] [--lam-lai S001 S002 ...]

Sau đó vẫn chạy `python -m studio nhan-clip <run> runs/<run>/motion/out` như quy trình.
"""
import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HF = "hyperframes@0.8.231"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--so-luong", type=int, default=8)
    ap.add_argument("--lam-lai", nargs="*", default=[], help="render lại các cảnh này dù đã có clip")
    ap.add_argument("--chi", nargs="*", default=None, help="chỉ render các cảnh này (xem thử), luôn render lại")
    a = ap.parse_args()
    run = Path(a.run).resolve()
    proj = run / "motion" / "du_an"
    out = run / "motion" / "out"
    out.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs" + os.pathsep + env.get("PATH", "")
    npx = shutil.which("npx.cmd", path=env["PATH"]) or "npx"
    pages = sorted((proj / "scenes").glob("S*.html"))
    if a.chi is not None:
        pages = [p for p in pages if p.stem in set(a.chi)]
        a.lam_lai = a.chi
    todo = [p.stem for p in pages if p.stem in a.lam_lai or not (out / f"{p.stem}.mp4").is_file()]
    print(f"{len(pages)} cảnh, cần render {len(todo)}")

    def one(sid):
        target = out / f"{sid}.mp4"
        r = subprocess.run([npx, "--yes", HF, "render", "-c", f"scenes/{sid}.html", "-o", str(target), "--fps", "24"],
                           cwd=proj, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        ok = r.returncode == 0 and target.is_file()
        return sid, ok, "" if ok else "\n".join((r.stderr or r.stdout).strip().splitlines()[-4:])

    fails = []
    with ThreadPoolExecutor(a.so_luong) as ex:
        for i, f in enumerate(as_completed([ex.submit(one, s) for s in todo]), 1):
            sid, ok, err = f.result()
            if not ok:
                fails.append(sid)
                print("LỖI", sid, err)
            if i % 20 == 0:
                print(f"  {i}/{len(todo)}")
    print("xong" if not fails else f"{len(fails)} cảnh lỗi: {' '.join(fails)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
