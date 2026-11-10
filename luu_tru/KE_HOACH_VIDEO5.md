# Kế hoạch video 5: 大倉財閥 (05/11/2026)

## Vì sao chọn 大倉

| Căn cứ | Số liệu |
|---|---|
| Nhóm thị trường đang lên | "Gia tộc, tài phiệt 家のその後": tổng view 30 ngày 4,2 triệu, cao nhất 7 nhóm; 8/10 kênh lập năm 2026 (tab "Thị trường Cty-Gia tộc") |
| Hai video mẫu | 渋沢栄一の家のその後 7,3 vạn trong 9 ngày (kênh 1.600 sub); 鈴木よねの生涯 18 vạn (kênh 278 sub). Tài phiệt Meiji + gia tộc kéo được người xem dù kênh nhỏ |
| Nhu cầu tên 大倉喜八郎 | Video dài cao nhất 50,8 vạn (マーキュリー御殿, 2022), 偉人エピソードX 8,1 vạn (2026) |
| Đối thủ cùng khuôn | **Chưa có**. Tìm 「大倉財閥 なぜ消えた」: 0 video; 「大倉商事 倒産」: cao nhất 1.151 view |
| Ảnh có giấy phép | 22 ảnh, 17 chân dung trên Commons (nhiều nhất trong danh sách ứng viên) |
| Nối với hôm nay | The Okura Tokyo (mở lại 2019), 大成建設, 東京経済大学, 大倉集古館, 帝国ホテル (cùng 渋沢 lập) |
| Kết thúc kiểu "công ty biến mất" | 大倉商事 phá sản năm 1998: có điểm kết rõ như カネボウ, 鈴木商店 |

So với 大映 (ứng viên còn lại): 大映 có nhu cầu cao hơn (39,7 vạn) nhưng đã có カカチャンネル và 偉人エピソードX làm; 大倉 thì chưa ai làm, và hợp hướng gia tộc mà 2 video mẫu chứng minh. 大映 để video 6.

## Dàn ý dự kiến (sẽ kiểm chứng ở bước nghiên cứu, mọi mốc phải có mã F)

Trục ba đời: 大倉喜八郎 (lập nghiệp) → 大倉喜七郎 (con, ホテルオークラ) → 大倉商事 (phá sản 1998).

| # | Chương | Nội dung chính |
|---|---|---|
| 0 | はじめに | Sảnh The Okura Tokyo hôm nay → tất cả từ một nhà → đỉnh cao, so với 三井・三菱 → 1998 → **3 câu hỏi đánh số** → lời hứa "xem hết thì sảnh khách sạn ấy nhìn khác đi" |
| 1 | 新発田の少年 | Quê 新発田, lên Edo, tiệm đồ khô |
| 2 | 鉄砲を売る | Cửa hàng súng thời 戊辰戦争: khởi đầu của tiếng "死の商人" (nêu như một cách gọi, có nguồn) |
| 3 | 大倉組 | Công ty thương mại, chi nhánh London |
| 4 | 渋沢と組む | 帝国ホテル, xây dựng (gốc của 大成建設); nối với video 渋沢 người xem vừa xem |
| 5 | 大陸へ | Đầu tư Trung Quốc (本渓湖), canh bạc lớn nhất |
| 6 | 学校と美術館 | 大倉商業学校 → 東京経済大学, 大倉集古館 (bảo tàng tư nhân đầu tiên), động đất 1923 |
| 7 | バロン大倉 | Con trai 喜七郎 kế nghiệp 1928 |
| 8 | 敗戦 | Mất tài sản ở lục địa, giải thể tài phiệt |
| 9 | ホテルオークラ | 1962, khách sạn của đời thứ hai |
| 10 | 大倉商事の最期 | Phá sản 1998 |
| 11 | なぜ消えたのか | Trả lời 3 câu hỏi; 3 nguyên nhân có số + quyết định + hậu quả; một góc nhìn khác |
| 12 | 残ったもの / おわりに | Những gì còn đến hôm nay, quay lại sảnh khách sạn, mời kể ký ức |

Tiêu đề dự kiến theo khuôn kênh: 「帝国ホテルもホテルオークラも作った大倉財閥はなぜ消えたのか｜…」 (vế sau chốt sau khi viết xong). Dòng dưới thumbnail cũng chốt sau.

## Việc mới so với video 4

1. **Bảng cách đọc tên riêng** (bình luận đối thủ chê giọng AI đọc sai): thêm `runs\<run>\cach_doc.json` (chữ → kana), chỉ thay trong lời gửi Genmax, phụ đề giữ chữ Hán. Sửa `studio\dung.py`, thêm test. Trước khi dựng cả video thì đọc thử 10 câu khó nhất (tốn ít credit) và nghe.
2. Kịch bản đạt thêm tiêu chí 22–25 trong `runs\TIEU_CHI_KICH_BAN.md` (3 câu hỏi đánh số, trục ba đời, so với tài phiệt quen, lời hứa ở mở đầu).
3. Tải phụ đề video 大倉 của マーキュリー御殿 và 偉人エピソードX vào `research\doi_thu\` để đo trùng (bước 4).
4. Người còn sống: chỉ nêu điều có trong tài liệu chính thức. Không nhắc đời tư không có nguồn.

## Các bước (theo `QUY_TRINH.md`)

| Bước | Việc | Tốn |
|---|---|---|
| 1–3 | Tạo lần chạy `20261105-okura`, nghiên cứu (`nguon.md` mã F), tải ảnh Commons + `credit.json`, kịch bản 12 chương | Token |
| 3b–4 | Tự chấm 25 tiêu chí, người điều phối đếm rào đón bằng máy, đo trùng | |
| 5–6 | Tách cảnh, điền hình, soát ảnh, render clip | Khoảng 25 phút máy |
| 7 | Thử khóa Genmax, đọc thử tên khó, rồi dựng giọng + nhạc | Credit Genmax |
| 8–10 | Kiểm tra video, âm thanh, phụ đề; thumbnail; SEO | |
| 11 | Đóng gói `tai_len\5_okura\` để người dùng tự tải lên | |
