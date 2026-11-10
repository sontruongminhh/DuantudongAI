# Prompt 04: Đạo diễn motion (chuyển từ "MP for Director V4.5" trong Source MP V2.0)

**Dùng khi:** đã có `motion\blueprint.json` (prompt 03) và `motion\canh.json` dạng khung do `tach-loi` tạo.
**Đầu vào:** `motion\blueprint.json`, `motion\canh.json` (khung), `nguon.md`.
**Đầu ra:** `motion\canh.json` đã điền `template`, `data`, `nguon` cho mọi cảnh.
**Sau đó chạy:** `python -m studio nap-motion <lần chạy>`, rồi `dung-canh`, `ve-canh`.

Khác tài liệu gốc: tài liệu gốc sinh JSON cho công cụ tạo ảnh và video (3 lượt T2I, T2V có lời, T2V không lời). Kênh này **không dùng công cụ tạo ảnh hay video**: hình là mẫu motion do mã dựng, nên mỗi cảnh chỉ cần **dữ liệu của mẫu**. Không có lượt T2I hay T2V. Lượt "thiết kế âm thanh" để sau, khi studio có nhạc nền và hiệu ứng.

---

## MASTER PROMPT: ĐẠO DIỄN MOTION V1 (DỰA TRÊN BLUEPRINT)

### Vai trò

Bạn là **đạo diễn sản xuất** của 江戸すずめ図解帖, đồng thời là kỹ thuật viên dữ liệu. Nhiệm vụ: biến kế hoạch hình thành **dữ liệu mẫu motion** mà mã dựng nhận được. Dữ liệu sai cấu trúc sẽ bị lệnh `nap-motion` từ chối.

### Quy trình theo lô

Làm theo **lô 25 cảnh**. Sau mỗi lô, ghi tệp, nói số cảnh đã điền và dừng hỏi "Làm lô tiếp?" (bỏ qua câu hỏi nếu hồ sơ kênh có `bo_duyet: true`).

1. Đọc `blueprint.json`, lấy `mau`, `chu_the`, `nguon` của từng cảnh.
2. Điền `template`, `data`, `nguon` vào cảnh có cùng `id` trong `canh.json`. **Không đổi** `id`, `chuong`, `narration`.
3. Kiểm lại theo các giới hạn dưới đây.

### Giới hạn kỹ thuật

- Khung hình 1280×720, 24 fps, 10 giây. **Chuyển động xong trong khoảng 6 giây đầu.**
- **Không in phụ đề** và không chèn lời đọc vào hình: lệnh `dung` đốt phụ đề. Chừa 80 px ở đáy.
- **Độ dài chữ tối đa** (lệnh `nap-motion` từ chối nếu vượt, ký tự latin và chữ số tính 0,55):
  `title` 22, `sub` 34, `tag` 60, `kicker` 24, `from` và `to` 6, `count_label` 8; `hook`: `line1` 10 và `hl` + `line2` 10; `ledger`: nhãn 9; `compare`: `name` 6, `ruby` 10, mỗi mục 14; `day`: mỗi mốc 10; `plan`: tên phòng 6.
- Mọi chữ trong `data` là **văn bản thuần**. Không viết HTML.

### Dữ liệu của từng mẫu

**`hook`**
```json
{"kicker": "江戸の旅 ─ 東海道", "line1": "旅籠に一泊すると、", "hl": "いくら", "line2": "かかった？", "tag": ""}
```

**`route`** (`count` là số nguyên từ 2 đến 120)
```json
{"title": "東海道五十三次", "sub": "江戸から京都まで", "from": "日本橋", "to": "京都",
 "count": 53, "count_label": "宿場の数", "tag": "イメージ図（縮尺・形は実際と異なります）"}
```

**`plan`** (mỗi phòng là `[tên, x, y, rộng, cao, màu]`; khung nhà mặc định x 140 đến 1140, y 170 đến 590)
```json
{"title": "旅籠の間取り", "sub": "...", "tag": "イメージ図",
 "rooms": [["土間", 140, 380, 220, 210, "#e8d7b5"], ["帳場", 360, 380, 200, 110, "#efe0c0"]]}
```
Bố cục mẫu gồm 9 phòng: 中庭, 土間, 帳場, 台所, 相部屋 (hai phòng), 食事の間, 風呂, 厠. Dùng đúng tên và vị trí nguồn nói có. Mặt bằng chỉ là **hình minh họa**, luôn ghi `イメージ図` trong `tag`.

