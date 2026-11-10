"""Gọi công cụ dựng trong engine/ với dữ liệu của lần chạy."""
import re

from .clip import check_clips
from .core import StudioError, load_engine, read_json
from .duyet import verify_gate
from .goi import image_mode, require_package_ok

# Bản thật và bản thử nằm ở hai thư mục khác nhau. Cổng 3 chỉ nhận render/.
OUTPUT_DIR = {"that": "render", "gia_lap": "render_gia_lap", "kiem_tra": "render_gia_lap"}
TRIMMED_DIR = "clips_cat"
TRIM_GAP = 0.4
TRIM_SHORTEST = 3.0


def build_config(profile):
    engine = load_engine()
    giong, dung, clip = profile["giong"], profile["dung"], profile["clip"]
    cfg = dict(engine.DEFAULT_CONFIG)
    cfg.update(
        provider=giong["provider"], model_id=giong.get("model_id"), voice_id=giong.get("voice_id"),
        ngon_ngu=profile["kenh"]["ngon_ngu"], toc_do=giong.get("toc_do") or 1.0,
        toc_do_toi_da=giong.get("toc_do_toi_da") or cfg["toc_do_toi_da"],
        am_luong_goc=dung.get("am_luong_goc") or 0.0,
        am_luong_nhac=dung.get("am_luong_nhac", cfg["am_luong_nhac"]),
        phu_de=dung.get("phu_de_in", True), do_phan_giai=list(clip["do_phan_giai"]), fps=dung["fps"],
        phu_de_kieu=dung.get("phu_de_kieu"),
    )
    return cfg


READINGS_FILE = "cach_doc.json"


def load_readings(run):
    """Bảng cách đọc tên riêng của lần chạy ({"新発田": "しばた"}); không có tệp thì trả về {}."""
    path = run.dir / READINGS_FILE
    if not path.is_file():
        return {}
    data = read_json(path)
    if not isinstance(data, dict) or not all(isinstance(k, str) and isinstance(v, str) and k and v
                                             for k, v in data.items()):
        raise StudioError(f"{READINGS_FILE} phải là object {{chữ: cách đọc}}, cả hai đều là chuỗi không rỗng")
    return data


def music_file(run):
    dung = run.profile["dung"]
    rel = dung.get("nhac_nen")
    if not rel:
        return None
    if not dung.get("nhac_nen_giay_phep"):
        raise StudioError("Có nhạc nền nhưng hồ sơ chưa ghi nhac_nen_giay_phep")
    path = run.channel_dir / rel
    if not path.is_file():
        raise StudioError(f"Không thấy nhạc nền {path}")
    return path


def write_engine_inputs(run, out_dir):
    """Viết lời đọc đúng theo số cảnh, không qua bước tự đoán đoạn."""
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt = out_dir / "mo_ta_giong.md"
    prompt.write_text(f"## Mô tả giọng đọc\n\n{run.profile['giong']['mo_ta']}\n", encoding="utf-8")
    lines = []
    for n, sc in enumerate(run.scenes(), start=1):
        text = re.sub(r"\s*\n\s*", " ", (sc.get("narration") or "").strip())
        if text:
            lines.append(f"[{n}] {text}")
    script = out_dir / "loi_doc.txt"
    script.write_text("\n\n".join(lines) + "\n", encoding="utf-8")
    readings = load_readings(run)
    if readings:
        # Bản gửi đi đọc sau khi thay tên riêng, chỉ để soát (phụ đề vẫn lấy loi_doc.txt)
        engine = load_engine()
        (out_dir / "loi_doc_giong.txt").write_text(engine.doc_theo_bang(script.read_text(encoding="utf-8"), readings),
                                                   encoding="utf-8")
    return prompt, script


def trim_targets(timeline, cfg, gap=TRIM_GAP, shortest=TRIM_SHORTEST):
    """Độ dài mới của từng clip, đủ cho lời đọc của nó và một khoảng nghỉ ngắn."""
    voice = {seg["clips"][0]: seg["audio_dur"] for seg in timeline["doan_loi"]}
    targets = {}
    for n, clip in enumerate(timeline["clips"], start=1):
        wanted = voice.get(n, 0) + cfg["dem_dau"] + cfg["dem_cuoi"] + gap
        targets[clip["file"]] = round(min(max(wanted, shortest), clip["goc"]), 3)
    return targets


def trim_clips(run):
    """Cắt clip vừa lời đọc vào clips_cat/ dựa trên bản dựng đã có. Clip gốc giữ nguyên, không gọi Genmax."""
    verify_gate(run, "G2")
    engine = load_engine()
    path = run.dir / "render" / "timeline.json"
    if not path.is_file():
        raise StudioError("Chưa có render/timeline.json. Hãy dựng video một lần trước")
    targets = trim_targets(read_json(path), build_config(run.profile))
    out = run.dir / TRIMMED_DIR
    out.mkdir(exist_ok=True)
    for name, seconds in targets.items():
        engine.run(["ffmpeg", "-y", "-i", str(run.dir / "clips" / name), "-t", str(seconds), "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", str(out / name)])
    total = sum(targets.values())
    run.log("Cắt clip vừa lời đọc", "ok", chi_tiet=f"{len(targets)} clip, {total / 60:.1f} phút")
    return total


def render(run, mode="that"):
    """mode: "that" tốn credit Genmax, "gia_lap" dùng tiếng bíp, "kiem_tra" chỉ ước lượng."""
    verify_gate(run, "G2")
    require_package_ok(run)
    if image_mode(run.profile):
        raise StudioError("Lần chạy này dùng chế độ ảnh, lệnh dung cho clip chưa áp dụng được")
    errors, warnings = check_clips(run)
    if errors:
        raise StudioError("Clip còn lỗi:\n  " + "\n  ".join(errors))
    for w in warnings:
        print(f"  ! {w}")

    engine = load_engine()
    profile = run.profile
    out_dir = run.dir / OUTPUT_DIR[mode]
    prompt, script = write_engine_inputs(run, out_dir)
    cfg = build_config(profile)
    cfg["cach_doc"] = load_readings(run) or None
    # Dựng lại thì kết quả kiểm tra cũ không còn giá trị
    (out_dir / "qc.json").unlink(missing_ok=True)
    clip_dir = run.dir / TRIMMED_DIR if (run.dir / TRIMMED_DIR).is_dir() else run.dir / "clips"
    try:
        result = engine.run_pipeline(clip_dir, prompt, out_dir, cfg, mode, user_keys=cfg.keys(),
                                     script_file=script, music=music_file(run))
    except (engine.GenmaxError, ValueError, RuntimeError) as e:
        run.log(f"Dựng video ({mode})", "loi", chi_tiet=str(e)[:500])
        raise StudioError(str(e)) from e
    run.log(f"Dựng video ({mode})", "ok", chi_tiet=str(result or "chỉ ước lượng"))
    return result
