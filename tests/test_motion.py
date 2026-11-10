"""Kiểm thử bước motion. Không gọi Genmax, YouTube hay HyperFrames thật."""
import shutil
import subprocess
from types import SimpleNamespace

import pytest
import yaml

from studio import bao_cao, core, goi, mau_motion, motion
from studio.core import StudioError, read_json, write_json
from test_studio import good_profile

NGUON = """# Nguồn

| Mã | Dữ kiện | Nguồn | Tin cậy | Ghi chú |
|---|---|---|---|---|
| F01 | Dữ kiện A | S1 | A | |
| F02 | Dữ kiện B | S2 | B | |
| F03 | Dữ kiện C | S3 | C | |
"""


def script(lines_per_chapter=2, size=20):
    text = "# Kịch bản\n\n## Kịch bản\n\n"
    n = 0
    for ch in ("HOOK · Chương 1", "WORLD · Chương 2"):
        text += f"### {ch}\n[HÌNH: bản đồ tuyến]\n((gió nhẹ))\n"
        for _ in range(lines_per_chapter):
            n += 1
            text += f"[NARRATIVE] {'あ' * (size - 1)}{n % 10}\n"
        text += "\n"
    return text + "## Bảng nguồn\n"


@pytest.fixture
def mrun(tmp_path):
    p = good_profile()
    p["kenh"]["ngon_ngu"] = "ja"
    p["clip"].update(do_phan_giai=[1280, 720], nguon="motion")
    p["dung"]["fps"] = 24
    p["noi_dung"].update(do_dai_phut=0.5, tu_cam=["夜這い"])
    p["quy_trinh"] = {"bo_duyet": True}
    channel = tmp_path / "channels" / "thu"
    channel.mkdir(parents=True)
    (channel / "profile.yaml").write_text(yaml.safe_dump(p, allow_unicode=True), encoding="utf-8")
    r = core.create_run(channel, tmp_path / "runs", "thu motion")
    text = "\n".join(f"## {h}\nNội dung" for h in core.brief_sections(r))
    (r.dir / "brief.md").write_text(text, encoding="utf-8")
    (r.dir / "nguon.md").write_text(NGUON, encoding="utf-8")
    return r


def scene(i, template, data, **kw):
    return {"id": f"S{i:03d}", "chuong": "HOOK", "narration": kw.pop("narration", "あいうえお"), "template": template,
            "nguon": kw.pop("nguon", []), "data": data, **kw}


HOOK = {"kicker": "江戸の旅", "line1": "旅籠に泊まると、", "hl": "いくら", "line2": "かかった？"}
LEDGER = {"title": "費用", "sub": "並べる", "rows": [["宿代", 200], ["昼食", 75]], "total_label": "合計"}
COMPARE = {"title": "ちがい", "sub": "食事", "left": {"name": "旅籠", "ruby": "はたご", "items": ["夕食つき"]},
           "right": {"name": "木賃宿", "ruby": "きちんやど", "items": ["自炊"]}}


def write_canh(run, scenes):
    (run.dir / "motion").mkdir(exist_ok=True)
    write_json(run.dir / "motion" / "canh.json", {"canh": scenes})


# ---------------------------------------------------------------- tách lời

def test_parse_script_gets_chapter_cue_and_pace():
    lines = motion.parse_script(script())
    assert len(lines) == 4
    assert lines[0]["chuong"] == "HOOK · Chương 1" and lines[0]["cue"] == "bản đồ tuyến" and lines[0]["pace"] == "NARRATIVE"
    assert lines[2]["id"].startswith("c01_b01")


def test_parse_script_needs_section():
    with pytest.raises(StudioError, match="Kịch bản"):
        motion.parse_script("không có mục")


def test_tach_loi_groups_by_budget_and_chapter(mrun):
    limit = goi.narration_budget(10, mrun.profile)
    size = limit // 2  # hai dòng vừa một cảnh
    (mrun.dir / "script.md").write_text(script(2, size), encoding="utf-8")
    n, wrote = motion.tach_loi(mrun)
    data = read_json(mrun.dir / "motion" / "dong_loi.json")
    assert n == 2 and wrote
    assert all(s["so_ky_tu"] <= limit for s in data["canh"])
    assert [s["id"] for s in data["canh"]] == ["S001", "S002"]
    assert data["canh"][0]["goi_y_hinh"] == ["bản đồ tuyến"]
    skeleton = read_json(mrun.dir / "motion" / "canh.json")["canh"]
    assert skeleton[0]["template"] is None and skeleton[0]["narration"]


