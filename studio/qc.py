"""Kiểm tra video đã dựng: đủ cảnh, đúng thứ tự, tiếng, hình và phụ đề."""
import re
import subprocess

from .core import StudioError, load_engine, now_iso, read_json, sha256, write_json

DURATION_TOLERANCE = 0.5
BLACK_MIN_SEC = 1
SILENCE_MIN_SEC = 3
SILENCE_MAX_RATIO = 0.5


def analyze_stream(path):
    """Giải mã toàn bộ tệp một lần để tìm đoạn đen, đoạn im lặng và lỗi giải mã."""
    p = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "level+info", "-i", str(path),
         "-vf", f"blackdetect=d={BLACK_MIN_SEC}:pic_th=0.98", "-af", f"silencedetect=n=-50dB:d={SILENCE_MIN_SEC}",
         "-f", "null", "-"],
        capture_output=True, text=True, encoding="utf-8", errors="replace")
    log = p.stderr
    black = [(float(a), float(b)) for a, b in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    silence = [float(d) for d in re.findall(r"silence_duration: ([\d.]+)", log)]
    decode_errors = [ln.strip() for ln in log.splitlines() if "[error]" in ln or "[fatal]" in ln]
    if p.returncode != 0 and not decode_errors:
        decode_errors = [f"ffmpeg dừng với mã {p.returncode}"]
    return black, silence, decode_errors


def parse_srt(text):
    """Trả về [(bắt đầu, kết thúc, chữ)]."""
    def seconds(h, m, s, ms):
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    pattern = r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)\s*\n(.*?)(?=\n\s*\n|\Z)"
    for m in re.finditer(pattern, text, flags=re.S):
        out.append((seconds(*m.groups()[:4]), seconds(*m.groups()[4:8]), m[9].strip()))
    return out


def _compact(text):
    return re.sub(r"\s+", "", text)


def check_timeline(timeline, scenes, total, limits):
    """Đối chiếu timeline với kịch bản đã duyệt. Trả về (lỗi, cảnh báo)."""
    errors, warnings = [], []
    want = [sc["id"] for sc in scenes]
    got = [c["file"].rsplit(".", 1)[0] for c in timeline["clips"]]
    if got != want:
        errors.append(f"Thứ tự cảnh sai hoặc thiếu cảnh: có {len(got)} clip, cần {len(want)}")
    if abs(timeline["tong_thoi_luong"] - total) > DURATION_TOLERANCE:
        errors.append(f"Video dài {total:.1f}s nhưng timeline ghi {timeline['tong_thoi_luong']:.1f}s")

    segments = timeline["doan_loi"]
    want_text = [re.sub(r"\s*\n\s*", " ", sc["narration"].strip()) for sc in scenes
                 if (sc.get("narration") or "").strip()]
    if [s["text"] for s in segments] != want_text:
        errors.append("Lời đọc trong timeline khác kịch bản đã duyệt")
    for a, b in zip(segments, segments[1:]):
        if a["voice_start"] + a["audio_dur"] > b["voice_start"] + 0.01:
            errors.append(f"Lời đọc chồng nhau ở clip {a['clips'][0]} và {b['clips'][0]}")
    if segments and segments[-1]["voice_start"] + segments[-1]["audio_dur"] > total + 0.01:
        errors.append("Lời đọc cuối dài hơn video")

    original = sum(c["goc"] for c in timeline["clips"])
    ratio = (total - original) / original if original else 0
    if ratio > limits.get("keo_hinh_toi_da_ti_le", 0.05):
        warnings.append(f"Hình bị kéo dài {ratio:.1%} so với clip gốc")
    max_freeze = limits.get("dung_hinh_toi_da_giay", 1.5)
    for c in timeline["clips"]:
        if c["dung_hinh"] > max_freeze:
            warnings.append(f"{c['file']}: dừng hình {c['dung_hinh']:.1f}s")
    return errors, warnings


def check_srt(srt, scenes, total):
    errors = []
    cues = parse_srt(srt)
    if not cues:
        return ["Phụ đề trống hoặc sai định dạng"]
    prev_end = 0.0
    for i, (start, end, _) in enumerate(cues, start=1):
        if end <= start or start < prev_end - 0.01:
            errors.append(f"Phụ đề dòng {i}: sai thứ tự thời gian")
        prev_end = end
    if prev_end > total + 0.01:
        errors.append("Phụ đề kéo dài quá hết video")
    narration = "".join(sc.get("narration") or "" for sc in scenes)
    if _compact("".join(c[2] for c in cues)) != _compact(narration):
        errors.append("Nội dung phụ đề khác kịch bản đã duyệt")
    return errors


def run_qc(run, folder="render"):
    """Ghi <folder>/qc.json và trả về kết quả."""
    engine = load_engine()
    out_dir = run.dir / folder
    final = out_dir / "final.mp4"
    for rel in ("final.mp4", "final.srt", "timeline.json"):
        if not (out_dir / rel).is_file():
            raise StudioError(f"Chưa có {folder}/{rel}. Hãy dựng video trước")
    profile = run.profile
    scenes = run.scenes()
    info = engine.probe(final)
    total = info["duration"]

    errors, warnings = check_timeline(read_json(out_dir / "timeline.json"), scenes, total, profile["dung"])
    errors += check_srt((out_dir / "final.srt").read_text(encoding="utf-8-sig"), scenes, total)
    if not info["has_audio"]:
        errors.append("Video không có âm thanh")
    want_size = list(profile["clip"]["do_phan_giai"])
    if [info["width"], info["height"]] != want_size:
        errors.append(f"Độ phân giải {info['width']}x{info['height']}, hồ sơ yêu cầu {want_size[0]}x{want_size[1]}")

    black, silence, decode_errors = analyze_stream(final)
    errors += [f"Lỗi giải mã: {e[:200]}" for e in decode_errors[:5]]
    errors += [f"Màn hình đen từ {a:.1f}s đến {b:.1f}s" for a, b in black]
    if total and sum(silence) / total > SILENCE_MAX_RATIO:
        errors.append(f"Hơn {SILENCE_MAX_RATIO:.0%} video bị im lặng")
    warnings += [f"Có đoạn im lặng {d:.1f}s" for d in silence]

    result = {"dat": not errors, "luc": now_iso(), "sha256_video": sha256(final), "thoi_luong": round(total, 3),
              "loi": errors, "canh_bao": warnings}
    write_json(out_dir / "qc.json", result)
    run.log(f"Kiểm tra video ({folder})", "ok" if not errors else "loi", chi_tiet=f"{len(errors)} lỗi, {len(warnings)} cảnh báo")
    return result


def require_qc_passed(run):
    """Cổng 3 chỉ nhận video thật đã qua kiểm tra, đúng tệp đang có."""
    path = run.dir / "render" / "qc.json"
    final = run.dir / "render" / "final.mp4"
    if not final.is_file():
        raise StudioError("Chưa có video thật trong render/. Bản giả lập không được duyệt để đăng")
    if not path.is_file():
        raise StudioError("Video chưa được kiểm tra")
    qc = read_json(path)
    if not qc["dat"]:
        raise StudioError("Video chưa đạt kiểm tra:\n  " + "\n  ".join(qc["loi"]))
    if qc["sha256_video"] != sha256(final):
        raise StudioError("Video đã đổi sau khi kiểm tra. Hãy kiểm tra lại")
    return qc
