# Quy trình kênh 4: lịch sử công ty Nhật đã biến mất

Bộ máy sao từ kenh2 (studio, motion HyperFrames, giọng MiniMax qua Genmax, tải lên YouTube), thêm ảnh tư liệu, 14 mẫu cảnh riêng, phụ đề dải đen, nhạc nền tự tạo, thumbnail và SEO tự sinh. Chiến lược ở `CHIEN_LUOC_KENH.md`, phân tích kênh mẫu ở `research\PHAN_TICH_KENH_MAU.md`, giọng và nhạc ở `research\GIONG.md`.

Mã kênh trong studio: `kigyo_shi` (`channels\kigyo_shi\profile.yaml`). Lệnh `python -m studio …` nhận **tên lần chạy** (ví dụ `20261104-kanebo`); lệnh `tools\…` nhận đường dẫn `runs\<run>`. Dùng `.venv\Scripts\python.exe`.

**Trạng thái 09/11/2026:** video 1 (リッカー), video 2 (カネボウ), video 3 (鈴木商店), video 4 (セゾングループ), video 5 (大倉財閥), video 6 (大映), video 7 (安田財閥), video 8 (三井家, mở loạt 「なぜ終わらなかったのか」), video 9 (岩崎家), video 10 (中内家 / ダイエー), video 11 (和田家 / ヤオハン), video 12 (堤家 / 西武) xong đến bước tải lên (`tai_len\1_…` tới `12_tsutsumi`), bài học ở `BAI_HOC.md`. **Video 1–9 còn lỗi hình đổi cảnh trước khi giọng đọc xong** (giọng trễ trung vị 1,7–2,5 giây; xem `BAI_HOC.md` video 10, lỗi 1); sửa được không tốn credit bằng các bước 6–7 mới. Video 1, 2, 4, 8, 9, 10 còn có phụ đề cắt số thập phân (「1.」|「5兆円」, `BAI_HOC.md` video 12, lỗi 4); engine đã sửa, dựng lại là hết. Làm **từng video một**: xong mỗi video thì ghi bài học vào `BAI_HOC.md`, sửa quy trình, rồi mới làm video sau. Hai video còn lại (三洋電機, 三光汽船) đã có kịch bản và dữ liệu hình, chưa dựng. Tên kênh: 日本一の終わり方; người dùng tự tải video lên từ `tai_len\`.

**Hai loạt trong kênh:** (1) 「なぜ消えたのか」: công ty / gia tộc từng số 1 rồi biến mất, chữ hỏi thumbnail 「なぜ消えた？」; (2) 「なぜ終わらなかったのか」 (từ video 8): gia tộc giàu lâu đời vẫn còn, chữ hỏi 「なぜ終わらない？」, thêm ba quy tắc: con số thị phần có nguồn A/B và năm, người còn sống / công ty đang hoạt động chỉ theo tài liệu chính thức, người viết liệt kê câu hiện trạng để tra lại (xem `BAI_HOC.md` video 8). Cả hai dùng cùng các bước dưới.

## Các bước một video

| # | Bước | Lệnh / công cụ | Kết quả |
|---|---|---|---|
| 1 | Chọn chủ đề | Công cụ đo: `research\tim_nguoi.py`, `research\tim_pha_san.py` (Wikipedia 12 tháng, Commons, YouTube), `tools\cham_chu_de.py` (yt-dlp, không cần khóa). `CHIEN_LUOC_KENH.md` mục 4: ưu tiên chủ đề đối thủ đã nổ view, **và có ảnh của chính công ty trên Commons** (ít nhất 1 chân dung người sáng lập/lãnh đạo, 3 ảnh sản phẩm hoặc nhà máy, tổng 15 ảnh liên quan; xem `BAI_HOC.md`). Tải phụ đề video đó: `yt-dlp --skip-download --write-auto-subs --sub-langs ja -o research\doi_thu\<ten> <url>` (chỉ để đo trùng, người viết không đọc) | Tên công ty |
| 2 | Tạo lần chạy | `python -m studio tao kigyo_shi <ten>` | `runs\<run>\` |
| 3 | Nghiên cứu, ảnh, kịch bản | Theo `runs\HUONG_DAN_NGHIEN_CUU.md`: `nguon.md` (mã F, mức A/B/C), ảnh Commons + `motion\anh\credit.json`, `brief.md`, `script.md` 12 chương 8.800–9.800 ký tự | |
| 3b | Chất lượng kịch bản | Theo `runs\TIEU_CHI_KICH_BAN.md` (25 tiêu chí: mở bằng thứ người xem chạm tới hôm nay, 3 câu hỏi đánh số, câu nói thật, trục ba đời với gia tộc, nối với hôm nay, quảng cáo và văn hóa, góc nhìn khác, kết quay lại mở đầu). Người viết tự chấm vào `brief.md`, người điều phối chấm lại bằng `tools\cham_lai.py runs\<run>\script.md` (rào đón dưới 20% số câu và không quá 2 câu liền, không nói 「ウィキペディア」, cùng đuôi không quá 2 câu, ít nhất 6 câu trong 「」) rồi mới điền hình. Sửa kịch bản sau khi đã điền hình thì chạy `tools\so_nhom_canh.py <bản cũ> <bản mới>` tới khi in GIỐNG | Bảng chấm |
| 4 | Kiểm kịch bản | `tools\check_script_ja.py runs\<run>\script.md --phut 26` và `tools\do_trung_loi.py runs\<run>\script.md research\doi_thu\<tệp>.ja.vtt` (đạt: trùng ≤ 3%, không đoạn nào quá 40 ký tự). Người điều phối tra lại các câu nói về hiện trạng (いまも…, 休館, 使われていない) bằng nguồn mới nhất (nguồn là kế hoạch có thời hạn thì tính xem đã hết hạn chưa), kiểm câu 「事典によると」 có đúng là コトバンク không (Wikipedia thì 「とされます」), mở văn bản gốc của câu mở đầu, và đối chiếu mọi câu agent điền hình báo "không có mã F" trước khi đọc giọng. Người còn sống liên quan vụ hình sự chỉ nêu khi đọc được bản án hoặc văn bản chính thức, và tên chỉ đi cùng đúng sự việc văn bản đó nêu tên | |
| 5 | Tách cảnh, điền hình | Theo `runs\HUONG_DAN_DIEN_CANH.md`: `tach-loi`, viết `runs\<run>\dien_mau.py` (dùng `studio\dien_k4.py`), `nap-motion`, `kiem-tra-goi`, `dung-canh` | `motion\canh.json`, trang HTML |
| 5b | Soát ảnh khớp lời | `tools\xem_anh_canh.py runs\<run>`: đọc mọi cảnh ảnh; ảnh nào không đúng nơi, đúng thời, đúng đối tượng thì đổi sang đồ họa trong `dien_mau.py` | |
| 6 | Render clip | `tools\ve_song_song.py runs\<run> --so-luong 10` (235 cảnh khoảng 24 phút), rồi `nhan-clip <run> runs\<run>\motion\out` (render lại thì thêm `--ghi-de`). Công cụ bỏ qua cảnh đã có clip: render lại toàn bộ thì đổi tên `motion\out` sang bản dự phòng trước, render vài cảnh thì `--lam-lai S028 …` | `clips\` |
| 7 | Giọng, nhạc, dựng | Trước tiên thử khóa Genmax bằng `GET /v1/default-voices` (miễn phí). Phải gọi `load_env()` từ `studio.core` trước `load_engine().Genmax()`, nếu không sẽ dùng biến khóa cũ trên máy và báo 401 sai. Vẫn 401 sau khi nạp `.env` thì người dùng thay khóa. Tên riêng khó ghi vào `runs\<run>\cach_doc.json` (`{"新発田": "しばた"}`; chỉ thay trong lời gửi đi đọc, phụ đề giữ chữ gốc), dò khóa ngắn làm đọc sai từ dài (別邸 → べつやしき), rồi `tools\doc_thu.py runs\<run> --so 12 --phai <tên chưa chắc>` đọc thử để người dùng nghe (tốn ít credit; chạy ngay sau bước 4, song song với điền hình). `dung <run>` (tốn credit Genmax, khoảng 20 phút; nếu đứt thì chạy lại, giọng đã có được giữ). **Sau lần dựng đầu, cho cảnh dài theo giọng thật:** `nap-motion` → `kiem-tra-goi` → `dung-canh` (độ dài mỗi cảnh = giọng thật + 1,2 giây, đọc từ `render\timeline.json`) → render lại các cảnh dài hơn clip (`tools\tim_lam_lai.py runs\<run> runs\<run>\lam_lai.txt`, rồi bước 6 với `--lam-lai $(cat runs\<run>\lam_lai.txt)`; chạy lại `tim_lam_lai.py` sau `nhan-clip` phải in 0 cảnh) → `nhan-clip --ghi-de` → đổi tên `clips_cat` cũ (nếu có, vì `dung` ưu tiên nó) → `dung` → `nap-motion` lần nữa nếu có câu được đọc lại ở tốc độ khác, render lại cảnh đổi độ dài → `cat-clip` → `dung` (dùng lại giọng). Đo độ lệch: `tools\do_lech_giong.py runs\<run>` phải in Đạt (không cảnh nào đổi hình trước khi giọng dứt) | `render\final.mp4`, `final.srt` |
| 8 | Kiểm tra video | `kiem-tra-video <run>` + `tools\kiem_am_thanh.py runs\<run>` + `tools\kiem_phu_de.py runs\<run>` (phụ đề cắt giữa từ) + xem 9 khung hình rải đều trong `final.mp4`. Phụ đề cắt giữa từ: thử câu mới bằng `split_caption(text, 20, "ja")` trong `engine\ai_film_studio.py` rồi mới sửa kịch bản | `render\qc.json` |
| 9 | Thumbnail | `publish\thumb.json` (`"kieu": "noi_bat"`, chủ ngữ là thứ đã mất, 「なぜ消えた？」 đỏ, nền chàm `"tong": "am"`, dải vàng; xem docstring; **giữ khung này cho mọi video**, video 13 đã thử kiểu đỏ nâu `"tong": "do"` và người dùng quay về khung cũ). Con số trên thumbnail đúng phạm vi nguồn → `tools\thumbnail_kigyo.py runs\<run>`. So ở cỡ điện thoại với thumbnail nhiều view của ngách; muốn thử phương án thì `thumb_A.json` → `thumbnail_A.jpg` | `publish\thumbnail.jpg` |
| 10 | SEO | `tao-seo <run>`, `publish\seo.json` → `tools\seo_kigyo.py runs\<run>` (mục lục từ mốc chương thật, tác giả ảnh từ `credit.json`; đọc cảnh báo tác giả). Tiêu đề: khuôn `{肩書き}・{社名}はなぜ消えたのか` được trùng, còn danh hiệu và vế sau `｜…` phải khác đối thủ. Dòng dưới thumbnail cũng không được trùng thumbnail đối thủ cùng chủ đề | `publish\metadata.json` |
| 10b | Đóng gói | `tools\dong_goi.py runs\<run> <số>_<tên>` (ví dụ `13_nakajima`): video, thumbnail, phụ đề, `THONG_TIN.txt` (tiêu đề, mô tả, thẻ, cài đặt) vào `tai_len\` để người dùng tự tải lên | `tai_len\<số>_<tên>\` |
| 11 | Tải lên riêng tư | `tai-len <run>` (cần kênh YouTube và `ket-noi-youtube`) | `video_id` |
| 12 | Công khai 17:00 JST | **Người dùng** hoặc yêu cầu rõ | |
| 13 | Đo sau 48 giờ | `bao-cao <run>` | `report.md` |

## Thông số đã chọn

| Mục | Giá trị | Căn cứ |
|---|---|---|
| Giọng | MiniMax Refined Storyteller `364839964033252`, tốc độ 0,85, `ky_tu_moi_giay: 6.4` | F0 136 Hz như kênh mẫu (`research\GIONG.md`; đo giọng mới bằng `tools\thu_giong.py`). Tốc độ 0,92 cho 5,6 ký tự/giây video, kênh mẫu 4,6. Đo giọng thật video 9–10: 5,44–5,52 ký tự/giây ở 0,85 |
| Độ dài cảnh | Theo lời, 3–20 giây (`clip.thoi_luong_giay: 20`); có giọng thật thì theo giọng thật. Chia cảnh tối đa 66 ký tự (`clip.ky_tu_toi_da: 66`); dòng lời dài hơn thì tách câu | Bản 12 giây làm giọng trễ hình (video 1–9); bỏ `ky_tu_toi_da` thì cảnh gộp tới 105 ký tự, hình đổi chậm (video 11) |
| Nhạc nền | `channels\kigyo_shi\assets\nhac_nen.wav` tự tổng hợp (`tools\tao_nhac_nen.py`), âm lượng 0,36 (nhắm -36 đến -24 dB ở khoảng lặng), tự giảm khi có lời | Không lấy nhạc kênh mẫu |
| Phụ đề | Chữ trắng trên dải đen 1/6 khung ở đáy (`dung.phu_de_kieu: dai_den`) | Như kênh mẫu |
| Hình | 14 mẫu trong `studio\mau_kigyo.py`, nền giấy chấm, chàm và son, dòng `出典` mọi cảnh, chừa 120 px đáy | Kiểu cảnh đo ở kênh mẫu, màu riêng |
| Bản đồ | Natural Earth (phạm vi công cộng), `motion\vendor\ne\` | |
| Thumbnail | Bố cục như kênh mẫu (tên công ty, chữ hỏi lớn, dải dưới, chân dung phải, nền trụ sở), màu chàm–trắng–vàng kim | |

## Quy tắc

- Mọi con số, tên riêng, năm trong lời đọc phải truy ra mã F trong `nguon.md`. Mức C không dùng. Mức B nói 「〜によると」.
- Quy đổi tiền ra giá trị hôm nay phải ghi cách tính trong `nguon.md`.
- Ảnh chỉ dùng loại có giấy phép rõ (CC0, PD, CC BY, CC BY-SA) và ghi tác giả trên hình và trong mô tả.
- Được làm lại đúng chủ đề, dữ kiện, dàn chương của video đối thủ. Không dùng video, thumbnail, nhạc, câu chữ kịch bản, tên, avatar, hashtag của họ. Bước 4 phải đạt trước khi đọc giọng.
- Chỉ tải lên riêng tư; công khai khi người dùng yêu cầu rõ.
