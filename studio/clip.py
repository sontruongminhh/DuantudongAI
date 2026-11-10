"""Nhận clip Muse vào đúng số cảnh và kiểm tra thông số."""
import shutil
from pathlib import Path

from .core import StudioError, load_engine, sha256, write_json
from .duyet import verify_gate

DURATION_TOLERANCE = 0.5


def _videos(folder):
    engine = load_engine()
    return [p for p in Path(folder).iterdir() if p.suffix.lower() in engine.VIDEO_EXT]


def import_clips(run, source, by_time=False, overwrite=False):
    """Chép clip từ thư mục tải về vào clips/S001.mp4... Không xóa tệp nguồn."""
    verify_gate(run, "G2")
    engine = load_engine()
    source = Path(source)
    if not source.is_dir():
        raise StudioError(f"Không thấy thư mục {source}")
    scenes = run.scenes()
    files = _videos(source)
    if len(files) != len(scenes):
        raise StudioError(f"Có {len(files)} clip nhưng gói có {len(scenes)} cảnh")
    key = (lambda p: p.stat().st_mtime) if by_time else (lambda p: engine.natural_key(p.name))
    files.sort(key=key)
    clips_dir = run.dir / "clips"
    existing = _videos(clips_dir)
    if existing and not overwrite:
        raise StudioError("clips/ đã có tệp. Thêm --ghi-de nếu muốn thay toàn bộ")
    for p in existing:
        p.unlink()
    manifest = []
    for sc, src in zip(scenes, files):
        dst = clips_dir / f"{sc['id']}{src.suffix.lower()}"
        shutil.copy2(src, dst)
        manifest.append({"canh": sc["id"], "nguon": src.name, "sha256": sha256(dst)})
    write_json(clips_dir / "manifest.json", {"thu_tu": "thoi_gian" if by_time else "ten_tep", "tep": manifest})
    run.log("Nhận clip Muse", "ok", "thu_cong", f"{len(files)} clip, xếp theo {'thời gian' if by_time else 'tên tệp'}")
    return manifest


def check_clips(run):
    """Trả về (lỗi, cảnh báo) của thư mục clip."""
    engine = load_engine()
    profile = run.profile
    want_size = list(profile["clip"]["do_phan_giai"])
    scenes = run.scenes()
    files = {p.stem: p for p in _videos(run.dir / "clips")}
    errors, warnings = [], []
    for sc in scenes:
        path = files.pop(sc["id"], None)
        if not path:
            errors.append(f"{sc['id']}: thiếu clip")
            continue
        try:
            info = engine.probe(path)
        except (RuntimeError, KeyError, ValueError) as e:
            errors.append(f"{sc['id']}: không đọc được clip ({str(e)[:120]})")
            continue
        planned = float(sc["planned_sec"])
        if abs(info["duration"] - planned) > DURATION_TOLERANCE:
            warnings.append(f"{sc['id']}: clip dài {info['duration']:.1f}s, dự kiến {planned:g}s")
        if [info["width"], info["height"]] != want_size:
            warnings.append(f"{sc['id']}: độ phân giải {info['width']}x{info['height']}, "
                            f"hồ sơ yêu cầu {want_size[0]}x{want_size[1]}")
    errors += [f"{name}: tệp không thuộc cảnh nào" for name in sorted(files)]
    return errors, warnings
