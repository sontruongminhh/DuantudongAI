# Hướng dẫn: nghiên cứu, tìm ảnh và viết kịch bản cho một video kênh 4

Kênh 4 (`E:\DuantudongAI\kenh4`, mã kênh `kigyo_shi`): phim tài liệu tiếng Nhật, khoảng 30–34 phút, về một công ty Nhật từng số 1 rồi biến mất. Không người dẫn, giọng AI nam điềm tĩnh, hình là đồ họa motion vẽ bằng code (khoảng 2/3) và ảnh tư liệu Wikimedia Commons (khoảng 1/3). Khán giả: người Nhật 45 tuổi trở lên.

Mỗi video có một thư mục lần chạy `runs\<run>\` (đã tạo sẵn, có `profile.yaml`, `brief.md`). Bạn làm 4 việc theo thứ tự và ghi kết quả vào đó.

## Quy tắc cứng

1. **Không xem, không đọc video, phụ đề hay kịch bản của kênh đối thủ** (kể cả `research\doi_thu\`). Chủ đề trùng với video đối thủ đã nổ view là cố ý, nhưng lời phải do bạn viết từ tài liệu gốc. Tài liệu công khai mà đối thủ liệt kê (luận văn, biên bản Quốc hội, lịch sử công ty) thì được đọc vì đó là nguồn gốc.
2. Mọi con số, năm, tên riêng trong lời đọc phải có mã F trong `nguon.md`. Mức **A** = tài liệu gốc/học thuật/công ty tự công bố/biên bản Quốc hội bạn đọc trực tiếp; **B** = tự điển (コトバンク), Wikipedia tiếng Nhật, báo; chỉ dùng kèm 「〜によると」「〜とされます」; **C** = không chắc, không dùng.
3. Quy đổi tiền ra giá trị hôm nay: ghi rõ cách tính trong `nguon.md` (chỉ số nào: 企業物価指数 của 日本銀行 hoặc 消費者物価指数; năm gốc; hệ số). Làm tròn và nói 「およそ」.
4. Không viết lời có thể gây hiểu lầm về người còn sống; chuyện gian lận kế toán, phá sản chỉ nói theo tài liệu (phán quyết, báo cáo chính thức).
5. Không gửi email hay thông tin cá nhân của ai đi đâu. Gọi API bằng User-Agent chung `kenh4-research/0.1 (personal research script)`.
6. Không chạy lệnh `dung`, `tai-len` hay bất cứ thứ gì tốn credit Genmax. Không sửa `studio\`, `engine\`, `tools\`.

## Việc 1. Nghiên cứu → `runs\<run>\nguon.md`

Nguồn nên dùng (đều có API hoặc trang công khai):
- J-STAGE: `https://api.jstage.jst.go.jp/searchapi/do?service=3&keyword=...` (luận văn, nhiều bài có PDF toàn văn).
- 国会会議録: `https://kokkai.ndl.go.jp/api/speech?any=...&recordPacking=json&maximumRecords=30`.
- NDL Search: `https://ndlsearch.ndl.go.jp/api/opensearch?title=...`.
- コトバンク `https://kotobank.jp/word/<語>`, Wikipedia tiếng Nhật, trang 沿革/会社の歴史 của các công ty kế thừa, kho luận văn đại học (CiNii, 機関リポジトリ).
- Thông cáo, báo cáo chính thức (産業再生機構, 金融庁, 判決).

Định dạng (máy đọc bảng này, cột 4 là mức tin cậy):

```
# Nguồn nghiên cứu: <công ty>

Ngày làm: 04/11/2026. Mức tin cậy: A / B / C (như hướng dẫn).

## Nguồn

| Mã | Nguồn | Loại |
|---|---|---|
| S1 | <tác giả, tên bài, tạp chí, năm, URL> | Luận văn |

## Dữ kiện

| Mã | Dữ kiện | Nguồn | Mức | Ghi chú |
|---|---|---|---|---|
| F01 | ... (ghi bằng tiếng Việt hoặc Nhật, có số và năm chính xác như nguồn) | S1 | A | |

## Quy đổi tiền

## Chưa xác nhận, không đưa vào lời đọc
```

Cần khoảng 60–100 dữ kiện, đủ cho: khởi nghiệp, người sáng lập/lãnh đạo chính, các bước ngoặt, đỉnh cao (con số "日本一"/"世界一" có nguồn), dấu hiệu suy, sụp đổ, cái gì còn lại hôm nay (thương hiệu, công ty con, toà nhà, địa danh).

## Việc 2. Ảnh → `runs\<run>\motion\anh\`

Tìm trên Wikimedia Commons (API `https://commons.wikimedia.org/w/api.php`, `generator=search`, `gsrnamespace=6`, `prop=imageinfo`, `iiprop=url|extmetadata|size`, `iiurlwidth=1600`). **Chỉ lấy** giấy phép Public domain, CC0, CC BY, CC BY-SA (ghi đúng phiên bản). Bỏ ảnh không rõ giấy phép, ảnh "fair use", logo còn bản quyền.

