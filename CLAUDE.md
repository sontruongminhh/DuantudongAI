# kenh4: kênh YouTube 日本一の終わり方

Kênh tiếng Nhật kể chuyện các gia tộc, công ty Nhật. Hai loạt: 「なぜ消えたのか」 và 「なぜ終わらなかったのか」. Mỗi video dài 30–35 phút, 12 chương. Trả lời người dùng bằng tiếng Việt.

## Đọc trước khi làm

- `QUY_TRINH.md`: các bước một video, lệnh từng bước, thông số đã chọn.
- `BAI_HOC.md`: lỗi và điều chỉnh sau từng video; đọc mục các video gần nhất.
- `runs\HUONG_DAN_NGHIEN_CUU.md`, `runs\TIEU_CHI_KICH_BAN.md`, `runs\HUONG_DAN_DIEN_CANH.md`: giao cho agent nghiên cứu, viết, điền hình.
- `research\CHU_DE_TIEP.md`: các chủ đề đã đo, ứng viên video sau.

## Cách làm việc

- Một video một lần. Xong video thì ghi `BAI_HOC.md` và `QUY_TRINH.md` rồi mới làm video sau.
- Người dùng yêu cầu làm video là đồng ý tốn credit Genmax (giọng) và Muse cho video đó.
- Gửi tệp nghe thử tên khó (`tools\doc_thu.py`) và chờ người dùng duyệt trước khi chạy `dung`.
- Đóng gói bằng `tools\dong_goi.py` vào `tai_len\<số>_<tên>`; người dùng tự tải lên.
- Thumbnail giữ khung cũ (`noi_bat`, tông `am`, dải vàng) cho mọi video.

## Không được

- Không đăng công khai hay đặt lịch khi người dùng chưa yêu cầu rõ. `tai-len` chỉ tải lên ở chế độ riêng tư.
- Không yêu cầu người dùng gửi khóa, mật khẩu, mã đăng nhập vào cuộc trò chuyện. Không đọc `.env`, `client_secret*.json`, `settings.json`. Không in hay dán khóa (kể cả khóa YouTube lộ trong URL lỗi).
- Không gửi email người dùng cho dịch vụ nào.
- Không sao chép kịch bản, hình ảnh, câu chữ, dấu ấn riêng của kênh khác. Agent viết kịch bản không đọc phụ đề đối thủ trong `research\doi_thu\` (chỉ dùng để đo trùng bằng `tools\do_trung_loi.py`). Không đưa `research\doi_thu\` lên GitHub.
- Không vượt kiểm tra bot của YouTube, không dùng cookie trình duyệt.
- Không báo đã kết nối, chạy thử, tự động hóa thành công khi chưa kiểm thật.
- Không sửa `engine\` khi chưa cần. Sửa `studio\` thì chạy `.venv\Scripts\python.exe -m pytest tests -q`.

## Nguồn và người còn sống

- Mọi con số, tên, năm trong lời đọc phải có mã F trong `nguon.md`. Mức B nói 「とされます」 hoặc 「〜によると」; 「事典によると」 chỉ dùng cho コトバンク, không cho Wikipedia.
- Câu hiện trạng (いまも…) phải mở nguồn mới nhất; nguồn là kế hoạch có thời hạn thì tính xem đã hết hạn chưa.
- Người còn sống: chỉ dùng văn bản chính thức hoặc bản án, và tên chỉ đi cùng đúng sự việc văn bản đó nêu tên. Không kể đời tư.

## Máy và lệnh

- Python: `.venv\Scripts\python.exe` (không dùng `python` của Windows Store). Lệnh studio: `python -m studio <lệnh> <run>`; công cụ trong `tools\` nhận `runs\<run>`.
- `yt-dlp`, `ffmpeg`, `ffprobe` dùng bản cài trên máy (không có trong `.venv`).
- Trong Bash, đặt `PYTHONIOENCODING=utf-8` khi in tiếng Nhật.
- Repo GitHub: `sontruongminhh/DuantudongAI` (công khai). `.gitignore` chặn khóa, `runs\`, `tai_len\`, video, âm thanh, phụ đề đối thủ.
