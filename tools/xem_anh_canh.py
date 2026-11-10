"""Liệt kê các cảnh dùng ảnh cùng lời đọc của cảnh, để soát ảnh có khớp lời không (trước khi render).

  python tools/xem_anh_canh.py runs/<run>

Video カネボウ: 6 cảnh ảnh không khớp lời (tờ quảng cáo 1903 đặt cạnh đoạn về nhà máy 1918, ảnh phố không rõ biển hiệu).
"""
import json
import sys
from pathlib import Path


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run = Path(sys.argv[1])
    cred = {r["file"]: r for r in json.loads((run / "motion" / "anh" / "credit.json").read_text("utf-8"))}
    last = None
    for sc in json.loads((run / "motion" / "canh.json").read_text("utf-8"))["canh"]:
        d = sc["data"]
        files = [d["anh"]] if d.get("anh") else [it[0] for it in d.get("items") or [] if isinstance(it, list)]
        if not files or sc["template"] not in ("anh", "chan_dung", "luoi_anh"):
            continue
        key = (sc["template"], tuple(files))
        if key != last:
            print(f"\n{sc['id']} {sc['template']}: {', '.join(files)}")
            for f in files:
                print(f"   ảnh: {(cred.get(f) or {}).get('mo_ta', '')[:90]}")
            cap = d.get("caps") or [d.get("name", ""), d.get("note", "")]
            print(f"   chữ trên hình: {' / '.join(c for c in cap if c)}")
        last = key
        print(f"   {sc['id']} lời: {sc['narration'][:70]}")


if __name__ == "__main__":
    main()
