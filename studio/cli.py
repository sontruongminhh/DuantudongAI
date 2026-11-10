"""Dòng lệnh: python -m studio <lệnh>."""
import argparse
import sys

from . import bao_cao, clip, core, duyet, dung, goi, motion, qc, seo
from .core import ROOT, Run, StudioError


def _run(name):
    return Run(ROOT / "runs" / name)


def _print_issues(errors, warnings):
    for e in errors:
        print(f"  LỖI: {e}")
    for w in warnings:
        print(f"  Cảnh báo: {w}")
    print("Đạt." if not errors else f"Không đạt: {len(errors)} lỗi.")
    return not errors


def cmd_tao_kenh(a):
    print(f"Đã tạo {core.create_channel(ROOT / 'channels', a.kenh) / 'profile.yaml'}")


def cmd_kiem_tra_kenh(a):
    missing = core.missing_fields(core.load_profile(ROOT / "channels" / a.kenh / "profile.yaml"))
    print("Hồ sơ đủ thông tin." if not missing else "Còn thiếu:\n  " + "\n  ".join(missing))
    if missing:
        sys.exit(1)


def cmd_tao(a):
    run = core.create_run(ROOT / "channels" / a.kenh, ROOT / "runs", a.ten)
    print(f"Đã tạo lần chạy {run.name}\nTiếp theo: {bao_cao.next_step(run)}")


def cmd_trang_thai(a):
    run = _run(a.lan_chay)
    print(f"Lần chạy: {run.name}\nKênh: {run.state['kenh']}\nTiếp theo: {bao_cao.next_step(run)}")


def cmd_kiem_tra_goi(a):
    run = _run(a.lan_chay)
    errors, warnings = goi.check_package(run)
    if not _print_issues(errors, warnings):
        sys.exit(1)
    print(f"Bảng xem lại: {goi.write_review(run)}")


def cmd_nap_shotlist(a):
    print(f"Đã nạp {goi.import_shotlist(_run(a.lan_chay))} cảnh vào scenes.json")


def cmd_gop_clip(a):
    print(f"Đã gộp thành {goi.import_shotlist_as_clips(_run(a.lan_chay))} clip trong scenes.json")


def cmd_xuat_lo(a):
    files = goi.export_batches(_run(a.lan_chay))
    print(f"Đã xuất {len(files)} lô vào {files[0].parent}")


def cmd_tach_loi(a):
    n, wrote = motion.tach_loi(_run(a.lan_chay), a.ghi_de)
    print(f"Đã tách lời đọc thành {n} cảnh. Danh sách ở motion\\dong_loi.json")
    print("Đã tạo khung motion\\canh.json, hãy điền mẫu và dữ liệu cho từng cảnh." if wrote
          else "motion\\canh.json đã có nên giữ nguyên. Thêm --ghi-de nếu muốn tạo lại khung.")


def cmd_nap_motion(a):
    n, warnings = motion.nap_motion(_run(a.lan_chay))
    for w in warnings:
        print(f"  Cảnh báo: {w}")
    print(f"Đã nạp {n} cảnh motion vào scenes.json")


def cmd_dung_canh(a):
    print(f"Đã dựng trang HTML cho {motion.dung_canh(_run(a.lan_chay))} cảnh")


def cmd_ve_canh(a):
    done, skipped = motion.ve_canh(_run(a.lan_chay), a.canh.split(",") if a.canh else None, a.lam_lai)
    print(f"Đã render {len(done)} cảnh" + (f", bỏ qua {len(skipped)} cảnh đã có clip" if skipped else "")
          + f". Clip ở runs\\{a.lan_chay}\\motion\\out")


def cmd_duyet(a):
    run = _run(a.lan_chay)
    print("Đã duyệt." if duyet.approve(run, a.cong) else "Cổng này đã được duyệt và tệp không đổi.")


def cmd_xuat_prompt(a):
    print(f"Đã xuất {goi.export_prompts(_run(a.lan_chay))}")


def cmd_nhan_clip(a):
    run = _run(a.lan_chay)
    print(f"Đã nhận {len(clip.import_clips(run, a.thu_muc, a.theo_thoi_gian, a.ghi_de))} clip.")
    print("Thứ tự chỉ dựa vào tên hoặc thời gian của tệp, hãy xem lại nội dung từng cảnh.")
    if not _print_issues(*clip.check_clips(run)):
        sys.exit(1)


def cmd_kiem_tra_clip(a):
    if not _print_issues(*clip.check_clips(_run(a.lan_chay))):
        sys.exit(1)


def cmd_dung(a):
    mode = "kiem_tra" if a.chi_kiem_tra else "gia_lap" if a.gia_lap else "that"
    dung.render(_run(a.lan_chay), mode)


def cmd_cat_clip(a):
    print(f"Đã cắt clip, tổng hình còn {dung.trim_clips(_run(a.lan_chay)) / 60:.1f} phút. Chạy lại lệnh dung để dựng")


def cmd_kiem_tra_video(a):
    result = qc.run_qc(_run(a.lan_chay), "render_gia_lap" if a.gia_lap else "render")
    if not _print_issues(result["loi"], result["canh_bao"]):
        sys.exit(1)


def cmd_tao_seo(a):
    print(f"Đã tạo {seo.create_metadata(_run(a.lan_chay))}")


def cmd_kiem_tra_seo(a):
    if not _print_issues(seo.check_metadata(_run(a.lan_chay)), []):
        sys.exit(1)


