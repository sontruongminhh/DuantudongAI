"""Bộ trợ giúp điền motion/canh.json cho video kênh 4 (mẫu trong studio/mau_kigyo.py).

Dùng trong runs/<run>/dien_mau.py:

    from studio.dien_k4 import K4
    K = K4(HERE)                                   # đọc motion/dong_loi.json (sau tach-loi)
    K.c(1, "chuong", no="第1章", title="はじめに", years="1887年〜2007年")
    K.c((2, 4), "so_lon", year="1936年", label="売上高", num="2億6204", unit="万円", src="松尾(2017)")
    K.c(5, "anh", anh="kanebo_tokyo.jpg", caps=["鐘紡 東京工場", "明治時代"])      # src ảnh tự lấy từ credit.json
    K.finish()                                     # kiểm đủ cảnh, ghi motion/canh.json, in lỗi nếu có

- c(n hoặc (đầu, cuối), mẫu, **data, nguon=[...]): cảnh đầu chạy hoạt ảnh, các cảnh sau trong khoảng giữ hình cuối.
  Riêng mẫu "anh": các cảnh sau đổi hướng trôi (vao → trai → ra → phai) thay vì đứng yên.
- nguon: bỏ trống thì lấy các mã F.. trong gợi ý hình của beat.
- src của ảnh: bỏ trống thì tự ghi 「画像：tác giả／giấy phép」 từ motion/anh/credit.json.
"""
import json
import re
import sys
from pathlib import Path

from . import mau_motion

PANS = ["vao", "trai", "ra", "phai"]


def _short_license(lic):
    lic = (lic or "").strip()
    if lic.lower().startswith(("public domain", "pd")):
        return "パブリックドメイン"
    return lic or "?"


class K4:
    def __init__(self, run_dir):
        self.dir = Path(run_dir)
        self.scenes = json.loads((self.dir / "motion" / "dong_loi.json").read_text("utf-8"))["canh"]
        self.by_id = {sc["id"]: sc for sc in self.scenes}
        cred = self.dir / "motion" / "anh" / "credit.json"
        self.credit = {r["file"]: r for r in json.loads(cred.read_text("utf-8"))} if cred.is_file() else {}
        self.anh_co = {f.name for f in (self.dir / "motion" / "anh").iterdir()} if (self.dir / "motion" / "anh").is_dir() else set()
        self.out = {}

    @staticmethod
    def sid(n):
        return f"S{n:03d}"

    def img_src(self, f):
        r = self.credit.get(f)
        if not r:
            return "画像：Wikimedia Commons"
        a = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", r.get("author") or "")).strip()
        a = a if a and len(a) <= 24 else ("作者不明" if not a else a[:22] + "…")
        return f"画像：{a}／{_short_license(r.get('license'))}（Wikimedia Commons）"

    def c(self, n, template, nguon=None, **data):
        first, last = (n, n) if isinstance(n, int) else n
        for k in range(first, last + 1):
            sid = self.sid(k)
            if sid not in self.by_id:
                raise SystemExit(f"Không có cảnh {sid} (tổng {len(self.scenes)} cảnh)")
            if sid in self.out:
                raise SystemExit(f"Cảnh {sid} điền hai lần")
            sc = self.by_id[sid]
            d = dict(data)
            if template in ("anh", "chan_dung") and not d.get("src"):
                d["src"] = self.img_src(d["anh"])
            if template == "luoi_anh" and not d.get("src"):
                d["src"] = "画像：Wikimedia Commons（作者は概要欄）"
            hold = k > first
            if template == "anh" and hold:
                start = PANS.index(data.get("pan", "vao")) if data.get("pan", "vao") in PANS else 0
                d["pan"] = PANS[(start + k - first) % len(PANS)]
                d.pop("caps", None) if k - first >= 2 else None
                hold = False
            ids = nguon if nguon is not None else sorted(set(re.findall(r"F\d+", " ".join(sc.get("goi_y_hinh") or []))))
            self.out[sid] = {"id": sid, "chuong": sc["chuong"], "narration": sc["narration"], "template": template,
                             "giu_hinh": hold, "nguon": list(ids), "data": d}

    def finish(self):
        sys.stdout.reconfigure(encoding="utf-8")
        missing = [sc["id"] for sc in self.scenes if sc["id"] not in self.out]
        errors = []
        for sid, sc in self.out.items():
            errors += [f"{sid} ({sc['template']}): {e}" for e in mau_motion.check_scene(sc, self.anh_co)]
        canh = [self.out[sc["id"]] for sc in self.scenes if sc["id"] in self.out]
        (self.dir / "motion" / "canh.json").write_text(json.dumps({"canh": canh}, ensure_ascii=False, indent=1), "utf-8")
        kinds = {}
        for sc in canh:
            kinds[sc["template"]] = kinds.get(sc["template"], 0) + 1
        photo = sum(kinds.get(t, 0) for t in ("anh", "chan_dung", "luoi_anh"))
        print(f"Ghi {len(canh)}/{len(self.scenes)} cảnh. Ảnh {photo / max(len(canh), 1):.0%}. " +
              ", ".join(f"{k} {v}" for k, v in sorted(kinds.items(), key=lambda x: -x[1])))
        if missing:
            print("CHƯA ĐIỀN:", " ".join(missing))
        for e in errors:
            print("LỖI", e)
        return not missing and not errors