- Mục tiêu 20–35 ảnh: chân dung người sáng lập và lãnh đạo, trụ sở, nhà máy, sản phẩm, quảng cáo cũ, địa danh hôm nay, tài liệu cũ (tạp chí, báo có PD).
- Tải bản thumb rộng 1600 px (hoặc nhỏ hơn nếu gốc nhỏ), đặt tên ngắn không dấu: `muto_sanji.jpg`, `honsha_1920.jpg`. Chỉ tải file ảnh JPG/PNG.
- Ghi `motion\anh\credit.json`: danh sách `{"file", "commons_title", "author", "license", "url", "mo_ta"}` (author bỏ thẻ HTML). Nếu trường tác giả không phải tên người (ví dụ 「投稿者によるスキャン」, "Own work", "Scan by uploader") thì ghi tên người đăng lấy bằng `iiprop=user`.
- Ghi `motion\anh\NGUON_ANH.md`: bảng như trên cho người đọc.

## Việc 3. Brief → `runs\<run>\brief.md`

Điền các mục có sẵn (chủ đề, từ khóa, tiêu đề dự kiến theo khuôn `{日本一の肩書き}・{社名}はなぜ消えたのか｜{比べる相手や数字}`, ý tưởng thumbnail: ảnh chân dung + ảnh nền nào, dòng 「…だったのに」).

## Việc 4. Kịch bản → `runs\<run>\script.md`

Đọc trước:
- `E:\DuantudongAI\kenh2\runs\20261104-toyotomi-kyodai-seiryokuzu\script.md` (định dạng thật đã chạy được, chỉ học định dạng, không học nội dung).
- `tools\check_script_ja.py` (các luật máy kiểm).

**Định dạng:**

```
# Kịch bản: <tiêu đề>

## Kịch bản

### HOOK · Chương 1: はじめに
[HÌNH: so_lon | 1936年、民間企業で売上1位 | F05]
((SILENCE 1s))
[TENSION] ...
[NARRATIVE] ...

### WORLD · Chương 2: <tên chương ngắn, ≤ 14 ký tự>
...

## Bảng nguồn

| Chương | Mã |
|---|---|
| Chương 1 | F01 F05 |
```

- Nhãn `HOOK WORLD STRUGGLE CLIMAX LEGACY ECHO` phải có đủ (máy kiểm). Gợi ý: Chương 1 HOOK (はじめに); 2–3 WORLD; 4–6 STRUGGLE; 7–9 CLIMAX; 10–11 LEGACY (なぜ消えたのか, 消えた物と残った物); 12 ECHO (おわりに).
- Mỗi dòng lời đọc bắt đầu bằng `[NARRATIVE]`, `[TENSION]` hoặc `[EPIC]`. Mỗi dòng là một câu hoặc hai câu ngắn, không vượt giới hạn ký tự mỗi cảnh mà `check_script_ja.py` báo.
- **Độ dài: 8.800–9.800 ký tự lời đọc** (kênh mẫu khoảng 9.500 ký tự cho 34 phút). Chạy: `.venv\Scripts\python.exe tools\check_script_ja.py runs\<run>\script.md --phut 26` (máy tính phút ở 6 ký tự/giây, giọng thật chậm hơn nên video sẽ khoảng 30–33 phút). Sửa đến khi không còn lỗi; cảnh báo thì cố giảm.
- **Cách kể:** câu ngắn, bình tĩnh, không giật gân, không 「衝撃」「驚愕」「皆さん」「チャンネル登録」. Mở bằng đỉnh cao có con số và quy đổi giá trị hôm nay, rồi 「ところが、その頂点から○年後…」, rồi câu hỏi 「なぜ消えてしまったのでしょうか」. Chương theo thời gian. Chương "なぜ消えたのか" tổng kết 3 nguyên nhân có dữ kiện. Chương "消えた物と残った物" kể cái còn lại hôm nay. Chương cuối ngắn, mời người xem kể ký ức về sản phẩm, nhà máy. Mỗi số liệu nói năm và đơn vị. Mức B nói 「〜によると」.
- **Gợi ý hình `[HÌNH: <kiểu> | <nội dung> | <mã F hoặc tên ảnh>]`**, mỗi beat 1–4 dòng lời. Kiểu phải là một trong:

