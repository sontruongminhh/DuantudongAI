"""Clip motion thay cho Muse: tách lời đọc thành cảnh, kiểm tra dữ liệu cảnh, dựng HTML và render bằng HyperFrames."""
import math
import os
import re
import shutil
import subprocess
from pathlib import Path

from . import mau_motion
from .core import PROJECT, StudioError, load_engine, read_json, write_json
from .dung import TRIM_GAP, TRIM_SHORTEST
from .goi import SCENE_ID, _banned_hits, narration_budget

HYPERFRAMES = "hyperframes@0.8.231"
RENDER_TIMEOUT = 600
NODE_DIR = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs"
PACE = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")
FACT_ROW = re.compile(r"^\|\s*(F\d+)\s*\|(.*)$")


def motion_dir(run):
    return run.dir / "motion"


VOICE_MARGIN = 0.2   # giây dư khi cảnh dài theo giọng thật, để bước cắt clip luôn có đủ hình


def voice_seconds(run):
    """Độ dài giọng thật của từng câu lời đọc ({lời: giây}) từ lần dựng trước (render/timeline.json); chưa dựng thì {}."""
    path = run.dir / "render" / "timeline.json"
    if not path.is_file():
        return {}
    return {seg["text"].strip(): seg["audio_dur"] for seg in read_json(path).get("doan_loi", [])
            if seg.get("text") and seg.get("audio_dur")}


def scene_seconds(narration, profile, voice=None):
    """Độ dài cảnh. Mặc định cố định theo clip.thoi_luong_giay. Nếu clip.thoi_luong_thay_doi: true thì theo lời đọc
    (ký tự / tốc độ đọc + khoảng lặng đầu, cuối và nghỉ như bước cắt clip), không ngắn hơn clip.thoi_luong_toi_thieu
    (mặc định 3 giây) và không dài hơn clip.thoi_luong_giay.
    voice: {lời: giây} của giọng thật (voice_seconds). Câu đã có giọng thì lấy độ dài thật thay cho ước lượng theo
    số ký tự, vì câu nhiều con số (1957年…) đọc lâu hơn hẳn số ký tự và làm giọng trễ sau hình."""
    clip = profile["clip"]
    longest = float(clip["thoi_luong_giay"])
    if not clip.get("thoi_luong_thay_doi"):
        return longest
    engine = load_engine()
    cfg = engine.DEFAULT_CONFIG
    pad = cfg["dem_dau"] + cfg["dem_cuoi"] + TRIM_GAP
    real = (voice or {}).get(narration.strip())
    if real:
        want = real + pad + VOICE_MARGIN
    else:
        # giong.ky_tu_moi_giay: tốc độ đo từ giọng thật (ở toc_do 1.0); không có thì dùng ước lượng của engine
        cps = profile["giong"].get("ky_tu_moi_giay") or engine.CHARS_PER_SEC.get(profile["kenh"]["ngon_ngu"], engine.DEFAULT_CPS)
        speed = profile["giong"].get("toc_do") or 1.0
        want = len(narration.strip()) / (cps * speed) + pad
    shortest = float(clip.get("thoi_luong_toi_thieu") or TRIM_SHORTEST)
    return min(max(math.ceil(round(want * 10, 6)) / 10, shortest), longest)


# ---------------------------------------------------------------- kịch bản → cảnh

def parse_script(md):
    """Các dòng lời đọc của script.md kèm chương, mã Saga và gợi ý hình của beat."""
    if "## Kịch bản" not in md:
        raise StudioError("script.md thiếu mục \"## Kịch bản\"")
    body = md.split("## Kịch bản", 1)[1].split("## Bảng nguồn", 1)[0]
    out, chapter, cue = [], None, None
    ci, bi, li = -1, 0, 0
    for raw in body.splitlines():
        s = raw.strip()
        if s.startswith("### "):
            ci, bi, li = ci + 1, 0, 0
            chapter = s[4:]
        elif s.startswith("[HÌNH:"):
            bi, li = bi + 1, 0
            cue = s[len("[HÌNH:"):].rstrip("]").strip()
        elif PACE.match(s):
            li += 1
            pace, text = PACE.match(s).groups()
            out.append({"id": f"c{ci:02d}_b{bi:02d}_l{li:02d}", "chuong": chapter, "cue": cue, "pace": pace,
                        "text": text.strip()})
    return out


