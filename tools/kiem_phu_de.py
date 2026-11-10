r"""Dò final.srt tìm dòng phụ đề bị cắt giữa từ (katakana, số, hán tự liền nhau ở hai dòng kề).
Dùng: .venv\Scripts\python.exe tools\kiem_phu_de.py runs\<run>"""
import re
import sys
from pathlib import Path

KATA = re.compile(r"[゠-ヿー]")
NHO = re.compile(r"[ンッーャュョァィゥェォ]")
SO = re.compile(r"[0-9０-９]")
HAN = re.compile(r"[一-鿿]")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    srt = Path(sys.argv[1]) / "render" / "final.srt"
    khoi = srt.read_text(encoding="utf-8-sig").strip().split("\n\n")
    T = [k.split("\n", 2)[2].replace("\n", "") for k in khoi if k.count("\n") >= 2]
    loi = []
    for a, c in zip(T, T[1:]):
        if not a or not c:
            continue
        if re.search(r"[0-9０-９][.．]$", a) and SO.match(c[0]):  # số thập phân bị cắt (1. | 5兆円)
            loi.append((a[-12:], c[:12]))
            continue
        if re.search(r"[。、」！？]$", a):
            continue
        if (KATA.match(a[-1]) and KATA.match(c[0])) or NHO.match(c[0]) or (SO.match(a[-1]) and re.match(r"[0-9０-９億万円年月%]", c[0])) \
                or (HAN.match(a[-1]) and HAN.match(c[0])):
            loi.append((a[-12:], c[:12]))
    for a, c in loi:
        print(f"  …{a} | {c}…")
    print(f"{len(T)} dòng phụ đề, {len(loi)} chỗ cắt giữa từ")
    print("Đạt." if not loi else "Sửa câu trong script.md (rút tên dài, thêm 「、」), rồi dựng lại.")


if __name__ == "__main__":
    main()
