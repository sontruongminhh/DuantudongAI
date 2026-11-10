# Kế hoạch nghiên cứu: người Nhật đang quan tâm ai? (07/11/2026)

Mục tiêu: chọn **một người** (nhà sáng lập, chủ gia tộc, doanh nhân đã mất) để làm video tiếp theo, dựa trên dữ liệu thật về mức quan tâm của người Nhật, không theo cảm tính.

## Câu hỏi cần trả lời

1. Người Nhật đang tìm đọc về ai nhiều nhất? (cầu chung)
2. Ai đang được quan tâm **tăng lên** trong vài tháng gần đây? (đà)
3. Video về người đó trên YouTube có được xem nhiều không? (cầu trên YouTube)
4. Đã có bao nhiêu video mới về người đó? (cung, cạnh tranh)
5. Có làm được theo chuẩn của kênh không? (đã mất, có chân dung giấy phép tự do, hợp một trong hai loạt)

## Nguồn dữ liệu

| Nguồn | Đo cái gì | Vì sao dùng |
|---|---|---|
| Wikipedia tiếng Nhật, lượt xem theo tháng (Wikimedia REST API, 11/2025–10/2026) | Cầu chung và đà tăng (3 tháng gần nhất so với 9 tháng trước) | Người Nhật tra Wikipedia khi xem phim, đọc báo, thấy tên trên tiền giấy hay trong phim truyền hình. Số đếm thật, miễn phí, không cần khóa |
| Wikidata | Năm sinh, năm mất | Loại người còn sống (quy tắc kênh), tìm năm tròn 2027 (100, 150 năm sinh / mất) |
| YouTube Data API | Video có tên người trong tiêu đề: view cao nhất, số video ≥10 vạn, số video và view tốt nhất trong 180 ngày | Cầu trên chính nền tảng của kênh, và độ dày cạnh tranh gần đây |
| Wikimedia Commons | Ảnh đại diện trang Wikipedia có trên Commons không | Thumbnail cần một khuôn mặt giấy phép tự do (bài học video 1) |

Không dùng: Google Trends (không có API chính thức, trang web chặn máy đọc), vidIQ (hết credit), phụ đề đối thủ.

## Ứng viên

79 người trong `research\tim_nguoi.py` (`UNG_VIEN`): tài phiệt Minh Trị, nhà sáng lập công ty còn tồn tại (loạt 「なぜ終わらなかったのか」), chủ công ty / gia tộc đã biến mất (loạt 「なぜ消えたのか」), thương gia thời Edo. Bỏ người kênh đã làm (大倉喜八郎, 安田善次郎, 三井高利, 堤清二, 永田雅一, 金子直吉, 鈴木よね). Người còn sống bị loại tự động.

## Cách chấm (0–100, chỉ để xếp hạng)

| Phần | Điểm | Cách tính |
|---|---|---|
| Cầu Wikipedia | 30 | log10(lượt xem 12 tháng) / 6 (100 vạn lượt = đủ) |
| Cầu YouTube | 30 | log10(view cao nhất) / 6,3 (200 vạn = đủ) |
| Đà tăng | 10 | 3 tháng gần / trung bình 9 tháng trước; ≥1,6 lần = đủ, ≤0,8 = 0 |
| Khoảng trống | 15 | 1 / (1 + số video 180 ngày / 4): chưa ai làm gần đây = đủ |
| Chân dung | 10 | Ảnh đại diện có trên Commons |
| Năm tròn 2027 | 5 | 2027 là năm tròn 50 / 100 / 150… năm sinh hoặc mất |

## Sau khi có bảng (người điều phối làm tay)

1. Đọc 15 người đầu: vì sao được quan tâm (phim truyền hình, tiền giấy, tin tức), video nhiều view là của ai, góc kể nào còn trống.
2. Loại người không hợp kênh: chỉ là nhà phát minh, không có câu chuyện công ty / gia tộc, hoặc đối thủ đã làm đúng góc của mình rất tốt gần đây.
3. Chọn 1 người + loạt (消 / 続) + góc kể, ghi vào `research\CHU_DE_TIEP.md`, rồi làm video theo `QUY_TRINH.md`.

## Chạy

```
.venv\Scripts\python.exe -I research\tim_nguoi.py
```
Kết quả: `research\data\tim_nguoi_<ngày>.md` (bảng xếp hạng) và `.json` (dữ liệu thô). Tốn khoảng 8.000 đơn vị quota YouTube (một lần trong ngày), chạy lại dùng bộ nhớ đệm.