| Kiểu | Dùng khi | Nội dung cần ghi trong gợi ý |
|---|---|---|
| `chuong` | dòng đầu mỗi chương (thẻ chương) | số chương, tên, khoảng năm |
| `anh` | ảnh toàn khung + 1–3 thẻ chú thích | tên file ảnh, chú thích |
| `chan_dung` | giới thiệu người | file ảnh, vai trò, tên, năm sinh–mất |
| `so_lon` | một con số lớn | năm, nhãn, số, đơn vị |
| `cot` | so 2–6 con số | các cặp nhãn–số |
| `tron` | tỷ lệ phần trăm | các phần |
| `danh_sach` | 2–5 ý | các ý ngắn |
| `nien_bieu` | 3–6 mốc năm | các mốc |
| `so_sanh` | hai bên đối chiếu | hai bên, mỗi bên 1–4 ý |
| `ban_do_diem` | địa điểm trên bản đồ Nhật/thế giới | tên địa điểm |
| `luoi_anh` | 2–4 ảnh sản phẩm có nhãn | file ảnh, nhãn |
| `trich_dan` | trích tài liệu (nền tối) | tên tài liệu, ngày, câu trích ngắn (đặt trong 「」 trong lời đọc nếu đọc lên) |
| `cau_hoi` | câu hỏi lớn trên nền tối (hook, chuyển chương) | câu hỏi |

  Nhắm khoảng 1/3 beat dùng `anh`/`chan_dung`/`luoi_anh` (theo số ảnh có được), còn lại là đồ họa.

- Cuối cùng chạy đo trùng với video đối thủ cùng chủ đề (nếu có tệp; xem tên trong lời giao việc):
  `.venv\Scripts\python.exe tools\do_trung_loi.py runs\<run>\script.md research\doi_thu\<tệp>.ja.vtt`
  Chỉ đọc kết quả của công cụ, không mở tệp `.vtt`. Không đạt thì viết lại các đoạn bị liệt kê bằng câu của bạn, chạy lại đến khi ĐẠT.

## Báo lại

Khi xong, trả lời ngắn (tiếng Việt): số dữ kiện A/B, số ảnh và giấy phép, số ký tự và kết quả hai lệnh kiểm, các điểm chưa chắc, và các dữ kiện mâu thuẫn giữa các nguồn.

## Bài học từ video 1–3 (bắt buộc, xem thêm `BAI_HOC.md`)

1. **Ảnh phải khớp lời của chính cảnh đó**: đúng nơi, đúng thời, đúng đối tượng. Ảnh minh họa chung (tàu, phố, cảng của nơi khác, năm khác) chỉ dùng khi chú thích ghi rõ 「イメージ」 hoặc năm chụp thật, và không đặt cạnh lời nói về một sự kiện cụ thể khác năm. Không chắc thì dùng đồ họa.
2. **Trường `author` trong `credit.json` chỉ ghi tên** (tiếng Nhật hoặc latin), không ghi chú tiếng Việt, không ngoặc giải thích. Ghi chú để trong `mo_ta`. Tác giả kiểu 「投稿者によるスキャン」, "Own work" thì ghi tên người đăng (`iiprop=user`).
3. **Tiêu đề**: khuôn `{肩書き}・{社名}はなぜ消えたのか｜…` được phép giống kênh khác, nhưng danh hiệu ở vế đầu và vế sau `｜…` phải khác tiêu đề các video đối thủ cùng chủ đề. Dùng đúng từ của nguồn (ví dụ "収入" chứ không "売上" nếu nguồn ghi 収入).
4. **Dòng dưới thumbnail**: nêu sản phẩm hoặc con số người xem nhớ, không viết chung chung, không trùng dòng thumbnail đối thủ.
5. **Ảnh của chính công ty**: cần chân dung người chính và ảnh sản phẩm, cửa hàng, trụ sở. Chân dung người sau 1950 thường còn bản quyền: chỉ dùng khi Commons ghi rõ giấy phép tự do.
6. Lệnh `python -m studio …` nhận **tên lần chạy** (ví dụ `20261105-saison-group`), lệnh `tools\…` nhận đường dẫn `runs\<run>`.
7. **Ảnh còn bản quyền ở Mỹ**: trang Commons có nhãn `Not-PD-US-URAA` (thường gặp ở áp phích, ảnh phim Nhật chỉ PD ở Nhật) thì không dùng. Nhân vật phim / hoạt hình còn bản quyền (ガメラ, ゴジラ…) chỉ thể hiện bằng đồ họa chữ (video 6).
8. **Bảng cách đọc** `runs\<run>\cach_doc.json` (tên riêng → kana, chỉ cho giọng): không dùng khóa một chữ nằm được trong từ dài hơn (邸 làm 別邸 thành べつやしき); ghi nguồn cách đọc ở cuối `nguon.md` (video 5–6).
9. **Câu về hiện trạng** (いまも…, 使われていない, 休館が続く, còn đứng ở…): tìm nguồn mới nhất và ghi năm của nguồn trong `nguon.md`. Nguồn cũ dễ sai: 両国公会堂 「2001年から使用停止」 nhưng tòa nhà đã bị phá, nay là 刀剣博物館 (video 7).
