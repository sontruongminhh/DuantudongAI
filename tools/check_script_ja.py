"""Kiểm tra kịch bản tiếng Nhật (script.md) theo runs/TIEU_CHI_KICH_BAN.md, phần đo được bằng máy.

  python tools/check_script_ja.py runs/<lan_chay>/script.md [--phut 16]

Đo theo ký tự, không theo từ. Giới hạn dòng lấy từ hồ sơ kênh (profile.yaml cạnh script.md) giống lệnh tach-loi.
Dữ kiện trong "## Bảng nguồn" được đối chiếu với nguon.md cạnh script.md nếu có.
"""
import argparse
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio import core, goi  # noqa: E402

CPS = 6.0                      # ký tự mỗi giây, hằng số "ja" của engine
SAGA = ("HOOK", "WORLD", "STRUGGLE", "CLIMAX", "LEGACY", "ECHO")
PACE = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")
PACE_CHARS = {"EPIC": (6, 26), "NARRATIVE": (18, None), "TENSION": (12, None)}
BANNED = ["衝撃", "驚愕", "絶句", "ヤバい", "必見", "信じられない", "この動画では", "チャンネル登録", "高評価", "こんにちは",
          "皆さん"]
QUESTION = re.compile(r"[？?]|か[。」]")
NUMBER = re.compile(r"[0-9０-９]+\s*(?:文|貫|里|町|km|キロ|軒|人|戸|年|日|泊|時間|倍|両|歳)"
                    r"|[一二三四五六七八九十百千万]+(?:文|貫|里|町|軒|人|年|日|泊|倍|両)")
GENERIC_ONE = {"一人", "一日", "一泊"}  # "一人", "一日" ... là cách nói thường, không phải số liệu
STRIP = re.compile(r"[\s、。！？!?「」『』（）()・…―ー,.]")
FACT = re.compile(r"F\d+")


def parse(md):
    """Danh sách chương; mỗi chương có beat gồm cue, sound và dòng lời đọc. Trả thêm các dòng sai mã nhịp."""
    if "## Kịch bản" not in md:
        return [], [], []
    body = md.split("## Kịch bản", 1)[1].split("## Bảng nguồn", 1)[0]
    chapters, stray, beat = [], [], None
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
            chapters[-1]["silences"] += s.startswith("((SILENCE")
        elif s.startswith("[HÌNH"):
            beat = {"cue": s, "lines": []}
            chapters[-1]["beats"].append(beat)
        elif PACE.match(s):
            if beat is None:
                beat = {"cue": None, "lines": []}
                chapters[-1]["beats"].append(beat)
            beat["lines"].append(PACE.match(s).groups())
        else:
            stray.append(s)
    sources = {}
    if "## Bảng nguồn" in md:
        for row in md.split("## Bảng nguồn", 1)[1].splitlines():
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if len(cells) >= 2 and FACT.search(cells[1]):
                sources[cells[0]] = FACT.findall(cells[1])
    return chapters, stray, sources


def facts_of(nguon_path):
    facts = {}
    if nguon_path.is_file():
        for raw in nguon_path.read_text("utf-8-sig").splitlines():
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if len(cells) >= 4 and FACT.fullmatch(cells[0]):
                facts[cells[0]] = cells[3].split()[0] if cells[3] else ""
    return facts


