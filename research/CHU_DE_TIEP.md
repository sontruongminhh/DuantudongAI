# Chọn chủ đề đi trước đối thủ (05/11/2026)

Mục tiêu: giữ khuôn video (công ty/gia tộc từng số 1 rồi biến mất, 12 chương), nhưng chọn chủ đề **kênh mẫu 看板を下ろした日 chưa làm**, tự tìm tư liệu, ra trước họ.

Công cụ: `tools\cham_chu_de.py research\ung_vien.json` → `research\cham_chu_de.json`. Điểm gồm: nhu cầu (view cao nhất của video có tên chủ đề) 40, ít đối thủ cùng khuôn 25, ảnh có giấy phép trên Commons 20, tư liệu (J-STAGE, 国会会議録) 15. Điểm chỉ để xếp hạng, không phải dự báo view.

## Phát hiện

1. **Khuôn 「…はなぜ消えた？」 đã bị nhiều kênh mới chép**: 時代の忘れもの, 消えた社名, 栄光よ、いずこへ。, 歴史の裏帳簿, 財閥と銀行の墓標, あの会社はなぜ消えた?, 消滅図鑑… Họ đã làm 安宅産業, 中島飛行機, 日産コンツェルン, 川崎造船所, セゾングループ, ダイエー, nhưng phần lớn chỉ được **49 đến 15.000 view**. Chiếm chủ đề trước là chưa đủ: cần chủ đề người xem tìm nhiều + chất lượng hơn hẳn (nguồn gốc, ảnh thật, kể rõ).
2. Kênh thắng trong ngách là kênh có góc riêng: 破綻、そのあと。 (アイワ 1,1 triệu), カカチャンネル (長崎屋 80 vạn), さよならの記録 (ヤオハン 15,7 vạn), 歴ビズ (ダイエー 23,6 vạn).
3. **Tài phiệt trước chiến tranh** (大倉, 浅野, 古河, 久原, 日窒, 森): gần như chưa ai làm, chân dung có giấy phép nhiều (大倉喜八郎 17, 浅野総一郎 13, 川崎/松方 26), nhưng video sẵn có ít view (dưới 2 vạn). Không chứng minh là ít người muốn xem: 鈴木商店 của kênh mẫu được 68,7 vạn view. Đây là vùng kênh mẫu có thể làm tiếp (cùng kiểu 鈴木商店, カネボウ), nên làm trước họ có lợi.

## Bảng điểm (rút gọn)

| Điểm | Chủ đề | Gia tộc / người | Video cao nhất có tên chủ đề | Đối thủ cùng khuôn ≥10 vạn | Ảnh PD/CC | Chân dung | Ghi chú |
|---|---|---|---|---|---|---|---|
| 95 | 大映 | 永田雅一 | 39,7 vạn | 0 (lớn nhất 4,9 vạn) | 47 | 3 | Hãng phim: 羅生門, 座頭市, ガメラ; phá sản 1971 |
| 92 | セゾングループ | 堤清二 (堤家) | 67,9 vạn | 0 (lớn nhất 1.136) | 57 | 5 | Gia tộc 堤; 無印良品, ファミマ, パルコ, ロフト còn sống |
| 94 | マイカル | ニチイ | 138 vạn | 0 (1,7 vạn) | 63 | 0 | Thiếu chân dung |
| 85 | 新東宝 | 大蔵貢 | 22,8 vạn | 0 (2,9 vạn) | 35 | 6 | Hãng phim nhỏ, đặc sắc |
| 83 | 中島飛行機 | 中島知久平 | 24,8 vạn | 1 (24,8 vạn) | 51 | 9 | Đã có video lớn và 2 bản nhái |
| 80 | 安宅産業 | 安宅英一 (安宅家) | 143 vạn* | 0 (5,9 vạn) | **0** | 0 | Không có ảnh: bỏ (bài học リッカー) |
| 77 | ヤオハン | 和田家 | 143 vạn* | 1 (15,7 vạn) | 31 | 0 | Đã có video lớn |
| 62 | 大倉財閥 | 大倉喜八郎 | 1,6 vạn | 0 | 22 | **17** | Tài phiệt Meiji; Hotel Okura, 大成建設 còn sống |
| 54 | 川崎造船所 | 松方幸次郎 | 469 | 0 | 50 | **26** | Bộ sưu tập Matsukata, 十五銀行 |
| 47 | 浅野財閥 | 浅野総一郎 | 1.632 | 0 | 24 | 13 | Xi măng, 京浜工業地帯 |