def beat_of(line):
    """Mã beat (cNN_bMM) của một dòng lời đọc."""
    return line["id"].rsplit("_l", 1)[0]


def split_scenes(lines, limit):
    """Gộp các dòng liên tiếp trong cùng một chương và cùng một beat thành cảnh, mỗi cảnh không quá limit ký tự lời đọc.
    Mỗi beat có một gợi ý hình, nên một cảnh không bao giờ chứa dòng của hai beat."""
    too_long = [ln for ln in lines if len(ln["text"]) > limit]
    if too_long:
        raise StudioError("Dòng lời đọc dài hơn giới hạn " + str(limit) + " ký tự của một cảnh:\n  "
                          + "\n  ".join(f"{ln['id']} ({len(ln['text'])} ký tự): {ln['text'][:40]}" for ln in too_long))
    groups, current, chars = [], [], 0
    for ln in lines:
        if current and (current[-1]["chuong"] != ln["chuong"] or beat_of(current[-1]) != beat_of(ln)
                        or chars + len(ln["text"]) > limit):
            groups.append(current)
            current, chars = [], 0
        current.append(ln)
        chars += len(ln["text"])
    if current:
        groups.append(current)
    return groups


def tach_loi(run, ghi_de=False):
    """Tách script.md thành cảnh 10 giây: motion/dong_loi.json và khung motion/canh.json để điền mẫu."""
    path = run.dir / "script.md"
    if not path.is_file():
        raise StudioError("Chưa có script.md")
    lines = parse_script(path.read_text(encoding="utf-8-sig"))
    if not lines:
        raise StudioError("script.md không có dòng lời đọc nào, mỗi dòng phải mở đầu bằng [NARRATIVE], [TENSION] hoặc [EPIC]")
    profile = run.profile
    clip_sec = float(profile["clip"]["thoi_luong_giay"])
    limit = narration_budget(clip_sec, profile)
    groups = split_scenes(lines, limit)
    scenes = []
    for i, g in enumerate(groups, start=1):
        text = "".join(ln["text"] for ln in g)
        # Cảnh tiếp theo của cùng một beat giữ nguyên hình, không chạy lại hoạt ảnh từ đầu
        hold = i > 1 and beat_of(groups[i - 2][-1]) == beat_of(g[0])
        scenes.append({"id": SCENE_ID.format(i), "chuong": g[0]["chuong"], "goi_y_hinh": [c for c in dict.fromkeys(ln["cue"] for ln in g) if c],
                       "narration": text, "so_ky_tu": len(text), "dong": [ln["id"] for ln in g], "giu_hinh": hold})
    out = motion_dir(run)
    out.mkdir(exist_ok=True)
    write_json(out / "dong_loi.json", {"gioi_han_ky_tu": limit, "canh": scenes})
    skeleton = out / "canh.json"
    wrote = ghi_de or not skeleton.is_file()
    if wrote:
        write_json(skeleton, {"canh": [{"id": s["id"], "chuong": s["chuong"], "narration": s["narration"], "template": None,
                                        "giu_hinh": s["giu_hinh"], "nguon": [], "data": {}} for s in scenes]})
    run.log("Tách lời đọc thành cảnh motion", "ok", chi_tiet=f"{len(lines)} dòng, {len(scenes)} cảnh, tối đa {limit} ký tự")
    return len(scenes), wrote


# ---------------------------------------------------------------- kiểm tra và nạp

def read_facts(run):
    """{mã dữ kiện: mức tin cậy} đọc từ bảng trong nguon.md. Cột thứ tư của bảng là mức tin cậy A, B hoặc C."""
    path = run.dir / "nguon.md"
    if not path.is_file():
        return {}
    facts = {}
    for raw in path.read_text(encoding="utf-8-sig").splitlines():
        m = FACT_ROW.match(raw.strip())
        if m:
            cells = [c.strip() for c in raw.strip().strip("|").split("|")]
            if len(cells) >= 4:
                facts[cells[0]] = cells[3].split()[0] if cells[3] else ""
    return facts


