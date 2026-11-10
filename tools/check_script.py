"""Kiểm tra kịch bản v2 theo QUY_TAC_KICH_BAN.md (phần đo được bằng máy).

  python tools/check_script.py videos/001_barentsz_1596/script.md
"""
import re
import statistics
import sys
from pathlib import Path

BANNED = ["bone-chilling", "spine-tingling", "delve", "unravel", "testament to", "tapestry", "realm",
          "buckle up", "in this video", "let's dive in", "mind-blowing", "you won't believe",
          "brilliant overlooked", "smash that like"]
WPM = 160
PACE = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")
PACE_WORDS = {"NARRATIVE": (8, 24), "TENSION": (3, 16), "EPIC": (2, 10)}
SAGA = ("HOOK", "WORLD", "STRUGGLE", "CLIMAX", "LEGACY", "ECHO")


def parse(md):
    """Trả về danh sách chương, mỗi chương gồm các beat; mỗi beat có cue, sound, lines."""
    body = md.split("## Kịch bản", 1)[1].split("## Bảng nguồn", 1)[0]
    chapters, stray = [], []
    beat = None
    for raw in body.splitlines():
        s = raw.strip()
        if s.startswith("### "):
            chapters.append({"title": s[4:], "beats": [], "silences": 0})
            beat = None
        elif not s:
            beat = None
        elif not chapters:
            continue
        elif s.startswith("(("):
            if s.startswith("((SILENCE"):
                chapters[-1]["silences"] += 1
            if beat is None:
                beat = {"cue": None, "sound": [], "lines": []}
                chapters[-1]["beats"].append(beat)
            beat["sound"].append(s)
        elif s.startswith("[HÌNH"):
            if beat is None or beat["cue"] or beat["lines"]:
                beat = {"cue": None, "sound": [], "lines": []}
                chapters[-1]["beats"].append(beat)
            beat["cue"] = s
        elif PACE.match(s):
            if beat is None:
                beat = {"cue": None, "sound": [], "lines": []}
                chapters[-1]["beats"].append(beat)
            beat["lines"].append(PACE.match(s).groups())
        else:
            stray.append(s)
    for c in chapters:  # bỏ các "beat" chỉ có nhạc đầu chương
        c["beats"] = [b for b in c["beats"] if b["lines"] or b["cue"]]
    return chapters, stray


def main(path):
    md = Path(path).read_text("utf-8")
    chapters, stray = parse(md)
    lines = [l for c in chapters for b in c["beats"] for l in b["lines"]]
    text = " ".join(t for _, t in lines)
    words = re.findall(r"[A-Za-z0-9'’-]+", text)
    sents = [s for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]
    lens = sorted(len(s.split()) for s in sents)
    counts = {p: sum(1 for k, _ in lines if k == p) for p in PACE_WORDS}
    issues = []

    print(f"Số từ lời đọc: {len(words)}  →  khoảng {len(words) / WPM:.1f} phút ở {WPM} từ/phút")
    print(f"Dòng lời đọc: {len(lines)} · NARRATIVE {counts['NARRATIVE']} · TENSION {counts['TENSION']} · EPIC {counts['EPIC']}")
    print(f"Câu: trung vị {statistics.median(lens)} từ · dài nhất {lens[-1]} từ · câu hỏi {sum(s.endswith('?') for s in sents)}")
    print("\nChương:")
    elapsed = 0
    for c in chapters:
        w = sum(len(t.split()) for b in c["beats"] for _, t in b["lines"])
        epic = sum(1 for b in c["beats"] for k, _ in b["lines"] if k == "EPIC")
        print(f"  {int(elapsed // 60)}:{int(elapsed % 60):02d}  {w:4} từ  {len(c['beats']):2} beat  EPIC {epic}  lặng {c['silences']}  {c['title']}")
        elapsed += w / WPM * 60
        if not c["title"].split(" ")[0] in SAGA:
            issues.append(f"Chương thiếu nhãn Saga: '{c['title']}'")
        if epic > 2:
            issues.append(f"Chương '{c['title']}' có {epic} dòng EPIC (tối đa 2)")
        if c["silences"] == 0 and not c["title"].startswith("HOOK"):
            issues.append(f"Chương '{c['title']}' chưa có khoảng lặng ((SILENCE))")
        for b in c["beats"]:
            if not b["cue"]:
                issues.append(f"Beat thiếu [HÌNH] ở chương '{c['title']}': {b['lines'][0][1][:50]}…")
            if not b["sound"]:
                issues.append(f"Beat thiếu tín hiệu âm thanh ở chương '{c['title']}': {(b['lines'] or [('', b['cue'])])[0][1][:50]}…")
    sagas = {c["title"].split(" · ")[0] for c in chapters} | {p for c in chapters for p in c["title"].split(" · ") if p in SAGA}
    missing = [s for s in SAGA if s not in sagas]
    if missing:
        issues.append(f"Thiếu phần Saga: {', '.join(missing)}")
    for k, t in lines:
        lo, hi = PACE_WORDS[k]
        if not lo <= len(t.split()) <= hi:
            print(f"  ! [{k}] {len(t.split())} từ (nên {lo}–{hi}): {t[:80]}")
    for s in stray:
        issues.append(f"Dòng không có mã nhịp: {s[:70]}")

    if not 3100 <= len(words) <= 3600:
        issues.append(f"Số từ {len(words)} ngoài khoảng 3.100–3.600")
    if not 9 <= statistics.median(lens) <= 14:
        issues.append(f"Trung vị câu {statistics.median(lens)} từ ngoài khoảng 9–14")
    for b in BANNED:
        if b in text.lower():
            issues.append(f"Có từ cấm: '{b}'")
    if "?" not in " ".join(text.split()[:WPM]):
        issues.append("Chưa có câu hỏi trong 60 giây đầu")
    if not re.search(r"would you", text[-400:], re.I):
        issues.append("Đoạn kết thiếu câu hỏi 'Would you…?'")

    print("\nKết quả:", "ĐẠT phần kiểm tra máy" if not issues else f"{len(issues)} lỗi")
    for i in issues:
        print("  ✗", i)
    print("\nPhần cần người duyệt: mục 12 trong QUY_TAC_KICH_BAN.md (sự thật, câu treo, giọng văn).")
    return not issues


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1]) else 1)
