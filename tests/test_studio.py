"""Kiểm thử không gọi Genmax, Muse hay YouTube."""
import json
import os
import shutil
import socket
import subprocess
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest
import yaml

from studio import bao_cao, clip, core, duyet, dung, goi, qc, seo, youtube
from studio.core import StudioError, read_json, write_json

NARRATION = ["Con đường này từng là tuyến buôn bán lớn nhất khu vực, nối những thành phố cảng với các vùng núi cao, "
             "và mỗi năm có hàng nghìn người đi qua.",
             "Hàng hóa đi qua đây trong suốt nhiều thế kỷ liền, từ muối và vải cho đến kim loại, "
             "khiến những khu chợ ven đường trở nên giàu có.",
             "Ngày nay chỉ còn lại những dấu tích trên nền đá, nhưng người dân địa phương vẫn kể lại câu chuyện "
             "của con đường cho thế hệ sau."]


def approve(run, gate):
    return duyet.approve(run, gate, confirm=lambda code: code)


def good_profile():
    p = yaml.safe_load((core.PROJECT / "channels" / "_mau" / "profile.yaml").read_text(encoding="utf-8"))
    p["kenh"].update(ten="Thử", chu_de_chinh="lịch sử", khan_gia="người lớn", ngon_ngu="vi", thi_truong="VN")
    p["noi_dung"].update(phong_cach_ke="kể chuyện", do_dai_phut=0.5, quy_chuan_nguon="ghi nguồn", ban_quyen="tự tạo",
                         tu_cam=["từ-cấm"])
    p["hinh_anh"].update(khoi_phong_cach="Cinematic documentary", mau_sac="warm tones", anh_sang="golden hour")
    p["clip"].update(thoi_luong_giay=10, do_phan_giai=[320, 180])
    p["giong"].update(mo_ta="Giọng nam trầm, ấm")
    p["youtube"].update(mau_tieu_de="{chu_de}", mau_mo_ta="{tom_tat}", channel_id="UCabc")
    return p


def good_scenes():
    prompts = ["Aerial view of an ancient trade road through mountains", "Camel caravan crossing a dusty valley",
               "Weathered stone ruins at sunset, no text"]
    return {"canh": [{"id": f"S{i:03d}", "narration": n, "visual_prompt": v, "audio_note": "gió nhẹ", "planned_sec": 10}
                     for i, (n, v) in enumerate(zip(NARRATION, prompts), start=1)]}


@pytest.fixture
def run(tmp_path):
    channel = tmp_path / "channels" / "thu"
    channel.mkdir(parents=True)
    (channel / "profile.yaml").write_text(yaml.safe_dump(good_profile(), allow_unicode=True), encoding="utf-8")
    r = core.create_run(channel, tmp_path / "runs", "chu de thu")
    text = "\n".join(f"## {h}\nNội dung" for h in core.brief_sections(r))
    (r.dir / "brief.md").write_text(text, encoding="utf-8")
    write_json(r.dir / "scenes.json", good_scenes())
    return r


def make_clip(path, sec=10):
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", f"testsrc2=s=320x180:r=24:d={sec}",
                    "-f", "lavfi", "-i", f"sine=frequency=220:d={sec}", "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)], check=True)


def make_inbox(tmp_path, n=3):
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    make_clip(inbox / "a1.mp4")
    for i in range(2, n + 1):
        shutil.copy(inbox / "a1.mp4", inbox / f"a{i}.mp4")
    return inbox


def fake_approved_upload(run):
    """Dựng trạng thái đã qua Cổng 3 mà không cần dựng video thật."""
    approve(run, "G1")
    approve(run, "G2")
    render = run.dir / "render"
    render.mkdir()
    (render / "final.mp4").write_bytes(b"video")
    (render / "final.srt").write_text("1\n00:00:00,000 --> 00:00:01,000\nx\n", encoding="utf-8")
    write_json(render / "qc.json", {"dat": True, "sha256_video": core.sha256(render / "final.mp4"), "loi": [],
                                    "canh_bao": [], "thoi_luong": 1})
    seo.create_metadata(run)
    path = run.dir / "publish" / "metadata.json"
    write_json(path, {**read_json(path), "tieu_de": "Tiêu đề", "mo_ta": "Mô tả", "ten_tep": "video.mp4", "hashtag": []})
    approve(run, "G3")