def check_scenes(run):
    """Trả về (lỗi, cảnh báo) của motion/canh.json."""
    path = motion_dir(run) / "canh.json"
    if not path.is_file():
        return ["Chưa có motion/canh.json, hãy chạy tach-loi"], []
    scenes = read_json(path).get("canh", [])
    profile = run.profile
    clip_sec = float(profile["clip"]["thoi_luong_giay"])
    banned = profile["noi_dung"].get("tu_cam") or []
    facts = read_facts(run)
    errors, warnings = [], []
    if not scenes:
        return ["motion/canh.json chưa có cảnh nào"], []
    anh_dir = motion_dir(run) / "anh"
    anh_co = {f.name for f in anh_dir.iterdir()} if anh_dir.is_dir() else set()
    for i, sc in enumerate(scenes, start=1):
        want = SCENE_ID.format(i)
        sid = sc.get("id")
        if sid != want:
            errors.append(f"Cảnh thứ {i}: id phải là {want}, đang là {sid}")
        sid = sid or want
        narration = (sc.get("narration") or "").strip()
        budget = narration_budget(clip_sec, profile)
        if len(narration) > budget:
            errors.append(f"{sid}: lời đọc {len(narration)} ký tự, vượt giới hạn {budget} ký tự của cảnh")
        if not narration:
            warnings.append(f"{sid}: cảnh không có lời đọc")
        for problem in mau_motion.check_scene(sc, anh_co):
            errors.append(f"{sid}: {problem}")
        for w in _banned_hits(f"{narration}\n{sc.get('data')}", banned):
            errors.append(f"{sid}: có từ cấm \"{w}\"")
        template = sc.get("template")
        if sc.get("thu"):
            warnings.append(f"{sid}: dữ liệu thử (thu), không dùng để đăng")
        elif template in mau_motion.NEEDS_SOURCE:
            ids = sc.get("nguon") or []
            if not ids:
                errors.append(f"{sid}: mẫu {template} có số liệu hoặc dữ kiện, phải ghi mã nguồn trong trường nguon")
            for fid in ids:
                grade = facts.get(fid)
                if grade is None:
                    errors.append(f"{sid}: mã nguồn {fid} không có trong nguon.md")
                elif grade == "C":
                    errors.append(f"{sid}: dữ kiện {fid} mức C chưa kiểm chứng, không dùng trong lời đọc hay hình")
                elif grade == "B":
                    warnings.append(f"{sid}: dữ kiện {fid} mức B, lời đọc phải nói \"theo ...\" hoặc \"có nơi\"")
    return errors, warnings


def nap_motion(run):
    """Kiểm tra motion/canh.json rồi ghi scenes.json cho các bước kiểm tra gói, duyệt và dựng."""
    errors, warnings = check_scenes(run)
    if errors:
        raise StudioError("Dữ liệu cảnh còn lỗi:\n  " + "\n  ".join(errors))
    scenes = read_json(motion_dir(run) / "canh.json")["canh"]
    profile = run.profile
    voice = voice_seconds(run)
    write_json(run.dir / "scenes.json", {"canh": [
        {"id": sc["id"], "chuong": sc.get("chuong"), "narration": sc.get("narration", ""),
         "visual_prompt": f"Motion template {sc['template']} for scene {sc['id']}", "audio_note": "",
         "planned_sec": scene_seconds(sc.get("narration", ""), profile, voice), "template": sc["template"],
         "nguon": sc.get("nguon") or [], "thu": bool(sc.get("thu"))}
        for sc in scenes]})
    run.log("Nạp cảnh motion", "ok", chi_tiet=f"{len(scenes)} cảnh, {len(warnings)} cảnh báo")
    return len(scenes), warnings


# ---------------------------------------------------------------- dựng HTML và render

def project_dir(run):
    return motion_dir(run) / "du_an"


