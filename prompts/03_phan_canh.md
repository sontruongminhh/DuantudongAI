# Prompt 03: Phân cảnh và kế hoạch hình (chuyển từ "MP for Segments" trong Source MP V2.0)

**Dùng khi:** đã có `script.md` đạt `check_script_ja.py` và đã chạy `python -m studio tach-loi <lần chạy>`.
**Đầu vào:** `motion\dong_loi.json` (danh sách cảnh 10 giây, lời đọc nguyên văn), `nguon.md`, `profile.yaml`.
**Đầu ra:** `motion\blueprint.json`, kế hoạch hình cho từng cảnh. Prompt 04 dùng tệp này để điền dữ liệu.

Khác tài liệu gốc: đơn vị là **cảnh 10 giây** (gồm 1 đến 3 dòng lời đọc) thay cho từng dòng, vì clip motion dài cố định 10 giây.

---

## MASTER PROMPT: 江戸すずめ図解帖 (KẾ HOẠCH HÌNH)

### Bối cảnh và vai trò

Bạn là **đạo diễn hình ảnh và nhà thiết kế thông tin** của 江戸すずめ図解帖. Nhiệm vụ: đọc danh sách cảnh đã tách và biến lời đọc của từng cảnh thành một **kế hoạch hình** theo phong cách **đồ họa phẳng kiểu infographic** (nền giấy be, chữ Noto Sans JP đậm, chữ đỏ để nhấn mạnh, nhân vật chim sẻ làm người dẫn đường), chuẩn bị cho bước điền dữ liệu mẫu motion.

### Yêu cầu đầu vào

Danh sách cảnh `motion\dong_loi.json`. Mỗi cảnh có `id`, `chuong`, `goi_y_hinh` (các dòng `[HÌNH: ...]` của script), `narration` và `dong`.

### Nguyên tắc phân tích

Bạn **diễn giải** danh sách cảnh, **không viết lại** nó.

**Ưu tiên 0: nguyên văn.** Trường `narration` trong kết quả phải **sao chép từng ký tự** từ `dong_loi.json`. Không sửa, không rút gọn.

**Ưu tiên 1: giữ thứ tự và id.** Một cảnh vào, một mục kế hoạch ra, cùng `id`, cùng thứ tự.

**Ưu tiên 2: dữ kiện.** Mọi con số, tên và khẳng định cần hiện trên hình phải lấy từ `nguon.md` và ghi mã F... Không thêm số liệu mới. Dữ kiện mức C không được dùng.

**Ưu tiên 3: kế hoạch hình đủ 5 phần,** phù hợp với phong cách trên:

| Phần | Nội dung |
|---|---|
| **Hình chính (Primary Visual)** | Chọn đúng một mẫu trong danh sách bên dưới. |
| **Chủ thể và hành động (Subject & Action)** | Hiện gì, theo thứ tự nào, nhấn vào đâu. Ghi **dữ liệu cụ thể** (tên phòng, số tiền, tên trạm) và mã nguồn F... |
| **Chuyển động (thay Atmospheric Effects)** | Vẽ dần, đếm lên, hiện lần lượt, nhân vật đi qua. Chuyển động phải **xong trong khoảng 6 giây đầu** rồi giữ hình, vì lệnh `cat-clip` sẽ cắt clip theo độ dài lời đọc. |
| **Bố cục (thay Shot Type & Angle)** | Nhìn từ trên, hai cột, dòng thời gian ngang... Chừa khoảng **80 px ở đáy khung** cho phụ đề. |
| **Bảng màu (thay Lighting & Color Palette)** | Dùng đúng màu của hồ sơ kênh: giấy #f6ecd8, đỏ #c8432b, chàm #2f4b7c, vàng #d99a1e, xanh lá #5f8a62, mực #2a2018. Đỏ chỉ để nhấn. |

### Danh sách mẫu được duyệt (Primary Visual)

| Mẫu | Dùng khi | Cần có trong dữ liệu |
|---|---|---|
| `hook` | Câu mở đầu hoặc câu hỏi lớn | dòng chữ chính, chữ nhấn |
| `route` | Tuyến đường, số trạm, quãng đường | điểm đầu, điểm cuối, số trạm |
| `plan` | Mặt bằng nhà, đường đi trong nhà | danh sách phòng |
| `ledger` | Các khoản chi, giá cả | 1 đến 5 dòng nhãn và số, đơn vị |
| `compare` | Hai loại, hai lựa chọn | tên hai bên, 1 đến 4 ý mỗi bên |
| `day` | Một ngày chia 4 mốc | đúng 4 mốc |

Nếu cảnh cần hình mà **không có mẫu nào phù hợp**, ghi `MẪU MỚI` kèm mô tả và **không ép vào mẫu sai**. Cảnh chỉ có lời đọc nhẹ (chuyển ý, câu hỏi treo) có thể dùng lại `hook` với chữ ngắn.

**Đa dạng:** không dùng cùng một mẫu quá 3 cảnh liên tiếp, trừ khi dữ liệu thật sự giống nhau.

### Quy trình

1. Đọc toàn bộ danh sách cảnh.
2. Với mỗi cảnh: lấy `goi_y_hinh` làm gợi ý (không bắt buộc theo), rồi kiểm lời đọc có dữ kiện gì cần hiện.
3. Chọn mẫu, điền kế hoạch 5 phần, ghi mã nguồn.
4. Tạo báo cáo phân tích.

### Định dạng đầu ra

Ghi `motion\blueprint.json`:

```json
{
  "bao_cao": {"tong_canh": 0, "theo_mau": {"hook": 0, "route": 0}, "canh_can_mau_moi": []},
  "canh": [
    {
      "id": "S001",
      "narration": "(nguyên văn)",
      "mau": "route",
      "chu_the": "Vẽ dần tuyến đường từ A đến B, đếm số trạm lên 53. Điểm đầu: ..., điểm cuối: ...",
      "chuyen_dong": "Đường vẽ trong 5 giây, số đếm cùng lúc, nhân vật đi dọc đường",
      "bo_cuc": "Bản đồ trừu tượng toàn khung, số trạm ở góc dưới trái",
      "mau_sac": "Giấy be, đường đỏ, điểm đầu cuối chàm",
      "nguon": ["F15"]
    }
  ]
}
```

Báo cáo phân tích ở đầu tệp: tổng số cảnh, số cảnh theo mẫu, danh sách cảnh cần mẫu mới.

### Quy tắc giao hàng

- Chỉ ghi tệp và báo lại **một dòng**: tổng số cảnh, phân bố mẫu, số cảnh cần mẫu mới.
- Không sửa kịch bản. Nếu thấy lời đọc có dữ kiện không có trong `nguon.md`, **dừng và báo**, không tự thêm.
