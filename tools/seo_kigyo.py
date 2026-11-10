"""Điền publish/metadata.json cho video kênh 4 từ publish/seo.json + mốc chương thật + ghi tác giả ảnh.

  python tools/seo_kigyo.py runs/<run>

Cần: render/timeline.json (sau lệnh dung), scenes.json, motion/anh/credit.json, publish/seo.json, publish/metadata.json (tao-seo).
seo.json:
  {"tieu_de": "...", "mo_dau": ["câu đỉnh cao", "ところが…", "câu hỏi…"], "tai_lieu": ["・…", "・…"],
   "ky_uc": "カネボウの化粧品や…の思い出があれば、ぜひコメント欄で教えてください。",
   "hashtag": ["#カネボウ", "#鐘紡", ...], "the": ["カネボウ", ...], "ten_tep": "kanebo.mp4", "anh_them": ["thumb nền.jpg"]}
Mô tả theo khuôn: mở đầu → ▼目次 → ◼️ 主な参考資料 → ◼️ 画像 → ký ức → ◼️ 制作について → hashtag.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIC_ORDER = ["CC BY", "CC BY-SA"]


def fmt(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def chapters(run):
    t = json.loads((run / "render" / "timeline.json").read_text("utf-8"))
    scenes = {s["id"]: s for s in json.loads((run / "scenes.json").read_text("utf-8"))["canh"]}
    out, last = [], None
    for c in t["clips"]:
        ch = scenes[c["file"][:-4]]["chuong"]
        if ch != last:
            last = ch
            name = ch.split(": ", 1)[1] if ": " in ch else ch
            out.append((int(c["bat_dau"]), name))
    total = t["tong_thoi_luong"]
    keep = [x for i, x in enumerate(out) if (out[i + 1][0] if i + 1 < len(out) else total) - x[0] >= 10]
    if keep and keep[0][0] != 0:
        keep[0] = (0, keep[0][1])
    return [f"{fmt(s)} {n}" for s, n in keep]


def used_images(run, extra):
    used = set(extra)
    thumb = run / "publish" / "thumb.json"
    if thumb.is_file():
        t = json.loads(thumb.read_text("utf-8"))
        used |= {t.get("nen"), t.get("chan_dung")} - {None}
    # scenes.json không giữ data của mẫu, ảnh nằm trong motion/canh.json
    for sc in json.loads((run / "motion" / "canh.json").read_text("utf-8"))["canh"]:
        d = sc.get("data") or {}
        if d.get("anh"):
            used.add(d["anh"])
        for it in d.get("items") or []:
            if isinstance(it, list) and it and str(it[0]).lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                used.add(it[0])
    return used


def credits(run, used):
    rows = json.loads((run / "motion" / "anh" / "credit.json").read_text("utf-8"))
    by = {}
    for r in rows:
        if r["file"] not in used:
            continue
        lic = r.get("license", "")
        key = "CC BY-SA" if "SA" in lic.upper() else "CC BY" if lic.upper().startswith("CC BY") else None
        if key:
            a = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", r.get("author") or "")).strip() or "作者不明"
            # Ghi chú tiếng Việt lọt vào trường tác giả (video カネボウ: 「Monami (ảnh); tượng: …」)
            if re.search(r"[ăđơưẠ-ỹ]|[;(（]", a):
                print(f"CẢNH BÁO: tác giả của {r['file']} có vẻ không phải tên: {a}")
            by.setdefault(key, [])
            if a not in by[key]:
                by[key].append(a)
    lines = [f"・{k}：{'、'.join(by[k])}" for k in LIC_ORDER if by.get(k)]
    lines.append("・そのほかはパブリックドメイン・CC0。地図は Natural Earth")
    return lines


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run = Path(sys.argv[1]).resolve()
    seo = json.loads((run / "publish" / "seo.json").read_text("utf-8"))
    chs = chapters(run)
    desc = "\n".join([
        *seo["mo_dau"], "",
        "▼目次", *chs, "",
        "◼️ 主な参考資料", *seo["tai_lieu"], "",
        "◼️ 画像（Wikimedia Commons）", *credits(run, used_images(run, seo.get("anh_them", []))), "",
        seo["ky_uc"], "",
        "◼️ 制作について",
        "図とアニメーション、BGMは自作です。ナレーションは合成音声（AI）を使用しています。",
        "内容に誤りがあれば、コメントで教えてください。", "",
        " ".join(seo["hashtag"]),
    ])
    path = run / "publish" / "metadata.json"
    m = json.loads(path.read_text("utf-8"))
    m.update({"tieu_de": seo["tieu_de"], "mo_ta": desc, "the": seo["the"], "hashtag": seo["hashtag"], "ten_tep": seo["ten_tep"]})
    path.write_text(json.dumps(m, ensure_ascii=False, indent=1), "utf-8")
    print(f"tiêu đề {len(seo['tieu_de'])} ký tự | mô tả {len(desc.encode('utf-8'))} byte | {len(chs)} chương | {len(seo['the'])} thẻ")


if __name__ == "__main__":
    main()
