"""Đường dẫn, trạng thái lần chạy và tiện ích dùng chung."""
import hashlib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

PROJECT = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("STUDIO_ROOT") or PROJECT)

REQUIRED_PROFILE = [
    "kenh.ten", "kenh.chu_de_chinh", "kenh.khan_gia", "kenh.ngon_ngu", "kenh.thi_truong",
    "noi_dung.phong_cach_ke", "noi_dung.do_dai_phut", "noi_dung.quy_chuan_nguon", "noi_dung.ban_quyen",
    "hinh_anh.khoi_phong_cach", "hinh_anh.mau_sac", "hinh_anh.anh_sang",
    "clip.thoi_luong_giay", "clip.do_phan_giai",
    "giong.mo_ta", "giong.provider",
    "dung.fps",
    "youtube.mau_tieu_de", "youtube.mau_mo_ta", "youtube.category_id",
]

BRIEF_TEMPLATE = """# Đề xuất chủ đề

## Chủ đề

## Từ khóa chính

## Từ khóa phụ

## Cụm từ người xem có thể tìm

## Ý định tìm kiếm

## Góc khai thác riêng

## Tiêu đề dự kiến

## Ý tưởng thumbnail

## Nguồn nghiên cứu

## Rủi ro
"""


class StudioError(Exception):
    pass


def load_env(path=PROJECT / ".env"):
    """Nạp tệp .env vào biến môi trường. Giá trị trong tệp được ưu tiên hơn biến cũ trên máy."""
    path = Path(path)
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name, sep, value = line.partition("=")
        name = name.strip()
        if sep and name and not name.startswith("#") and value.strip():
            os.environ[name] = value.strip().strip("\"'")


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)  # thay một lần, mất điện giữa chừng không làm hỏng tệp cũ


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_engine():
    """Nạp công cụ dựng trong engine/."""
    engine_dir = str(PROJECT / "engine")
    if engine_dir not in sys.path:
        sys.path.insert(0, engine_dir)
    import ai_film_studio
    return ai_film_studio


# ---------------------------------------------------------------- hồ sơ kênh

def load_profile(path):
    path = Path(path)
    if not path.is_file():
        raise StudioError(f"Không thấy hồ sơ {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8-sig")) or {}


def get_field(profile, dotted):
    value = profile
    for key in dotted.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value


def missing_fields(profile):
    return [f for f in REQUIRED_PROFILE if get_field(profile, f) in (None, "", [])]


def create_channel(channels_dir, name):
    if not re.fullmatch(r"[\w-]+", name) or name.startswith("_"):
        raise StudioError("Tên kênh chỉ gồm chữ, số, dấu gạch và không bắt đầu bằng _")
    dst = Path(channels_dir) / name
    if dst.exists():
        raise StudioError(f"Kênh {name} đã có")
    (dst / "assets").mkdir(parents=True)
    shutil.copy(PROJECT / "channels" / "_mau" / "profile.yaml", dst / "profile.yaml")
    return dst


# ---------------------------------------------------------------- lần chạy

class Run:
    def __init__(self, path):
        self.dir = Path(path)
        if not (self.dir / "state.json").is_file():
            raise StudioError(f"Không thấy lần chạy {self.dir}")

    @property
    def name(self):
        return self.dir.name

    @property
    def state(self):
        return read_json(self.dir / "state.json")

    @property
    def profile(self):
        return load_profile(self.dir / "profile.yaml")

    @property
    def channel_dir(self):
        return Path(self.state["thu_muc_kenh"])

    def update(self, **fields):
        write_json(self.dir / "state.json", {**self.state, **fields})

    def log(self, buoc, ket_qua, kieu="tu_dong", chi_tiet=""):
        """kieu: tu_dong | thu_cong | duyet. ket_qua: ok | canh_bao | loi."""
        st = self.state
        st["su_kien"].append({"luc": now_iso(), "buoc": buoc, "ket_qua": ket_qua, "kieu": kieu,
                              "chi_tiet": chi_tiet})
        write_json(self.dir / "state.json", st)

    def scenes(self):
        path = self.dir / "scenes.json"
        if not path.is_file():
            raise StudioError(f"Chưa có {path.name}")
        try:
            return read_json(path).get("canh", [])
        except json.JSONDecodeError as e:
            raise StudioError(f"{path.name} không phải JSON hợp lệ: {e}") from e


def create_run(channel_dir, runs_dir, slug):
    channel_dir = Path(channel_dir)
    profile_file = channel_dir / "profile.yaml"
    missing = missing_fields(load_profile(profile_file))
    if missing:
        raise StudioError("Hồ sơ kênh còn thiếu: " + ", ".join(missing))
    slug = re.sub(r"[^\w-]+", "-", slug).strip("-")
    if not slug:
        raise StudioError("Tên lần chạy không hợp lệ")
    run_dir = Path(runs_dir) / f"{datetime.now().strftime('%Y%m%d')}-{slug}"
    if run_dir.exists():
        raise StudioError(f"Lần chạy {run_dir.name} đã có")
    (run_dir / "clips").mkdir(parents=True)
    shutil.copy(profile_file, run_dir / "profile.yaml")
    (run_dir / "brief.md").write_text(BRIEF_TEMPLATE, encoding="utf-8")
    write_json(run_dir / "scenes.json", {"canh": []})
    write_json(run_dir / "state.json", {
        "id": run_dir.name, "kenh": channel_dir.name, "thu_muc_kenh": str(channel_dir.resolve()),
        "tao_luc": now_iso(), "video_id": None, "su_kien": [],
    })
    run = Run(run_dir)
    run.log("Tạo lần chạy", "ok")
    return run


def brief_sections(run):
    """Trả về {tiêu đề mục: nội dung} của brief.md."""
    text = (run.dir / "brief.md").read_text(encoding="utf-8-sig")
    parts = re.split(r"^##\s+(.+?)\s*$", text, flags=re.M)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}