class FakeRequest:
    def __init__(self, result):
        self.result = result

    def execute(self):
        return self.result

    def next_chunk(self, num_retries=0):
        return None, self.result


class FakeYouTube:
    def __init__(self, channel="UCabc", privacy="private"):
        self.channel, self.privacy, self.inserted = channel, privacy, []

    def channels(self):
        return self

    def videos(self):
        return self

    def captions(self):
        return self

    def thumbnails(self):
        return self

    def playlistItems(self):
        return self

    def list(self, **kw):
        if "mine" in kw:
            return FakeRequest({"items": [{"id": self.channel, "snippet": {"title": "Kênh"}}]})
        return FakeRequest({"items": [{"status": {"privacyStatus": self.privacy}}]})

    def insert(self, **kw):
        self.inserted.append(kw)
        return FakeRequest({"id": "VID123"})

    def set(self, **kw):
        return FakeRequest({})

    def update(self, **kw):
        self.updated = kw
        return FakeRequest({})


# ---------------------------------------------------------------- hồ sơ và gói nội dung

def test_profile_missing_blocks_run(tmp_path):
    channel = tmp_path / "kenh"
    channel.mkdir()
    shutil.copy(core.PROJECT / "channels" / "_mau" / "profile.yaml", channel / "profile.yaml")
    with pytest.raises(StudioError, match="kenh.ten"):
        core.create_run(channel, tmp_path / "runs", "x")


def test_env_file_overrides_old_key(tmp_path, monkeypatch):
    monkeypatch.setenv("GENMAX_API_KEY", "khoa-cu")
    env = tmp_path / ".env"
    env.write_text('# ghi chú\nGENMAX_API_KEY="khoa-moi"\nKHONG_CO_GIA_TRI=\n', encoding="utf-8")
    monkeypatch.delenv("KHONG_CO_GIA_TRI", raising=False)
    core.load_env(env)
    assert os.environ["GENMAX_API_KEY"] == "khoa-moi"
    assert "KHONG_CO_GIA_TRI" not in os.environ


def test_good_package_passes(run):
    assert goi.check_package(run)[0] == []


@pytest.mark.parametrize("prompt", ["Ruins with subtitles at the bottom", "A sign that says welcome",
                                    'Poster reading "Silk Road"', "Cảnh có phụ đề ở dưới"])
def test_prompt_requesting_text_rejected(run, prompt):
    data = good_scenes()
    data["canh"][0]["visual_prompt"] = prompt
    write_json(run.dir / "scenes.json", data)
    assert any("S001" in e for e in goi.check_package(run)[0])


def test_negated_text_allowed(run):
    data = good_scenes()
    data["canh"][0]["visual_prompt"] = "Ruins at dawn, no subtitles, without captions"
    write_json(run.dir / "scenes.json", data)
    assert goi.check_package(run)[0] == []


def test_narration_budget_enforced(run):
    data = good_scenes()
    data["canh"][1]["narration"] = "chữ " * 80
    write_json(run.dir / "scenes.json", data)
    assert any("vượt giới hạn" in e for e in goi.check_package(run)[0])


def test_budget_matches_japanese_estimate(run):
    profile = run.profile
    profile["kenh"]["ngon_ngu"] = "ja"
    assert goi.narration_budget(10, profile) == 56


def test_narration_copied_into_prompt_rejected(run):
    data = good_scenes()
    data["canh"][0]["visual_prompt"] = "Scene: " + NARRATION[0]
    write_json(run.dir / "scenes.json", data)
    assert any("nguyên văn" in e for e in goi.check_package(run)[0])


def test_banned_word_rejected(run):
    data = good_scenes()
    data["canh"][0]["narration"] = "Câu có từ-cấm ở đây."
    write_json(run.dir / "scenes.json", data)
    assert any("từ cấm" in e for e in goi.check_package(run)[0])


def test_wrong_scene_order_rejected(run):
    data = good_scenes()
    data["canh"][0]["id"], data["canh"][1]["id"] = "S002", "S001"
    write_json(run.dir / "scenes.json", data)
    assert goi.check_package(run)[0]