def test_tach_loi_never_mixes_two_beats_and_holds_the_image(mrun):
    line = "[NARRATIVE] あいうえおかきくけこさしすせそたち"
    text = "\n".join(["# Kịch bản", "", "## Kịch bản", "", "### HOOK · Chương 1", "[HÌNH: ban_do | a]", line, line,
                      "[HÌNH: ledger | b]", line, "## Bảng nguồn", ""])
    (mrun.dir / "script.md").write_text(text, encoding="utf-8")
    limit = goi.narration_budget(10, mrun.profile)
    assert limit >= 36                      # hai dòng đầu vừa một cảnh, nhưng không được gộp với dòng của beat sau
    assert motion.tach_loi(mrun)[0] == 2
    scenes = read_json(mrun.dir / "motion" / "dong_loi.json")["canh"]
    assert [s["goi_y_hinh"] for s in scenes] == [["ban_do | a"], ["ledger | b"]]
    assert [s["giu_hinh"] for s in scenes] == [False, False]


def test_tach_loi_marks_continuation_scenes_of_one_beat_as_held(mrun):
    limit = goi.narration_budget(10, mrun.profile)
    line = "[NARRATIVE] " + "あ" * (limit - 2)
    text = "\n".join(["# Kịch bản", "", "## Kịch bản", "", "### HOOK · Chương 1", "[HÌNH: ban_do | a]", line, line, line,
                      "## Bảng nguồn", ""])
    (mrun.dir / "script.md").write_text(text, encoding="utf-8")
    assert motion.tach_loi(mrun)[0] == 3
    assert [s["giu_hinh"] for s in read_json(mrun.dir / "motion" / "canh.json")["canh"]] == [False, True, True]


def test_hold_scene_locks_the_timeline_at_the_end():
    held = mau_motion.build({**scene(1, "ledger", LEDGER), "giu_hinh": True})
    assert "tl.seek=f" in held and "tl.seek=f" not in mau_motion.build(scene(1, "ledger", LEDGER))


def test_tach_loi_splits_when_lines_do_not_fit(mrun):
    limit = goi.narration_budget(10, mrun.profile)
    (mrun.dir / "script.md").write_text(script(2, limit - 2), encoding="utf-8")
    assert motion.tach_loi(mrun)[0] == 4


def test_tach_loi_rejects_line_longer_than_scene(mrun):
    limit = goi.narration_budget(10, mrun.profile)
    (mrun.dir / "script.md").write_text(script(1, limit + 5), encoding="utf-8")
    with pytest.raises(StudioError, match="dài hơn giới hạn"):
        motion.tach_loi(mrun)


def test_tach_loi_keeps_filled_canh_unless_overwrite(mrun):
    (mrun.dir / "script.md").write_text(script(2, 10), encoding="utf-8")
    write_canh(mrun, [scene(1, "hook", HOOK)])
    assert motion.tach_loi(mrun)[1] is False
    assert read_json(mrun.dir / "motion" / "canh.json")["canh"][0]["template"] == "hook"
    assert motion.tach_loi(mrun, ghi_de=True)[1] is True
    assert read_json(mrun.dir / "motion" / "canh.json")["canh"][0]["template"] is None


# ---------------------------------------------------------------- kiểm tra dữ liệu cảnh

def test_check_scene_validates_template_and_fields():
    assert mau_motion.check_scene(scene(1, "hook", HOOK)) == []
    assert "không có" in mau_motion.check_scene(scene(1, "không-có", {}))[0]
    assert any("line2" in e for e in mau_motion.check_scene(scene(1, "hook", {**HOOK, "line2": ""})))
    assert mau_motion.check_scene(scene(1, "ledger", {**LEDGER, "rows": [["a", -1]]}))
    assert mau_motion.check_scene(scene(1, "route", {"title": "t", "sub": "s", "from": "a", "to": "b", "count": 1,
                                                     "count_label": "c"}))
    assert mau_motion.check_scene(scene(1, "day", {"title": "t", "sub": "s", "stops": [["a", "b"]] * 3}))
    assert mau_motion.check_scene(scene(1, "plan", {"title": "t", "sub": "s", "rooms": [["a", 1, 2]]}))
    assert mau_motion.check_scene(scene(1, "compare", {**COMPARE, "left": {"name": "x"}}))


