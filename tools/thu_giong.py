"""Nghe thử giọng: tạo mẫu đọc qua Genmax (tốn ít credit) rồi đo cao độ F0 và tốc độ đọc.

  python tools/thu_giong.py <thu_muc_ra> <voice_id>:<ten> [<voice_id>:<ten> ...] [--toc-do 1.0]
  python tools/thu_giong.py <thu_muc_ra> --chi-do      (chỉ đo lại các tệp .mp3 đã có)

Đo F0 bằng tự tương quan trên khung 46 ms, dải 70–400 Hz, như cách đo giọng kênh mẫu trong trình duyệt.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MAU = ("1936年、鐘紡は民間の会社として日本でいちばん多くを売り上げました。今の物価に直すと、およそ2300億円です。"
       "ところが、それからおよそ70年後の2007年、カネボウという会社は姿を消します。なぜ、消えてしまったのでしょうか。")


def doc_wav(path, sr=16000):
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", str(path), "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768, sr


def do_f0(x, sr):
    n = 2048
    vals, speech = [], 0
    for i in range(0, len(x) - n, n // 2):
        f = x[i:i + n]
        if np.sqrt((f ** 2).mean()) < 0.02:
            continue
        speech += 1
        f = f - f.mean()
        ac = np.correlate(f, f, "full")[n - 1:]
        lo, hi = sr // 400, sr // 70
        lag = lo + int(np.argmax(ac[lo:hi]))
        if ac[lag] / (ac[0] + 1e-9) > 0.6:
            vals.append(sr / lag)
    v = np.array(vals)
    return {"p25": round(float(np.percentile(v, 25)), 1), "trung_vi": round(float(np.median(v)), 1),
            "p75": round(float(np.percentile(v, 75)), 1), "giay_noi": round(speech * (n // 2) / sr, 2)} if len(v) else {}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("giong", nargs="*")
    ap.add_argument("--toc-do", type=float, default=1.0)
    ap.add_argument("--chi-do", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if not a.chi_do:
        from studio.core import load_env
        load_env()
        from engine.genmax import Genmax
        g = Genmax()
        for item in a.giong:
            vid, name = item.split(":", 1)
            h = g.tts(MAU, vid, "ja", provider="minimax", model_id="speech-2.8-hd", speed=a.toc_do)
            g.download(h["result"]["audio_url"], out / f"{name}.mp3")
            print("tạo", name)
    res = {}
    for mp3 in sorted(out.glob("*.mp3")):
        x, sr = doc_wav(mp3)
        dur = len(x) / sr
        f0 = do_f0(x, sr)
        res[mp3.stem] = {**f0, "giay": round(dur, 2), "ky_tu_moi_giay": round(len(MAU) / dur, 2)}
        print(f"{mp3.stem:24s} F0 {f0.get('p25')}–{f0.get('trung_vi')}–{f0.get('p75')} Hz, {dur:.1f} giây, "
              f"{len(MAU) / dur:.2f} ký tự/giây")
    (out / "ket_qua.json").write_text(json.dumps({"mau": MAU, "toc_do": a.toc_do, "ket_qua": res}, ensure_ascii=False, indent=2),
                                      encoding="utf-8")


if __name__ == "__main__":
    main()
