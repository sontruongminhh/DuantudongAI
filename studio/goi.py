"""Kiểm tra gói nội dung và xuất prompt gửi Muse."""
import csv
import re

from .core import StudioError, brief_sections, load_engine, read_json, write_json

# Prompt hình ảnh không được yêu cầu chữ, lời thoại hoặc phụ đề
TEXT_REQUEST = re.compile(
    r"\b(subtitles?|captions?|voice ?-?overs?|narrat\w+|on-screen text|title card|speech bubbles?|says?|saying)\b"
    r"|phụ đề|lời thoại|lời thuyết minh|lời đọc|chữ trên màn hình",
    re.I)
QUOTED = re.compile(r"[\"“”「」『』]")
# Phần phủ định như "no subtitles" là hợp lệ
NEGATED = re.compile(r"\b(no|without|not|không có|không)\s+[^,.;]*", re.I)
SCENE_ID = "S{:03d}"
OVERLAP_CHARS = 24  # đủ dài để không báo nhầm các cụm chung như tên địa danh
IMAGE_BUDGET_TOLERANCE = 1.25
BATCH_SIZE = 25


def narration_budget(scene_sec, profile):
    """Số ký tự lời đọc tối đa vừa với cảnh. clip.ky_tu_toi_da (nếu có) cố định con số này cho cảnh thường,
    để đổi giọng hay tốc độ đọc giữa chừng mà cách chia cảnh vẫn như cũ."""
    fixed = profile["clip"].get("ky_tu_toi_da")
    if fixed and scene_sec >= float(profile["clip"]["thoi_luong_giay"]):
        return int(fixed)
    engine = load_engine()
    cfg = engine.DEFAULT_CONFIG
    # Cùng tốc độ đọc với motion.scene_seconds (giong.ky_tu_moi_giay đo từ giọng thật), nếu không thì cảnh
    # dài theo lời đọc luôn bị báo thiếu chỗ khi giọng thật đọc nhanh hơn hằng số của engine
    cps = profile["giong"].get("ky_tu_moi_giay") or engine.CHARS_PER_SEC.get(profile["kenh"]["ngon_ngu"], engine.DEFAULT_CPS)
    speed = profile["giong"].get("toc_do") or 1.0
    # Chế độ ảnh: độ dài cảnh chỉ là ước lượng và sẽ theo giọng thật, nên chỉ chặn lời đọc lệch quá xa
    if image_mode(profile):
        return int(scene_sec * cps * speed * IMAGE_BUDGET_TOLERANCE)
    # Clip có độ dài cố định, được phép làm chậm tới clip.keo_cham để vừa lời đọc
    usable = scene_sec * (profile["clip"].get("keo_cham") or 1.0)
    return int(max(usable - cfg["dem_dau"] - cfg["dem_cuoi"], 0) * cps * speed)


def image_mode(profile):
    return profile["clip"].get("che_do") == "anh"


def _banned_hits(text, banned):
    low = text.lower()
    return [w for w in banned if w and str(w).lower() in low]


def check_brief(run):
    """Trả về danh sách lỗi của brief.md."""
    sections = brief_sections(run)
    return [f"brief.md: mục \"{name}\" còn trống" for name, body in sections.items() if not body] \
        or ([] if sections else ["brief.md: không có mục nào"])


