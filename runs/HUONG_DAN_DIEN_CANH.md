# Hướng dẫn bước 2: điền hình cho từng cảnh (kênh 4)

Làm sau khi `script.md` đã qua `check_script_ja.py` và `do_trung_loi.py`. Làm trong `E:\DuantudongAI\kenh4`. Vẫn **không** chạy `dung`, `tai-len` hay lệnh tốn credit.

## 1. Tách cảnh

Lệnh `-m studio` nhận **tên lần chạy** (ví dụ `20261104-kanebo`), không nhận đường dẫn. Các lệnh `tools...` thì nhận đường dẫn `runs<run>`.

```
.venv\Scripts\python.exe -m studio tach-loi <run>
```

Ghi `motion\dong_loi.json`: mỗi cảnh có `id` (S001…), `chuong`, `narration`, `goi_y_hinh` (gợi ý `[HÌNH: …]` của beat). Một beat có thể thành 1–3 cảnh liên tiếp.

## 2. Viết `runs\<run>\dien_mau.py`

```python
"""Điền hình cho video <công ty>. Chạy: .venv\\Scripts\\python.exe runs\\<run>\\dien_mau.py"""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from studio.dien_k4 import K4  # noqa: E402

K = K4(HERE)
K.c(1, "chuong", no="第1章", title="はじめに", years="1887年〜2007年")
K.c((2, 3), "so_lon", year="1936年", label="民間企業の売上1位", num="2億6204", unit="万円",
    compare="今の企業物価でおよそ2300億円", src="松尾(2017)")
...
sys.exit(0 if K.finish() else 1)
```

- Đọc `motion\dong_loi.json` (narration + goi_y_hinh) rồi gán mẫu cho **mọi** cảnh. `K.c((đầu, cuối), …)` cho cả beat: cảnh đầu chạy hoạt ảnh, cảnh sau giữ hình (ảnh thì tự đổi hướng trôi).
- Hình phải **khớp lời đọc của chính cảnh đó**: con số, năm, tên trên hình phải đúng như lời và như `nguon.md`. Đổi hình khi lời chuyển sang ý mới, kể cả trong cùng beat (khi đó chia khoảng nhỏ hơn).
- Cố đừng để một hình đứng quá 3 cảnh liền (khoảng 30 giây). Kênh mẫu đổi hình trung vị mỗi 10 giây.
- `src` (dòng 出典 góc trên trái): với đồ họa, ghi ngắn tên nguồn chính, ví dụ `松尾(2017)`, `国会会議録 1985年5月`, `コトバンク「鐘紡」`. Ảnh thì để trống, máy tự ghi tác giả và giấy phép.
- `nguon`: để trống thì máy lấy mã F trong gợi ý hình. Nếu hình dùng dữ kiện khác thì ghi rõ `nguon=["F12", "F13"]`. Mẫu có số liệu bắt buộc có mã F mức A hoặc B.
- Tỷ lệ nhắm tới: khoảng 30% cảnh là ảnh (`anh`, `chan_dung`, `luoi_anh`). Mỗi chương nên có ít nhất 1–2 cảnh ảnh nếu có ảnh hợp.

## 3. Các mẫu và dữ liệu

Xem ví dụ chạy được trong `thu_nghiem\thu_mau_k4.py` và ảnh kết quả `thu_nghiem\out\luoi_k4.png`. Giới hạn độ dài do máy kiểm (tính theo ký tự toàn khổ; chữ số và chữ latin tính 0,55).

