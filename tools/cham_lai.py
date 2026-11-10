r"""Chấm lại kịch bản bằng máy (bước 3b, người điều phối), không tin bảng tự chấm.

Dùng: .venv\Scripts\python.exe tools\cham_lai.py runs\<run>\script.md
Đạt khi: câu rào đón < 20% và không quá 2 câu liền; không nói 「ウィキペディア」; 「百科事典」 ≤ 3;
không quá 2 câu liền cùng đuôi; ≥ 6 câu nói trong 「」; không có từ cấm (衝撃, 驚愕, ヤバい, 皆さん, チャンネル登録).
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
DONG = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")
RAO = re.compile(r"とされ|によると|によれば|と伝えられ|といわれ|と言われ|という記録|説が|諸説")
CAM = ["衝撃", "驚愕", "ヤバい", "皆さん", "チャンネル登録"]


def cau_cua(script):
    cau = []
    for line in script.splitlines():
        m = DONG.match(line.strip())
        if m:
            cau += [c + "。" for c in re.split(r"。", m.group(2).strip()) if c.strip()]
    return cau


def duoi(c):
    c = re.sub(r"[。」]+$", "", c)
    return c[-3:]


def chuoi_dai(flags):
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def main():
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    cau = cau_cua(text)
    loi = "".join(cau)
    rao = [bool(RAO.search(c)) for c in cau]
    ty_le = sum(rao) / len(cau) if cau else 0
    # chuỗi cùng đuôi
    d, run_d, max_d, vi_du = None, 0, 0, ""
    for c in cau:
        e = duoi(c)
        run_d = run_d + 1 if e == d else 1
        d = e
        if run_d > max_d:
            max_d, vi_du = run_d, e
    trich = len(re.findall(r"「[^」]{6,}」", loi))
    dem = {
        "Câu": len(cau),
        "Câu rào đón": f"{sum(rao)} ({ty_le:.0%}), chuỗi dài nhất {chuoi_dai(rao)}",
        "ウィキペディア": loi.count("ウィキペディア") + loi.count("Wikipedia"),
        "百科事典": loi.count("百科事典"),
        "Cùng đuôi liền nhau": f"{max_d} (…{vi_du})",
        "Câu nói / trích trong 「」 (≥6 ký tự)": trich,
        # 「看板を下ろした日」 là tên kênh mẫu: không dùng dấu ấn riêng của kênh khác
        "Từ cấm": [w for w in CAM if w in loi] + re.findall(r"看板[^。]{0,6}下ろ", loi),
    }
    for k, v in dem.items():
        print(f"{k}: {v}")
    loi_ = []
    if ty_le >= 0.20 or chuoi_dai(rao) > 2:
        loi_.append("rào đón")
    if dem["ウィキペディア"]:
        loi_.append("nói Wikipedia")
    if dem["百科事典"] > 3:
        loi_.append("百科事典 > 3")
    if max_d > 2:
        loi_.append("cùng đuôi > 2")
    if trich < 6:
        loi_.append("ít câu nói thật")
    if dem["Từ cấm"]:
        loi_.append("từ cấm")
    # in vị trí chuỗi rào đón dài
    run = []
    for c, f in zip(cau, rao):
        run = run + [c] if f else []
        if len(run) == 3:
            print("  Chuỗi rào đón:", " / ".join(x[:30] for x in run))
    print("ĐẠT." if not loi_ else "CHƯA ĐẠT: " + ", ".join(loi_))
    sys.exit(1 if loi_ else 0)


if __name__ == "__main__":
    main()