def check_package(run):
    """Trả về (lỗi, cảnh báo) của scenes.json."""
    profile = run.profile
    scenes = run.scenes()
    banned = profile["noi_dung"].get("tu_cam") or []
    clip_sec = float(profile["clip"]["thoi_luong_giay"])
    errors, warnings = [], []
    if not scenes:
        return ["scenes.json chưa có cảnh nào"], []

    seen_prompts = {}
    total = 0.0
    for i, sc in enumerate(scenes, start=1):
        want = SCENE_ID.format(i)
        sid = sc.get("id")
        if sid != want:
            errors.append(f"Cảnh thứ {i}: id phải là {want}, đang là {sid}")
        sid = sid or want
        narration = (sc.get("narration") or "").strip()
        prompt = (sc.get("visual_prompt") or "").strip()
        try:
            sec = float(sc.get("planned_sec"))
        except (TypeError, ValueError):
            errors.append(f"{sid}: planned_sec không hợp lệ")
            sec = clip_sec
        total += sec
        if sec <= 0 or sec > clip_sec:
            errors.append(f"{sid}: planned_sec {sec:g} phải nằm trong khoảng 0 đến {clip_sec:g} giây")

        if not prompt:
            errors.append(f"{sid}: thiếu visual_prompt")
        positive = NEGATED.sub("", prompt)
        hit = TEXT_REQUEST.search(positive)
        if hit:
            errors.append(f"{sid}: visual_prompt yêu cầu chữ hoặc lời đọc (\"{hit[0]}\")")
        if QUOTED.search(positive):
            errors.append(f"{sid}: visual_prompt có dấu ngoặc kép, có thể khiến công cụ vẽ chữ")
        compact = re.sub(r"\s+", "", narration)
        prompt_compact = re.sub(r"\s+", "", prompt)
        window = min(OVERLAP_CHARS, len(compact))
        if window and any(compact[k:k + window] in prompt_compact for k in range(len(compact) - window + 1)):
            errors.append(f"{sid}: visual_prompt chứa nguyên văn lời đọc")

        # Cảnh dài theo lời đọc (clip.thoi_luong_thay_doi) đã được định độ dài cho vừa lời, có khi theo giọng thật
        # đọc nhanh hơn ước lượng; chỉ còn phải chặn lời quá dài so với cảnh dài nhất
        variable = profile["clip"].get("thoi_luong_thay_doi") and not image_mode(profile)
        budget = narration_budget(clip_sec if variable else sec, profile)
        if len(narration) > budget:
            errors.append(f"{sid}: lời đọc {len(narration)} ký tự, vượt giới hạn {budget} ký tự của cảnh")
        if "\n\n" in narration:
            errors.append(f"{sid}: lời đọc không được có dòng trống")
        if not narration:
            warnings.append(f"{sid}: cảnh không có lời đọc")

        for w in _banned_hits(f"{narration}\n{prompt}", banned):
            errors.append(f"{sid}: có từ cấm \"{w}\"")
        if prompt in seen_prompts:
            warnings.append(f"{sid}: visual_prompt trùng với {seen_prompts[prompt]}")
        seen_prompts.setdefault(prompt, sid)

    target = float(profile["noi_dung"]["do_dai_phut"]) * 60
    if target and abs(total - target) / target > 0.15:
        warnings.append(f"Tổng thời lượng {total / 60:.1f} phút lệch hơn 15% so với mục tiêu "
                        f"{target / 60:g} phút")
    return errors, warnings


def require_package_ok(run):
    errors, _ = check_package(run)
    if errors:
        raise StudioError("Gói nội dung còn lỗi:\n  " + "\n  ".join(errors))


def build_prompt(scene, profile):
    """Ghép khối phong cách cố định vào prompt của cảnh."""
    if image_mode(profile):  # prompt từ shotlist đã có sẵn phong cách
        return scene["visual_prompt"].strip()
    style = profile["hinh_anh"]
    parts = [style.get("khoi_phong_cach"), style.get("mau_sac"), style.get("anh_sang"),
             scene["visual_prompt"].strip(), style.get("them_cuoi_prompt")]
    return ". ".join(str(p).strip().rstrip(".") for p in parts if p) + "."


def import_shotlist(run):
    """Chuyển shotlist.json của quy trình dựng bằng ảnh thành scenes.json để kiểm tra và duyệt."""
    path = run.dir / "shotlist.json"
    if not path.is_file():
        raise StudioError("Chưa có shotlist.json")
    shots = read_json(path)["shots"]
    if not shots:
        raise StudioError("shotlist.json chưa có cảnh nào")
    write_json(run.dir / "scenes.json", {"canh": [
        {"id": SCENE_ID.format(i), "ma_shot": s["id"], "chuong": s["chapter"], "narration": s["narration"],
         "visual_prompt": s["prompt"], "audio_note": " · ".join(s.get("sound") or []), "planned_sec": s["duration"],
         "tham_chieu": s.get("refs") or []}
        for i, s in enumerate(shots, start=1)]})
    run.log("Nạp shotlist", "ok", chi_tiet=f"{len(shots)} cảnh")
    return len(shots)


def _clip_prompt(group, bible):
    """Ghép mô tả cố định với cảnh để mọi clip giữ cùng nhân vật, lều và phong cách."""
    first = group[0]["blueprint"]
    refs = sorted({r for s in group for r in s.get("refs") or []})
    place = first.get("setting") or bible["ice_age"]
    parts = [bible["style"], place] + [bible["blocks"][r] for r in refs if r in bible["blocks"]]
    scene = f"{first['shot_angle']}. {first['subject_action']}. {first['atmosphere']}. {first['lighting_palette']}"
    if len(group) > 1:
        scene += f". Camera then drifts to show: {group[1]['blueprint']['subject_action']}"
    extras = [bible["fixes"][k] for k in ("mammoth", "figurine") if k in scene.lower()]
    scene = scene.replace("one small finger resting at the cheek", bible["fixes"]["child_hand"])
    tail = [scene] + extras + [bible["motion"][group[0]["pace"]]]
    # Bản ngắn dùng trong tin nhắn hàng loạt: mô tả cố định chỉ ghi một lần ở đầu tin nhắn
    names = [bible["blocks"][r].split(",")[0] for r in refs if r in bible["blocks"]]
    short = [f"Place: {first['setting']}"] if first.get("setting") else []
    short += [f"Uses: {', '.join(names)}"] if names else []
    return ". ".join(parts + tail) + ".", ". ".join(short + tail) + "."


