# Có làm được như kênh mẫu bằng bộ máy kenh2 không?

Kiểm tra ngày 04/11/2026. **Kết luận: làm được.** Khoảng 80% đã có sẵn và đã chạy thật ở kenh2. Phần còn thiếu đều đã thử được bản đầu, không có phần nào bế tắc. Điểm cần chú ý nhất là **ảnh tư liệu**: có nhiều hay ít tùy chủ đề.

## Kenh2 đã chạy thật được gì

| Phần | Bằng chứng |
|---|---|
| Từ kịch bản đến video cuối | 5 video làm trọn (`kenh2\runs\2026110*`), dài 17–26 phút, 1280×720 |
| Tải lên YouTube | 5 video đã có `video_id` trong `state.json` |
| Giọng tiếng Nhật | MiniMax qua Genmax, đã dùng cho cả 5 video |
| Thumbnail | Vẽ bằng HTML, có bản có chân dung (`lam_thumbnail.py` từng run) |
| SEO | `viet_seo.py`, `publish\metadata.json` từng run |
| Kiểm thử | `pytest`: 117 bài kiểm thử đều qua |

## Thử mới hôm nay

| Phần | Kết quả | Ghi chú |
|---|---|---|
| Tra tư liệu tự động | ✔ J-STAGE, biên bản Quốc hội, NDL Search đều trả kết quả qua API | 中島飛行機: 534 bài nghiên cứu, 93 lần trong biên bản Quốc hội |
| Tải ảnh Wikimedia, tự ghi tác giả | ✔ `thu_nghiem\tai_anh.py`, ghi `credit.json` | 3 ảnh phạm vi công cộng |
| 6 kiểu cảnh như kênh mẫu | ✔ thẻ chương, chân dung, số lớn, ảnh toàn khung, biểu đồ cột, trích tài liệu (`thu_nghiem\dung_thu.py`) | Render bằng HyperFrames, không lỗi. Xem `thu_nghiem\out\luoi.png` |
| Dòng `出典` trên mọi cảnh | ✔ | Trên cảnh ảnh sáng thì khó đọc, cần thêm nền tối sau chữ |
| Phụ đề dải đen | ✔ chạy được (`thu_nghiem\out\thu_ghep.mp4`) | Dòng trên lòi khỏi dải: tăng dải lên khoảng 130 px hoặc giảm cỡ chữ |

## Điểm vướng: ảnh tư liệu theo chủ đề

| Chủ đề | Ảnh trên Wikimedia Commons |
|---|---|
| 中島飛行機 (1917–1945) | Nhiều: chân dung người sáng lập, trụ sở thời Taisho, nhà máy, quảng cáo cũ, máy bay. Phần lớn là phạm vi công cộng |
| 安宅産業 (phá sản 1977) | Gần như không có ảnh liên quan |

Ảnh chụp sau chiến tranh phần lớn còn bản quyền. Kênh mẫu chọn công ty có ảnh trước chiến tranh (鈴木商店, カネボウ), hoặc dùng ảnh CC BY do người dùng Commons chụp lại toà nhà, sản phẩm (三光汽船, リッカー). Vì vậy **bước chọn chủ đề phải kiểm tra ảnh trước**. Chủ đề ít ảnh thì tăng tỷ lệ cảnh đồ họa, hoặc bỏ.

## Còn phải làm

1. ~~Sao bộ máy kenh2 sang kenh4~~ (xong, 122 kiểm thử qua). Còn tạo hồ sơ kênh mới.
2. Đưa 6 mẫu thử vào `studio\mau_motion.py` (kèm kiểm tra dữ liệu và kiểm thử). Làm thêm: danh sách gạch đầu dòng, biểu đồ tròn, bản đồ chấm điểm, 4 thẻ, lưới ảnh.
3. Nối `tai_anh.py` vào quy trình: tìm ảnh theo kịch bản, tự ghép danh sách tác giả vào mô tả.
4. Công cụ tra tư liệu (J-STAGE, Quốc hội, NDL) và chấm điểm "đủ ảnh" cho từng chủ đề.
5. Chỉnh giọng chậm lại (kênh mẫu 4,6 ký tự/giây), thêm nhạc nền có giấy phép, sửa phụ đề.
6. Mục lục chương tự sinh trong mô tả.
7. Làm 1 video thật dài khoảng 30 phút (đề xuất カネボウ, chủ đề nổ view nhất của đối thủ), so với kênh mẫu. Trước khi đọc giọng chạy `tools\do_trung_loi.py`.

Chưa kiểm tra: tốn bao nhiêu credit Genmax cho video 30 phút (lâu hơn video kenh2 khoảng 1,5 lần), và giọng đọc chậm hơn nghe có tự nhiên không.