def test_export_includes_style_and_no_narration(run):
    approve(run, "G1")
    approve(run, "G2")
    text = goi.export_prompts(run).read_text(encoding="utf-8")
    assert "Cinematic documentary" in text and "no on-screen text" in text
    assert not any(n in text for n in NARRATION)


def image_mode_run(run):
    profile = run.profile
    profile["clip"]["che_do"] = "anh"
    (run.dir / "profile.yaml").write_text(yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8")
    write_json(run.dir / "shotlist.json", {"style": "A", "shots": [
        {"id": "c00_b01_l01", "chapter": "HOOK", "narration": "A short line of narration here.",
         "prompt": "Gouache style. Wide shot. A small shelter in snow.", "sound": ["SOUND: wind"], "duration": 3.0,
         "refs": ["ref_camp_ext"]}]})
    return run


def test_import_shotlist_builds_valid_package(run):
    image_mode_run(run)
    assert goi.import_shotlist(run) == 1
    scene = run.scenes()[0]
    assert scene["id"] == "S001" and scene["ma_shot"] == "c00_b01_l01" and scene["planned_sec"] == 3.0
    assert goi.check_package(run)[0] == []


def test_image_mode_budget_allows_estimate_error(run):
    profile = image_mode_run(run).profile
    assert goi.narration_budget(5, profile) == 100


def test_shared_place_name_is_not_copied_narration(run):
    data = good_scenes()
    data["canh"][0]["narration"] = "They lived near the Yana River for a long time."
    data["canh"][0]["visual_prompt"] = "Setting: a frozen plain near the Yana River at dusk"
    write_json(run.dir / "scenes.json", data)
    assert not any("nguyên văn" in e for e in goi.check_package(run)[0])


def test_image_mode_prompt_not_doubled(run):
    image_mode_run(run)
    goi.import_shotlist(run)
    assert goi.build_prompt(run.scenes()[0], run.profile) == "Gouache style. Wide shot. A small shelter in snow."


def test_shotlist_change_invalidates_gate2(run):
    image_mode_run(run)
    goi.import_shotlist(run)
    approve(run, "G1")
    approve(run, "G2")
    path = run.dir / "shotlist.json"
    write_json(path, {**read_json(path), "style": "B"})
    with pytest.raises(StudioError, match="shotlist.json"):
        duyet.verify_gate(run, "G2")


def test_clip_render_refused_in_image_mode(run):
    image_mode_run(run)
    goi.import_shotlist(run)
    approve(run, "G1")
    approve(run, "G2")
    with pytest.raises(StudioError, match="chế độ ảnh"):
        dung.render(run, "gia_lap")


def test_clips_group_lines_and_repeat_fixed_blocks(run):
    write_json(run.dir / "muse" / "bo_quy_chuan.json", {
        "style": "STYLE", "ice_age": "ICE", "blocks": {"ref_child": "BOY BLOCK"},
        "motion": {"NARRATIVE": "SLOW"}, "fixes": {"mammoth": "ANATOMY", "figurine": "FIG", "child_hand": "HANDS"}})
    def shot(i, chapter="A", refs=("ref_child",)):
        return {"id": f"s{i}", "chapter": chapter, "narration": "word " * 12, "pace": "NARRATIVE", "duration": 4.0,
                "refs": list(refs), "sound": [], "blueprint": {
                    "shot_angle": "wide", "subject_action": f"mammoth action {i}", "atmosphere": "snow",
                    "lighting_palette": "blue", "setting": None}}
    write_json(run.dir / "shotlist.json", {"shots": [shot(1), shot(2), shot(3), shot(4, "B")]})
    assert goi.import_shotlist_as_clips(run) == 3
    scenes = run.scenes()
    assert scenes[0]["ma_shot"] == ["s1", "s2"] and scenes[-1]["ma_shot"] == ["s4"]
    prompt = scenes[0]["visual_prompt"]
    assert "BOY BLOCK" in prompt and "STYLE" in prompt and "ANATOMY" in prompt and "action 2" in prompt
    assert goi.check_package(run)[0] == []
    assert "Uses: BOY BLOCK" in scenes[0]["prompt_ngan"] and "STYLE" not in scenes[0]["prompt_ngan"]
    with pytest.raises(StudioError, match="Cổng"):
        goi.export_batches(run)
    approve(run, "G1")
    approve(run, "G2")
    files = goi.export_batches(run, size=2)
    assert len(files) == 2
    text = files[0].read_text(encoding="utf-8")
    assert "STYLE" in text and "BOY BLOCK" in text and "S001:" in text and "S003:" not in text


# ---------------------------------------------------------------- cổng duyệt

def test_empty_brief_cannot_be_approved(tmp_path):
    channel = tmp_path / "k"
    channel.mkdir()
    (channel / "profile.yaml").write_text(yaml.safe_dump(good_profile(), allow_unicode=True), encoding="utf-8")
    r = core.create_run(channel, tmp_path / "runs", "x")
    with pytest.raises(StudioError, match="còn trống"):
        approve(r, "G1")


def test_wrong_code_does_not_approve(run):
    with pytest.raises(StudioError, match="Chưa duyệt"):
        duyet.approve(run, "G1", confirm=lambda code: "sai")
    assert not (run.dir / "approvals" / "G1.json").exists()


def test_code_tolerates_terminal_noise_but_not_other_codes(run):
    assert duyet.approve(run, "G1", confirm=lambda code: f" {code.upper()}\r\n") is True
    (run.dir / "approvals" / "G1.json").unlink()
    with pytest.raises(StudioError, match="Đã nhận"):
        duyet.approve(run, "G1", confirm=lambda code: "abc")


def test_profile_can_turn_off_gates_but_not_qc(run):
    profile = run.profile
    profile["quy_trinh"] = {"bo_duyet": True}
    (run.dir / "profile.yaml").write_text(yaml.safe_dump(profile, allow_unicode=True), encoding="utf-8")
    assert duyet.verify_gate(run, "G3") is None
    with pytest.raises(StudioError, match="giả lập"):
        qc.require_qc_passed(run)
    fake = FakeYouTube()
    with pytest.raises(StudioError):
        youtube.upload(run, service=fake)
    assert fake.inserted == []


def test_non_tty_cannot_approve(run, monkeypatch):
    monkeypatch.setattr("sys.stdin", open(Path(__file__)))
    with pytest.raises(StudioError, match="tự chạy"):
        duyet.approve(run, "G1")


def test_gates_are_ordered(run):
    with pytest.raises(StudioError, match="Cổng 1"):
        approve(run, "G2")
    approve(run, "G1")
    with pytest.raises(StudioError, match="Cổng 2"):
        approve(run, "G3")


def test_edit_after_approval_invalidates(run):
    approve(run, "G1")
    approve(run, "G2")
    data = good_scenes()
    data["canh"][0]["narration"] = "Lời đã bị sửa sau khi duyệt."
    write_json(run.dir / "scenes.json", data)
    with pytest.raises(StudioError, match="mất hiệu lực"):
        duyet.verify_gate(run, "G2")
    with pytest.raises(StudioError, match="mất hiệu lực"):
        goi.export_prompts(run)


def test_gia_lap_render_cannot_pass_gate3(run):
    approve(run, "G1")
    approve(run, "G2")
    (run.dir / "render_gia_lap").mkdir()
    (run.dir / "render_gia_lap" / "final.mp4").write_bytes(b"x")
    seo.create_metadata(run)
    with pytest.raises(StudioError, match="giả lập"):
        approve(run, "G3")


# ---------------------------------------------------------------- SEO

def test_metadata_validation(run):
    seo.create_metadata(run)
    errors = seo.check_metadata(run)
    assert any("Tiêu đề" in e for e in errors) and any("ten_tep" in e for e in errors)
    path = run.dir / "publish" / "metadata.json"
    write_json(path, {**read_json(path), "tieu_de": "x" * 101, "mo_ta": "<b>", "ten_tep": "a.mp4", "tre_em": None,
                      "lich_dang": "2020-01-01T00:00:00Z", "the": ["a" * 501], "hashtag": ["#thieu"]})
    text = "\n".join(seo.check_metadata(run))
    for needle in ("Tiêu đề", "dấu <", "tre_em", "quá khứ", "thẻ", "#thieu"):
        assert needle in text


def test_tag_length_counts_commas_and_quotes(run):
    seo.create_metadata(run)
    path = run.dir / "publish" / "metadata.json"
    # 20 thẻ 22 ký tự: 440 ký tự thô, nhưng thành 499 khi tính ngoặc kép và dấu phẩy
    fit = ["a b" + "c" * 19] * 20
    write_json(path, {**read_json(path), "the": fit})
    assert not any("thẻ" in e for e in seo.check_metadata(run))
    write_json(path, {**read_json(path), "the": fit + ["x"]})
    assert any("thẻ" in e for e in seo.check_metadata(run))


def test_review_page_escapes_html(run):
    fake_approved_upload(run)
    path = run.dir / "publish" / "metadata.json"
    write_json(path, {**read_json(path), "mo_ta": "a & b"})
    page = seo.write_review_page(run).read_text(encoding="utf-8")
    assert "a &amp; b" in page and "Riêng tư" in page


# ---------------------------------------------------------------- YouTube (giả lập dịch vụ)

def test_upload_refused_without_gate3(run):
    fake = FakeYouTube()
    with pytest.raises(StudioError, match="Cổng"):
        youtube.upload(run, service=fake)
    assert fake.inserted == []


def test_upload_refused_when_video_changed(run):
    fake_approved_upload(run)
    (run.dir / "render" / "final.mp4").write_bytes(b"video khac")
    fake = FakeYouTube()
    with pytest.raises(StudioError, match="mất hiệu lực"):
        youtube.upload(run, service=fake)
    assert fake.inserted == []


def test_upload_refused_when_metadata_changed(run):
    fake_approved_upload(run)
    path = run.dir / "publish" / "metadata.json"
    write_json(path, {**read_json(path), "tieu_de": "Tiêu đề khác"})
    with pytest.raises(StudioError, match="mất hiệu lực"):
        youtube.upload(run, service=FakeYouTube())


def test_upload_refused_for_wrong_channel(run):
    fake_approved_upload(run)
    fake = FakeYouTube(channel="UCkhac")
    with pytest.raises(StudioError, match="không sở hữu"):
        youtube.upload(run, service=fake)
    assert fake.inserted == []


def test_upload_is_always_private_and_not_repeated(run):
    fake_approved_upload(run)
    fake = FakeYouTube()
    assert youtube.upload(run, service=fake) == "VID123"
    status = fake.inserted[0]["body"]["status"]
    assert status["privacyStatus"] == "private"
    assert status["containsSyntheticMedia"] is True and status["selfDeclaredMadeForKids"] is False
    with pytest.raises(StudioError, match="đã tải lên"):
        youtube.upload(run, service=fake)
    assert "VID123" in bao_cao.write_report(run).read_text(encoding="utf-8")


def test_update_metadata_changes_snippet_only(run):
    fake_approved_upload(run)
    fake = FakeYouTube()
    with pytest.raises(StudioError, match="chưa tải"):
        youtube.update_metadata(run, service=fake)
    youtube.upload(run, service=fake)
    assert youtube.update_metadata(run, service=fake) == "VID123"
    assert fake.updated["part"] == "snippet" and "status" not in fake.updated["body"]
    assert fake.updated["body"]["snippet"]["title"] == "Tiêu đề"


def test_upload_flags_unexpected_public_status(run, capsys):
    fake_approved_upload(run)
    youtube.upload(run, service=FakeYouTube(privacy="public"))
    assert "public" in capsys.readouterr().out
    assert any(e["ket_qua"] == "loi" for e in run.state["su_kien"])


def test_schedule_keeps_private():
    body = youtube.build_body({"tieu_de": "t", "mo_ta": "m", "category_id": "27", "ngon_ngu": "vi",
                               "ngon_ngu_am_thanh": "vi", "tre_em": False, "noi_dung_tong_hop": True,
                               "lich_dang": "2030-01-01T00:00:00Z"})
    assert body["status"]["privacyStatus"] == "private" and body["status"]["publishAt"] == "2030-01-01T00:00:00Z"


def test_oauth_redirect_survives_stray_connections():
    """Lỗi thật: kết nối rỗng của trình duyệt làm lệnh kết nối YouTube dừng trước khi bạn cấp quyền."""
    server, received = youtube._redirect_server()
    port = server.server_port

    def browser():
        socket.create_connection(("localhost", port)).close()
        for path in ("/favicon.ico", "/?code=abc&state=xyz"):
            for _ in range(20):
                try:
                    urllib.request.urlopen(f"http://localhost:{port}{path}", timeout=5)
                    break
                except urllib.error.HTTPError:
                    break
                except OSError:
                    time.sleep(0.1)

    thread = threading.Thread(target=browser)
    thread.start()
    with server:
        uri = youtube._wait_for_redirect(server, received, seconds=20)
    thread.join()
    assert "code=abc" in uri and "state=xyz" in uri


def test_oauth_redirect_times_out_clearly():
    server, received = youtube._redirect_server()
    with server, pytest.raises(StudioError, match="chạy lại"):
        youtube._wait_for_redirect(server, received, seconds=0)


# ---------------------------------------------------------------- kiểm tra video

def test_qc_timeline_detects_faults():
    scenes = good_scenes()["canh"]
    timeline = {"tong_thoi_luong": 30.0,
                "clips": [{"file": f"S00{i}.mp4", "goc": 10.0, "dung_hinh": 0.0} for i in (2, 1, 3)],
                "doan_loi": [{"text": "sai lời", "voice_start": 0.0, "audio_dur": 5.0, "clips": [1, 1]},
                             {"text": NARRATION[1], "voice_start": 4.0, "audio_dur": 30.0, "clips": [2, 2]}]}
    errors, _ = qc.check_timeline(timeline, scenes, 30.0, {})
    text = "\n".join(errors)
    for needle in ("Thứ tự", "khác kịch bản", "chồng nhau", "dài hơn video"):
        assert needle in text


def test_qc_srt_detects_faults():
    scenes = good_scenes()["canh"]
    srt = "1\n00:00:05,000 --> 00:00:01,000\nkhác\n\n2\n00:00:50,000 --> 00:00:55,000\ncũng khác\n"
    text = "\n".join(qc.check_srt(srt, scenes, 30.0))
    for needle in ("sai thứ tự", "quá hết video", "khác kịch bản"):
        assert needle in text


def test_qc_detects_black_and_silence(tmp_path):
    path = tmp_path / "den.mp4"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "lavfi", "-i", "color=black:s=320x180:r=24:d=5",
                    "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo:d=5", "-c:v", "libx264", "-preset", "ultrafast",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(path)], check=True)
    black, silence, decode_errors = qc.analyze_stream(path)
    assert black and silence and not decode_errors