\* view cao nhất có thể là video khác chủ đề nhưng có tên trong tiêu đề (quảng cáo cũ, tin tức). Danh sách đủ 34 ứng viên ở `research\cham_chu_de.json`.

## Đề xuất thứ tự

1. **セゾングループ (堤清二 và gia tộc 堤)**: nhu cầu cao, thương hiệu người xem đang dùng hằng ngày (無印良品, ファミリーマート, パルコ, ロフト, 西友), đối thủ cùng khuôn chỉ 1.136 view, đủ ảnh và chân dung. Câu chuyện gia tộc mạnh: cha 堤康次郎, hai anh em cùng cha khác mẹ 清二 và 義明.
2. **大映 (永田雅一)**: hãng phim từng giành giải lớn quốc tế, các thương hiệu người lớn tuổi nhớ (座頭市, ガメラ, 大魔神), phá sản 1971. Ít đối thủ, nhiều ảnh.
3. **大倉財閥 (大倉喜八郎)**: tài phiệt Meiji, nhiều chân dung, chưa ai làm, cùng kiểu 鈴木商店. Đi trước kênh mẫu ở vùng tài phiệt.

Hai video đã có kịch bản và hình (三洋電機, 三光汽船) vẫn dựng được bất cứ lúc nào; đó là chủ đề trùng đối thủ.

## Cập nhật 05/11/2026: bảng thị trường và video 5

- Bảng 38 kênh ngách công ty / gia tộc: Google Sheet tab "Thị trường Cty-Gia tộc" (bản gốc `research\data\thi_truong_kigyo_20261105.tsv`, dựng lại: `python -I research\quet_thi_truong.py` rồi `python -I research\lam_bang_thi_truong.py`).
- Nhu cầu đo lại bằng YouTube API: 大倉喜八郎 có video 50,8 vạn và 8,1 vạn (trước đây ghi 1,6 vạn là thiếu); 堤康次郎 9 video ≥10 vạn; 岩崎弥太郎 9; 小林一三 5; 安田善次郎 3; 大映 3.
- Video 5 chọn **大倉財閥**, kế hoạch ở `luu_tru\KE_HOACH_VIDEO5.md`. 大映 để video 6.

## Cập nhật 07/11/2026: đo mức quan tâm theo người (`research\tim_nguoi.py`)

Kế hoạch ở `research\KE_HOACH_TIM_NGUOI.md`, bảng đủ 62 người ở `research\data\tim_nguoi_20261107.md`. Năm người đầu:

| Điểm | Người | Wiki 12 tháng | Đà tăng | YouTube cao nhất | Video 180 ngày | Nhận xét |
|---|---|---|---|---|---|---|
| 81,7 | 本田宗一郎 | 15,1 vạn | ×1,4 | 175 vạn | 3 | Khoảng trống lớn, nhưng không có câu chuyện gia tộc / tài phiệt; hậu duệ còn sống |
| 80,9 | 岩崎弥太郎 (三菱) | 24,4 vạn | ×1,74 (10/2026: 5,7 vạn, gấp 3,5 lần bình thường) | 213 vạn | 11 | Đang nóng; 岩崎弥之助 cũng tăng tháng 10. Đối thủ kể đời tư 弥太郎, chưa ai kể bốn đời 岩崎 |
| 76,0 | 堤康次郎 | 9,9 vạn | ×1,34 | 85 vạn | 6 | Trùng một phần video 4 (セゾン) |
| 74,7 | 井深大 | 8,8 vạn | ×1,7 (tăng một tháng) | 49 vạn | 17 | Đông đối thủ |
| 74,4 | 松下幸之助 | 23,5 vạn | ×0,78 (đang giảm) | 221 vạn | 4 | Phần lớn là video kinh doanh / phát biểu |