def test_check_scene_blocks_text_that_would_overflow():
    assert any("line1" in e for e in mau_motion.check_scene(scene(1, "hook", {**HOOK, "line1": "あ" * 11})))
    assert mau_motion.check_scene(scene(1, "ledger", {**LEDGER, "rows": [["あ" * 10, 5]]}))
    assert mau_motion.check_scene(scene(1, "hook", {**HOOK, "kicker": "あ" * 25}))
    # chữ số latin hẹp hơn chữ Nhật nên nhãn có số vẫn vừa
    assert mau_motion.check_scene(scene(1, "ledger", {**LEDGER, "rows": [["昼食（70〜80文）", 5]]})) == []
    day = {"title": "t", "sub": "s", "stops": [["朝", "あ" * 11], ["昼", "x"], ["夕", "y"], ["夜", "z"]]}
    assert any("mốc" in e for e in mau_motion.check_scene(scene(1, "day", day)))
    wide = {**COMPARE, "left": {**COMPARE["left"], "items": ["あ" * 15]}}
    assert any("tối đa 14" in e for e in mau_motion.check_scene(scene(1, "compare", wide)))


def test_check_scenes_requires_source_for_data_templates(mrun):
    write_canh(mrun, [scene(1, "hook", HOOK), scene(2, "ledger", LEDGER)])
    errors, _ = motion.check_scenes(mrun)
    assert any("S002" in e and "mã nguồn" in e for e in errors)
    assert not any("S001" in e for e in errors)


def test_check_scenes_source_grades(mrun):
    write_canh(mrun, [scene(1, "ledger", LEDGER, nguon=["F01"]), scene(2, "ledger", LEDGER, nguon=["F02"]),
                      scene(3, "ledger", LEDGER, nguon=["F03"]), scene(4, "ledger", LEDGER, nguon=["F99"])])
    errors, warnings = motion.check_scenes(mrun)
    assert not any("S001" in e for e in errors)
    assert any("S002" in w and "mức B" in w for w in warnings)
    assert any("S003" in e and "mức C" in e for e in errors)
    assert any("S004" in e and "F99" in e for e in errors)


def test_check_scenes_test_data_is_warned_not_blocked(mrun):
    write_canh(mrun, [scene(1, "ledger", LEDGER, thu=True)])
    errors, warnings = motion.check_scenes(mrun)
    assert errors == [] and any("thử" in w for w in warnings)


def test_check_scenes_banned_word_ids_and_budget(mrun):
    limit = goi.narration_budget(10, mrun.profile)
    write_canh(mrun, [scene(1, "hook", HOOK, narration="夜這いの話"), scene(3, "hook", HOOK, narration="あ" * (limit + 1))])
    errors, _ = motion.check_scenes(mrun)
    assert any("từ cấm" in e for e in errors)
    assert any("id phải là S002" in e for e in errors)
    assert any("vượt giới hạn" in e for e in errors)


def test_check_scenes_without_file(mrun):
    assert "tach-loi" in motion.check_scenes(mrun)[0][0]


# ---------------------------------------------------------------- nạp vào scenes.json

def test_nap_motion_writes_scenes_that_pass_package_check(mrun):
    write_canh(mrun, [scene(1, "hook", HOOK, narration="旅籠に泊まると、いくらかかったのでしょうか。"),
                      scene(2, "compare", COMPARE, nguon=["F01"], narration="旅籠は食事つきでした。")])
    n, warnings = motion.nap_motion(mrun)
    scenes = read_json(mrun.dir / "scenes.json")["canh"]
    assert n == 2 and [s["id"] for s in scenes] == ["S001", "S002"]
    assert scenes[1]["template"] == "compare" and scenes[1]["nguon"] == ["F01"] and scenes[0]["planned_sec"] == 10
    errors, _ = goi.check_package(mrun)
    assert errors == []