def test_qc_detects_corrupt_file(tmp_path):
    path = tmp_path / "hong.mp4"
    make_clip(path, 2)
    data = bytearray(path.read_bytes())
    path.write_bytes(bytes(data[:len(data) // 2]))
    assert qc.analyze_stream(path)[2]


# ---------------------------------------------------------------- toàn luồng

def test_clip_count_mismatch_rejected(run, tmp_path):
    approve(run, "G1")
    approve(run, "G2")
    inbox = make_inbox(tmp_path, 2)
    with pytest.raises(StudioError, match="2 clip"):
        clip.import_clips(run, inbox)


def test_render_blocked_before_gate2(run):
    with pytest.raises(StudioError, match="Cổng 2"):
        dung.render(run, "gia_lap")


def test_full_flow_with_fake_voice(run, tmp_path):
    """Gói nội dung -> clip -> giọng bíp -> dựng -> kiểm tra, không tốn credit."""
    approve(run, "G1")
    approve(run, "G2")
    goi.export_prompts(run)
    clip.import_clips(run, make_inbox(tmp_path))
    assert clip.check_clips(run)[0] == []
    assert sorted(p.name for p in (run.dir / "clips").glob("*.mp4")) == ["S001.mp4", "S002.mp4", "S003.mp4"]

    final = dung.render(run, "gia_lap")
    assert final == run.dir / "render_gia_lap" / "final.mp4"
    assert not (run.dir / "render").exists()

    result = qc.run_qc(run, "render_gia_lap")
    assert result["dat"], result["loi"]
    timeline = read_json(run.dir / "render_gia_lap" / "timeline.json")
    assert [c["file"] for c in timeline["clips"]] == ["S001.mp4", "S002.mp4", "S003.mp4"]
    assert [s["clips"] for s in timeline["doan_loi"]] == [[1, 1], [2, 2], [3, 3]]

    # Bản giả lập không thể đi tiếp tới Cổng 3
    seo.create_metadata(run)
    with pytest.raises(StudioError, match="giả lập"):
        approve(run, "G3")
    report = bao_cao.write_report(run).read_text(encoding="utf-8")
    assert "Thủ công" in report and "chưa tải lên" in report


def test_trim_targets_fit_voice_within_clip():
    timeline = {"clips": [{"file": f"S00{i}.mp4", "goc": 10.0} for i in (1, 2, 3, 4)],
                "doan_loi": [{"clips": [1, 1], "audio_dur": 5.0}, {"clips": [2, 2], "audio_dur": 20.0},
                             {"clips": [3, 3], "audio_dur": 0.5}]}
    targets = dung.trim_targets(timeline, {"dem_dau": 0.25, "dem_cuoi": 0.35})
    assert targets == {"S001.mp4": 6.0, "S002.mp4": 10.0, "S003.mp4": 3.0, "S004.mp4": 3.0}


def test_next_step_guides_user(run):
    assert "G1" in bao_cao.next_step(run)
    approve(run, "G1")
    assert "G2" in bao_cao.next_step(run)
    approve(run, "G2")
    assert "xuat-prompt" in bao_cao.next_step(run)


def test_config_never_contains_key(run):
    cfg = dung.build_config(run.profile)
    assert cfg["api_key"] is None
    assert json.dumps(run.state).lower().find("api_key") == -1


def test_client_file_is_per_channel_when_profile_names_one(tmp_path, monkeypatch):
    from studio import youtube
    own = tmp_path / "rieng" / "kenh_a.json"
    own.parent.mkdir()
    own.write_text("{}", encoding="utf-8")
    shared = tmp_path / "chung.json"
    shared.write_text("{}", encoding="utf-8")
    for name, yt in (("kenh_a", {"oauth_client_file": "%THU_GOC%/rieng/kenh_a.json"}), ("kenh_b", {})):
        d = tmp_path / "channels" / name
        d.mkdir(parents=True)
        (d / "profile.yaml").write_text(yaml.safe_dump({"youtube": yt}), encoding="utf-8")
    monkeypatch.setattr(youtube, "ROOT", tmp_path)
    monkeypatch.setenv("THU_GOC", str(tmp_path))
    monkeypatch.setenv("YOUTUBE_OAUTH_CLIENT_FILE", str(shared))
    assert youtube.client_file("kenh_a") == own
    assert youtube.client_file("kenh_b") == shared
    assert youtube.client_file() == shared
    own.unlink()
    with pytest.raises(StudioError, match="OAuth client"):
        youtube.client_file("kenh_a")


def test_doc_theo_bang_uu_tien_khoa_dai_va_mot_luot():
    engine = core.load_engine()
    bang = {"大倉喜八郎": "おおくらきはちろう", "大倉": "おおくら", "新発田": "しばた"}
    assert engine.doc_theo_bang("新発田の大倉喜八郎と大倉家", bang) == "しばたのおおくらきはちろうとおおくら家"
    assert engine.doc_theo_bang("そのまま", None) == "そのまま"


def test_synth_segment_doc_theo_bang_phu_de_giu_chu_goc():
    engine = core.load_engine()

    class Maker:
        provider = "minimax"
        texts = []

        def make(self, text, speed):
            self.texts.append(text)
            return None, 1.0

    cfg = {**engine.DEFAULT_CONFIG, "cach_doc": {"新発田": "しばた"}}
    seg = engine.synth_segment({"clips": [1, 1], "text": "新発田に生まれた"}, [5.0], cfg, Maker())
    assert Maker.texts == ["しばたに生まれた"]
    assert seg["text"] == "新発田に生まれた" and seg["loi_giong"] == "しばたに生まれた"


def test_load_readings_kiem_dinh_dang(run):
    assert dung.load_readings(run) == {}
    (run.dir / "cach_doc.json").write_text('{"新発田": "しばた"}', encoding="utf-8")
    assert dung.load_readings(run) == {"新発田": "しばた"}
    (run.dir / "cach_doc.json").write_text('{"新発田": ""}', encoding="utf-8")
    with pytest.raises(StudioError, match="cach_doc"):
        dung.load_readings(run)