Đề xuất video 9: **岩崎家 (三菱)**, loạt 「なぜ終わらなかったのか」. Bốn đời chủ 弥太郎 → 弥之助 → 久弥 → 小弥太; khác 三井 và 安田 (tự xin giải thể), 小弥太 phản đối giải thể. Chưa rõ vì sao lượt xem 岩崎弥太郎 tăng vọt tháng 10/2026 (không thấy phim truyền hình liên quan).

Lỗi công cụ cần sửa: 根津嘉一郎, 武藤山治, 鴻池善右衛門, 野村徳七, 大林芳五郎, 早川徳次 bị loại nhầm "còn sống" (trang ja.wikipedia là trang định hướng hoặc Wikidata thiếu năm mất); 松方幸次郎, 鳥井信治郎 thiếu lượt xem (tên trang khác chữ).

## 07/11/2026 (tối): gia tộc đã phá sản / biến mất nào được quan tâm (loạt 「なぜ消えたのか」)

Công cụ: `research\tim_pha_san.py` (dùng lại cách đo của `tim_nguoi.py`, thêm trang công ty / ngân hàng, tự chuyển sang yt-dlp khi hết hạn mức API). Bảng đầy đủ 60 tên: `research\data\tim_pha_san_20261107.md`. Điểm tổng bị kéo lệch bởi tên ít người tìm nhưng có ảnh, nên đọc theo cầu thật (Wikipedia + video dài trên YouTube) và độ dày cạnh tranh.

| Gia tộc | Wikipedia 12 tháng | Video dài nhiều view nhất | Cạnh tranh gần đây | Ghi chú |
|---|---|---|---|---|
| 淀屋 (大坂, bị 幕府 tịch thu toàn bộ năm 1705) | 28.108 (trang 淀屋) | 21,4 vạn (江戸ログ), 17,9 vạn, 14,8 vạn; Shorts 164 vạn | Ít video dài trong 180 ngày (3,2 vạn, 5.800) | Hợp tên kênh nhất: "người giàu nhất Nhật Bản mất hết sau một đêm". Đối thủ dùng số phóng đại 「総資産200兆円」. Không có chân dung; ảnh 淀屋橋, 堂島米市場, ukiyo-e nhiều trên Commons |
| 和田家 / ヤオハン (phá sản 1997) | 58.947 + 和田一夫 11.110 | 143 vạn (カカチャンネル), 16,3 vạn (10/2026) | 5 video, có video riêng về 「和田家はどうなったのか」 | Câu chuyện gia đình mạnh (mẹ 和田カツ), nhưng nhiều người trong nhà còn sống, ít ảnh tự do, không có chân dung |
| 中内家 / ダイエー | 201.540 + 中内㓛 88.081 | 107 vạn (中田敦彦), 25,4 vạn (歴ビズ 09/2026) | Dày: 12 video trong 180 ngày | Cầu lớn nhất nhưng cạnh tranh dày nhất; con trai còn sống; công ty vẫn còn trong Aeon |
| 横井英樹 / ホテルニュージャパン | 188.517 + 91.428 | 99 vạn, 44 vạn | 11 video trong 180 ngày | Không phải gia tộc; tai nạn hỏa hoạn 33 người chết, dễ thành nội dung giật gân |
| 鴻池家 | 51.464 (鴻池財閥) | 2,9 vạn (日本一族史) | Gần như trống | Cầu YouTube thấp |
| 松方家 (十五銀行, 川崎造船所, 1927) | 30.695 + 15.000, tăng 1,4–1,5 lần | Chỉ có video PR triển lãm | Trống | Đang có triển lãm 松方幸次郎 ở 兵庫県立美術館 (mùa thu 2026), nhưng cầu video dài chưa thấy |

**Đề xuất: 淀屋** (loạt 「なぜ消えたのか」). Góc kể: bốn đời từ 常安 (khai phá 中之島, lập chợ gạo, tiền thân 堂島米市場, sàn kỳ hạn đầu tiên trên thế giới) tới 辰五郎 (闕所 năm 1705), rồi chuyện chi nhánh ở 倉吉 nối nghiệp (cần kiểm nguồn). Mọi con số phải lấy từ tài liệu: không dùng 「200兆円」 của đối thủ. Thumbnail không có mặt người: dùng ukiyo-e 淀屋橋, chữ lớn.