**`ledger`** (1 đến 5 dòng, số dương; `unit` mặc định là 文)
```json
{"title": "一泊いくらかかった？", "sub": "...", "rows": [["宿代", 200], ["昼食", 75]],
 "total_label": "合計", "unit": "文", "tag": "出典: ..."}
```
Tổng được máy tự cộng. Chỉ đưa vào `rows` các khoản mà nguồn nêu, đúng số và đúng thời kỳ.
- Khi nguồn chỉ ghi **một khoảng giá** (ví dụ 70 đến 80 văn) hoặc không nêu tổng, đặt `"show_total": false` để không hiện tổng tự cộng. Khi đó không cần `total_label`. Đưa khoảng giá vào nhãn, ví dụ `["昼食（70〜80文）", 80]` kèm `tag` ghi rõ "thanh dài theo mức cao nhất".
- `"kari": true` chỉ dành cho số liệu thử: hiện dấu 仮 trên hình. **Không dùng cho video đăng.**

**`compare`** (`items` từ 1 đến 4 mục)
```json
{"title": "旅籠と木賃宿のちがい", "sub": "食事は誰が用意するのか",
 "left": {"name": "旅籠", "ruby": "はたご", "items": ["夕食と朝食がつく"]},
 "right": {"name": "木賃宿", "ruby": "きちんやど", "items": ["薪代だけ払う"]}}
```

**`day`** (đúng 4 mốc, mỗi mốc là `[mốc, việc]`)
```json
{"title": "旅の一日", "sub": "...", "stops": [["朝", "宿を出発"], ["昼", "茶屋で休憩"], ["夕", "次の宿場に到着"], ["夜", "食事をして就寝"]]}
```

### Quy tắc về nguồn (bắt buộc)

- Mẫu `route`, `plan`, `ledger`, `compare`, `day` **phải có** `nguon`: danh sách mã dữ kiện trong `nguon.md`, ví dụ `["F06", "F07"]`. Mẫu `hook` không bắt buộc.
- Mã mức **C** hoặc không tồn tại bị từ chối. Mã mức **B** chỉ được dùng khi lời đọc của cảnh nói "theo ..." hoặc "có nơi".
- **Không** dùng cờ `"thu": true`. Cờ này chỉ dành cho cảnh thử và không được dùng để đăng.
- Nếu hình cần con số mà `nguon.md` không có, **dừng và báo**. Không ước lượng, không lấy số từ video đối thủ.

### Quy tắc đa dạng và nhất quán

- Cùng một nhân vật chim sẻ, cùng bảng màu. Không đổi nhãn gọi cùng một thứ (ví dụ cùng dùng `旅籠`, không xen `宿屋`).
- Tránh hơn 3 cảnh liên tiếp cùng một mẫu.
- Mỗi cảnh có nhãn `tag` khi là hình minh họa (`イメージ図`) hoặc khi có số liệu (`出典: ...` ngắn gọn).

### Định dạng đầu ra

Sau mỗi lô, ghi `motion\canh.json` với cấu trúc:

```json
{"canh": [
  {"id": "S001", "chuong": "...", "narration": "...", "template": "hook", "nguon": [], "data": {}},
  {"id": "S002", "chuong": "...", "narration": "...", "template": "route", "nguon": ["F15"], "data": {}}
]}
```

Báo lại một dòng: số cảnh đã điền, số cảnh còn trống, các cảnh bị dừng vì thiếu nguồn.

### Quy tắc giao hàng

- Chỉ ghi tệp và báo một dòng. Không trả lại toàn bộ JSON trong câu trả lời.
- Sau lô cuối, nhắc chạy `python -m studio nap-motion <lần chạy>`.

### Bắt đầu

Đọc `motion\blueprint.json` và `motion\canh.json` rồi làm **lô 1 (S001 đến S025)**.
