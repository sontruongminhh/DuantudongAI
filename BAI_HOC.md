# Bài học sau từng video (kênh 4)

Người dùng muốn làm **từng video một**, xong mỗi video thì rút kinh nghiệm, sửa quy trình rồi mới làm video tiếp theo (04/11/2026).

## Video 1: リッカー (`runs\20261104-riccar`, 04/11/2026)

**Kết quả:** `render\final.mp4` dài 30:34, 235 cảnh, 12 chương, đạt `kiem-tra-video` và `tools\kiem_am_thanh.py`. Chưa tải lên (chưa có kênh YouTube). Thumbnail và `publish\metadata.json` đã xong.

| Đo | Video 1 | Kênh mẫu (カネボウ) |
|---|---|---|
| Độ dài | 30:34 | 34:36 |
| Lời đọc (bỏ dấu câu) | 8.857 ký tự, 4,8 ký tự/giây video | 9.050 ký tự, 4,4 ký tự/giây |
| Độ to | -14,0 LUFS | — |
| Nhạc ở khoảng lặng | -26,5 dB (giọng khoảng -16 dB) | nghe được, YouTube ghi 「音楽」 |
| Cảnh ảnh | 13% | khoảng 30% |
| Trùng lời đối thủ | 0,6% | — |

**Thời gian thật:** nghiên cứu và kịch bản khoảng 45 phút (trợ lý), điền hình khoảng 25 phút, render 235 cảnh 24 phút (10 luồng), tạo giọng khoảng 20 phút (có một lần đứt), mỗi lần dựng lại 4–6 phút.

### Lỗi gặp và đã sửa

