"""Kiểm âm thanh video cuối: độ to tổng, mức nhạc ở khoảng lặng giữa lời, và tiếng ở câu cuối.

  python tools/kiem_am_thanh.py runs/<run>

Bắt hai lỗi gặp ở video リッカー mà kiem-tra-video không bắt: nhạc quá nhỏ (-49 dB), câu cuối mất tiếng.
Đạt khi: tổng khoảng -14 LUFS, nhạc ở khoảng lặng từ -36 đến -24 dB, mọi đoạn lời (kiểm 5 đoạn cuối và 5 đoạn ngẫu nhiên) có tiếng.
"""
import json
import random
import re
import subprocess
import sys
from pathlib import Path


def mean_db(video, start, dur):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", str(video), "-vn",
                        "-af", "volumedetect", "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    m = re.search(r"mean_volume: (-?[\d.]+) dB", r.stderr)
    return float(m.group(1)) if m else -99.0


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run = Path(sys.argv[1])
    video = run / "render" / "final.mp4"
    t = json.loads((run / "render" / "timeline.json").read_text("utf-8"))
    segs = t["doan_loi"]
    ok = True
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(video), "-vn", "-af", "ebur128", "-f", "null", "-"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    lufs = float(re.findall(r"I:\s+(-?[\d.]+) LUFS", r.stderr)[-1])
    print(f"Độ to tổng: {lufs:.1f} LUFS (nhắm -14)")
    ok &= -15.5 <= lufs <= -12.5
    gaps = sorted(((segs[i + 1]["voice_start"] - (segs[i]["voice_start"] + segs[i]["audio_dur"]), segs[i]["voice_start"] + segs[i]["audio_dur"])
                   for i in range(len(segs) - 1)), reverse=True)[:5]
    levels = [mean_db(video, s + 0.15, g - 0.3) for g, s in gaps if g > 0.6]
    if levels:
        med = sorted(levels)[len(levels) // 2]
        print(f"Nhạc ở khoảng lặng: {med:.1f} dB (nhắm -36 đến -24)")
        ok &= -36 <= med <= -24
    else:
        print("Không có khoảng lặng đủ dài để đo nhạc")
    random.seed(1)
    pick = segs[-5:] + random.sample(segs[:-5], min(5, len(segs) - 5))
    mute = [s for s in pick if mean_db(video, s["voice_start"] + 0.2, max(s["audio_dur"] - 0.4, 0.5)) < -35]
    for s in mute:
        print(f"MẤT TIẾNG ở {s['voice_start']:.1f}s: {s['text'][:30]}")
    ok &= not mute
    print("Đạt." if ok else "KHÔNG ĐẠT.")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
