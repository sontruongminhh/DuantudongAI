# Chiến lược kênh 4: lịch sử các công ty Nhật đã biến mất

Căn cứ: `research\PHAN_TICH_KENH_MAU.md` (kênh mẫu 看板を下ろした日). Các mục ghi "THỬ" là giả định, đo lại sau 5 video đầu.

## 1. Định vị

- **Ngách:** công ty từng số 1 Nhật Bản (hoặc thế giới) rồi biến mất hoặc mất tên.
- **Khán giả:** người Nhật 45 tuổi trở lên, hoài niệm Showa, thích bài học kinh doanh.
- **Giữ giống kênh mẫu:** độ dài 27–35 phút, dàn 12 chương, giọng kể bình tĩnh, ảnh tư liệu, bản đồ, phụ đề đốt vào hình, nhịp 2–3 ngày một video.
- **Khác kênh mẫu (bắt buộc):** tên, avatar, màu thumbnail, câu mở đầu riêng, và một góc kể riêng (chọn 1 ở mục 2).

## 2. Ba góc kể để chọn (cần người dùng quyết)

| Góc | Ý tưởng | Ưu | Nhược |
|---|---|---|---|
| A. "Còn lại gì" | Mỗi video kết bằng việc đi tìm dấu vết hôm nay: toà nhà, thương hiệu, công ty con còn sống | Gần kênh mẫu nhất, dễ làm | Dễ bị xem là bản sao |
| B. "Con người" | Kể theo số phận nhân viên, người sáng lập sau khi sụp đổ (giống hướng 破綻、そのあと。 đang 1,1 triệu view) | Cảm xúc mạnh, bình luận nhiều | Cần nguồn về đời người, khó tìm hơn |
| C. "Bài học quản trị" | Mỗi video rút 3 sai lầm quản trị có số liệu, so với công ty hôm nay | Khán giả doanh nhân, CPM cao | Khô hơn với người xem hoài niệm |

Đề xuất: **A làm nền + chương cuối kiểu C** ("3つの判断"), vì bình luận kênh mẫu đầy bài học quản trị.

## 3. Công thức SEO (THỬ)

**Tiêu đề** (35–45 ký tự):
```
{danh hiệu số 1}の{tên công ty}は、なぜ消えたのか｜{chi tiết so sánh hoặc con số}
```
Dùng biến thể khác kênh mẫu một chút (ví dụ `消えたのか` thay vì `消えた？`, hoặc đưa con số lên đầu), không chép nguyên câu.

**Thumbnail** (tự sinh bằng script, xem QUY_TRINH):
- Ảnh chân dung đen trắng người sáng lập, ảnh nền trụ sở, đều lấy từ Wikimedia Commons có giấy phép.
- Màu riêng: đề xuất nền tối xanh đậm, chữ trắng + vàng nhạt, nhãn tên công ty màu khác đỏ của kênh mẫu.
- 3 vùng chữ: tên công ty, câu hỏi lớn, dòng "thành tích" nhỏ.

**Mô tả:** câu đỉnh cao có số và quy đổi tiền hôm nay → câu "nhưng ○ năm sau" → câu hỏi → mục lục tự sinh → nguồn → ghi tác giả ảnh tự sinh → câu mời kể ký ức → hashtag.

**Thẻ:** kênh mẫu không dùng thẻ. Ta vẫn điền 10–15 thẻ (tên công ty, tên khác, người sáng lập, ngành, 企業史, 昭和, 倒産...) vì không mất gì. Không dùng tên kênh khác.

**Khai báo:** nội dung tổng hợp "Có" (giọng AI), không dành cho trẻ em, danh mục Giáo dục (27).

**Giờ đăng:** 17:00 giờ Nhật, 3 video mỗi tuần (THỬ).

## 4. Làm lại chủ đề đối thủ đã nổ view (quyết định 04/11/2026)

Người dùng quyết định: **được làm lại đúng chủ đề** các video đối thủ đang nổ view. Chủ đề và dữ kiện lịch sử là của chung, khán giả đã chứng minh họ muốn xem.

| Được giống đối thủ | Phải là của mình |
|---|---|
| Công ty, mốc năm, con số, nhân vật, các sự kiện chính | Lời kịch bản: viết từ nguồn gốc (`nguon.md`), không dịch hay diễn đạt lại lời đối thủ |
| Dàn 12 chương, độ dài, nhịp cảnh | Hình, màu, phụ đề, thumbnail, tên kênh |
| Công thức tiêu đề, mô tả, giờ đăng | Câu chữ tiêu đề và mô tả |

