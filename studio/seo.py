"""Thông tin đăng tải YouTube và trang xem lại trước khi duyệt lần cuối."""
import html
import re
from datetime import datetime, timezone
from pathlib import Path

from .core import StudioError, read_json, write_json
from .duyet import THUMBNAIL

TITLE_MAX = 100
DESCRIPTION_MAX_BYTES = 5000
TAGS_MAX_CHARS = 500
FILE_NAME = re.compile(r"[^\\/:*?\"<>|]+\.mp4")


def create_metadata(run):
    """Tạo bản khung từ hồ sơ kênh. Tiêu đề, mô tả và thẻ được viết sau đó."""
    path = run.dir / "publish" / "metadata.json"
    if path.exists():
        raise StudioError("publish/metadata.json đã có")
    profile = run.profile
    yt = profile["youtube"]
    lang = profile["kenh"]["ngon_ngu"]
    write_json(path, {
        "tieu_de": "", "mo_ta": "", "the": list(yt.get("the_co_dinh") or []), "hashtag": list(yt.get("hashtag") or []),
        "ten_tep": "", "category_id": str(yt["category_id"]), "ngon_ngu": lang, "ngon_ngu_am_thanh": lang,
        "tre_em": yt.get("tre_em"), "noi_dung_tong_hop": yt.get("noi_dung_tong_hop"),
        "danh_sach_phat": yt.get("danh_sach_phat"), "lich_dang": None, "tai_phu_de": True,
    })
    return path


def parse_schedule(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value or ""):
        raise ValueError
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def check_metadata(run):
    """Trả về danh sách lỗi của publish/metadata.json."""
    path = run.dir / "publish" / "metadata.json"
    if not path.is_file():
        return ["Chưa có publish/metadata.json"]
    m = read_json(path)
    errors = []
    title, desc = m.get("tieu_de") or "", m.get("mo_ta") or ""
    tags = m.get("the") or []
    if not 1 <= len(title) <= TITLE_MAX:
        errors.append(f"Tiêu đề phải dài từ 1 đến {TITLE_MAX} ký tự")
    if not desc:
        errors.append("Thiếu mô tả")
    if len(desc.encode("utf-8")) > DESCRIPTION_MAX_BYTES:
        errors.append(f"Mô tả vượt {DESCRIPTION_MAX_BYTES} byte")
    if any(c in title + desc for c in "<>"):
        errors.append("Tiêu đề và mô tả không được có dấu < hoặc >")
    # YouTube tính cả dấu phẩy giữa các thẻ và cặp ngoặc kép của thẻ có khoảng trắng
    if sum(len(t) + 2 * (" " in t) for t in tags) + max(len(tags) - 1, 0) > TAGS_MAX_CHARS:
        errors.append(f"Tổng độ dài thẻ vượt {TAGS_MAX_CHARS} ký tự")
    for tag in m.get("hashtag") or []:
        if tag not in desc:
            errors.append(f"Hashtag {tag} chưa có trong mô tả")
    if not FILE_NAME.fullmatch(m.get("ten_tep") or ""):
        errors.append("ten_tep phải là tên tệp hợp lệ kết thúc bằng .mp4")
    for field in ("tre_em", "noi_dung_tong_hop"):
        if not isinstance(m.get(field), bool):
            errors.append(f"{field} phải là true hoặc false")
    if not m.get("category_id"):
        errors.append("Thiếu category_id")
    if m.get("lich_dang"):
        try:
            if parse_schedule(m["lich_dang"]) <= datetime.now(timezone.utc):
                errors.append("lich_dang đã ở trong quá khứ")
        except ValueError:
            errors.append("lich_dang phải có dạng 2026-12-31T13:00:00Z (giờ UTC)")
    low = f"{title}\n{desc}\n{' '.join(tags)}".lower()
    for w in run.profile["noi_dung"].get("tu_cam") or []:
        if w and str(w).lower() in low:
            errors.append(f"Có từ cấm \"{w}\"")
    if (run.dir / "publish").is_dir():
        extras = [p.name for p in (run.dir / "publish").iterdir()
                  if p.name.startswith("thumbnail") and p.name != Path(THUMBNAIL).name]
        if extras:
            errors.append(f"Thumbnail phải tên thumbnail.jpg, đang có {', '.join(extras)}")
    return errors


def write_review_page(run):
    """Trang tĩnh để xem video và toàn bộ thông tin trước khi duyệt Cổng 3."""
    from .qc import require_qc_passed
    qc = require_qc_passed(run)
    m = read_json(run.dir / "publish" / "metadata.json")
    e = html.escape
    rows = [
        ("Tiêu đề", m.get("tieu_de")), ("Mô tả", m.get("mo_ta")), ("Thẻ", ", ".join(m.get("the") or [])),
        ("Hashtag", " ".join(m.get("hashtag") or [])), ("Tên tệp", m.get("ten_tep")),
        ("Danh mục", m.get("category_id")), ("Ngôn ngữ", m.get("ngon_ngu")),
        ("Danh sách phát", m.get("danh_sach_phat") or "Không"),
        ("Quyền riêng tư khi tải lên", "Riêng tư"),
        ("Lịch đăng (UTC)", m.get("lich_dang") or "Không, video giữ ở chế độ riêng tư"),
        ("Dành cho trẻ em", "Có" if m.get("tre_em") else "Không"),
        ("Khai báo nội dung tổng hợp", "Có" if m.get("noi_dung_tong_hop") else "Không"),
        ("Tải phụ đề lên", "Có" if m.get("tai_phu_de") else "Không"),
    ]
    table = "".join(f"<tr><th>{e(k)}</th><td>{e(str(v or ''))}</td></tr>" for k, v in rows)
    warnings = "".join(f"<li>{e(w)}</li>" for w in qc["canh_bao"]) or "<li>Không có</li>"
    thumb = f'<h2>Thumbnail</h2><img src="../{THUMBNAIL}" alt="Thumbnail">' if (run.dir / THUMBNAIL).is_file() else \
        "<h2>Thumbnail</h2><p>Chưa có, YouTube sẽ tự chọn khung hình.</p>"
    page = f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Duyệt video</title>
<style>
body{{font:16px/1.5 system-ui,sans-serif;max-width:960px;margin:0 auto;padding:16px;background:#fff;color:#111}}
video,img{{width:100%;height:auto;background:#000}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #bbb;padding:8px;text-align:left;vertical-align:top;white-space:pre-wrap}}
th{{width:28%}}
</style></head><body>
<h1>Duyệt lần cuối: {e(run.name)}</h1>
<video controls src="../render/final.mp4"><track kind="subtitles" src="../render/final.srt"></video>
{thumb}
<h2>Thông tin đăng tải</h2><table>{table}</table>
<h2>Cảnh báo khi kiểm tra</h2><ul>{warnings}</ul>
<p>Sau khi xem xong, chạy trong cửa sổ dòng lệnh: <code>python -m studio duyet {e(run.name)} G3</code></p>
</body></html>
"""
    path = run.dir / "review" / "index.html"
    path.parent.mkdir(exist_ok=True)
    path.write_text(page, encoding="utf-8")
    return path
