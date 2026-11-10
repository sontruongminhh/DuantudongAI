"""Báo cáo sau mỗi lần chạy. Chỉ ghi những gì có trong tệp và nhật ký."""
from .core import brief_sections, read_json

KIND = {"tu_dong": "Tự động", "thu_cong": "Thủ công", "duyet": "Duyệt"}
RESULT = {"ok": "Thành công", "canh_bao": "Cảnh báo", "loi": "Lỗi"}


def _cell(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ")


def next_step(run):
    """Bước tiếp theo dựa trên tệp và lời duyệt hiện có."""
    from .duyet import verify_gate
    from .core import StudioError
    d, name = run.dir, run.name

    def approved(gate):
        try:
            verify_gate(run, gate)
            return True
        except StudioError:
            return False

    if not approved("G1"):
        return f"Hoàn thiện brief.md, rồi bạn chạy: python -m studio duyet {name} G1"
    motion = (run.profile.get("clip") or {}).get("nguon") == "motion"
    if motion:
        if not (d / "script.md").is_file():
            return "Viết script.md theo runs\\HUONG_DAN_NGHIEN_CUU.md và runs\\TIEU_CHI_KICH_BAN.md, rồi kiểm bằng: python tools\\check_script_ja.py " \
                   f"runs\\{name}\\script.md"
        if not (d / "motion" / "dong_loi.json").is_file():
            return f"python -m studio tach-loi {name}"
        scenes_ok = bool(read_json(d / "scenes.json").get("canh"))
        if not scenes_ok:
            canh = read_json(d / "motion" / "canh.json").get("canh", [])
            if not canh or any(not sc.get("template") for sc in canh):
                return "Điền template và data cho từng cảnh trong motion\\canh.json theo runs\\HUONG_DAN_DIEN_CANH.md"
            return f"python -m studio nap-motion {name}"
    if not approved("G2"):
        if motion:
            return f"Chạy kiem-tra-goi, rồi bạn chạy: python -m studio duyet {name} G2"
        return f"Viết scenes.json, chạy kiem-tra-goi, rồi bạn chạy: python -m studio duyet {name} G2"
    has_clips = any(p.suffix.lower() in (".mp4", ".mov", ".mkv", ".webm", ".m4v") for p in (d / "clips").iterdir())
    if motion:
        if not has_clips:
            out = d / "motion" / "out"
            rendered = len(list(out.glob("S*.mp4"))) if out.is_dir() else 0
            if rendered < len(read_json(d / "scenes.json")["canh"]):
                return f"python -m studio dung-canh {name}, rồi python -m studio ve-canh {name}"
            return f"python -m studio nhan-clip {name} runs\\{name}\\motion\\out"
    else:
        if not (d / "muse" / "prompts.md").is_file() and not (d / "muse" / "lo").is_dir():
            return f"python -m studio xuat-prompt {name}"
        if not has_clips:
            return f"Tạo clip trên Muse theo muse/prompts.md, rồi chạy: python -m studio nhan-clip {name} <thư mục clip>"
    if not (d / "render" / "final.mp4").is_file():
        return f"python -m studio dung {name} (bước này tốn credit Genmax)"
    if not (d / "render" / "qc.json").is_file():
        return f"python -m studio kiem-tra-video {name}"
    if not read_json(d / "render" / "qc.json")["dat"]:
        return "Sửa lỗi trong render/qc.json rồi dựng lại"
    if not (d / "publish" / "metadata.json").is_file():
        return f"python -m studio tao-seo {name}"
    if not approved("G3"):
        return f"Hoàn thiện metadata.json, chạy trang-duyet, rồi bạn chạy: python -m studio duyet {name} G3"
    if not run.state.get("video_id"):
        return f"python -m studio tai-len {name}"
    return f"Đã tải lên. Tạo báo cáo: python -m studio bao-cao {name}"


def write_report(run):
    state = run.state
    sections = brief_sections(run)
    lines = [f"# Báo cáo lần chạy {run.name}", ""]
    lines += ["## Chủ đề và nghiên cứu", ""]
    for key in ("Chủ đề", "Từ khóa chính", "Từ khóa phụ", "Nguồn nghiên cứu"):
        lines += [f"**{key}:** {sections.get(key) or 'Chưa có'}", ""]

    lines += ["## Tệp đầu ra", ""]
    for rel in ("brief.md", "scenes.json", "goi_noi_dung.md", "muse/prompts.md", "render/final.mp4", "render/final.srt",
                "render/timeline.json", "render/qc.json", "publish/metadata.json", "publish/thumbnail.jpg",
                "review/index.html"):
        status = str(run.dir / rel) if (run.dir / rel).is_file() else "Chưa có"
        lines.append(f"- `{rel}`: {status}")
    lines.append("")

    qc_path = run.dir / "render" / "qc.json"
    lines += ["## Kiểm tra video", ""]
    if qc_path.is_file():
        qc = read_json(qc_path)
        lines.append(f"Kết quả: {'Đạt' if qc['dat'] else 'Không đạt'}, dài {qc['thoi_luong']} giây.")
        lines += [f"- Lỗi: {x}" for x in qc["loi"]] + [f"- Cảnh báo: {x}" for x in qc["canh_bao"]]
    else:
        lines.append("Chưa kiểm tra.")
    lines.append("")

    lines += ["## YouTube", ""]
    meta_path = run.dir / "publish" / "metadata.json"
    if meta_path.is_file():
        meta = read_json(meta_path)
        lines += [f"- Tiêu đề: {meta.get('tieu_de') or 'Chưa có'}", f"- Thẻ: {', '.join(meta.get('the') or []) or 'Chưa có'}",
                  f"- Lịch đăng: {meta.get('lich_dang') or 'Không'}"]
    video_id = state.get("video_id")
    lines.append(f"- Trạng thái: đã tải lên, video_id {video_id}, "
                 f"quyền riêng tư {(state.get('youtube_status') or {}).get('privacyStatus', 'chưa xác nhận')}"
                 if video_id else "- Trạng thái: chưa tải lên")
    lines += ["", "## Nhật ký", "", "| Thời gian (UTC) | Bước | Kiểu | Kết quả | Chi tiết |", "|---|---|---|---|---|"]
    lines += [f"| {e['luc']} | {_cell(e['buoc'])} | {KIND.get(e['kieu'], e['kieu'])} | "
              f"{RESULT.get(e['ket_qua'], e['ket_qua'])} | {_cell(e['chi_tiet'])} |" for e in state["su_kien"]]
    path = run.dir / "report.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path
