# Giọng đọc và nhạc nền kênh 4 (04/11/2026)

## Giọng kênh mẫu

Đo video カネボウ của 看板を下ろした日 (`8rj2Ah_Eyw0`), giây 905–935: phát trong trình duyệt, nối vào Web Audio (không ra loa, không tải tệp), tự tương quan 70–400 Hz.

| | F0 p25 – trung vị – p75 | Ghi chú |
|---|---|---|
| Kênh mẫu | 112 – **136** – 165 Hz | Giọng nam, cao vừa. Mô tả video không ghi tên giọng. 9.050 ký tự phụ đề / 34,6 phút ≈ 4,4–4,6 ký tự mỗi giây video |

## Nghe thử MiniMax (qua Genmax, tốc độ 1.0, mẫu 113 ký tự)

Công cụ: `tools/thu_giong.py`. Tệp mẫu ở `research/giong_thu/moi/`. Cách đo bằng Python cho số gần với cách đo trong trình duyệt (kiểm bằng mẫu kenh2: lệch 0–8 Hz).

| Giọng (voice_id) | F0 | Ký tự/giây | Gần kênh mẫu |
|---|---|---|---|
| **Refined Storyteller (364839964033252)** | 119 – **136** – 169 | 6,23 | **Gần nhất** |
| Serious Commander (209536448462912) | 134 – 162 – 188 | 5,66 | Cao hơn |
| Gentle Butler (209536448462915) | 93 – 119 – 144 | 5,85 | Trầm hơn |
| Shiryobukai Katarite (303589579907151) | 91 – 103 – 114 | 6,26 | Trầm hơn nhiều |
| Intellectual Narrator (364839964033246, kenh2) | 93 – 112 – 132 | — | Trầm hơn |

**Chọn: Refined Storyteller, tốc độ 0,92.** Cộng khoảng nghỉ giữa cảnh, nhịp video dự kiến khoảng 4,6–5 ký tự mỗi giây như kênh mẫu. Cần nghe thử bằng tai và đo lại sau video 1.

## Nhạc nền

Kênh mẫu có nhạc nền nhỏ (YouTube đánh dấu `[音楽]`), không ghi tên bài. Không lấy nhạc từ video của họ.

Kênh 4 dùng nhạc tự tổng hợp: `tools/tao_nhac_nen.py` → `channels/kigyo_shi/assets/nhac_nen.wav` (piano rải hợp âm thứ, pad, bass, có vang, 64 BPM, 120 giây, lặp liền, -17,5 LUFS). Engine tự giảm nhạc khi có lời (`am_luong_nhac` 0,12). Chưa nghe bằng tai. Nếu muốn nhạc có sẵn chất lượng cao hơn, có thể dùng thư viện nhạc miễn phí bản quyền (ví dụ DOVA-SYNDROME), người dùng tự tải và ghi giấy phép vào `nhac_nen_giay_phep`.