**Sửa đề xuất (07/11, sau khi người dùng hỏi lại):** đề xuất 淀屋 ở trên đọc sai dữ liệu. "Ít cạnh tranh" của 淀屋 là do ít người xem, không phải khoảng trống: video mới nhất về 淀屋 trong 180 ngày chỉ đạt 3,2 vạn, còn video mới về ダイエー đạt 25,4 vạn (歴ビズ 09/2026), về ヤオハン 16,3 vạn (さよならの記録 10/2026), về ホテルニュージャパン 22,5 vạn (10/2026). Thước đo đúng là **video mới gần đây còn đạt bao nhiêu view**, không phải số video cạnh tranh. Đề xuất mới: **中内家 / ダイエー** (từng 売上日本一, cầu lớn nhất), rồi tới **和田家 / ヤオハン**. 淀屋 để sau.

## 09/11/2026: video 11 chọn **和田家 / ヤオハン** (loạt 「なぜ消えたのか」)

Theo thứ tự đã đề xuất ngày 07/11 (sau ダイエー). Video dài tiếng Nhật về chủ đề (yt-dlp, 09/11): カカチャンネル 143 vạn (2021), さよならの記録 16,7 vạn (10/2026), その後の日本 2,1 vạn (10/2026), 偉人の人生訓 1,7 vạn (01/2026), ビジネス謎解きプラネット 0,5 vạn (10/2026); thêm video tiếng Quảng Đông của Mill MILK 50,6 vạn (khán giả 香港). Phụ đề 5 video tiếng Nhật ở `research\doi_thu\yaohan_*.ja.vtt` (chỉ để đo trùng). Cách làm như video 10: gom mạch được xem nhiều (熱海 1930, 熱海大火 1950, 和田カツ, ブラジル 1971, 香港 1990, 上海 1995, 社債 và 粉飾, 1997, 和田一夫 về sau), nguồn và câu chữ riêng, gia tộc ba đời làm sợi chỉ. Lần chạy `runs\20261109-wada-ke`.

## 09/11/2026: video 12 chọn **堤家 / 西武鉄道** (loạt 「なぜ消えたのか」, người dùng chọn)

Đo lượt xem video dài tiếng Nhật (yt-dlp, 09/11): 堤義明 / 西武 mạnh nhất trong các ứng viên còn lại: 禁断のパイオニア列伝 26,9 vạn (09/2026), Grand Slam Highlights 34,5 vạn (08/2026, chuyện đời tư), 政経電論TV 88,6 vạn (02/2025), 偉人エピソードX 35,4 vạn, カカチャンネル (コクド) 173 vạn (2020). So sánh: そごう 11,5 vạn (04/2026) và 3,7 vạn (10/2026); 住友家 2,7 vạn (09/2026); 長崎屋 1,1 vạn (04/2026); 山一證券 1–2 vạn; ホテルニュージャパン 14,1 vạn (10/2026, không phải gia tộc). Ràng buộc: 堤義明 có lẽ còn sống (không thấy tin mất) → chỉ dùng bản án 2005, văn bản chính thức của công ty và báo lớn có 「によると」, không kể đời tư; chương 堤康次郎 trùng một phần video 4 (セゾン) nên kể từ góc 西武鉄道 / コクド. Phụ đề 6 video đối thủ ở `research\doi_thu\seibu_*.ja.vtt` (chỉ để đo trùng). Lần chạy `runs\20261109-tsutsumi-ke`.

## 09/11/2026: ứng viên video 13 (sau khi xem 5 video lịch sử quân sự đang nổ)

Đo bằng yt-dlp (video ≥10 phút):

