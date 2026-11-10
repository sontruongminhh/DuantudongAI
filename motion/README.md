# Motion thay cho clip Muse

Cảnh motion 10 giây dựng bằng HyperFrames, xuất ra `S001.mp4`... đúng định dạng mà `nhan-clip` của studio nhận. Các bước còn lại (giọng, dựng, cắt, QC, SEO, tải lên) giữ nguyên. Quy trình đầy đủ ở `..\QUY_TRINH.md`.

## Cần có

- Node.js 22 trở lên (đã cài v26.13.0 bằng `winget install OpenJS.NodeJS.LTS`), FFmpeg, Chrome.
- HyperFrames (Apache-2.0) chạy qua `npx hyperframes@0.8.231`. Telemetry đã tắt bằng `npx hyperframes telemetry disable`.
- GSAP 3.15.0 ở `vendor\gsap.min.js` (giấy phép "no charge" của GSAP).
- Font `Noto Sans JP` do HyperFrames tự tải về lần đầu và lưu cache. Không dùng `Yu Gothic` hay `Meiryo` trong cảnh vì bộ kiểm tra báo lỗi font.

## Lệnh của studio

```
python -m studio tach-loi <run>      # script.md -> motion\dong_loi.json và khung motion\canh.json
python -m studio nap-motion <run>    # kiểm tra canh.json rồi ghi scenes.json
python -m studio dung-canh <run>     # ghi trang HTML từng cảnh vào motion\du_an\scenes
python -m studio ve-canh <run>       # render thành motion\out\S001.mp4... (--canh S001,S004  --lam-lai)
python -m studio nhan-clip <run> runs\<run>\motion\out
```

Một cảnh 10 giây render mất khoảng 10 giây. Cảnh đã có clip thì `ve-canh` bỏ qua, trừ khi thêm `--lam-lai`.

## Thư mục

| Đường dẫn | Nội dung |
|---|---|
| `..\studio\mau_motion.py` | Mẫu cảnh (`hook`, `route`, `plan`, `ledger`, `compare`, `day`), bộ kiểm tra dữ liệu và giới hạn độ dài chữ |
| `..\studio\motion.py` | Tách lời đọc, kiểm tra cảnh, dựng HTML, render |
| `vendor\gsap.min.js`, `mau_du_an\` | Tệp chép vào mỗi dự án render |
| `dung_canh.py` | Công cụ nhỏ dựng 6 cảnh mẫu ra một thư mục, dùng để thử mẫu mới |
| `thu\demo` | Dự án thử đầu tiên và video 60 giây tiếng bíp |

## Lưu ý

- Clip không in phụ đề. Lệnh `dung` đốt phụ đề tiếng Nhật khi dựng. Chừa khoảng 80 px ở đáy khung.
- Chuyển động xong trong khoảng 6 giây đầu rồi giữ hình, vì `cat-clip` cắt clip theo độ dài lời đọc.
- Số liệu trong `dung_canh.py` (6 cảnh mẫu) là dữ liệu thử có cờ `thu` và `kari`. Không dùng cho video đăng.
- Muốn thêm mẫu: viết hàm trong `studio\mau_motion.py`, thêm vào `TEMPLATES`, `SCHEMA` (trường bắt buộc) và `check_length` (giới hạn chữ), rồi thêm kiểm thử trong `tests\test_motion.py`. Phải xem khung hình thật sau khi render.
- Nhân vật chim sẻ đội nón là mẫu tự vẽ, chưa phải nhân vật chính thức.

## Mẫu `ban_do` (bản đồ thế lực theo năm)

Mẫu tô màu các nhóm (quốc, vùng) theo thế lực qua nhiều mốc năm, có đồng hồ năm, nhãn mốc và thanh đếm lãnh thổ. Hình lấy từ `assets\ban_do_map.js`, do `tools\gunmap.py` tạo từ shapefile (Python thuần, không cần thư viện ngoài):

```
python tools\gunmap.py <tệp.shp> runs\<run>\motion\ban_do --id <trường> --ten <trường> --nhom <trường quốc>
```

`dung-canh` tự chép `motion\ban_do\ban_do_map.js` vào dự án nếu có. Dữ liệu cảnh: `palette` (1 đến 7 thế lực, `{mã: [màu, tên]}`), `snapshots` (2 đến 12 mốc, mỗi mốc có `year`, `label`, `owners {nhóm: thế lực}`), cần `nguon`. Kiểm thử: `tests\test_ban_do.py` (không cần PyYAML).

Đo thử với 700 hình giả: render cảnh 10 giây mất 7,4 giây, clip 0,37 MB. Dữ liệu thật (郡地図) chưa dùng.

## Cảnh dài thay đổi theo lời đọc

Mặc định mọi cảnh dài đúng `clip.thoi_luong_giay` (10 giây). Đặt trong hồ sơ kênh hoặc hồ sơ lần chạy:

    clip:
      thoi_luong_giay: 10          # dài nhất
      thoi_luong_thay_doi: true    # cảnh dài theo lời đọc
      thoi_luong_toi_thieu: 3      # tùy chọn, mặc định 3 giây

Độ dài mỗi cảnh = số ký tự lời đọc / (ký tự mỗi giây x tốc độ) + 0,25 + 0,35 + 0,4 giây lặng, làm tròn lên 0,1 giây, rồi kẹp trong khoảng tối thiểu đến `thoi_luong_giay` (hàm `scene_seconds` trong studio/motion.py). `nap-motion` ghi giá trị này vào `planned_sec` của scenes.json, `dung-canh` ghi vào `data-duration` của trang cảnh nên HyperFrames render đúng độ dài đó.

Các mẫu được thiết kế cho 10 giây. Cảnh ngắn hơn thì hoạt ảnh được nén cho vừa (chừa 0,3 giây cuối để dừng hình); cảnh dài đủ thì nhịp giữ nguyên. Đã thử: cảnh 3,7 giây và 6,4 giây render đúng độ dài, bản đồ 3 mốc nén vào 5 giây vẫn tới mốc cuối. Tốc độ đọc 6 ký tự mỗi giây chưa đo bằng giọng thật; bước `cat-clip` vẫn dùng được để cắt tiếp sau lần dựng đầu.

## Tùy chọn mẫu thêm trong vòng điền mẫu của video bản đồ (03/11/2026)

- `giu_hinh: true` (trong canh.json): cảnh tiếp theo của cùng một beat hiện ngay trạng thái cuối của hoạt ảnh, không chạy lại từ đầu. `tach-loi` tự đặt khi một beat kéo dài qua nhiều cảnh. Một cảnh không bao giờ chứa dòng của hai beat (mỗi beat một gợi ý hình).
- `ban_do`: thêm `base` (trạng thái từ cảnh trước, hiện ngay), `peak` (số lớn nhất để thanh chú giải không đổi thang giữa các cảnh), `owners` có thể rỗng; quốc rời khỏi bản đồ được tô lại màu xám. Dùng để hiện thế lực dần theo lời đọc.
- `day`, `hook`: `chara: false` bỏ chim và mặt trời (kênh chưa có nhân vật đại diện).
- `ledger`: số lẻ chỉ hiện thập phân ở hàng có số lẻ.
- Script điền mẫu cho video Sengoku: `runs/20261102-sengoku-seiryokuzu/dien_mau.py` (mỗi đoạn cảnh một mẫu, mã nguồn lấy từ gợi ý hình của beat).
