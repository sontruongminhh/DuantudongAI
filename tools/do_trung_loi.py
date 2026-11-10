"""Đo độ trùng lời giữa kịch bản của mình và bản lời video đối thủ (tiếng Nhật).

Dùng khi làm lại chủ đề đối thủ đã nổ view: được trùng chủ đề và dữ kiện,
không được trùng câu chữ. Chạy trước khi đọc giọng.

    python tools/do_trung_loi.py runs/<run>/script.md research/doi_thu/*.txt

Cách đo: bỏ khoảng trắng và dấu câu, cắt thành cụm N ký tự liên tiếp, đếm tỷ lệ
cụm của mình có trong bản lời đối thủ. Ghép các cụm trùng liền nhau thành đoạn
trùng để người xem lại. Đoạn nằm trong 「」 được coi là trích tài liệu gốc.
Thoát mã 1 nếu không đạt.
"""
import re
import sys
import unicodedata
from pathlib import Path

N = 12                  # độ dài cụm (ký tự)
TY_LE_TOI_DA = 0.03     # tối đa 3% cụm trùng
DOAN_TOI_DA = 40        # đoạn trùng dài hơn mức này (ngoài 「」) thì không đạt
DOAN_BAO_CAO = 20       # đoạn trùng từ mức này trở lên thì liệt kê

_BO = re.compile(r"[\s　、。，．,.!?！？・…‥ー―\-「」『』（）()\[\]【】〈〉《》\"'“”‘’:：;；]")


def lam_sach(text):
    """Trả (chuỗi đã chuẩn hóa, vị trí gốc của từng ký tự)."""
    text = unicodedata.normalize("NFKC", text)
    out, pos = [], []
    for i, ch in enumerate(text):
        if not _BO.match(ch):
            out.append(ch)
            pos.append(i)
    return "".join(out), pos


def loi_doc(script):
    """Lấy phần lời đọc từ script.md: bỏ tiêu đề, ghi chú hình, nhãn [..] và ((..))."""
    lines = []
    for ln in script.splitlines():
        s = ln.strip()
        if not s or s.startswith("#") or s.startswith("[HÌNH") or s.startswith("(("):
            continue
        s = re.sub(r"^\[[A-Z_ ]+\]\s*", "", s)
        s = re.sub(r"\(\(.*?\)\)", "", s)
        lines.append(s)
    return "\n".join(lines)


def doc_vtt(text):
    """Phụ đề tự động YouTube (.vtt) → văn bản: bỏ mốc giờ, thẻ, và dòng lặp do phụ đề cuộn."""
    out, last = [], None
    for ln in text.splitlines():
        s = ln.strip()
        if not s or "-->" in s or s.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")):
            continue
        s = re.sub(r"<[^>]+>", "", s).strip()
        if s and s != last and s != "[音楽]":
            out.append(s)
            last = s
    # bỏ dòng là phần đầu của dòng kế tiếp (phụ đề cuộn hiện dần)
    return "\n".join(x for i, x in enumerate(out) if not (i + 1 < len(out) and out[i + 1].startswith(x)))


def doc_tep(path):
    text = Path(path).read_text(encoding="utf-8")
    return doc_vtt(text) if str(path).endswith(".vtt") else text


def vung_trich(text):
    """Các khoảng [a, b) nằm trong 「」 hoặc 『』 của văn bản gốc."""
    return [(m.start(), m.end()) for m in re.finditer(r"「[^」]*」|『[^』]*』", text)]


def do(cua_minh, doi_thu, n=N):
    a, pos = lam_sach(cua_minh)
    b, _ = lam_sach(doi_thu)
    if len(a) < n or len(b) < n:
        return {"ty_le": 0.0, "doan": [], "so_cum": 0}
    tap_b = {b[i:i + n] for i in range(len(b) - n + 1)}
    trich = vung_trich(cua_minh)

    def la_trich(i0, i1):
        g0, g1 = pos[i0], pos[i1 - 1] + 1
        return any(x <= g0 and g1 <= y for x, y in trich)

    trung = [a[i:i + n] in tap_b for i in range(len(a) - n + 1)]
    phu = [False] * len(a)
    for i, t in enumerate(trung):
        if t:
            for k in range(i, i + n):
                phu[k] = True
    # Tỷ lệ không tính cụm nằm trọn trong 「」 (trích tài liệu gốc)
    tinh = [t for i, t in enumerate(trung) if not la_trich(i, i + n)]
    doan, i = [], 0
    while i < len(a):
        if not phu[i]:
            i += 1
            continue
        j = i
        while j < len(a) and phu[j]:
            j += 1
        if j - i >= DOAN_BAO_CAO:
            doan.append({"dai": j - i, "chu": cua_minh[pos[i]:pos[j - 1] + 1], "trich": la_trich(i, j)})
        i = j
    return {"ty_le": sum(tinh) / max(len(tinh), 1), "doan": doan, "so_cum": len(trung)}


def dat(kq):
    if kq["ty_le"] > TY_LE_TOI_DA:
        return False
    return not any(d["dai"] > DOAN_TOI_DA and not d["trich"] for d in kq["doan"])


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    sys.stdout.reconfigure(encoding="utf-8")
    goc = Path(argv[0]).read_text(encoding="utf-8")
    cua_minh = loi_doc(goc) if argv[0].endswith(".md") else goc
    tat_ca_dat = True
    for p in argv[1:]:
        kq = do(cua_minh, doc_tep(p))
        ok = dat(kq)
        tat_ca_dat &= ok
        print(f"{'ĐẠT' if ok else 'KHÔNG ĐẠT'}  {Path(p).name}: trùng {kq['ty_le']:.1%} "
              f"(tối đa {TY_LE_TOI_DA:.0%}), {len(kq['doan'])} đoạn trùng ≥{DOAN_BAO_CAO} ký tự")
        for d in kq["doan"]:
            nhan = "trích" if d["trich"] else ("QUÁ DÀI" if d["dai"] > DOAN_TOI_DA else "xem lại")
            print(f"   [{nhan}, {d['dai']} ký tự] {d['chu']}")
    return 0 if tat_ca_dat else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