def dung_canh(run):
    """Ghi trang HTML của từng cảnh vào motion/du_an/scenes."""
    errors, _ = check_scenes(run)
    if errors:
        raise StudioError("Dữ liệu cảnh còn lỗi:\n  " + "\n  ".join(errors))
    gsap = PROJECT / "motion" / "vendor" / "gsap.min.js"
    template = PROJECT / "motion" / "mau_du_an"
    if not gsap.is_file() or not template.is_dir():
        raise StudioError("Thiếu motion/vendor/gsap.min.js hoặc motion/mau_du_an")
    dest = project_dir(run)
    (dest / "assets").mkdir(parents=True, exist_ok=True)
    (dest / "scenes").mkdir(exist_ok=True)
    shutil.copy2(gsap, dest / "assets" / "gsap.min.js")
    ban_do_map = motion_dir(run) / "ban_do" / "ban_do_map.js"   # tools/gunmap.py tạo, dùng cho mẫu ban_do
    if ban_do_map.is_file():
        shutil.copy2(ban_do_map, dest / "assets" / "ban_do_map.js")
    anh = motion_dir(run) / "anh"    # ảnh phạm vi công cộng của run (chân dung...), nguồn ghi trong anh/NGUON_ANH.md
    if anh.is_dir():
        (dest / "assets" / "anh").mkdir(exist_ok=True)
        for f in anh.iterdir():
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
                shutil.copy2(f, dest / "assets" / "anh" / f.name)
    for f in template.iterdir():
        shutil.copy2(f, dest / f.name)
    scenes = read_json(motion_dir(run) / "canh.json")["canh"]
    profile = run.profile
    voice = voice_seconds(run)
    total = 0.0
    for sc in scenes:
        seconds = scene_seconds(sc.get("narration", ""), profile, voice)
        total += seconds
        (dest / "scenes" / f"{sc['id']}.html").write_text(mau_motion.build(sc, seconds), encoding="utf-8")
    run.log("Dựng trang HTML cảnh motion", "ok", chi_tiet=f"{len(scenes)} cảnh, tổng {total / 60:.1f} phút")
    return len(scenes)


def _env():
    env = os.environ.copy()
    if NODE_DIR.is_dir() and str(NODE_DIR) not in env.get("PATH", ""):
        env["PATH"] = str(NODE_DIR) + os.pathsep + env.get("PATH", "")
    return env


def ve_canh(run, ids=None, lam_lai=False, runner=subprocess.run):
    """Render các cảnh thành clip motion/out/S001.mp4... Cảnh đã có clip thì bỏ qua, trừ khi lam_lai."""
    env = _env()
    npx = shutil.which("npx.cmd", path=env["PATH"]) or shutil.which("npx", path=env["PATH"])
    if not npx:
        raise StudioError("Chưa cài Node.js. Cài bằng: winget install OpenJS.NodeJS.LTS")
    proj = project_dir(run)
    pages = sorted((proj / "scenes").glob("S*.html")) if (proj / "scenes").is_dir() else []
    if not pages:
        raise StudioError("Chưa có trang cảnh, hãy chạy dung-canh trước")
    wanted = set(ids) if ids else None
    out = motion_dir(run) / "out"
    out.mkdir(exist_ok=True)
    fps = str(run.profile["dung"]["fps"])
    done, skipped = [], []
    for page in pages:
        sid = page.stem
        if wanted is not None and sid not in wanted:
            continue
        target = out / f"{sid}.mp4"
        if target.is_file() and not lam_lai:
            skipped.append(sid)
            continue
        cmd = [npx, "--yes", HYPERFRAMES, "render", "-c", f"scenes/{sid}.html", "-o", str(target), "--fps", fps]
        try:
            res = runner(cmd, cwd=proj, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace",
                         timeout=RENDER_TIMEOUT)
        except subprocess.TimeoutExpired as e:
            raise StudioError(f"{sid}: render quá {RENDER_TIMEOUT} giây") from e
        if res.returncode != 0 or not target.is_file():
            tail = "\n".join((res.stderr or res.stdout or "").strip().splitlines()[-6:])
            run.log(f"Render cảnh {sid}", "loi", chi_tiet=tail[:500])
            raise StudioError(f"{sid}: render lỗi\n{tail}")
        done.append(sid)
    if wanted and not (set(done) | set(skipped)) >= wanted:
        raise StudioError("Không có cảnh: " + ", ".join(sorted(wanted - set(done) - set(skipped))))
    run.log("Render cảnh motion", "ok", chi_tiet=f"{len(done)} cảnh mới, {len(skipped)} cảnh đã có")
    return done, skipped
