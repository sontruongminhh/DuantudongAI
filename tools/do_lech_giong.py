r"""Đo hình và giọng có khớp không sau khi dựng: giọng bắt đầu trễ bao nhiêu so với cảnh của nó, và cảnh nào đổi hình
trước khi giọng đọc xong. Đọc runs\<run>\render\timeline.json, không gọi Genmax.

  .venv\Scripts\python.exe tools\do_lech_giong.py runs\<run> [runs\<run2> …]

Đạt khi không cảnh nào đổi hình trước khi giọng dứt (cho phép 0,2 giây). Xem BAI_HOC.md video 10, lỗi 1.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
CHO_PHEP = 0.2


def do(run):
    t = json.loads((Path(run) / "render" / "timeline.json").read_text(encoding="utf-8"))
    clips, segs = t["clips"], t.get("doan_loi", [])
    tre, som = [], []
    for s in segs:
        if "voice_start" not in s:
            continue
        dau, cuoi = clips[s["clips"][0] - 1], clips[s["clips"][1] - 1]
        tre.append(s["voice_start"] - dau["bat_dau"])
        tran = s["voice_start"] + s["audio_dur"] - (cuoi["bat_dau"] + cuoi["thoi_luong"])
        if tran > CHO_PHEP:
            som.append((cuoi["file"], round(tran, 2)))
    return sorted(tre), som, len(segs)


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    loi = False
    for run in sys.argv[1:]:
        tre, som, n = do(run)
        if not tre:
            print(f"{run}: timeline.json không có voice_start")
            continue
        print(f"{run}: giọng trễ hình trung vị {tre[len(tre) // 2]:.2f}s, lớn nhất {tre[-1]:.2f}s; "
              f"cảnh đổi hình trước khi giọng dứt {len(som)}/{n}")
        for f, x in som[:10]:
            print(f"   {f}: giọng còn {x}s sau khi hết cảnh")
        loi = loi or bool(som)
    print("Không đạt." if loi else "Đạt.")
    sys.exit(1 if loi else 0)


if __name__ == "__main__":
    main()
