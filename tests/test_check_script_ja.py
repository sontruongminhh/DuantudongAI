"""Kiểm thử công cụ kiểm tra kịch bản tiếng Nhật."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import check_script_ja as cs  # noqa: E402

LIMIT = 50
Q_OPEN = "旅籠に一泊すると、いくらかかったのでしょうか。"
Q_END = "あなたなら、どちらの宿を選びますか。"
FILL = "旅人は日が暮れる前に次の宿場へ着こうと、ゆっくりと歩いていました。"


def chapter(label, lines, silence=True):
    out = f"### {label}\n[HÌNH: bản đồ tuyến]\n" + ("((SILENCE 1s))\n" if silence else "")
    return out + "".join(f"[{k}] {t}\n" for k, t in lines) + "\n"


def good_script(reps=1):
    body = "# Kịch bản\n\n## Kịch bản\n\n"
    labels = ["HOOK · Chương 1", "WORLD · Chương 2", "STRUGGLE · Chương 3", "CLIMAX · Chương 4", "LEGACY · Chương 5",
              "ECHO · Chương 6"]
    for i, label in enumerate(labels):
        lines = [("NARRATIVE", FILL)] * reps
        if i == 0:
            lines = [("TENSION", Q_OPEN)] + lines
        if i == 5:
            lines = lines + [("TENSION", Q_END)]
        body += chapter(label, lines)
    body += "## Bảng nguồn\n\n| Chương | Dữ kiện |\n|---|---|\n"
    body += "".join(f"| {label} | F01 |\n" for label in labels)
    return body


def run(md, minutes=1, facts=None):
    return cs.check(md, LIMIT, minutes, facts or {"F01": "A"})


def test_parse_counts_chapters_and_sources():
    chapters, stray, sources = cs.parse(good_script())
    assert len(chapters) == 6 and stray == [] and sources["HOOK · Chương 1"] == ["F01"]


def test_good_script_has_no_issues_when_length_matches():
    md = good_script(reps=2)
    chars = run(md)[0]["ky_tu"]
    assert chars > 0
    _, issues, _, _ = run(md, minutes=chars / cs.CPS / 60)
    assert issues == []


def test_length_out_of_range_is_an_issue():
    _, issues, _, _ = run(good_script(reps=1), minutes=16)
    assert any("Số ký tự" in i for i in issues)


def test_missing_saga_and_question_checks():
    md = good_script().replace("ECHO · Chương 6", "KẾT · Chương 6").replace(Q_END, FILL).replace(Q_OPEN, FILL)
    _, issues, _, _ = run(md)
    assert any("Thiếu phần Saga: ECHO" in i for i in issues)
    assert any("60 giây đầu" in i for i in issues) and any("Đoạn kết chưa có câu hỏi" in i for i in issues)


def test_banned_phrases_and_overlong_line():
    md = good_script().replace(FILL, "衝撃の" + FILL + "あ" * LIMIT, 1)
    _, issues, _, _ = run(md)
    assert any("衝撃" in i for i in issues) and any("vượt giới hạn" in i for i in issues)


def test_profile_banned_words_are_checked():
    md = good_script().replace(FILL, "夜這いの話をします。" + FILL, 1)
    assert not any("夜這い" in i for i in run(md)[1])
    _, issues, _, _ = cs.check(md, LIMIT, 1, {"F01": "A"}, banned=["夜這い"])
    assert any("夜這い" in i for i in issues)


def test_epic_limit_per_chapter():
    md = good_script(reps=3).replace("[NARRATIVE]", "[EPIC]", 3)  # ba dòng đầu cùng nằm trong chương 1
    _, issues, _, _ = run(md)
    assert any("3 dòng EPIC" in i for i in issues)
    _, issues, _, _ = run(good_script(reps=3).replace("[NARRATIVE]", "[EPIC]", 2))
    assert not any("EPIC" in i for i in issues)


def test_missing_cue_is_an_issue():
    md = good_script().replace("### WORLD · Chương 2\n[HÌNH: bản đồ tuyến]\n", "### WORLD · Chương 2\n")
    _, issues, _, _ = run(md)
    assert any("Beat thiếu [HÌNH:]" in i and "WORLD" in i for i in issues)


def test_stray_line_without_pace_code():
    md = good_script().replace("[NARRATIVE] " + FILL, FILL, 1)
    _, issues, _, _ = run(md)
    assert any("không có mã nhịp" in i for i in issues)


def test_sources_checked_against_grades():
    _, issues, warns, _ = run(good_script(), facts={"F01": "C"})
    assert any("mức C" in i for i in issues)
    _, issues, warns, _ = run(good_script(), facts={"F01": "B"})
    assert not any("mức C" in i for i in issues) and any("mức B" in w for w in warns)
    _, issues, _, _ = run(good_script(), facts={"F02": "A"})
    assert any("không có trong nguon.md" in i for i in issues)
    _, issues, _, _ = run(good_script().split("## Bảng nguồn")[0])
    assert any("Bảng nguồn" in i for i in issues)


def test_numbers_are_listed_for_review():
    md = good_script().replace(FILL, "宿代は一泊二百文ほどで、三十軒の宿が並んでいました。", 1)
    _, _, _, numbers = run(md)
    assert any("文" in n for _, n in numbers) and any("軒" in n for _, n in numbers)


def test_numbers_skip_everyday_one_and_catch_kan():
    md = good_script().replace(FILL, "一日に一人で、四貫五百文を使いました。", 1)
    _, _, _, numbers = run(md)
    listed = [n for _, n in numbers]
    assert "一日" not in listed and "一人" not in listed
    assert any("貫" in n for n in listed) and any("五百文" in n or "四貫" in n for n in listed)


def test_empty_script_reports_structure_problem():
    _, issues, _, _ = run("何もない")
    assert issues and "## Kịch bản" in issues[0]