def test_scene_seconds_is_fixed_unless_profile_asks_for_variable(mrun):
    assert motion.scene_seconds("あ" * 20, mrun.profile) == 10
    profile = mrun.profile
    profile["clip"]["thoi_luong_thay_doi"] = True
    # ja: 6 ký tự mỗi giây. 30 ký tự = 5 giây, cộng 0,25 + 0,35 + 0,4 giây lặng = 6 giây
    assert motion.scene_seconds("あ" * 30, profile) == 6.0
    assert motion.scene_seconds("あ" * 2, profile) == 3.0          # không ngắn hơn 3 giây
    assert motion.scene_seconds("あ" * 200, profile) == 10         # không dài hơn clip.thoi_luong_giay
    profile["clip"]["thoi_luong_toi_thieu"] = 4
    assert motion.scene_seconds("あ" * 2, profile) == 4.0
    # tốc độ đo được từ giọng thật thay cho ước lượng 6 ký tự mỗi giây: 30 / 5 + 1 = 7 giây
    profile["giong"]["ky_tu_moi_giay"] = 5
    assert motion.scene_seconds("あ" * 30, profile) == 7.0
    # câu đã có giọng thật: lấy độ dài giọng + 1 giây lặng + 0,2 giây dư, không theo số ký tự
    voice = {"あ" * 30: 7.0}
    assert motion.scene_seconds("あ" * 30, profile, voice) == 8.2
    assert motion.scene_seconds(" " + "あ" * 30 + " ", profile, voice) == 8.2
    assert motion.scene_seconds("い" * 30, profile, voice) == 7.0      # câu mới chưa có giọng: vẫn ước lượng
    assert motion.scene_seconds("あ" * 30, profile, {"あ" * 30: 30.0}) == 10   # vẫn chặn ở clip.thoi_luong_giay


def test_voice_seconds_reads_previous_render(mrun):
    assert motion.voice_seconds(mrun) == {}
    (mrun.dir / "render").mkdir(exist_ok=True)
    (mrun.dir / "render" / "timeline.json").write_text(
        '{"doan_loi": [{"text": "一つ目。", "audio_dur": 2.5}, {"text": "", "audio_dur": 1.0}]}', encoding="utf-8")
    assert motion.voice_seconds(mrun) == {"一つ目。": 2.5}


def test_nap_motion_and_dung_canh_use_variable_length(mrun):
    text = (mrun.dir / "profile.yaml").read_text(encoding="utf-8")
    (mrun.dir / "profile.yaml").write_text(text.replace("clip:", "clip:\n  thoi_luong_thay_doi: true", 1), encoding="utf-8")
    write_canh(mrun, [scene(1, "hook", HOOK, narration="あ" * 30), scene(2, "hook", HOOK, narration="あ" * 2)])
    motion.nap_motion(mrun)
    assert [s["planned_sec"] for s in read_json(mrun.dir / "scenes.json")["canh"]] == [6.0, 3.0]
    assert goi.check_package(mrun)[0] == []
    motion.dung_canh(mrun)
    pages = motion.project_dir(mrun) / "scenes"
    first = (pages / "S001.html").read_text(encoding="utf-8")
    assert 'data-duration="6"' in first and 'data-duration="3"' in (pages / "S002.html").read_text(encoding="utf-8")
    assert "timeScale(1/K)" in first and "(6-.3)/N" in first


def test_build_defaults_to_ten_seconds():
    assert 'data-duration="10"' in mau_motion.build(scene(1, "hook", HOOK))


def test_nap_motion_refuses_bad_data(mrun):
    write_canh(mrun, [scene(1, "ledger", LEDGER)])
    with pytest.raises(StudioError, match="mã nguồn"):
        motion.nap_motion(mrun)
    assert read_json(mrun.dir / "scenes.json")["canh"] == []


# ---------------------------------------------------------------- dựng HTML và render

def test_dung_canh_writes_html_and_escapes_text(mrun):
    write_canh(mrun, [scene(1, "hook", {**HOOK, "hl": "<i>&</i>"}),
                      scene(2, "compare", COMPARE, nguon=["F01"])])
    assert motion.dung_canh(mrun) == 2
    proj = motion.project_dir(mrun)
    html = (proj / "scenes" / "S001.html").read_text(encoding="utf-8")
    assert "&lt;i&gt;&amp;&lt;/i&gt;" in html and "<i>&</i>" not in html
    assert 'data-composition-id="S001"' in html and 'data-width="1280"' in html
    assert (proj / "assets" / "gsap.min.js").is_file() and (proj / "hyperframes.json").is_file()