def import_shotlist_as_clips(run):
    """Gộp các dòng lời đọc thành clip 10 giây của Muse, mỗi clip có prompt video đầy đủ."""
    path, bible_path = run.dir / "shotlist.json", run.dir / "muse" / "bo_quy_chuan.json"
    if not path.is_file() or not bible_path.is_file():
        raise StudioError("Cần shotlist.json và muse/bo_quy_chuan.json")
    profile = run.profile
    if image_mode(profile):
        raise StudioError("Hồ sơ đang ở chế độ ảnh")
    bible = read_json(bible_path)
    clip_sec = float(profile["clip"]["thoi_luong_giay"])
    limit = narration_budget(clip_sec, profile)
    groups, current, chars = [], [], 0
    for shot in read_json(path)["shots"]:
        size = len(shot["narration"])
        if current and (current[-1]["chapter"] != shot["chapter"] or chars + 1 + size > limit):
            groups.append(current)
            current, chars = [], 0
        current.append(shot)
        chars += size + 1
    groups.append(current)
    scenes = []
    for i, g in enumerate(groups, start=1):
        full, short = _clip_prompt(g, bible)
        scenes.append({
            "id": SCENE_ID.format(i), "ma_shot": [s["id"] for s in g], "chuong": g[0]["chapter"],
            "narration": " ".join(s["narration"] for s in g), "visual_prompt": full, "prompt_ngan": short,
            "audio_note": " · ".join(x for s in g for x in s.get("sound") or []), "planned_sec": clip_sec,
            "tham_chieu": sorted({r for s in g for r in s.get("refs") or []})})
    write_json(run.dir / "scenes.json", {"canh": scenes})
    run.log("Gộp cảnh thành clip", "ok", chi_tiet=f"{len(scenes)} clip")
    return len(scenes)


def export_batches(run, size=BATCH_SIZE):
    """Tin nhắn hàng loạt gửi Muse. Chỉ chạy khi gói đã qua Cổng 2."""
    from .duyet import verify_gate
    verify_gate(run, "G2")
    scenes = run.scenes()
    bible = read_json(run.dir / "muse" / "bo_quy_chuan.json")
    head = (f"Create videos with Muse Video in the exact order below. Each clip is 16:9 and about 10 seconds. "
            f"Do not ask questions. Keep running when I say continue. Name each file exactly with its clip id, "
            f"for example S001.mp4. Apply these fixed rules to every clip. STYLE: {bible['style']}. "
            f"DEFAULT PLACE: {bible['ice_age']}. " + " ".join(f"{v}." for v in bible["blocks"].values()) + " CLIPS:")
    out = run.dir / "muse" / "lo"
    out.mkdir(parents=True, exist_ok=True)
    files = []
    for n in range(0, len(scenes), size):
        batch = scenes[n:n + size]
        lines = [f"{sc['id']}: {sc['prompt_ngan']}" for sc in batch]
        path = out / f"lo_{n // size + 1:02d}.txt"
        path.write_text(head + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
        files.append(path)
    run.log("Xuất lô Muse", "ok", chi_tiet=f"{len(files)} lô, {len(scenes)} clip")
    return files


def write_review(run):
    """Bảng liên kết cảnh để xem khi duyệt gói nội dung."""
    def cell(text):
        return str(text or "").replace("|", "\\|").replace("\n", " ")
    rows = ["# Gói nội dung", "", "## Kịch bản", ""]
    scenes = run.scenes()
    rows += [sc["narration"].strip() + "\n" for sc in scenes if (sc.get("narration") or "").strip()]
    rows += ["## Bảng cảnh", "", "| Cảnh | Giây | Lời đọc | Prompt hình | Âm thanh |", "|---|---|---|---|---|"]
    rows += [f"| {sc['id']} | {sc['planned_sec']} | {cell(sc.get('narration'))} | "
             f"{cell(sc.get('visual_prompt'))} | {cell(sc.get('audio_note'))} |" for sc in scenes]
    path = run.dir / "goi_noi_dung.md"
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return path


def export_prompts(run):
    """Xuất prompt cho Muse. Chỉ chạy khi gói đã qua Cổng 2."""
    from .duyet import verify_gate
    verify_gate(run, "G2")
    profile = run.profile
    out = run.dir / "muse"
    out.mkdir(exist_ok=True)
    rows = [(sc["id"], build_prompt(sc, profile)) for sc in run.scenes()]
    (out / "prompts.md").write_text("".join(f"## {sid}\n\n{p}\n\n" for sid, p in rows), encoding="utf-8")
    with open(out / "prompts.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "prompt"])
        w.writerows(rows)
    run.log("Xuất prompt Muse", "ok", chi_tiet=f"{len(rows)} cảnh")
    return out / "prompts.md"
