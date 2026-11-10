"""Kiểm thử công cụ đo trùng lời với đối thủ."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import do_trung_loi as dt  # noqa: E402

DOI_THU = ("昭和の初め、鐘紡は日本で一番売上の大きい会社でした。紡績工場は全国に広がり、"
           "従業員は数万人を数えました。しかし戦後、繊維産業は急速に力を失っていきます。")
RIENG = ("大正から昭和にかけて、この会社の糸は世界の市場へ運ばれていった。"
         "工場の町には寮や学校が建ち、女工たちの暮らしを支えた。やがて化学繊維の時代が来る。")


def test_khong_trung_thi_dat():
    kq = dt.do(RIENG, DOI_THU)
    assert kq["ty_le"] == 0
    assert dt.dat(kq)


def test_chep_nguyen_cau_thi_khong_dat():
    kq = dt.do(RIENG + DOI_THU, DOI_THU)
    assert kq["ty_le"] > dt.TY_LE_TOI_DA
    assert not dt.dat(kq)
    assert any(d["dai"] > dt.DOAN_TOI_DA for d in kq["doan"])


def test_doi_dau_cau_van_bi_bat():
    # Chỉ đổi dấu câu, khoảng trắng, chữ số toàn khổ: vẫn là chép
    sua = DOI_THU.replace("、", " ").replace("。", "！")
    kq = dt.do(RIENG + sua, DOI_THU)
    assert not dt.dat(kq)


def test_doan_trong_ngoac_la_trich():
    tai_lieu = "本日ヲ以テ当社ハ一切ノ営業ヲ停止シ従業員各位ニ深ク感謝ノ意ヲ表スル次第デアリマス"
    cua_minh = RIENG * 6 + "当時の新聞はこう伝えた。「" + tai_lieu + "」"
    kq = dt.do(cua_minh, "記事の一部です。" + tai_lieu + "と書かれていました。")
    assert kq["doan"] and all(d["trich"] for d in kq["doan"])
    assert dt.dat(kq)


def test_loi_doc_bo_nhan_va_ghi_chu():
    md = "# Tiêu đề\n### Chương 1\n[HÌNH: ảnh nhà máy]\n((SILENCE 1s))\n[NARRATIVE] 工場が動き出した。\n"
    assert dt.loi_doc(md) == "工場が動き出した。"