| Gia tộc / công ty | Video gần đây | Cạnh tranh cùng khuôn | Ghi chú |
|---|---|---|---|
| **中島家 / 中島飛行機** | 24,8 vạn (09/2026, AIで蘇る戦争の記憶), 7,3 vạn (01/2026), 47,7 vạn (SUBARU 2024) | 消えた社名 「中島飛行機はなぜ消えた？」 2,3 vạn (03/11/2026) | Chạm nhóm xem lịch sử quân sự đang nổ. 51 ảnh PD/CC, 9 chân dung. 知久平 là nghị sĩ, 鉄道大臣 → có 国会会議録. Người còn sống ít. Tránh góc 「六連星」 của video 24,8 vạn |
| 鮎川家 / 日産コンツェルン | 12 vạn (29/10/2026), 2,2 vạn | 日本一族史 「鮎川家」 2.045 | Mãn Châu, nghi phạm chiến tranh hạng A; hậu duệ còn sống, nhiều công ty còn hoạt động |
| 渋沢家 (その後) | ギルド日本史 7,8 vạn (27/10/2026) | | Góc 「その後どうなったのか」; không phải "biến mất" |
| 横井英樹 | 14,1 vạn (10/2026), 44 vạn | dày | Không phải gia tộc; vụ cháy 33 người chết, dễ giật gân |

## 10/11/2026: video 14 chọn **鮎川家 / 日産コンツェルン** (loạt 「なぜ消えたのか」)

Ứng viên kế trong bảng video 13. Đo lại bằng yt-dlp (video ≥10 phút, 20 kết quả đầu):

| Chủ đề | Video dài nhiều view nhất | Cạnh tranh cùng khuôn | Ghi chú |
|---|---|---|---|
| **鮎川義介 / 日産** | 偉人エピソードX 12,3 vạn, 禁断のパイオニア列伝 2,2 vạn | 日本一族史 「鮎川家」 2.047, 歴史全史アーカイブ 6.645 | Chạm nhóm Mãn Châu / chiến tranh; nhiều thứ còn tới nay (日産, 日立, ニッスイ, ENEOS) |
| 渋沢家 その後 | RekiShock 28,7 vạn (vợ), 戦国BANASHI 11,1 vạn, ギルド 7,9 vạn | dày | Hợp loạt 「なぜ終わらなかったのか」 hoặc góc その後 |
| 住友家 | カカチャンネル 36,5 vạn (cũ), 日本一族史 2,7 vạn | | Loạt 「なぜ終わらなかったのか」 |
| そごう / 水島廣雄 | 偉人の人生訓 11,5 vạn, 1,5 vạn | 看板を下ろした日 3.722 | Không phải gia tộc |
| 山一證券 | カカチャンネル 100 vạn + 87 vạn (cũ) | | Không phải gia tộc; video mới chỉ ~1 vạn |
| 浅野総一郎 / 久原房之助 | 1,9 vạn / 9.314 | | Cầu nhỏ |

Phụ đề 4 video đối thủ ở `research\doi_thu\aikawa_*.ja.vtt` (chỉ để đo trùng). Lần chạy `runs\20261110-aikawa-ke`.

## 12/11/2026: video 15 chọn **住友家** (loạt 「なぜ終わらなかったのか」)

Đo bằng yt-dlp (video ≥10 phút, kèm tháng đăng):

| Chủ đề | Video dài nhiều view | Ghi chú |
|---|---|---|
| **住友家** | 春日陽 「三大財閥トップの生活」 64,8 vạn (05/2025), カカチャンネル 「住友」 36,5 vạn (01/2023), 歴史全史アーカイブ 「財閥史」 9,9 vạn (10/2026) | Cùng khuôn chỉ 日本一族史 2,7 vạn. Đủ bộ ba 三井 (video 8) – 岩崎 (video 9) – 住友. Video 8 đã ghi là chủ đề kế của loạt 2 |
| 淀屋 | 江戸ログ 21,4 vạn (08/2026), 禁断の歴史ランキング 7,3 vạn (10/2026) | Cầu đã lên so với 07/11; không có chân dung |
| 渋沢家 その後 | ギルド日本史 8,0 vạn (10/2026) | Đối thủ vừa làm đúng góc này |
| 北海道拓殖銀行, そごう | 看板を下ろした日 14,6 vạn và 5,1 vạn (11/2026) | Kênh mẫu vừa làm: tránh |
| 長崎屋 | 名門落日録 4,4 vạn (11/2026) | Đối thủ vừa làm |
| 古河, 浅野, 鴻池, 松方 | 1–3 vạn | Cầu nhỏ |

Phụ đề 3 video đối thủ ở `research\doi_thu\sumitomo_*.ja.vtt` (chỉ để đo trùng). Lần chạy `runs\20261112-sumitomo-ke`.
