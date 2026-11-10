r"""Đọc thử các câu có nhiều tên riêng khó nhất, để nghe cách đọc trước khi tạo giọng cả video.
Tốn một ít credit Genmax (mặc định 10 câu). Câu đã đọc thì giữ, chạy lại không tốn thêm.

Dùng: .venv\Scripts\python.exe tools\doc_thu.py runs\<run> [--so 10] [--phai 鶴吉 釜山 …]
Kết quả: runs\<run>\doc_thu\01.mp3 … và doc_thu\danh_sach.txt (câu gốc + câu gửi đi đọc).
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

from studio.core import load_engine, load_env  # noqa: E402

DONG = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")


def chon_cau(script, bang, so, phai=()):
    cau = []
    for line in script.splitlines():
        m = DONG.match(line.strip())
        if m:
            text = m.group(2).strip()
            khoa = {k for k in bang if k in text}
            if khoa:
                cau.append((len(khoa), text, khoa))
    # Ưu tiên câu nhiều tên khó; tên nào đã có trong câu đã chọn thì câu sau ít điểm hơn
    chon, da = [], set()
    for w in phai:  # tên bắt buộc nghe: lấy câu đầu tiên chứa tên đó
        c = next((c for c in cau if w in c[1] and c[1] not in chon), None)
        if c and w not in da:
            chon.append(c[1])
            da |= c[2]
    for _ in range(max(so - len(chon), 0)):
        cau.sort(key=lambda c: (len(c[2] - da), c[0]), reverse=True)
        if not cau or not (cau[0][2] - da):
            break
        n, text, khoa = cau.pop(0)
        chon.append(text)
        da |= khoa
    return chon, set(bang) - da


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--so", type=int, default=10)
    ap.add_argument("--phai", nargs="*", default=[], help="tên bắt buộc có trong câu đọc thử")
    a = ap.parse_args()
    run = Path(a.run)
    import yaml
    profile = yaml.safe_load((run / "profile.yaml").read_text(encoding="utf-8"))
    bang = json.loads((run / "cach_doc.json").read_text(encoding="utf-8"))
    cau, thieu = chon_cau((run / "script.md").read_text(encoding="utf-8"), bang, a.so, a.phai)
    load_env()
    engine = load_engine()
    client = engine.Genmax()
    g = profile["giong"]
    out = run / "doc_thu"
    out.mkdir(exist_ok=True)
    dong = []
    for i, text in enumerate(cau, 1):
        voice = engine.doc_theo_bang(text, bang)
        key = hashlib.sha1(json.dumps([g["voice_id"], g.get("toc_do"), voice]).encode()).hexdigest()[:10]
        mp3 = out / f"{i:02d}_{key}.mp3"
        if not mp3.exists():
            task = client.tts(voice, g["voice_id"], profile["kenh"]["ngon_ngu"], g["provider"], g.get("model_id"),
                              g.get("toc_do") or 1.0)
            client.download(task["result"]["audio_url"], mp3)
        dong.append(f"{mp3.name}\n  gốc : {text}\n  đọc : {voice}")
        print(f"[{i}/{len(cau)}] {mp3.name}")
    (out / "danh_sach.txt").write_text("\n\n".join(dong) + "\n", encoding="utf-8")
    print(f"Đã đọc {len(cau)} câu vào {out}")
    if thieu:
        print(f"{len(thieu)} tên trong cach_doc.json chưa có trong các câu đọc thử (tăng --so hoặc dùng --phai):",
              " ".join(sorted(thieu)[:30]))


if __name__ == "__main__":
    main()