| # | Lỗi | Nguyên nhân | Sửa |
|---|---|---|---|
| 1 | `kiem-tra-goi` báo 232 cảnh "vượt giới hạn ký tự" | `goi.narration_budget` dùng tốc độ đọc 6,0 của engine, `motion.scene_seconds` dùng 6,9 đo từ giọng thật | `studio\goi.py` dùng `giong.ky_tu_moi_giay` như nhau |
| 2 | Tạo giọng đứt ở đoạn 93/235 | Genmax quá thời gian khi tải tệp giọng, không có thử lại | `engine\genmax.py`: tải tệp thử lại 4 lần; lệnh GET thử lại khi mạng lỗi (POST không thử lại để khỏi tốn credit hai lần). Giọng đã tải được giữ, chạy lại `dung` làm tiếp |
| 3 | 8 giây cuối mất cả giọng lẫn nhạc | Luồng tiếng gốc của video ghép hụt so với hình; bộ trộn lấy độ dài theo luồng đó | `engine\ai_film_studio.py`: khi `am_luong_goc` = 0 dùng nền im lặng tự tạo đúng độ dài video |
| 4 | Nhạc nền gần như không nghe thấy (-49 dB) | `am_luong_nhac` 0,12 quá nhỏ | Đặt 0,45 cho cả kênh (nhạc ở khoảng lặng -26,5 dB, tự hạ khi có lời) |
| 5 | Chữ niên biểu xuống dòng còn một chữ (「販/売」) | Trình duyệt ngắt dòng tham | `studio\mau_kigyo.py`: `text-wrap: balance` cho mọi chữ |
| 6 | Mô tả bỏ sót tác giả ảnh CC BY-SA | `seo_kigyo.py` tìm ảnh trong `scenes.json` (không có data) | Đọc `motion\canh.json` và `publish\thumb.json` |
| 7 | Tác giả ghi 「投稿者によるスキャン」 | Commons để trường tác giả là "bản quét của người đăng" | Ghi tên người đăng (API `iiprop=user`), ví dụ `Meomeo15` |
| 8 | Render lại cảnh nhưng video không đổi | `nhan-clip` từ chối khi `clips\` đã có tệp | Thêm `--ghi-de`, rồi `cat-clip` và `dung` |
| 9 | Khó dò lỗi khi 3 video chạy cùng lúc | Làm song song | Làm từng video một |

Công cụ mới: `tools\kiem_am_thanh.py` (độ to, nhạc ở khoảng lặng, câu nào mất tiếng).

### Điều chỉnh cho video sau

1. **Chọn chủ đề có ảnh của chính công ty.** リッカー không có ảnh nào của công ty, người sáng lập hay sản phẩm trên Commons, nên chỉ 13% cảnh là ảnh và thumbnail phải dùng ảnh phố 銀座. Trước khi viết, đếm ảnh: cần ít nhất 1 chân dung người sáng lập hoặc lãnh đạo, 3 ảnh sản phẩm hoặc nhà máy, tổng 15 ảnh liên quan trực tiếp. Bốn video còn lại đã đạt 21–41%.
2. **Kiểm âm thanh là bước bắt buộc** sau `dung` cuối: `tools\kiem_am_thanh.py`.
3. **Xem 9 khung hình rải đều** trong `final.mp4`, không chỉ xem clip lẻ: thấy được dải phụ đề, nhịp đổi hình, tỷ lệ ảnh.
4. **Nhịp đọc** nhanh hơn kênh mẫu khoảng 10%. Chờ người dùng nghe: nếu thấy nhanh, đổi `giong.toc_do` 0,85 → 0,8 cho video sau (video đã có giọng thì giữ nguyên).
5. Người dùng nghe thử giọng, nhạc trước khi tạo giọng video 2.

### Chưa kiểm

- Chưa nghe bằng tai (giọng ở tốc độ 0,85, nhạc tự tổng hợp).
- Chưa tải lên: cần tạo kênh YouTube và chạy `ket-noi-youtube`.

## Video 2: カネボウ (`runs\20261104-kanebo`, 05/11/2026)

**Kết quả:** `render\final.mp4` dài 32:13, 221 cảnh, 12 chương, đạt `kiem-tra-video` và `kiem_am_thanh.py` (-14,0 LUFS, nhạc ở khoảng lặng -24,2 dB). Giọng tạo xong ngay lần đầu, không đứt. Ảnh 24% số cảnh. Tiêu đề: 「戦前の収入日本一・カネボウはなぜ消えたのか｜鐘ヶ淵の綿問屋から解散までの120年」. Chưa tải lên.

**Thời gian thật:** soát và sửa 20 phút, render 221 cảnh khoảng 22 phút, giọng + dựng 2 lần khoảng 30 phút. Các lỗi của video 1 không lặp lại.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | 6 cảnh ảnh không khớp lời: tờ quảng cáo 1903 đặt cạnh đoạn về nhà máy 淀川 năm 1918; ảnh phố 有馬 có biển hiệu không rõ là Kanebo | Thay bằng bản đồ, danh sách, trích luận văn, so sánh. Công cụ mới `tools\xem_anh_canh.py` in mỗi cảnh ảnh kèm mô tả ảnh và lời đọc, để soát trước khi render |
| 2 | Trường tác giả ảnh có ghi chú tiếng Việt (「Monami (ảnh); tượng: …」) lọt vào mô tả YouTube | Sửa `credit.json`; `seo_kigyo.py` giờ cảnh báo khi tác giả có chữ tiếng Việt hoặc ngoặc |
| 3 | Tiêu đề trùng gần nguyên vế đầu tiêu đề đối thủ (「戦前の売上日本一・カネボウはなぜ…」), trong khi nguồn của mình nói "収入" | Đổi thành 「戦前の収入日本一」: đúng nguồn và không chép |
| 4 | Dòng dưới thumbnail chung chung (「日本一の会社だったのに…」) | Dùng sản phẩm người xem nhớ: 「ナイーブもねるねるねるねも作ったのに…」 |

### Điều chỉnh cho video sau

1. Sau `dien_mau.py`, chạy `tools\xem_anh_canh.py runs\<run>` và đọc hết: ảnh phải đúng nơi, đúng thời, đúng đối tượng mà lời đang nói. Không chắc thì thay bằng đồ họa.
2. So tiêu đề với tiêu đề video đối thủ cùng chủ đề: không trùng vế đầu, không trùng cụm từ dài hơn 8 ký tự.
3. Dòng dưới thumbnail: nêu sản phẩm hoặc con số người xem nhớ, không viết chung chung.

## Video 3: 鈴木商店 (`runs\20261104-suzuki-shoten`, 05/11/2026)

**Kết quả:** `render\final.mp4` dài 32:17, 239 cảnh, 12 chương, đạt `kiem-tra-video` và `kiem_am_thanh.py` (-14,0 LUFS, nhạc ở khoảng lặng -26,0 dB). Giọng xong ngay lần đầu. Ảnh 29% số cảnh. Tiêu đề: 「三井物産を抜いた日本一の商社・鈴木商店はなぜ消えたのか｜年商15億円から10年で」. Chưa tải lên.

**Thời gian thật:** soát 15 phút, render + giọng + dựng 2 lần chạy liền một lệnh khoảng 55 phút. Không lỗi kỹ thuật.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | S090: ảnh di dân lên tàu năm 1921 đặt ở đoạn khai chiến 1914 | Đổi sang `danh_sach` |
| 2 | S115: ảnh tàu hãng khác, chú thích dễ hiểu là tàu của 鈴木 | Thêm 「（イメージ）」 vào chú thích |
| 3 | Dòng dưới thumbnail 「三井物産を抜いて日本一だったのに…」 gần trùng thumbnail kênh mẫu (「三井物産を抜いたのに…」) | Đổi thành 「年商15億円の日本一だったのに…」 |

### Điều chỉnh

1. Luật tiêu đề ở video 2 ("không trùng cụm dài hơn 8 ký tự") quá chặt với khuôn chung `{肩書き}・{社名}はなぜ消えたのか`: phần khuôn và tên công ty được phép trùng, còn vế đầu (danh hiệu) và vế sau `｜…` phải khác đối thủ.
2. Thumbnail cũng phải so với thumbnail đối thủ cùng chủ đề (dòng dưới hay trùng nhất vì cùng dữ kiện). Xem danh sách dòng dưới của kênh mẫu ở `research\PHAN_TICH_KENH_MAU.md` mục 3.
3. Khi xem 9 khung hình, khung chụp ở đầu cảnh có thể chưa có chữ hay điểm (hoạt ảnh chưa chạy). Thấy trống thì chụp lại giữa cảnh trước khi kết luận lỗi.

## Video 4: セゾングループ (`runs\20261105-saison-group`, 05/11/2026)

Video đầu tiên chọn bằng `tools\cham_chu_de.py` (chủ đề kênh mẫu chưa làm) và viết theo `runs\TIEU_CHI_KICH_BAN.md`.

**Kết quả:** `render\final.mp4` dài khoảng 31:15, 226 cảnh, 12 chương. Đạt `kiem-tra-video` và `kiem_am_thanh.py` (-14,0 LUFS, nhạc ở khoảng lặng -24,6 dB). Ảnh chiếm 27% số cảnh. Trùng với 5 video đối thủ 0–0,1%. Tiêu đề: 「池袋西武を日本一にした百社の王国・セゾングループはなぜ消えたのか｜おいしい生活の61年」. Chưa tải lên.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Người viết tự chấm đạt cả 21 mục, nhưng lời đọc nói 「ウィキペディアによると」 16 lần, 「百科事典」 11 lần; 56/241 câu rào đón, có chuỗi 5 câu liền | Người điều phối chấm lại. Bỏ tên Wikipedia khỏi lời đọc, gộp và đổi kiểu rào đón; còn 45/241 câu, không quá 2 câu liền |
| 2 | Sửa câu làm đổi cách gộp dòng thành cảnh (gộp tham lam đến 66 ký tự), làm lệch số cảnh từ S017 | Chỉnh độ dài câu tới khi cách gộp y như cũ; so bằng `split_scenes` trên bản cũ và bản mới. Không phải đánh số lại `dien_mau.py` |
| 3 | Nêu ngày sắp tới (tầng 7 mở 6/11/2026) sẽ cũ ngay khi đăng | Viết 「この秋から冬にかけて」 |
| 4 | Genmax trả 401: khóa trong `.env` và khóa trong biến môi trường hệ thống đều hỏng | Người dùng tự thay khóa trong `.env`. Thử khóa bằng `GET /v1/default-voices` (miễn phí) trước khi chạy `dung` |
| 5 | Phụ đề cắt giữa từ katakana dài (「インベストメ / ント」, 「ル / テアトル」) | Viết lại câu ngắn hơn hoặc thêm 「」/「、」 quanh tên dài. Sau khi dựng, dò `final.srt` tìm chỗ cắt giữa từ |

### Điều chỉnh

1. Lời đọc không nói 「ウィキペディア」. Dữ kiện mức B dùng 「〜とされます」「〜と伝えられます」, nguồn để ở dòng 出典 và mô tả. 「百科事典によると」 chỉ dùng cho 1–3 dữ kiện chính.
2. Bước 3b: người điều phối luôn đếm rào đón bằng máy (tỉ lệ dưới 20%, không chuỗi quá 2 câu) chứ không tin bảng tự chấm.
3. Sửa kịch bản sau khi đã điền hình: chạy so cách gộp cảnh trước khi `tach-loi --ghi-de`.
4. Tên riêng katakana dài hơn khoảng 10 ký tự: rút gọn trong lời đọc, để tên đầy đủ trên hình.
5. Trước `dung`: thử khóa Genmax bằng lệnh miễn phí.

## Video 5: 大倉財閥 (`runs\20261105-okura-zaibatsu`, 05/11/2026)

Chủ đề chọn từ bảng thị trường mới (Google Sheet tab "Thị trường Cty-Gia tộc"): nhóm "gia tộc, tài phiệt 家のその後" đang lên, chưa ai làm 大倉財閥 theo khuôn なぜ消えた. Kịch bản viết thêm 4 tiêu chí 22–25 (3 câu hỏi đánh số, trục ba đời, so với tài phiệt quen, lời hứa cuối mở đầu).

**Kết quả:** `render\final.mp4` dài 31:52, 227 cảnh, 12 chương. 142 dữ kiện (95 mức A), 31 ảnh, ảnh 29% số cảnh. Rào đón 10%, trùng với 3 video đối thủ 0,0%. -14,0 LUFS, nhạc ở khoảng lặng -25,6 dB (âm lượng 0,40), phụ đề 588 dòng không cắt giữa từ. Tiêu đề: 「帝国ホテルも大成建設も生んだ一族・大倉財閥はなぜ消えたのか｜鉄砲店からオークラまで三代」. Đóng gói ở `tai_len\5_okura`.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Kịch bản có 2 câu 「看板が…下ろされた」: gần tên kênh mẫu 看板を下ろした日 | Viết lại; `tools\cham_lai.py` giờ bắt mẫu 「看板…下ろ」 |
| 2 | Bảng cách đọc có khóa ngắn 邸=やしき sẽ đọc 別邸 thành 「べつやしき」 | Thêm 別邸=べってい. Trước khi tạo giọng, dò chỗ kana bị kẹp giữa chữ Hán |
| 3 | Thumbnail kiểu cũ kém nổi bật so với 18 thumbnail nhiều view của ngách (người dùng chưa hài lòng) | Kiểu `noi_bat`: chủ ngữ rất to viền dày, 「なぜ消えた？」 đỏ, nền chàm, mặt to, dải dưới vàng. Người dùng duyệt, đổi cho cả 5 video |
| 4 | Bản nháp thumbnail 「帝国ホテルも大成建設も なぜ消えた？」 hiểu nhầm là hai công ty đó đã mất | Chủ ngữ của 「なぜ消えた？」 phải là thứ đã mất (大倉財閥); thứ còn sống để ở hộp nhãn |
| 5 | Ảnh 堤清二 (thumbnail セゾン) nhỏ, nền trắng | Tách nền bằng flood fill, phóng to; thêm dòng `credit.json` cho ảnh đã chỉnh |
| 6 | 4 chỗ phụ đề cắt giữa từ (「二|代目」, khoảng trắng trong tên tòa nhà, 「ジャン|プ」, 「オリ|ンピック」) | Thêm 「、」, tách câu, đổi khoảng trắng thành 「・」; giữ độ dài để `so_nhom_canh.py` in GIỐNG |
| 7 | `kiem_phu_de.py`, `so_nhom_canh.py` lỗi khi in chữ Nhật trên Windows | Thêm `sys.stdout.reconfigure(encoding="utf-8")` |

### Điều chỉnh

1. Mỗi video có `cach_doc.json` (tên riêng → kana, chỉ cho giọng; phụ đề giữ chữ kanji). Người viết ghi, người điều phối dò khóa ngắn, `tools\doc_thu.py` đọc thử khoảng 12 câu (có `--phai` cho tên chưa chắc), người dùng nghe trước khi tạo giọng cả video.
2. Bước 3b dùng `tools\cham_lai.py` thay cho đếm tay.
3. Thumbnail dùng kiểu `noi_bat` (`"kieu": "noi_bat"` trong `thumb.json`); so ở cỡ điện thoại với thumbnail nhiều view của ngách trước khi chốt. Thử phương án: `tools\thumbnail_kigyo.py runs\<run> thumb_A.json` → `thumbnail_A.jpg`.
4. Nhạc nền 0,40 cho -25 dB đến -26 dB ở khoảng lặng; giữ 0,40 cho video sau.

## Video 6: 大映 (`runs\20261105-daiei`, 05/11/2026)

**Kết quả:** `render\final.mp4` dài 31:53, 225 cảnh, 12 chương. 151 dữ kiện (53 A, 98 B), 24 ảnh dùng được, ảnh 28% số cảnh. Rào đón 7%, 17 câu nói thật. -14,0 LUFS, nhạc ở khoảng lặng -24,6 dB (âm lượng 0,36), phụ đề 583 dòng không cắt giữa từ. Tiêu đề: 「『羅生門』とガメラを生んだ映画会社・大映はなぜ消えたのか｜金獅子賞から破産までの29年」. Đóng gói ở `tai_len\6_daiei`. Bảng cách đọc 143 mục, người dùng nghe duyệt.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | YouTube bắt xác minh "không phải bot", yt-dlp không tải được phụ đề đối thủ | Không lách. Bỏ bước đo trùng cho video này; người viết chỉ dùng tài liệu gốc, tiêu đề so tay với 3 tiêu đề đối thủ |
| 2 | Hai áp phích 『羅生門』『地獄門』 trên Commons là PD ở Nhật nhưng có nhãn **Not-PD-US-URAA** (còn bản quyền ở Mỹ) | Bỏ (cất ở `motion\anh_bo\`), thay bằng ảnh quảng bá PD-US-not renewed / no notice |
| 3 | Bảng cách đọc ghi 封切られた = ふうぎられた | Sửa thành ふうきられた |
| 4 | 3 chỗ phụ đề cắt giữa số / từ (「7|067館」, 「11億|人」, 「ミュ|ージアム」) | Tách câu tại số, đặt tên dài trong 「」; `so_nhom_canh.py` GIỐNG |
| 5 | Nhạc ở khoảng lặng dao động giữa hai lần dựng (-27,2 rồi -23,7 dB ở cùng âm lượng 0,40) | Hạ 0,36 → -24,6 dB. Đo lại sau mỗi lần dựng cuối |
| 6 | Chỉ có một chân dung 永田 giấy phép tự do, dùng 8 lần | Mỗi lần ghi 「写真は1955年」; chấp nhận khi không có ảnh khác |

### Điều chỉnh

1. Ảnh Commons có nhãn `Not-PD-US-URAA` hoặc chỉ PD ở Nhật: không dùng (YouTube có người xem ở Mỹ). Ưu tiên `PD-US-not renewed`, `PD-US-no notice`, `PD-Japan-oldphoto` không kèm URAA.
2. Chủ đề phim ảnh: nhân vật (ガメラ, 大魔神, 座頭市) còn bản quyền → chỉ dùng đồ họa chữ.
3. Âm lượng nhạc mặc định cho video sau: 0,36.
4. Nếu YouTube chặn yt-dlp: không lách, không dùng cookie người dùng; báo người dùng và bỏ bước đo trùng.

## Video 7: 安田財閥 (`runs\20261106-yasuda-zaibatsu`, 06/11/2026)

**Kết quả:** `render\final.mp4` dài 31:52, 227 cảnh, 12 chương. 166 dữ kiện (81 A, 81 B, 3 A/B; F166 do người điều phối thêm), 32 ảnh Commons + 1 chân dung tách nền, ảnh 29% số cảnh. Rào đón 6%, 19 câu nói thật, trùng với 3 video đối thủ (偉人エピソードX, ギルド日本史, 名家の歴史) 0,0%. -14,0 LUFS, nhạc ở khoảng lặng -29,1 dB (âm lượng 0,36), phụ đề 587 dòng không cắt giữa từ. Tiêu đề: 「安田講堂を贈った銀行王の一族・安田財閥はなぜ消えたのか｜日本一の預金から富士銀行まで三代」. Đóng gói ở `tai_len\7_yasuda`. Bảng cách đọc 168 mục, người dùng nghe 14 câu và duyệt.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Kịch bản nói 両国公会堂 「2001年からは使われていません」 (nguồn cũ), nhưng tòa nhà đã bị phá, nơi đó nay là 刀剣博物館 (mở 2018) | Người điều phối tra lại, sửa câu, thêm F166. Ảnh 2014 ghi 「建物はいまはない」 |
| 2 | Phụ đề cắt giữa số 「600|万円」 | Thêm 「、」 trước số; `so_nhom_canh.py` GIỐNG, chạy `tach-loi` (không `--ghi-de`) → `dien_mau.py` → `nap-motion` → `dung` |
| 3 | Chân dung 安田 gốc chỉ 450×550, nền chuyển màu nên tô loang không tách được | Cắt theo đường viền vẽ tay, lọc median bỏ hạt in lưới, phóng 4× LANCZOS (`yasuda_zenjiro_tach.png`, PD như gốc) |
| 4 | Chữ niên biểu và ghi chú chân dung xuống dòng giữa từ trên hình (「安/田屋」) | Mốc niên biểu ≤ 8 ký tự, ghi chú chân dung ≤ 20 ký tự |
| 5 | Agent điền hình lỡ chạy `nap-motion` cho lần chạy khác (大映) để so cảnh báo | Không hại (ghi lại từ `canh.json` không đổi). Prompt sau ghi rõ: chỉ chạy lệnh cho lần chạy của mình |

### Điều chỉnh

1. Câu về hiện trạng ("いまも…", "使われていません", "休館が続いて") phải kiểm bằng nguồn mới nhất; người điều phối tra lại các câu này ở chương 11–12 trước khi tách cảnh.
2. Đọc thử tên khó (`doc_thu.py`) chạy song song với bước điền hình: chỉ cần `script.md` và `cach_doc.json`, tiết kiệm thời gian chờ người dùng nghe.
3. Âm lượng nhạc 0,36 đã là mặc định trong `channels\kigyo_shi\profile.yaml`.
4. yt-dlp lần này tải được phụ đề đối thủ: chặn bot là lúc có lúc không, mỗi video vẫn thử một lần (không lách).

## Video 8: 三井家 (`runs\20261106-mitsui-ke`, 06/11/2026), video đầu của loạt 「なぜ終わらなかったのか」

**Kết quả:** `render\final.mp4` dài 32:22, 229 cảnh, 12 chương. 162 dữ kiện (127 A, 28 B, 7 A/B), 33 ảnh Commons + 3 ảnh cắt / tách nền, ảnh 30% số cảnh. Rào đón 3%, 26 câu nói thật. -14,0 LUFS, nhạc ở khoảng lặng -29,3 dB (âm lượng 0,36), phụ đề 617 dòng. Tiêu đề: 「三越も三井物産も生んだ一族・三井家はなぜ終わらなかったのか｜分けない家訓と外の番頭」. Thumbnail 「三井家 / なぜ終わらない？」. Đóng gói ở `tai_len\8_mitsui`. Bảng cách đọc 201 mục, người dùng nghe 16 câu và duyệt (池田成彬 = いけだしげあき).

### Loạt mới: gia tộc không kết thúc

- Người dùng muốn thêm chủ đề "gia tộc giàu lâu đời, chiếm thị phần ra sao". Nhu cầu đo ngày 06/11: video về 三井・三菱・住友 59–65 vạn view, 岩崎弥太郎 4 video 24–39 vạn, 堤康次郎 32–39 vạn, cùng tệp người xem với kênh.
- Làm thành loạt trong kênh, không đổi kênh: câu hỏi 「なぜ終わらなかったのか」, chữ hỏi thumbnail 「なぜ終わらない？」, giữ mọi quy trình. Kết nối với các video "đã biến mất" (安田, 大倉, 鈴木商店) bằng bảng so sánh có nguồn.
- Ba điều thêm cho loạt này: (1) con số thị phần / quy mô phải có nguồn A/B và năm số liệu; (2) người còn sống và công ty đang hoạt động chỉ nêu theo tài liệu chính thức, phần hôm nay ngắn và trung tính; (3) người viết liệt kê mọi câu hiện trạng kèm mã F và năm nguồn để người điều phối tra.
- Nguồn A tốt nhất là trang lịch sử chính thức của chính tập đoàn (三井広報委員会 「三井ヒストリー」, tư liệu 三井文庫). Phần tự đánh giá của tập đoàn (ví dụ 「平和主義勢力」) không đưa vào lời đọc; góc nhìn khác lấy từ từ điển học thuật.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | YouTube lại chặn tải phụ đề đối thủ (video 7 tải được, video 8 không) | Không lách. Bỏ đo trùng; người viết chỉ dùng tài liệu gốc, tránh mọi cụm từ trong 6 tiêu đề đối thủ |
| 2 | YouTube Data API hết hạn mức (429) giữa lúc đo nhu cầu | Dùng `yt-dlp --flat-playlist -j "ytsearch25:…"` để tìm đối thủ; hạn mức cấp lại theo giờ Thái Bình Dương |
| 3 | Phụ đề cắt giữa số 「272|年後」 | Thêm 「、」 trước số; `so_nhom_canh.py` GIỐNG |
| 4 | Máy báo 2 chỗ 「オリエンタル・|バンク」「デパートメント・|ストーア」 | Giữ: ngắt ngay sau 「・」 là ranh giới từ; câu sau là trích dẫn nguyên văn |
| 5 | Tranh 高利 vẽ cả người ngồi, mặt nhỏ | Ảnh cắt nửa trên `takatoshi_jo.jpg` cho cảnh, `takatoshi_tach.png` (tách nền, phóng 2×) cho thumbnail |

### Điều chỉnh

1. `kiem_phu_de.py` báo chỗ ngắt ngay sau 「・」: xem bằng mắt, được giữ nếu là ranh giới từ.
2. Chủ đề loạt 「なぜ終わらなかったのか」 kế tiếp: 住友 (別子銅山, 400 năm), 鴻池, 茂木家 (キッコーマン). 岩崎家 đã làm ở video 9. Đo nhu cầu lại khi API còn hạn mức.

## Video 9: 岩崎家 (`runs\20261107-iwasaki-ke`, 07/11/2026), loạt 「なぜ終わらなかったのか」

**Kết quả:** `render\final.mp4` dài 33:31, 231 cảnh, 12 chương. 156 dữ kiện (127 A, 20 B, 9 A/B), 36 ảnh Commons cùng 2 ảnh cắt / tách nền; ảnh chiếm 27% số cảnh. Rào đón 2%, 37 câu trong 「」. Trùng 0% với phụ đề 4 video đối thủ. Âm thanh -14,0 LUFS, nhạc ở khoảng lặng -26,0 dB; phụ đề 627 dòng, 0 chỗ ngắt giữa từ. Tiêu đề: 「スリーダイヤと丸の内の一族・岩崎家はなぜ終わらなかったのか｜弟に託し、海を手放した四代」. Thumbnail: 「スリーダイヤの一族 / 岩崎家 / なぜ終わらない？ / 解散を最後まで拒んだのに…」. Đóng gói ở `tai_len\9_iwasaki`. Bảng cách đọc 161 mục; người dùng nghe 16 câu và duyệt.

### Điều làm tốt

- Chủ đề chọn bằng dữ liệu (`research\tim_nguoi.py`): lượt xem Wikipedia tăng 1,74 lần, đối thủ chỉ kể đời tư của 弥太郎. Góc kể là bốn đời chủ và 3 câu hỏi về quyết định kinh doanh. Không có chuyện thê thiếp.
- Nguồn A chính là loạt 「三菱人物伝」 của 三菱史料館, gồm bốn bài cho bốn đời. Trang mitsubishi.com chặn script (403) nên đọc bằng trình duyệt.
- Phụ đề đối thủ tải được cả 4 video, nên đo trùng được.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Lệnh thử khóa Genmax báo 401 dù khóa đúng: lệnh thử không gọi `load_env()`, nên dùng biến khóa cũ trên máy | Thử khóa bằng `load_env()` rồi mới `load_engine().Genmax()`; đã ghi vào `QUY_TRINH.md` bước 7 |
| 2 | Lời đọc có chi tiết 「給料を半分に削って」 không có trong `nguon.md` (agent điền hình phát hiện) | Bỏ chi tiết đó; `so_nhom_canh.py` GIỐNG. Người điều phối dò mọi con số, chi tiết trong lời đọc ngược về mã F |
| 3 | Câu hiện trạng 「補修のため休館」 không khớp lời trang chính thức (「建物工事のため、当面の間、休館」) | Viết theo đúng lời trang chính thức của chủ thể |
| 4 | Chạy `dung → cat-clip → dung` trong một lệnh: lần `dung` đầu dừng ở bước tạo giọng, `cat-clip` báo thiếu `timeline.json`, nhưng lần `dung` thứ hai vẫn xuất video (chưa cắt clip) | Đọc toàn bộ kết quả từng lệnh, không chỉ vài dòng cuối; chạy lại `cat-clip` → `dung` |
| 5 | Phụ đề cắt giữa 5 tên dài (荘田|平五郎, ジ|ョサイア, ウォート|ン, 三菱商|事, 飛行|機) | Thêm 「、」 trước tên; một dòng phụ đề khoảng 16 ký tự |
| 6 | Ảnh 弥太郎 có dòng chữ "Provision of reference: Mitsubishi Archives"; venv không có PIL | Cắt bằng ffmpeg; tách nền bằng Python hệ thống |
| 7 | Dòng dưới thumbnail người viết đề xuất gõ sai 「最後まので」 | Soát chính tả mọi chữ trên thumbnail trước khi giao |

### Điều chỉnh

1. Câu cuối mỗi chương phải kéo sang chương sau bằng một việc sắp xảy ra, không chỉ báo "bước sang thời…".
2. Ảnh chiếm 27%, dưới mức 30%, vì kịch bản trích dẫn dày (33 cảnh trích dẫn). Lần sau khi nguồn có nhiều trích dẫn, gộp bớt trích dẫn ngắn vào lời kể.

## Video 10: 中内家 / ダイエー (`runs\20261107-nakauchi-ke`, 07–08/11/2026), loạt 「なぜ消えたのか」

**Kết quả:** `render\final.mp4` dài 34:35, 224 cảnh, 12 chương. 27 nguồn, 152 dữ kiện (78 A, 68 B, 6 A/B), 36 ảnh Commons; ảnh chiếm 28% số cảnh. Rào đón 9%, 9 cảnh trích dẫn (video 9 có 33). Trùng tối đa 0,1% với phụ đề 8 video đối thủ. Âm thanh -14,0 LUFS, nhạc ở khoảng lặng -29,0 dB; phụ đề 609 dòng, 0 chỗ cắt giữa từ. Hình và giọng khớp ở 224/224 cảnh. Tiêu đề: 「三越を抜いた薬局の一家・中内家はなぜ消えたのか｜すき焼きから始まった三代」. Thumbnail: 「ダイエー創業の一家 / 中内家 / なぜ消えた？ / 三越を抜いて日本一だったのに…」, nền ダイエー三宮 sập năm 1995. Đóng gói ở `tai_len\10_nakauchi`. Bảng cách đọc 97 mục; người dùng nghe 17 câu và duyệt.

### Điều làm tốt

- Chủ đề chọn theo **lượt xem của video mới (180 ngày) về chủ đề**, không theo số đối thủ: ダイエー có video 25,4 vạn view tháng 9/2026. Lần đầu mình đề xuất 淀屋 vì ít cạnh tranh; người dùng chỉ ra cầu nhỏ, và người dùng đúng.
- Theo hướng của người dùng: **gom các mạch được xem nhiều nhất của chủ đề** (すき焼き ở ルソン, 千林 1957, 30 năm với 松下, vượt 三越 1972, ローソン, ホークス, mô hình đất, động đất 1995, イオン), mỗi mạch có nguồn riêng và câu chữ riêng; gia tộc ba đời làm sợi chỉ. Người viết không mở phụ đề đối thủ, đo trùng vẫn 0–0,1%.
- Câu trả lời "vì sao sụp đổ" lấy đúng 4 nguyên nhân do 産業再生機構 viết (A), không tự suy diễn.
- Câu hiện trạng tra lại cả bốn: ダイエー資料館 mở lại 9/9/2026, cửa hàng 学園都市 đổi sang フードスタイル 28/8, lộ trình đổi tên cửa hàng, 中内潤 là 理事長. Tin "tên cửa hàng tháng 10/2026" không có thông cáo nên không nói.
- Chữ 㓛 (U+34DB) hiện đúng ở Yu Gothic (phụ đề) và Noto Sans/Serif JP (hình): kiểm bằng ffmpeg drawtext và khung hình dựng thử.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | **Hình đổi cảnh trước khi giọng đọc xong** ở 176/224 cảnh, giọng trễ hình trung vị 2 giây, tối đa 3,25 (cảnh trích dẫn hiện trống trong lúc giọng còn đọc câu cũ). Lỗi có ở **cả 9 video trước**. Gốc: (a) `ky_tu_moi_giay: 6.9` cao hơn giọng thật (5,44–5,52 ký tự/giây ở tốc độ 0,85, tức 6,4); (b) câu nhiều con số (1957年…) đọc lâu hơn số ký tự; (c) cảnh tối đa 12 giây. Clip ngắn hơn giọng, `cat-clip` không kéo dài được, bộ dựng cho giọng trễ tới 3 giây rồi mới kéo hình | `studio\motion.py`: cảnh đã có giọng thật (`render\timeline.json`) lấy độ dài **giọng thật + 1,2 giây**; câu chưa có giọng vẫn ước lượng. `studio\goi.py`: cảnh dài theo lời chỉ chặn theo cảnh dài nhất. Hồ sơ: `ky_tu_moi_giay: 6.4`, `thoi_luong_giay: 20`. Thêm bài kiểm; 132 đạt. Sau sửa: trễ trung vị 0,25 giây (đúng khoảng lặng đầu cảnh), 0/224 cảnh đổi sớm |
| 2 | Sửa hồ sơ kênh nhưng lần chạy không đổi: mỗi lần chạy có bản sao `runs\<run>\profile.yaml` | Sửa cả bản sao của lần chạy |
| 3 | `ve_song_song.py` bỏ qua cảnh đã có clip nên không vẽ lại; `dung` ưu tiên `clips_cat\` cũ | Đổi tên `motion\out` và `clips_cat` sang bản dự phòng rồi mới render, dựng |
| 4 | Câu bị đọc nhanh ở lần dựng đầu (clip ngắn) được đọc lại ở tốc độ thường khi clip đủ dài, nên dài hơn cảnh đã định (S028) | Sau lần dựng đầu theo clip mới, `nap-motion` lại để lấy độ dài giọng mới, chỉ render lại cảnh dài hơn clip (`--lam-lai`) |
| 5 | Phụ đề cắt giữa 5 cụm (丸|和, ドム|ドム, ト|ポス, 兵庫県|内, 拡大路|線) | Thêm 「、」 trước tên trong 「」 và giữa các cụm trích liền nhau |
| 6 | Mô tả ghi 「Unknown author」 và 「hamakamui / Hamakamui」 thành hai người | Sửa `credit.json` (作者不明, Hamakamui) rồi tạo lại SEO |

### Điều chỉnh

1. Sau mỗi lần `dung`, đo độ lệch hình–giọng: đọc `timeline.json` (`voice_start` − `bat_dau` của cảnh; điểm hết giọng so với điểm hết cảnh). Đạt khi không cảnh nào đổi hình trước khi giọng dứt.
2. Thứ tự dựng mới: `dung` lần đầu (có giọng) → `nap-motion` + `dung-canh` (độ dài theo giọng thật) → render lại cảnh đổi độ dài → `nhan-clip --ghi-de` → bỏ `clips_cat` cũ → `dung` → `cat-clip` → `dung`.
3. Người còn sống (中内潤, 中内正): chức vụ ở công ty và trường lấy từ trang chính thức (A) và báo lớn (神戸新聞, 読売, B, có 「によると」); không kể đời tư hay động cơ.
4. Không có chân dung tự do của nhân vật chính thì thumbnail dùng ảnh nơi chốn mạnh nhất của câu chuyện (cửa hàng sập năm 1995 còn rõ biển).

## Video 11: 和田家 / ヤオハン (`runs\20261109-wada-ke`, 09/11/2026), loạt 「なぜ消えたのか」

**Kết quả:** `render\final.mp4` dài 33:45, 221 cảnh, 12 chương. 23 nguồn, 167 dữ kiện (37 A, 129 B, 1 A/B), 36 ảnh Commons; ảnh chiếm 26% số cảnh. Rào đón 12%, 10 cảnh trích dẫn. Trùng tối đa 0,2% với phụ đề 5 video đối thủ. Âm thanh -14,0 LUFS, nhạc ở khoảng lặng -28,7 dB; phụ đề 604 dòng, 0 chỗ cắt giữa từ. Giọng trễ hình trung vị 0,25 giây, **0/221 cảnh đổi hình trước khi giọng dứt ngay từ lần làm đầu theo quy trình mới**. Tiêu đề: 「ヤオハンを興した熱海の一家・和田家はなぜ消えたのか｜母の八百屋と五人の息子」. Thumbnail: 「ヤオハン創業の一家 / 和田家 / なぜ消えた？ / 上海に百万人を集めたのに…」, nền 第一八佰伴, ảnh cưới 1928 của 良平・カツ. Đóng gói ở `tai_len\11_wada`. Người dùng nghe 12 câu và duyệt cách đọc ngay lần đầu.

### Điều làm tốt

- Mở bằng một tin hiện tại có văn bản chính thức: マックスバリュ東海 thông báo ヤオハン商品券 hết dùng 30/9/2026, hoàn tiền đến 26/2/2027 (PDF ngày 1/10/2026, người điều phối mở đọc lại). Kết quay về 「引き出しの商品券」.
- Mâu thuẫn nguồn được xử lý theo mức A: 16 cửa hàng bán năm 1997 cho セイフー (ダイエー系, 有報), **không phải ジャスコ** như lời giao việc; 「100万人超」 (上海市, A) nói trước, 107万人 (B) nói sau.
- Quy trình dựng mới (video 10) chạy trơn: dựng đầu còn 44 cảnh đổi sớm → `nap-motion` theo giọng thật → render lại 102 cảnh → `cat-clip` → 0/221.
- Thử cách sửa phụ đề bằng chính `split_caption` của engine (`max_chars` 20, tiếng Nhật) trước khi sửa kịch bản: 4 chỗ sửa một lần là hết.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | `tach-loi` chỉ ra 138 cảnh (video 10: 224) vì số ký tự mỗi cảnh tính theo `thoi_luong_giay: 20` mới → cảnh dài, hình đổi chậm | Thêm `clip.ky_tu_toi_da: 66` (mức video 10) vào hồ sơ kênh và lần chạy: chia cảnh như cũ, độ dài cảnh vẫn tới 20 giây theo giọng thật. Tách 4 dòng lời dài hơn 66 ký tự thành hai câu. 221 cảnh |
| 2 | Người viết gắn người em kế của 一夫 với vụ bị bắt năm 1998 chỉ bằng Wikipedia và báo (người có thể còn sống; bản án không đọc được) | Bỏ câu nối tên; chỉ nói 「旧経営陣の3人が…疑いで」 kèm 「報道によると」. 粉飾 dẫn từ 国会会議録 (2001, 2002: 7 năm, lộ ra khi phá sản), không nói "lộ ra năm 1996" |
| 3 | Agent điền hình phát hiện 6 câu không có mã F hoặc vượt nội dung mã F (mua công ty Hồng Kông, ngân hàng nghi sổ sách, 湯船・ツツジ, Trung Quốc không đòi bồi thường, cơ sở 生長の家 ở Brazil, cửa hàng Hồng Kông thành ジャスコ) | Viết lại theo đúng mã F; giữ cách chia cảnh bằng `so_nhom_canh.py` (chỉnh độ dài câu tới khi in GIỐNG) |
| 4 | Phụ đề cắt giữa 4 cụm (ショッピングセン|ター ×2, シンガ|ポール, ジャパ|ン) | Thêm 「、」 hoặc đổi cách nói; đọc lại 4 câu, render lại 1 cảnh dài thêm (S153) |
| 5 | Mô tả SEO viết 「熱海の大火から会社更生法までの67年」 (1950→1997 là 47 năm) | Sửa 「熱海での開業から…67年」 |
| 6 | Ảnh gợi ý sai thời/nơi: ảnh 熱海 2007 và 2010 cạnh lời về 1950 và về 飯塚・上海, ảnh 熱海 thời Minh Trị cho năm 1930, cửa hàng 小田原 không thuộc 16 cửa hàng bán năm 1997 | Agent điền hình đổi sang đồ họa sau khi xem `xem_anh_canh.py` |

### Điều chỉnh

1. Hồ sơ kênh có `clip.ky_tu_toi_da: 66`: tách cảnh theo nhịp hình cũ, độ dài cảnh theo giọng thật. Dòng lời nào dài hơn 66 ký tự thì tách câu trước khi `tach-loi`.
2. Giao người viết: **mọi câu có chi tiết cụ thể (hành động, đồ vật, lý do) phải có mã F chứa đúng chi tiết đó**; người điều phối đối chiếu các câu agent điền hình báo "không có mã F" trước khi đọc giọng.
3. Người còn sống liên quan vụ hình sự: chỉ nêu khi có bản án hoặc văn bản chính thức đọc được; nếu không, nói về nhóm (旧経営陣) và không nối với người trong gia đình.
4. Sửa phụ đề: thử câu mới bằng `split_caption(text, 20, "ja")` của `engine\ai_film_studio.py` trước khi sửa kịch bản.
5. Số năm trong mô tả SEO (「…までのN年」) phải tính lại từ hai mốc ghi trong câu.

## Video 12: 堤家 / 西武鉄道・コクド (`runs\20261109-tsutsumi-ke`, 09/11/2026), loạt 「なぜ消えたのか」

**Kết quả:** `render\final.mp4` dài 34:18, 227 cảnh, 12 chương. 36 nguồn, 149 dữ kiện (115 A, 30 B, 4 A/B), 40 ảnh Commons (dùng 36); ảnh chiếm 26% số cảnh. Rào đón 6%. Trùng 0,0% với phụ đề 6 video đối thủ. Âm thanh -14,0 LUFS, nhạc ở khoảng lặng -28,1 dB; phụ đề 609 dòng, 0 chỗ cắt giữa từ; 0/227 cảnh đổi hình trước khi giọng dứt. Tiêu đề: 「軽井沢から西武を築いた一家・堤家はなぜ消えたのか｜名義株と土地の百年」. Thumbnail: 「西武を築いた一家 / 堤家 / なぜ消えた？ / 電車もホテルも球団も持っていたのに…」, chân dung 堤康次郎 1955, nền 赤坂プリンス新館. Đóng gói ở `tai_len\12_tsutsumi`. Người dùng chọn chủ đề trong 3 phương án (đo lượt xem video dài gần đây) và duyệt 14 câu đọc thử ngay lần đầu.

### Điều làm tốt

- Chọn chủ đề bằng lượt xem video dài gần đây (yt-dlp 09/11): 堤義明 / 西武 26,9 vạn (09/2026) so với そごう 11,5 vạn, 住友家 2,7 vạn. Hỏi người dùng vì có ràng buộc người còn sống và trùng một phần video 4.
- Trục là một cơ chế có tài liệu chính thức (名義株: 有報 訂正, báo cáo 監視委, bản án dân sự 2008/2011, 国会), không phải đời tư. Đối thủ dùng nhiều chuyện tình cảm, tài sản cá nhân; mình không dùng mà trùng vẫn 0%.
- Mở và các câu hiện trạng 2026 đều mở văn bản gốc: 適時開示 tăng giá vé 「2002年以来24年ぶり」, mua lại khách sạn 紀尾井町 qua SPC (29/7/2026).
- Quy trình dựng mới chạy đúng lần thứ hai: dựng đầu 32 cảnh đổi sớm → render lại 117 cảnh → 0/227. Phụ đề đạt ngay vì người viết thử `split_caption` từ lúc viết.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Người còn sống trong vụ hình sự: văn bản chính thức (国会会議録 2005/3) nêu tên người bị bắt và khởi tố, nhưng không văn bản chính thức đọc được nào nêu tên cùng bản án (báo cáo 監視委 chỉ ghi 「会社役員」) | Câu bị tố giác/khởi tố nêu tên theo 国会 (F152); câu mức án dùng 「会長だった被告」. Rút câu để giữ cách chia cảnh (`so_nhom_canh.py` GIỐNG) |
| 2 | Câu không có mã F (khách sạn 箱根 do 村野藤吾 thiết kế năm 1978) và câu nói vượt nguồn (vượt 8割 là "không được niêm yết tiếp") | Thay bằng dữ kiện có mã (品川 1978, A); viết lại đúng chữ nguồn |
| 3 | Thumbnail đặt chân dung 康次郎 cạnh dòng 「世界の番付で4年首位」, nhưng người đứng đầu Forbes là 義明 | Đổi dòng dưới sang 「電車もホテルも球団も持っていたのに…」 (đúng với cả gia đình) |
| 4 | **Số thập phân bị cắt thành hai dòng phụ đề** (「およそ1.」 \| 「5兆円です。」): `split_caption` coi 「.」 là hết câu. `kiem_phu_de.py` không bắt vì chỉ xét katakana/kanji/số liền nhau. Có ở 6 video đã đóng gói: video 1 (9 chỗ), 2 (3), 4 (2), 8 (6), 9 (6), 10 (2) | `engine\ai_film_studio.py`: không tách câu sau dấu chấm đứng trước chữ số; thêm `tests\test_phu_de.py` (134 đạt). `kiem_phu_de.py` bắt thêm kiểu lỗi này. Video cũ cần dựng lại (không tốn credit), gộp vào việc sửa giọng trễ hình video 1–9 |
| 5 | Tên tác giả Commons 「っ」 trông như lỗi gõ trong mô tả | Tra API Commons: tên tài khoản đúng là 「っ」; ghi 「User:っ」 |

### Điều chỉnh

1. Người còn sống trong vụ hình sự: tên chỉ đi cùng sự việc mà văn bản chính thức nêu tên (bắt, khởi tố); mức án theo bản án/監視委, gọi bằng chức danh nếu văn bản không nêu tên.
2. Thumbnail: dòng dưới phải đúng với người trên chân dung (hoặc với cả gia đình).
3. Video 1–10 khi dựng lại để sửa giọng trễ hình thì phụ đề số thập phân tự đúng (engine đã sửa); chạy `kiem_phu_de.py` sau khi dựng.

## Học từ kênh khác: ポロッポ 世界の深層チャンネル (09/11/2026)

Video `IJvgS0sFu-g` (投資ジャーナル事件 / 中江滋樹): **425.855 view sau 5 ngày**, kênh chỉ 1.320 người đăng ký, 28:32, 11 chương. Cùng kiểu nguồn với mình (国会会議録, 警察白書, Commons, ảnh AI có ghi chú). Phụ đề và storyboard lưu ở `research\doi_thu\hoc\` (người viết không đọc).

**Cảnh báo:** đây là một video nổ lẻ. 6 video khác của kênh 131–12.305 view; hai video sau bắt chước công thức tiêu đề 「…して死んだ…の末路」 chỉ được 5.202 và 131 view. Chủ đề (ヤクザ, 天才相場師, chết cô độc) có thể là phần lớn lý do. Học kỹ thuật kể, không học công thức tiêu đề, không chép câu chữ, phong cách hình hay dấu ấn của họ.

### So với kênh mình (video 12)

| Điểm | Họ | Mình |
|---|---|---|
| Câu đầu | Kết cục cực đoan của nhân vật trong 1 câu (mất tiền ai, chết ở đâu) | Tin hiện tại (tăng giá vé 2026), rồi Forbes |
| Mở bài | 4 câu hỏi cụ thể, mỗi câu là một **điểm vô lý trong hồ sơ** (con số cảnh sát đổi giữa hai kỳ 国会; ngày bắt trùng một sự kiện khác), hứa "nối lại sẽ ra một giả thuyết" | Hứa chung "xem xong sẽ thấy…" |
| Tên chương | Câu hỏi (cũng là tên chương trên thanh thời gian YouTube) | Danh từ (千ヶ滝の六十万坪) |
| Cuối chương | Nhắc lại câu hỏi → "答えは…" trả lời rõ → đặt câu hỏi của chương sau | Câu TENSION hướng tới chương sau; cả kịch bản chỉ 4 「でしょうか」 |
| Nói với người xem | Hỏi người xem đoán; nhắc "nhớ chi tiết ở chương trước" | Gần như không |
| Vật xuyên suốt | Một đồ vật (biểu đồ vẽ tay) xuất hiện từ lúc nhỏ, quay lại 4 lần, là câu trả lời cuối | Có (vé tàu), nhưng chỉ ở đầu và cuối |
| Quy mô tiền | Đổi ra số tháng lương của người mới đi làm thời đó | Đổi ra m², năm |
| Kết | Chương 考察: xếp lại mọi manh mối, đưa một kết luận, câu cuối về con người | Chương なぜ消えたのか trả lời 3 câu hỏi (gần giống) |
| Hình | Một phong cách minh họa thống nhất, nhân vật lặp lại; **sơ đồ giải thích cơ chế** (kim tự tháp hội viên, vòng lặp mua → giá lên); trích 国会 dạng tờ giấy, gạch chữ đỏ; đánh số manh mối ①②③ | Ảnh Commons + thẻ chữ + clip AI; cơ chế (名義株) chủ yếu bằng gạch đầu dòng |
| Thumbnail | 3 lớp chữ, dòng dưới là **một bí ẩn cụ thể** (một đồ vật để lại) | Dòng dưới là tóm tắt (「…持っていたのに…」) |
| Mô tả | Chương dạng câu hỏi, link video liên quan, danh sách nguồn có ngày họp 国会, ghi chú ảnh AI, câu hỏi mời bình luận | Có nguồn, chưa có câu hỏi mời bình luận |

### Áp dụng được (chờ người dùng duyệt)

1. Mở bài: câu đầu là kết cục của gia đình; sau đó 3 điểm vô lý **lấy từ văn bản chính thức** (số liệu lệch giữa hai tài liệu, ngày trùng nhau), hứa trả lời cuối video.
2. Tên chương dạng câu hỏi; mỗi chương kết bằng câu trả lời rõ rồi câu hỏi mới.
3. Chọn một vật xuyên suốt có nguồn, cho quay lại ít nhất 3 lần.
4. Thumbnail: dòng dưới là một bí ẩn cụ thể có thật trong video.
5. Hình: thêm loại cảnh sơ đồ cơ chế (cần thêm mẫu trong motion, không tốn credit).
6. Giữ chuẩn của mình: giả thuyết phải ghi rõ là giả thuyết và chỉ dựng từ dữ kiện có mã F; người còn sống vẫn theo quy tắc văn bản chính thức.

## Học từ 4 kênh lịch sử mới (09/11/2026)

5 video người dùng gửi, đều đăng 02–08/11/2026, kênh đều mới và ít người đăng ký (412–4.120), đều dùng hình AI và giọng AI:

| Kênh | Video | View | Các video khác của kênh |
|---|---|---|---|
| 兵器再審 (412 đk) | 機関銃 奉天でロシアの4倍 | 70,9 vạn | **đều tay**: 6/7 video 6,7–42 vạn |
| 兵器再審 | 三八式歩兵銃は本当に時代遅れだったのか | 42,4 vạn | |
| 日本史の古書店 (2.730 đk) | 大奥はその後どうなったのか | 136,9 vạn | 1,5–13 vạn |
| 硝煙の記憶 (1.720 đk) | 203高地 | 26,2 vạn | 2,3–30,9 vạn |
| 老後の知恵袋 (1.430 đk) | 近衛師団 (ngôi thứ hai 「あなた」) | 19,9 vạn | 0,4–14,7 vạn, 21 video cùng khuôn |

### Điểm chung đáng học

1. **Tiêu đề lật một điều ai cũng tin**, rồi hỏi lại bằng hồ sơ: 「本当に…だったのか」, 「…なのに、なぜ…」, 「その後どうなったのか」. Câu trong ngoặc 「」 là lời đồn/nhận định cũ; 【】 chứa từ khóa tra cứu.
2. **Mở bài:** nêu điều ai cũng biết → một con số đảo ngược nó (ví dụ bị áp đảo ở trận trước, gấp 4 lần đối thủ hai tháng sau) → hứa trả lời 3 câu hỏi theo thứ tự. 日本史の古書店 còn trả lời trước một câu ngay đầu video và hứa người xem "kể lại được cho người khác".
3. **Kết bằng một điều bất ngờ thứ hai** (đã thắng nhờ thứ đó nhưng sách giáo khoa sau chiến tranh lại không coi nó là chính), không kết bằng tóm tắt.
4. **Thành thật về giới hạn nguồn:** ghi rõ chỗ nào nguồn không biết, số khác nhau giữa các tài liệu, tranh AI là tái hiện. Kênh mình đã làm vậy; cứ giữ.
5. **Chương con dày** (20–30 mốc chương, mỗi mốc 1–2 phút), tên mốc là sự việc cụ thể kèm năm.
6. **Thumbnail:** tranh màu đậm, có cảnh và người đang hành động, chữ vàng/đỏ viền đen chiếm nửa ảnh, 1 con số hoặc 1 câu hỏi. **So cạnh nhau, thumbnail video 12 của mình (ảnh đen trắng, nền chàm) là cái mờ nhất.**
7. **Nhóm người xem:** lịch sử quân sự Minh Trị – Chiêu Hòa và Edo đang có lượng xem gợi ý rất lớn; kênh 412 người đăng ký vẫn ra 70 vạn view. Đề tài công ty/gia tộc gắn với chiến tranh (máy bay, đóng tàu, tài phiệt mới ở Mãn Châu) chạm được nhóm này.

### Áp dụng cho kênh mình (chờ người dùng duyệt)

- Video 13 thử tiêu đề dạng "lật một điều ai cũng tin" có nguồn, giữ nhãn loạt 「なぜ消えたのか」 ở sau dấu ｜.
- Thử thumbnail kiểu mới: nền là cảnh màu (ảnh AI tái hiện có ghi chú, hoặc ảnh Commons tô màu), chữ to hơn, một con số. Làm 2 phương án để người dùng so.
- Mở bài: điều ai cũng biết → con số đảo ngược → 3 câu hỏi; câu kết là điều bất ngờ thứ hai.

## Video 13: 中島家 / 中島飛行機 (`runs\20261109-nakajima-ke`, 09–10/11/2026), loạt 「なぜ消えたのか」

**Kết quả:** `render\final.mp4` dài 34:14, 228 cảnh, 12 chương. 25 nguồn, 143 dữ kiện (86 A, 54 B, 1 A/B, 2 C không dùng), 43 ảnh Commons; ảnh chiếm 24% số cảnh. Rào đón 14%. Trùng ≤0,2% với phụ đề 5 video đối thủ. Âm thanh -14,0 LUFS, nhạc ở khoảng lặng -27,5 dB; phụ đề 594 dòng, 0 chỗ cắt giữa từ; 0/228 cảnh đổi hình trước khi giọng dứt (dựng đầu xong render lại 116 cảnh). Tiêu đề: 「零戦の6割を造った一家・中島家はなぜ消えたのか｜太田の家と飛行機の30年」. Thumbnail khung cũ (`noi_bat`, tông `am`, dải vàng): 「零戦の6割を造った一家 / 中島家 / なぜ消えた？ / 戦闘用機体の37%を造っていたのに…」. Đã thử thêm bản B (tông đỏ nâu, chữ vàng, dải trắng); người dùng chọn B rồi đổi lại khung cũ để đồng bộ với các video trước. Đóng gói ở `tai_len\13_nakajima`. Người dùng duyệt 23 câu đọc thử ngay lần đầu.

### Điều làm tốt

- Áp dụng 3 kỹ thuật học từ kênh khác: mở bằng điều ai cũng tin (「零戦は、三菱の飛行機」) → con số đảo ngược (6割以上, USSBS 37%) → tin 2026; 3 câu hỏi đánh số, chương 10–11 trả lời từng câu, cuối mỗi chương là câu hỏi dẫn sang chương sau; vật xuyên suốt là ngôi nhà 旧中島家住宅 (chương 1, 2, 3, 4, 9, 11, 12).
- Mở và câu hiện trạng 2026 đều mở văn bản gốc: thông cáo SUBARU 25/9/2026 (FAN MEETING) và 29/10/2026 (45.157 xe), 『文化財だより』 1/2026.
- Ngôi nhà chỉ có 2 ảnh: agent điền hình thay các beat thừa bằng niên biểu ngôi nhà, thẻ 家紋, thẻ số liệu, không ảnh nào quá 3 lần.

### Lỗi gặp và đã sửa

| # | Lỗi | Sửa |
|---|---|---|
| 1 | Câu hiện trạng dựa trên **kế hoạch có hạn**: 「2024年から2年の計画で調べが進められています」, đến 11/2026 kế hoạch có thể đã xong | Đổi sang 「市は2024年から2年の計画で、建物を調べてきました」 |
| 2 | Câu hiện trạng lấy từ sách 2017 (「いまも利根川の堤防が見えます」) | Đổi thành sự kiện địa lý không đổi (「家の南側には、利根川が流れています」) |
| 3 | 3 câu chỉ có nguồn Wikipedia nhưng viết 「人名事典によると」/「事典は書いています」 | Đổi sang 「とされます」/「と伝えられます」; 「事典」 chỉ dùng cho コトバンク |
| 4 | Agent điền hình báo 12 câu không có mã F hoặc nói vượt nguồn (năm mở nhà máy tách lẻ khi nguồn ghi gộp 1939–41, 「太田と小泉の疎開先」, 「所長を降りるか買い取るか」…) | Đối chiếu từng câu, sửa 8 câu, giữ số câu để `so_nhom_canh.py` GIỐNG, rồi `tach-loi` → `dien_mau.py` → `nap-motion` → `kiem-tra-goi` → `dung-canh` |
| 5 | Dòng dưới thumbnail 「戦闘機の37%」 nói hẹp sai: USSBS ghi "combat airframes" (mọi máy bay chiến đấu) | 「戦闘用機体の37%」 |
| 6 | Một đoạn 28 ký tự trùng đối thủ (câu năm 1931, 資本金 600万円) | Viết lại câu |
| 7 | Máy không có thư viện đọc PDF; công cụ đọc web giới hạn 10 MB; API Commons trả 429 | `pip install --target <scratchpad>\lib pypdf` rồi `PYTHONPATH`; Commons thì mở trang bằng trình duyệt trong app |
| 8 | `seo_kigyo.py` cảnh báo tác giả 「Japanese Railroad Cr…（Panoramio）」 trông như bị cắt | Trang Commons ghi đúng như vậy (Panoramio cắt tên từ lúc tải lên) → giữ nguyên |

### Điều chỉnh

1. Câu hiện trạng: nếu nguồn là một kế hoạch có thời hạn, tính xem đến ngày làm video đã hết hạn chưa; hết hoặc sắp hết thì viết ở thì đã làm.
2. Mức B từ Wikipedia nói 「とされます」/「と伝えられます」, không gắn 「事典によると」.
3. Thumbnail giữ khung cũ cho mọi video để kênh đồng bộ (người dùng đã xem kiểu đỏ nâu và không chọn). Con số trên thumbnail phải đúng phạm vi của nguồn (戦闘機 ≠ 戦闘用機体).
4. Tiêu đề 「零戦の6割」 dựa trên nguồn B (Wikipedia; hai trang lệch nhau 6割以上 / 約2/3); không tìm được báo cáo USSBS riêng về 中島 (Corporation Report No. II). Nếu sau này có, bổ sung nguồn A.