| Mẫu | Trường | Giới hạn |
|---|---|---|
| `chuong` | `no` ("第3章"), `title`, `years` | title ≤ 13 |
| `anh` | `anh` (tên tệp), `caps` [≤3 dòng], `pan` (vao/ra/trai/phai), `x`,`y` (điểm canh %, mặc định 50/40), `bw` (true = đen trắng), `cap_vi_tri` ("tren"/"duoi") | mỗi cap ≤ 24 |
| `chan_dung` | `anh`, `role`, `name`, `years`, `note`, `x`,`y` (canh mặt, mặc định 50/25), `bw` (mặc định true) | name ≤ 8, role ≤ 22, note ≤ 40 |
| `so_lon` | `year`, `label`, `num`, `unit`, `compare` | num+unit ≤ 9, label ≤ 22, compare ≤ 34 |
| `cot` | `title`, `sub`, `bars` [[nhãn, số, chữ trên cột]] 2–6, `nhan` (chỉ số cột đỏ, mặc định cột cuối) | nhãn ≤ 8 (≤ 6 khi > 4 cột) |
| `tron` | `title`, `parts` [[nhãn, %]] 2–5 cộng ≈ 100, `nhan` | nhãn ≤ 9 |
| `danh_sach` | `title`, `sub`, `items` 2–5, `nhan` [chỉ số đỏ] | ý ≤ 26 |
| `nien_bieu` | `title`, `stops` [[năm, việc]] 3–6, `nhan` | năm ≤ 7, việc ≤ 16 |
| `so_sanh` | `title`, `left`/`right` {name, sub, items 1–4} | name ≤ 10, ý ≤ 14 |
| `ban_do_diem` | `title`, `vung` (nhat_ban / dong_a / the_gioi), `points` [[tên, kinh độ, vĩ độ, ("trai" để nhãn bên trái)]] 1–6, `nhan` | tên ≤ 10 |
| `luoi_anh` | `title`, `items` [[tệp, nhãn]] 2–4 (một hàng ảnh dọc) | nhãn ≤ 12 (≤ 10 khi 3–4 ảnh) |
| `bon_the` | `center`, `items` đúng 4 | thẻ ≤ 9, center ≤ 10 |
| `trich_dan` | `lines` [tên tài liệu + ngày, câu trích…] 2–4 | tên ≤ 40, câu ≤ 24 |
| `cau_hoi` | `lines` 1–3 (nền tối, chữ lớn) | dòng ≤ 16 |

Mọi mẫu (trừ `chuong`, `cau_hoi`) cần `src`. Có thể thêm `kari: true` chỉ khi thử, không dùng cho video đăng. `title`, `sub` của mọi mẫu: title ≤ 22, sub ≤ 34.

## 4. Kiểm và dựng trang

```
.venv\Scripts\python.exe runs\<run>\dien_mau.py
.venv\Scripts\python.exe -m studio nap-motion <run>
.venv\Scripts\python.exe -m studio kiem-tra-goi <run>
.venv\Scripts\python.exe -m studio dung-canh <run>
```

Sửa đến khi không còn lỗi. Rồi render thử khoảng 12 cảnh đa dạng để xem bằng mắt (chữ tràn, ảnh cắt mất mặt, số sai):

```
.venv\Scripts\python.exe tools\ve_song_song.py runs\<run> --so-luong 6 --chi S001 S010 S025
ffmpeg -y -loglevel error -ss 5 -i runs\<run>\motion\out\S010.mp4 -frames:v 1 -vf scale=640:-1 runs\<run>\motion\xem_S010.png
```

Chọn ít nhất mỗi mẫu một cảnh, và mọi cảnh chân dung (xem mặt có bị cắt không). Không cần render hết; người điều phối sẽ render toàn bộ.

## 5. SEO và thumbnail

Ghi `runs\<run>\publish\thumb.json` và `runs\<run>\publish\seo.json` theo docstring của `tools\thumbnail_kigyo.py` và `tools\seo_kigyo.py`.
- Tiêu đề theo khuôn kênh: `{日本一の肩書き}・{社名}はなぜ消えたのか｜{比べる相手や数字}`, 35–48 ký tự, không dùng 【】. Không chép nguyên tiêu đề đối thủ.
- `mo_dau`: 3 câu (đỉnh cao + con số + giá trị hôm nay; 「ところが、その頂点から○年後…」; câu hỏi + "…の○年を追います").
- `tai_lieu`: 4–7 dòng `・tác giả「tên」tạp chí (năm)` lấy từ `nguon.md`.
- `ky_uc`: câu mời kể ký ức về sản phẩm, nhà máy.
- `hashtag`: 5–7 cái, gồm `#企業史` `#昭和` (hoặc `#大正`, `#平成` cho đúng thời).
- `the`: 12–18 thẻ (tên công ty, tên cũ, người, ngành, sản phẩm, 企業史, 倒産, 経営史...).
- Chạy `.venv\Scripts\python.exe -m studio tao-seo <run>` để tạo khung `metadata.json` (seo_kigyo.py chạy sau khi có giọng).
- Chạy `.venv\Scripts\python.exe tools\thumbnail_kigyo.py runs\<run>` và xem `publish\thumbnail.jpg`: chữ không đè mặt người, tên công ty ≤ 8 ký tự, dòng dưới ≤ 20 ký tự.

## Báo lại

Số cảnh, tỷ lệ ảnh, các cảnh đã xem bằng mắt và vấn đề còn lại.