Lý do giữ lời riêng dù hình khác: bản quyền nằm ở câu chữ lời đọc, không ở hình. YouTube xử lý khiếu nại bản quyền theo nội dung, và video "đọc lại kịch bản người khác" bị xếp vào nội dung lặp lại (không bật kiếm tiền). Một khiếu nại có thể thành gậy cảnh cáo, 3 gậy là mất kênh.

Kiểm soát bằng máy: lưu bản lời video đối thủ vào `research\doi_thu\<kenh>_<cong_ty>.txt`, rồi trước khi đọc giọng chạy:

```
python tools/do_trung_loi.py runs/<run>/script.md research/doi_thu/*.txt
```

Đạt khi trùng ≤ 3% và không có đoạn nào trùng quá 40 ký tự (trừ câu trích tài liệu gốc trong 「」). Không đạt thì viết lại các đoạn được liệt kê.

**Hàng đợi ưu tiên** (đã kiểm ảnh Wikimedia ngày 04/11/2026):

| # | Chủ đề | View đối thủ | Ảnh có giấy phép |
|---|---|---|---|
| 1 | カネボウ | 1.078.000 | Có: nhà máy Tokyo, Hyogo (PD), chân dung 武藤山治 (PD), công viên Kanebo (CC0), ảnh không ảnh Sumoto 1975 |
| 2 | 鈴木商店 | 687.000 | Có: chân dung 金子直吉 (PD), trụ sở bị đốt 1918 (PD), kho cũ (CC BY) |
| 3 | 三光汽船 | 58.800 | Chưa kiểm |
| 4 | リッカー | mới đăng | Chưa kiểm |

Video đầu tiên đề xuất: **カネボウ**. Lý do: view cao nhất ngách, nhiều ảnh, sản phẩm người lớn tuổi nhớ (mỹ phẩm, kẹo, tơ lụa). Theo dõi thêm video nổ view của các kênh cùng ngách (mục 8 `research\PHAN_TICH_KENH_MAU.md`) và đưa vào hàng đợi.

## 5. Danh sách 25 chủ đề tiếp theo (chưa kiểm chứng dữ kiện)

Cột "Đối thủ" là kết quả tìm nhanh ngày 04/11/2026, chưa đủ.

| # | Công ty | Danh hiệu | Năm biến mất | Đối thủ đã làm |
|---|---|---|---|---|
| 1 | 安宅産業 | 10大総合商社 | 1977 | chưa thấy |
| 2 | 中島飛行機 | 東洋最大の航空機メーカー | 1945 | chưa thấy |
| 3 | 山一證券 | 四大証券 | 1997 | nhiều |
| 4 | 北海道拓殖銀行 | 都市銀行で初の破綻 | 1997 | có |
| 5 | ヤオハン | 国際流通グループ | 1997 | chưa thấy |
| 6 | 永大産業 | 戦後最大の倒産(当時) | 1978 | chưa thấy |
| 7 | 興人 | 化学繊維 | 1975 | chưa thấy |
| 8 | 日窒コンツェルン | 戦前の化学財閥 | 1945 | chưa thấy |
| 9 | 理研コンツェルン | 科学者の財閥 | 1940年代 | chưa thấy |
| 10 | 大倉財閥 | 明治の政商 | 戦後 | chưa thấy |
| 11 | 久原鉱業 | 鉱山王 | 1928(改組) | chưa thấy |
| 12 | 赤井電機(AKAI) | オープンリール世界的ブランド | 2000 | chưa thấy |
| 13 | マイカル | 流通大手 | 2001 | chưa thấy |
| 14 | 長崎屋 | 衣料スーパー | 2000 | chưa thấy |
| 15 | そごう | 売上日本一の百貨店 | 2000 | có |
| 16 | ダイエー | 売上日本一のスーパー | 2015 | nhiều |
| 17 | レナウン | アパレル日本一 | 2020 | có |
| 18 | 日本債券信用銀行 | 長期信用銀行 | 1998 | chưa thấy |
| 19 | 千代田生命 | 生命保険 | 2000 | chưa thấy |
| 20 | エルピーダメモリ | 日本唯一のDRAM | 2012 | chưa thấy |
| 21 | 林原 | 岡山の研究企業 | 2011 | chưa thấy |
| 22 | 雪印食品 | 雪印グループ | 2002 | chưa thấy |
| 23 | 大沢商会 | カメラ商社 | 1984 | chưa thấy |
| 24 | 日本熱学工業 | エアコン | 1974 | chưa thấy |
| 25 | セゾングループ | 流通・文化の巨大グループ | 2001(解体) | chưa thấy |

Ưu tiên: công ty có **sản phẩm người lớn tuổi nhớ** (như カネボウ) và **chưa có đối thủ làm**. Video カネボウ (sản phẩm quen) gấp 18 lần 三光汽船 (ngành hẹp).
