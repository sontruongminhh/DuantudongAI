# DuantudongAI · kenh4

Bộ công cụ làm video cho kênh YouTube tiếng Nhật **日本一の終わり方**: chuyện các gia tộc và công ty Nhật, loạt 「なぜ消えたのか」 và 「なぜ終わらなかったのか」. Mỗi video 30–35 phút, 12 chương, hình là ảnh Wikimedia Commons và đồ họa tự dựng, giọng đọc AI (Genmax).

## Thư mục

| Thư mục / tệp | Nội dung |
|---|---|
| `QUY_TRINH.md` | Các bước một video, lệnh từng bước, thông số đã chọn |
| `BAI_HOC.md` | Lỗi gặp và điều chỉnh sau từng video |
| `CHIEN_LUOC_KENH.md` | Chiến lược kênh, cách chọn chủ đề |
| `CLAUDE.md` | Quy tắc cố định cho trợ lý AI làm việc trong dự án |
| `studio/` | Lệnh chính `python -m studio <lệnh> <run>`: tạo lần chạy, tách lời, nạp cảnh, dựng, SEO, tải lên |
| `engine/` | Lõi dựng video, phụ đề, gọi Genmax |
| `tools/` | Công cụ từng bước: kiểm kịch bản, đo trùng lời, đọc thử, render song song, kiểm âm thanh và phụ đề, thumbnail, SEO, đóng gói |
| `research/` | Công cụ đo chủ đề (Wikipedia, YouTube) và ghi chép chủ đề |
| `runs/*.md` | Hướng dẫn nghiên cứu, tiêu chí kịch bản, hướng dẫn điền hình |
| `motion/`, `channels/` | Mẫu cảnh động, bản đồ, hồ sơ kênh, ảnh kênh |
| `tests/` | Kiểm thử (`pytest`) |
| `luu_tru/` | Kế hoạch cũ, giữ để tra lại |
| `Tổng hợp kênh nghiên cứu thị trường/` | Link bảng tổng hợp các kênh đã nghiên cứu |

Không có trên repo (chặn bởi `.gitignore`): `.env` (khóa API), `runs/<lần chạy>/` (dữ liệu từng video), `tai_len/` (video đã đóng gói), video, âm thanh, phụ đề đối thủ.

## Cài đặt

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Cài riêng trên máy: `yt-dlp`, `ffmpeg`, `ffprobe`. Khóa API (Genmax, YouTube) để trong `.env`.

Kiểm thử: `.venv\Scripts\python.exe -m pytest tests -q`

## Một video

Tóm tắt; lệnh đầy đủ ở `QUY_TRINH.md`.

1. Chọn chủ đề, tạo lần chạy: `python -m studio tao kigyo_shi <tên>`
2. Nghiên cứu nguồn, ảnh, viết kịch bản; kiểm bằng `tools\check_script_ja.py`, `tools\cham_lai.py`, `tools\do_trung_loi.py`
3. Tách lời, điền hình, đọc thử tên khó (`tools\doc_thu.py`), chờ duyệt
4. Render clip (`tools\ve_song_song.py`), dựng giọng (`python -m studio dung`), cho cảnh dài theo giọng thật (`tools\tim_lam_lai.py`)
5. Kiểm video, thumbnail (`tools\thumbnail_kigyo.py`), SEO (`tools\seo_kigyo.py`)
6. Đóng gói: `tools\dong_goi.py runs\<run> <số>_<tên>`
