"""Ba cổng duyệt. Lời duyệt gắn với mã băm: tệp đổi thì phải duyệt lại."""
import getpass
import hashlib
import re
import sys

from .core import StudioError, now_iso, read_json, sha256, write_json

GATE_NAMES = {"G1": "chủ đề và định hướng", "G2": "gói nội dung", "G3": "video và thông tin đăng tải"}
THUMBNAIL = "publish/thumbnail.jpg"


def gate_files(run, gate):
    if gate == "G1":
        return ["brief.md"]
    if gate == "G2":
        files = ["brief.md", "profile.yaml", "scenes.json"]
        # Chế độ ảnh: kịch bản và thiết kế hình cũng thuộc phần được duyệt
        files += [f for f in ("script.md", "video.json", "shotlist.json", "muse/bo_quy_chuan.json")
                  if (run.dir / f).is_file()]
        return files
    if gate == "G3":
        files = ["scenes.json", "render/final.mp4", "render/final.srt", "publish/metadata.json"]
        if (run.dir / THUMBNAIL).is_file():
            files.append(THUMBNAIL)
        return files
    raise StudioError(f"Không có cổng {gate}")


def _hashes(run, gate):
    out = {}
    for rel in gate_files(run, gate):
        path = run.dir / rel
        if not path.is_file():
            raise StudioError(f"Cổng {gate} cần tệp {rel}, nhưng chưa có")
        out[rel] = sha256(path)
    return out


def _combined(hashes):
    joined = "\n".join(f"{k}={v}" for k, v in sorted(hashes.items()))
    return hashlib.sha256(joined.encode()).hexdigest()


def verify_gate(run, gate):
    """Báo lỗi nếu cổng chưa duyệt hoặc tệp đã đổi sau khi duyệt."""
    if (run.profile.get("quy_trinh") or {}).get("bo_duyet"):
        return None
    path = run.dir / "approvals" / f"{gate}.json"
    if not path.is_file():
        raise StudioError(f"Chưa duyệt {GATE_NAMES[gate]} (Cổng {gate[1]})")
    saved = read_json(path)
    current = _hashes(run, gate)
    changed = sorted(k for k in set(current) | set(saved["tep"]) if current.get(k) != saved["tep"].get(k))
    if changed:
        raise StudioError(f"Cổng {gate[1]} mất hiệu lực vì tệp đã đổi sau khi duyệt: {', '.join(changed)}")
    return saved


def _precheck(run, gate):
    from .goi import check_brief, check_package
    if gate == "G1":
        errors = check_brief(run)
        if errors:
            raise StudioError("\n".join(errors))
    if gate == "G2":
        verify_gate(run, "G1")
        errors, _ = check_package(run)
        if errors:
            raise StudioError("Gói nội dung còn lỗi:\n  " + "\n  ".join(errors))
    if gate == "G3":
        from .qc import require_qc_passed
        from .seo import check_metadata
        verify_gate(run, "G2")
        require_qc_passed(run)
        errors = check_metadata(run)
        if errors:
            raise StudioError("Thông tin đăng tải còn lỗi:\n  " + "\n  ".join(errors))


def _ask_human(code):
    if not sys.stdin.isatty():
        raise StudioError("Lệnh duyệt phải do bạn tự chạy trong cửa sổ dòng lệnh")
    return input(f"Gõ mã {code} để duyệt, hoặc Enter để hủy: ").strip()


def approve(run, gate, confirm=_ask_human):
    """Ghi lời duyệt sau khi người duyệt gõ đúng mã của đúng các tệp đang xem."""
    if gate not in GATE_NAMES:
        raise StudioError(f"Không có cổng {gate}. Chọn G1, G2 hoặc G3")
    if (run.dir / "approvals" / f"{gate}.json").exists():
        try:
            verify_gate(run, gate)
        except StudioError:
            pass
        else:
            return False
    _precheck(run, gate)
    if gate == "G2":
        from .goi import write_review
        print(f"Xem gói nội dung tại: {write_review(run)}")
    hashes = _hashes(run, gate)
    print(f"Duyệt {GATE_NAMES[gate]} cho lần chạy {run.name}:")
    for rel in hashes:
        print(f"  {rel}")
    code = _combined(hashes)[:6]
    answer = confirm(code)
    # Bỏ ký tự thừa do cửa sổ dòng lệnh chèn vào, nhưng vẫn phải đủ đúng mã
    if re.sub(r"[^0-9a-f]", "", answer.lower()) != code:
        run.log(f"Cổng {gate[1]}", "canh_bao", "duyet", "Không duyệt")
        raise StudioError(f"Chưa duyệt, không có gì thay đổi. Mã cần gõ: {code}. Đã nhận: {answer!r}")
    write_json(run.dir / "approvals" / f"{gate}.json", {
        "cong": gate, "ma": _combined(hashes), "tep": hashes, "duyet_luc": now_iso(), "nguoi_duyet": getpass.getuser(),
    })
    run.log(f"Cổng {gate[1]}", "ok", "duyet", GATE_NAMES[gate])
    return True
