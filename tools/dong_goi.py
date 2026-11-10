r"""Đóng gói một video để người dùng tự tải lên YouTube.

  .venv\Scripts\python.exe tools\dong_goi.py runs\<run> <số>_<tên>      ví dụ: runs\20261109-nakajima-ke 13_nakajima

Tạo tai_len\<số>_<tên>\ gồm: <tên>.mp4 (render\final.mp4), thumbnail.jpg (publish\thumbnail.jpg),
phu_de_ja.srt (render\final.srt), THONG_TIN.txt (tiêu đề, mô tả, thẻ từ publish\metadata.json + phần cài đặt).
Chạy sau tools\seo_kigyo.py (QUY_TRINH bước 10).
"""
import json
import shutil
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent

CAI_DAT = """【Cài đặt】
- Dành cho trẻ em: Không
- Nội dung bị thay đổi hoặc tổng hợp (Altered content): Có — giọng đọc AI
- Danh mục: Giáo dục (Education)
- Ngôn ngữ video và tiêu đề: Tiếng Nhật
- Phụ đề: phụ đề đã in sẵn trong hình; có thể tải thêm phu_de_ja.srt (Tiếng Nhật) để có phụ đề bật/tắt
- Thumbnail: thumbnail.jpg
"""


def dong_goi(run: Path, ten_thu_muc: str, dich_goc: Path = GOC / "tai_len") -> Path:
    if "_" not in ten_thu_muc:
        raise SystemExit("Tên thư mục phải có dạng <số>_<tên>, ví dụ 13_nakajima")
    ten = ten_thu_muc.split("_", 1)[1]
    can = {"render/final.mp4", "render/final.srt", "publish/thumbnail.jpg", "publish/metadata.json"}
    thieu = [c for c in sorted(can) if not (run / c).is_file()]
    if thieu:
        raise SystemExit(f"Thiếu: {', '.join(thieu)}")

    m = json.loads((run / "publish/metadata.json").read_text(encoding="utf-8"))
    mo_ta = m["mo_ta"].rstrip()
    the = ", ".join(m["the"])
    if len(the) > 500:
        raise SystemExit(f"Thẻ dài {len(the)} ký tự, YouTube giới hạn 500")

    dich = dich_goc / ten_thu_muc
    dich.mkdir(parents=True, exist_ok=True)
    txt = (f"【タイトル / Tiêu đề】\n{m['tieu_de']}\n\n【説明 / Mô tả】\n{mo_ta}\n\n"
           f"【タグ / Thẻ】（dán vào ô Thẻ, cách nhau bằng dấu phẩy）\n{the}\n\n{CAI_DAT}")
    (dich / "THONG_TIN.txt").write_text(txt, encoding="utf-8")
    shutil.copy2(run / "render/final.mp4", dich / f"{ten}.mp4")
    shutil.copy2(run / "publish/thumbnail.jpg", dich / "thumbnail.jpg")
    shutil.copy2(run / "render/final.srt", dich / "phu_de_ja.srt")
    return dich


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    dich = dong_goi(Path(sys.argv[1]), sys.argv[2])
    m = json.loads((Path(sys.argv[1]) / "publish/metadata.json").read_text(encoding="utf-8"))
    print(f"tiêu đề {len(m['tieu_de'])} ký tự | thẻ {len(m['the'])} | hashtag cuối mô tả: {'#' in m['mo_ta'].rstrip().splitlines()[-1]}")
    for f in sorted(dich.iterdir()):
        print(f"  {f.name}  {f.stat().st_size:,} byte")


if __name__ == "__main__":
    main()
