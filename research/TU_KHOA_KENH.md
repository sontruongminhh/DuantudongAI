# Từ khóa kênh 日本一の終わり方 (06/11/2026)

Nguồn: 38 kênh trong bảng thị trường ngách công ty / gia tộc (`research\data\thi_truong_kigyo_20261105.tsv`), lấy bằng YouTube Data API: từ khóa kênh (`brandingSettings.channel.keywords`) và thẻ của 10 video nhiều view nhất mỗi kênh. Dữ liệu thô: `research\data\tag_kenh_thi_truong_20261106.json`.

## Bộ từ khóa kênh (dán vào ô Từ khóa)

YouTube Studio → Cài đặt → Kênh → Thông tin cơ bản → Từ khóa. Ô nhập tách từ bằng **dấu phẩy** (API lưu thành dấu cách). 41 từ, dưới 500 ký tự.

```
日本一の終わり方, 企業史, 会社の歴史, 経営史, 経済史, 日本史, 歴史解説, ドキュメンタリー, 企業ドキュメンタリー, 日本企業, 大企業, 財閥, 財閥の歴史, 財閥解体, 四大財閥, 一族の歴史, 創業者, 創業家, 実業家, 経営者, 倒産, 経営破綻, 破綻のその後, 消えた企業, 消えた会社, なぜ消えた, 栄枯盛衰, 日本経済, バブル崩壊, 明治, 大正, 昭和, 昭和史, 平成, 銀行, 百貨店, 商社, 家電メーカー, 映画会社, 聞き流し, 作業用
```

| Nhóm | Từ | Căn cứ |
|---|---|---|
| Tên kênh | 日本一の終わり方 | Để người tìm đúng tên kênh ra kênh mình |
| Thể loại chung | 企業史, 会社の歴史, 経営史, 経済史, 日本史, 歴史解説, ドキュメンタリー, 企業ドキュメンタリー | Từ khóa kênh dùng nhiều nhất trong ngách (企業 7 kênh, 歴史解説 6, ドキュメンタリー 5, 日本史 5); thẻ video 日本史 8 kênh, 企業史 6 kênh |
| Tài phiệt, gia tộc | 財閥, 財閥の歴史, 財閥解体, 四大財閥, 一族の歴史, 創業者, 創業家, 実業家, 経営者 | 財閥 trong từ khóa 3 kênh; thẻ 財閥解体 3 kênh, 71 vạn view; nhóm gia tộc đang tăng nhanh nhất ngách |
| Biến mất | 倒産, 経営破綻, 破綻のその後, 消えた企業, 消えた会社, なぜ消えた, 栄枯盛衰 | 経営破綻 5 kênh, 倒産 4 kênh; đúng khuôn tiêu đề của kênh |
| Thời kỳ | 明治, 大正, 昭和, 昭和史, 平成, 日本経済, バブル崩壊 | 昭和 5 kênh, バブル崩壊 5 kênh; video của kênh trải từ Minh Trị tới Bình Thành |
| Ngành đã và sẽ làm | 銀行, 百貨店, 商社, 家電メーカー, 映画会社 | Ngành của 7 video đã làm và các ứng viên kế tiếp |
| Cách xem | 聞き流し, 作業用 | 2 kênh cùng khuôn video dài có lời đọc dùng (歴ビズ, あの会社はなぜ消えた?) |

**Không đưa vào, có lý do:**
- 「しくじり企業」: tên loạt video riêng của カカチャンネル, không dùng dấu ấn kênh khác.
- 「ゆっくり解説」「ずんだもん」 (850 vạn và 230 vạn view): kênh mình không dùng kiểu này, đưa vào là gây hiểu nhầm.
- Tên kênh đối thủ, 「戦国武将」「家系図」: không phải nội dung của kênh mình.

## Thẻ chung cho mọi video (thêm vào cuối 18 thẻ riêng của từng video)

`企業史, 経営史, 日本企業, 歴史, ドキュメンタリー, 昭和` (cộng 財閥, 財閥解体 nếu video là tài phiệt). Đây là các thẻ được nhiều kênh nhiều view dùng chung: 歴史 6 kênh (394 vạn view), ビジネス 8 kênh, 日本企業 5 kênh (146 vạn), ドキュメンタリー 6 kênh.

## Lưu ý

- Từ khóa kênh tác động không nhiều: 11/38 kênh không ghi từ khóa nào, kể cả kênh lớn như 破綻、そのあと。, 禁断のパイオニア列伝, ぼくひぐま。. Tiêu đề, thumbnail và thời gian xem vẫn quyết định phần lớn lượt đề xuất.
- Danh mục: các kênh trong ngách chủ yếu dùng Giáo dục (27) hoặc Con người & blog (22). Kênh mình dùng Giáo dục là hợp.
- Làm lại: chạy lại khối lệnh trong phiên 06/11 (YouTube API, bộ nhớ đệm `research\cache\`).
