"""Kiểm thử các mẫu cảnh kênh 4 (studio/mau_kigyo.py)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "thu_nghiem"))
from studio import mau_kigyo as k4, mau_motion  # noqa: E402
import thu_mau_k4  # noqa: E402

ANH = {"honsha_taisho.jpg", "handa_kumitate.jpg", "nakajima_chikuhei.jpg"}


def test_moi_mau_deu_dung_duoc_va_khong_loi():
    seen = set()
    for i, (t, d) in enumerate(thu_mau_k4.S, 1):
        sc = {"id": f"S{i:03d}", "template": t, "data": d}
        assert mau_motion.check_scene(sc, ANH) == [], t
        page = mau_motion.build(sc, 8)
        assert 'data-composition-id="S%03d"' % i in page and "#f3eee3" in page
        seen.add(t)
    assert seen == set(k4.TEMPLATES_K4)


def test_mau_kenh2_khong_bi_doi_mau_nen():
    sc = {"id": "S001", "template": "hook", "data": {"kicker": "a", "line1": "b", "hl": "c", "line2": "d"}}
    assert "#f3eee3" not in mau_motion.build(sc)


def test_dong_xuat_xu_va_thoat_html():
    sc = {"id": "S001", "template": "so_lon", "data": {"label": "<b>売上</b>", "num": "15", "unit": "億円", "src": "桂(1977)"}}
    page = mau_motion.build(sc)
    assert "出典：桂(1977)" in page and "&lt;b&gt;" in page


def test_bat_loi_du_lieu():
    bad = [
        ("anh", {"anh": "khong_co.jpg", "src": "x"}, "không có ảnh"),
        ("cot", {"title": "t", "bars": [["a", 1, "1"]], "src": "x"}, "bars"),
        ("tron", {"title": "t", "parts": [["a", 40], ["b", 40]], "src": "x"}, "100%"),
        ("nien_bieu", {"title": "t", "stops": [["1900", "a"], ["1910", "b"]], "src": "x"}, "stops"),
        ("ban_do_diem", {"points": [["ニューヨーク", -74.0, 40.7]], "src": "x"}, "ngoài vùng"),
        ("cau_hoi", {"lines": ["この会社はなぜ消えてしまったのでしょうか長すぎる"]}, "tối đa 16"),
        ("chan_dung", {"anh": "nakajima_chikuhei.jpg", "name": "x"}, "thiếu trường src"),
    ]
    for t, d, want in bad:
        errs = mau_motion.check_scene({"template": t, "data": d}, ANH)
        assert any(want in e for e in errs), (t, errs)


def test_ban_do_chieu_dung_vi_tri():
    tokyo = k4.project("nhat_ban", 139.7, 35.7)
    osaka = k4.project("nhat_ban", 135.5, 34.7)
    assert osaka[0] < tokyo[0] and osaka[1] > tokyo[1]
    l, t, *_ = k4._projection("the_gioi")
    x, _ = k4.project("the_gioi", -175, 0)       # mép trái được dời sang phải
    assert x > k4.project("the_gioi", 170, 0)[0]
    assert any(iso == "JPN" for iso, _ in k4.map_paths("nhat_ban"))
    assert all(iso != "ATA" for iso, _ in k4.map_paths("the_gioi"))


def test_can_nguon_cho_mau_co_so_lieu():
    assert {"so_lon", "cot", "nien_bieu"} <= mau_motion.NEEDS_SOURCE
    assert "anh" not in k4.NEEDS_SOURCE_K4