def check(md, limit, minutes=16, facts=None, banned=()):
    """Trả về (số liệu, lỗi, cảnh báo, các con số cần đối chiếu). banned: từ cấm thêm của hồ sơ kênh (tu_cam)."""
    chapters, stray, sources = parse(md)
    issues, warns = [], []
    lines = [(c["title"], k, t) for c in chapters for b in c["beats"] for k, t in b["lines"]]
    text = "".join(t for _, _, t in lines)
    chars = len(STRIP.sub("", text))
    sents = [s for s in re.split(r"(?<=[。！？])", text) if s.strip()]
    lens = sorted(len(STRIP.sub("", s)) for s in sents) or [0]
    stats = {"ky_tu": chars, "phut": chars / CPS / 60, "dong": len(lines), "cau": len(sents), "trung_vi_cau": statistics.median(lens)}
    if not chapters or not lines:
        return stats, ["Không thấy chương hoặc dòng lời đọc. Cần mục \"## Kịch bản\", chương \"### ...\" và dòng [NARRATIVE]/[TENSION]/[EPIC]"], [], []

    lo, hi = int(minutes * 60 * CPS * 0.88), int(minutes * 60 * CPS * 1.12)
    if not lo <= chars <= hi:
        issues.append(f"Số ký tự {chars} ngoài khoảng {lo}–{hi} (mục tiêu {minutes:g} phút, {CPS:g} ký tự/giây)")
    if not 20 <= stats["trung_vi_cau"] <= 48:
        warns.append(f"Trung vị câu {stats['trung_vi_cau']:g} ký tự, nên 20–48")

    labels = {w for c in chapters for w in re.split(r"[ ·:]", c["title"]) if w in SAGA}
    for s in SAGA:
        if s not in labels:
            issues.append(f"Thiếu phần Saga: {s}")
    for c in chapters:
        epic = sum(1 for b in c["beats"] for k, _ in b["lines"] if k == "EPIC")
        if epic > 2:
            issues.append(f"Chương \"{c['title']}\" có {epic} dòng EPIC (tối đa 2)")
        for b in c["beats"]:
            if not b["cue"]:
                issues.append(f"Beat thiếu [HÌNH:] ở chương \"{c['title']}\": {b['lines'][0][1][:24]}…")
    for title, k, t in lines:
        n = len(t)
        low, high = PACE_CHARS[k]
        high = high or limit
        if n > limit:
            issues.append(f"[{k}] {n} ký tự, vượt giới hạn {limit} của một cảnh: {t[:24]}…")
        elif not low <= n <= high:
            warns.append(f"[{k}] {n} ký tự (nên {low}–{high}): {t[:24]}…")
    for s in stray:
        issues.append(f"Dòng không có mã nhịp: {s[:40]}")

    for w in [*BANNED, *(str(b) for b in banned if b)]:
        if w in text:
            issues.append(f"Có từ không dùng: {w}")
    if not QUESTION.search(text[:int(60 * CPS)]):
        issues.append("Chưa có câu hỏi trong 60 giây đầu")
    if not QUESTION.search(text[-300:]):
        issues.append("Đoạn kết chưa có câu hỏi")

    if not sources:
        issues.append("Thiếu bảng \"## Bảng nguồn\" (cột 1: tên chương, cột 2: mã dữ kiện F..)")
    else:
        for c in chapters:
            if c["title"] not in sources:
                warns.append(f"Chương \"{c['title']}\" chưa có dòng trong bảng nguồn")
        for title, ids in sources.items():
            for fid in ids:
                grade = (facts or {}).get(fid)
                if facts and grade is None:
                    issues.append(f"Mã {fid} (chương \"{title}\") không có trong nguon.md")
                elif grade == "C":
                    issues.append(f"Mã {fid} (chương \"{title}\") mức C chưa kiểm chứng")
                elif grade == "B":
                    warns.append(f"Mã {fid} (chương \"{title}\") mức B, lời đọc phải nói \"theo ...\" hoặc \"có nơi\"")
    numbers = [(title, m.group(0)) for title, _, t in lines for m in NUMBER.finditer(t) if m.group(0) not in GENERIC_ONE]
    return stats, issues, warns, numbers


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("script", type=Path)
    ap.add_argument("--phut", type=float, default=16, help="độ dài mục tiêu (phút)")
    a = ap.parse_args()
    profile_path = a.script.parent / "profile.yaml"
    if not profile_path.is_file():
        sys.exit(f"Không thấy {profile_path}. Chạy trong thư mục lần chạy của studio.")
    profile = core.load_profile(profile_path)
    limit = goi.narration_budget(float(profile["clip"]["thoi_luong_giay"]), profile)
    facts = facts_of(a.script.parent / "nguon.md")
    stats, issues, warns, numbers = check(a.script.read_text("utf-8-sig"), limit, a.phut, facts,
                                          profile["noi_dung"].get("tu_cam") or [])
    print(f"Ký tự lời đọc: {stats['ky_tu']} → khoảng {stats['phut']:.1f} phút ở {CPS:g} ký tự/giây (chưa nghe giọng thật)")
    print(f"Dòng {stats['dong']} · câu {stats['cau']} · trung vị câu {stats['trung_vi_cau']:g} ký tự · giới hạn mỗi cảnh {limit} ký tự")
    for w in warns:
        print("  !", w)
    if numbers:
        print("\nCon số trong lời đọc, hãy đối chiếu với nguon.md:")
        for title, n in numbers:
            print(f"  {title}: {n}")
    print("\nKết quả:", "ĐẠT phần kiểm tra máy" if not issues else f"{len(issues)} lỗi")
    for i in issues:
        print("  ✗", i)
    print("\nPhần cần người duyệt: dữ kiện đúng nguồn, câu treo, giọng văn, chỗ nói rõ nguồn mức B.")
    return not issues


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