def test_ledger_stamp_and_total_options():
    html = mau_motion.build(scene(1, "ledger", LEDGER))
    assert "仮" not in html and 'id="tot"' in html and 'id="stamp"' not in html
    assert 'id="stamp"' in mau_motion.build(scene(1, "ledger", {**LEDGER, "kari": True}))
    no_total = {k: v for k, v in LEDGER.items() if k != "total_label"}
    assert mau_motion.check_scene(scene(1, "ledger", no_total))  # thiếu total_label khi vẫn hiện tổng
    no_total["show_total"] = False
    assert mau_motion.check_scene(scene(1, "ledger", no_total)) == []
    html = mau_motion.build(scene(1, "ledger", no_total))
    assert 'id="tot"' not in html and 'getElementById("tn")' not in html


def test_dung_canh_refuses_bad_data(mrun):
    write_canh(mrun, [scene(1, "hook", {})])
    with pytest.raises(StudioError, match="thiếu trường"):
        motion.dung_canh(mrun)


def fake_runner(calls, fail=()):
    def runner(cmd, cwd=None, **kw):
        calls.append(cmd)
        sid = cmd[cmd.index("-c") + 1].split("/")[1].split(".")[0]
        if sid in fail:
            return SimpleNamespace(returncode=1, stdout="", stderr="lỗi giả\nchi tiết")
        from pathlib import Path
        Path(cmd[cmd.index("-o") + 1]).write_bytes(b"mp4")
        return SimpleNamespace(returncode=0, stdout="", stderr="")
    return runner


@pytest.fixture
def rendered(mrun, monkeypatch):
    monkeypatch.setattr(motion.shutil, "which", lambda *a, **k: "npx")
    write_canh(mrun, [scene(1, "hook", HOOK), scene(2, "hook", HOOK), scene(3, "hook", HOOK)])
    motion.dung_canh(mrun)
    return mrun


def test_ve_canh_renders_skips_and_redoes(rendered):
    calls = []
    done, skipped = motion.ve_canh(rendered, runner=fake_runner(calls))
    assert done == ["S001", "S002", "S003"] and skipped == []
    cmd = calls[0]
    assert cmd[:4] == ["npx", "--yes", motion.HYPERFRAMES, "render"] and cmd[cmd.index("--fps") + 1] == "24"
    assert cmd[cmd.index("-c") + 1] == "scenes/S001.html"
    done, skipped = motion.ve_canh(rendered, runner=fake_runner([]))
    assert done == [] and skipped == ["S001", "S002", "S003"]
    done, _ = motion.ve_canh(rendered, ["S002"], lam_lai=True, runner=fake_runner([]))
    assert done == ["S002"]


def test_ve_canh_reports_failure_and_unknown_scene(rendered):
    with pytest.raises(StudioError, match="S002: render lỗi"):
        motion.ve_canh(rendered, runner=fake_runner([], fail={"S002"}))
    assert (rendered.dir / "motion" / "out" / "S001.mp4").is_file()
    with pytest.raises(StudioError, match="S009"):
        motion.ve_canh(rendered, ["S009"], runner=fake_runner([]))


def test_ve_canh_needs_node_and_pages(mrun, monkeypatch):
    monkeypatch.setattr(motion.shutil, "which", lambda *a, **k: None)
    with pytest.raises(StudioError, match="Node.js"):
        motion.ve_canh(mrun)
    monkeypatch.setattr(motion.shutil, "which", lambda *a, **k: "npx")
    with pytest.raises(StudioError, match="dung-canh"):
        motion.ve_canh(mrun)


# ---------------------------------------------------------------- bước tiếp theo

def test_next_step_follows_motion_flow(mrun, monkeypatch):
    monkeypatch.setattr(motion.shutil, "which", lambda *a, **k: "npx")
    assert "script.md" in bao_cao.next_step(mrun)
    limit = goi.narration_budget(10, mrun.profile)
    (mrun.dir / "script.md").write_text(script(2, limit // 2), encoding="utf-8")
    assert "tach-loi" in bao_cao.next_step(mrun)
    motion.tach_loi(mrun)
    assert "Điền template" in bao_cao.next_step(mrun)
    write_canh(mrun, [scene(1, "hook", HOOK, narration="あ"), scene(2, "hook", HOOK, narration="い")])
    assert "nap-motion" in bao_cao.next_step(mrun)
    motion.nap_motion(mrun)
    motion.dung_canh(mrun)
    assert "dung-canh" in bao_cao.next_step(mrun) and "ve-canh" in bao_cao.next_step(mrun)
    motion.ve_canh(mrun, runner=fake_runner([]))
    assert "nhan-clip" in bao_cao.next_step(mrun) and "motion" in bao_cao.next_step(mrun)