def cmd_trang_duyet(a):
    print(f"Mở trang này để xem: {seo.write_review_page(_run(a.lan_chay))}")


def cmd_ket_noi_youtube(a):
    from . import youtube
    for c in youtube.connect(a.kenh):
        print(f"Đã kết nối kênh: {c['ten']}\nChép vào youtube.channel_id trong hồ sơ: {c['id']}")


def cmd_tai_len(a):
    from . import youtube
    print(f"Đã tải lên ở chế độ riêng tư, video_id: {youtube.upload(_run(a.lan_chay))}")


def cmd_cap_nhat_seo(a):
    from . import youtube
    print(f"Đã cập nhật SEO cho video {youtube.update_metadata(_run(a.lan_chay))}")


def cmd_bao_cao(a):
    print(f"Đã ghi {bao_cao.write_report(_run(a.lan_chay))}")


def build_parser():
    ap = argparse.ArgumentParser(prog="python -m studio", description="Quy trình video YouTube có 3 cổng duyệt")
    sub = ap.add_subparsers(dest="lenh", required=True)

    def add(name, func, help_text, *args):
        p = sub.add_parser(name, help=help_text)
        for arg in args:
            p.add_argument(arg)
        p.set_defaults(func=func)
        return p

    add("tao-kenh", cmd_tao_kenh, "Tạo hồ sơ kênh mới", "kenh")
    add("kiem-tra-kenh", cmd_kiem_tra_kenh, "Liệt kê thông tin hồ sơ còn thiếu", "kenh")
    add("tao", cmd_tao, "Tạo lần chạy mới", "kenh", "ten")
    add("trang-thai", cmd_trang_thai, "Xem bước tiếp theo", "lan_chay")
    add("kiem-tra-goi", cmd_kiem_tra_goi, "Kiểm tra scenes.json", "lan_chay")
    add("nap-shotlist", cmd_nap_shotlist, "Tạo scenes.json từ shotlist.json", "lan_chay")
    add("gop-clip", cmd_gop_clip, "Gộp shotlist thành clip 10 giây và tạo prompt video", "lan_chay")
    add("xuat-lo", cmd_xuat_lo, "Xuất tin nhắn hàng loạt cho Muse sau Cổng 2", "lan_chay")
    p = add("tach-loi", cmd_tach_loi, "Tách script.md thành cảnh 10 giây cho motion", "lan_chay")
    p.add_argument("--ghi-de", action="store_true", help="Tạo lại khung motion/canh.json, mất dữ liệu đã điền")
    add("nap-motion", cmd_nap_motion, "Kiểm tra motion/canh.json rồi ghi scenes.json", "lan_chay")
    add("dung-canh", cmd_dung_canh, "Dựng trang HTML từng cảnh motion", "lan_chay")
    p = add("ve-canh", cmd_ve_canh, "Render cảnh motion thành clip bằng HyperFrames", "lan_chay")
    p.add_argument("--canh", help="Chỉ render các cảnh này, ví dụ S001,S004")
    p.add_argument("--lam-lai", action="store_true", help="Render lại cả cảnh đã có clip")
    add("duyet", cmd_duyet, "Duyệt một cổng (bạn tự chạy)", "lan_chay", "cong")
    add("xuat-prompt", cmd_xuat_prompt, "Xuất prompt cho Muse", "lan_chay")
    p = add("nhan-clip", cmd_nhan_clip, "Chép clip vào đúng số cảnh", "lan_chay", "thu_muc")
    p.add_argument("--theo-thoi-gian", action="store_true", help="Xếp theo thời gian tệp thay vì tên tệp")
    p.add_argument("--ghi-de", action="store_true", help="Thay toàn bộ clip đang có")
    add("kiem-tra-clip", cmd_kiem_tra_clip, "Kiểm tra thông số clip", "lan_chay")
    p = add("dung", cmd_dung, "Tạo giọng và dựng video", "lan_chay")
    p.add_argument("--gia-lap", action="store_true", help="Dùng tiếng bíp, không tốn credit, ra render_gia_lap/")
    p.add_argument("--chi-kiem-tra", action="store_true", help="Chỉ ước lượng thời lượng")
    add("cat-clip", cmd_cat_clip, "Cắt clip vừa lời đọc sau lần dựng đầu", "lan_chay")
    p = add("kiem-tra-video", cmd_kiem_tra_video, "Kiểm tra video đã dựng", "lan_chay")
    p.add_argument("--gia-lap", action="store_true", help="Kiểm tra render_gia_lap/")
    add("tao-seo", cmd_tao_seo, "Tạo khung metadata.json", "lan_chay")
    add("kiem-tra-seo", cmd_kiem_tra_seo, "Kiểm tra metadata.json", "lan_chay")
    add("trang-duyet", cmd_trang_duyet, "Tạo trang xem video trước khi duyệt", "lan_chay")
    add("ket-noi-youtube", cmd_ket_noi_youtube, "Đăng nhập YouTube cho kênh", "kenh")
    add("tai-len", cmd_tai_len, "Tải lên ở chế độ riêng tư sau Cổng 3", "lan_chay")
    add("cap-nhat-seo", cmd_cap_nhat_seo, "Cập nhật SEO cho video đã tải lên", "lan_chay")
    add("bao-cao", cmd_bao_cao, "Ghi báo cáo", "lan_chay")
    return ap


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    core.load_env()
    args = build_parser().parse_args()
    try:
        args.func(args)
    except StudioError as e:
        sys.exit(f"LỖI: {e}")
