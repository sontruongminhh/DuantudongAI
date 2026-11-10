"""Bộ công cụ điền mẫu hình kiểu điện ảnh (ban_do2, doi_dau, compare/ledger/day tông tối) cho script dien_mau.py của từng run.

Dùng:
    from studio.dien_mau_chung import Ve
    V = Ve(HERE, houses=HOUSES, portraits=A, wareki=WAREKI, timeline=[1491, 1590], marks=MARKS)
    V.show(1, 1491, "伊豆", {...}) ... V.vs(...) ... V.cmp_(...) ... V.led(...) ... V.day(...)
    V.finish(opening={"no": "すずめの勢力図帖", "title": "...", "sub": "..."})

- Khóa owners: "国" tô cả quốc, "国/郡" tô một quận (quận thời Minh Trị).
- houses: {tên: [màu, tên hiển thị, chữ huy hiệu, sọc?]}; portraits: {tên người: {file, x, y, z}} (ảnh ở motion/anh).
- Mã nguồn (nguon) của mỗi cảnh lấy từ các mã F.. trong gợi ý hình của beat. Cảnh đầu mỗi chương có thẻ chương.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

from . import mau_motion

TAG_MAP = "「郡地図 Ver 1.1」を加工して作成 ・ 色なしは諸勢力または不明"
TAG_SOFT = "「郡地図 Ver 1.1」を加工 ・ 斜線は勢力の届いた範囲(イメージ)"
TAG_IMG = "「郡地図 Ver 1.1」を加工 ・ 画像：Wikimedia Commons"
TAG_NUM = "数字は辞典やウィキペディアの記述。資料で違うことがあります"
TAG_VS = "数字は辞典やウィキペディア ・ 画像：Wikimedia Commons"


def P(*names):
    return [n + "国" for n in names]


def own(house, *provs):
    return {g: house for g in P(*provs)}


class Ve:
    def __init__(self, run_dir, houses, portraits, wareki, timeline, marks):
        self.dir = Path(run_dir)
        self.houses, self.A, self.wareki = houses, portraits, wareki
        self.timeline, self.marks = timeline, marks
        self.scenes = json.loads((self.dir / "motion" / "dong_loi.json").read_text("utf-8"))["canh"]
        self.counties = {}
        for f in json.loads((self.dir / "motion" / "ban_do" / "ban_do_map.json").read_text("utf-8")):
            self.counties.setdefault(f["g"], []).append(f["name"])
        self.chap = {sc["id"]: sc["chuong"].split(":", 1)[1].strip() for sc in self.scenes}
        self.first = {}
        for sc in self.scenes:
            self.first.setdefault(sc["chuong"], sc["id"])
        self.out = {}
        self.cur, self.focus = {}, None

    # ------------------------------------------------------------ tiện ích
    @staticmethod
    def sid(n):
        return f"S{n:03d}"

    def gun(self, house, prov, *names):
        g = prov + "国"
        names = names or self.counties[g]
        for n in names:
            assert n in self.counties[g], f"{g} không có {n}"
        return {f"{g}/{n}": house for n in names}

    def person(self, name, role):
        return {"name": name, "role": role, "anh": self.A[name]} if name in self.A else {"name": name, "role": role}

    def reset(self, owners=None, focus=None):
        self.cur, self.focus = dict(owners or {}), focus

    # ------------------------------------------------------------ bản đồ
    def show(self, n, year, label, owners, tag=TAG_MAP, hold=None, extra=None, reset=False, focus=None,
             note=None, who=None, chapter=None):
        base = {} if reset else dict(self.cur)
        snaps = [(year, label, owners)] if extra is None else extra
        names = []
        for o in [base] + [s[2] for s in snaps]:
            for h in o.values():
                if h not in names:
                    names.append(h)
        names.sort(key=list(self.houses).index)
        key = {h: f"h{i}" for i, h in enumerate(names)}
        if who and who[0] in self.A and tag == TAG_MAP:
            tag = TAG_IMG
        data = {"chapter": chapter or self.chap[self.sid(n)], "timeline": self.timeline, "marks": self.marks, "tag": tag,
                "palette": {key[h]: self.houses[h] for h in names},
                "snapshots": [{"year": y, "label": lab, "wareki": self.wareki.get(y, ""),
                               "owners": {g: key[h] for g, h in o.items()}} for y, lab, o in snaps]}
        if base:
            data["base"] = {g: key[h] for g, h in base.items()}
        if focus:
            data["focus"] = focus
        if (focus or None) != (self.focus or None):
            data["focus0"] = self.focus
        if note:
            data["note"] = {"title": note[0], "lines": list(note[1:])}
        if who:
            data["person"] = self.person(*who)
        if hold is None:
            hold = bool(base) and base == snaps[-1][2] and (focus or None) == (self.focus or None)
        self.out[self.sid(n)] = {"template": "ban_do2", "giu_hinh": hold, "data": data}
        self.cur, self.focus = dict(snaps[-1][2]), focus

    # ------------------------------------------------------------ đối đầu, thẻ, bảng, dòng thời gian
    def vs(self, first, last, title, sub, L, R, steps, stats=None):
        """L, R: (tên, vai, tên chân dung hoặc chữ huy hiệu, [các dòng], màu?). steps: số dòng hiện mỗi cảnh (trái, phải)."""
        prev = None
        for k, n in enumerate(range(first, last + 1)):
            nl, nr = steps[k]

            def side(d, c, color):
                o = {"name": d[0], "role": d[1], "items": d[3][:max(c, 1)], "color": color}
                if d[2] in self.A:
                    o["anh"] = self.A[d[2]]
                else:
                    o["badge"] = d[2]
                return o
            data = {"title": title, "sub": sub, "tag": TAG_VS, "left": side(L, nl, L[4] if len(L) > 4 else "#3f7fd9"),
                    "right": side(R, nr, R[4] if len(R) > 4 else "#d9463a")}
            if stats:
                data["stats"] = stats
            self.out[self.sid(n)] = {"template": "doi_dau", "giu_hinh": prev == (nl, nr), "data": data}
            prev = (nl, nr)

    def cmp_(self, first, last, title, sub, L, R, steps, tag=TAG_NUM):
        prev = None
        for k, n in enumerate(range(first, last + 1)):
            nl, nr = steps[k]
            side = lambda s, c: {"name": s[0], "ruby": s[1], "items": s[2][:max(c, 1)]}   # noqa: E731
            self.out[self.sid(n)] = {"template": "compare", "giu_hinh": prev == (nl, nr),
                                     "data": {"title": title, "sub": sub, "tag": tag, "toi": True,
                                              "left": side(L, nl), "right": side(R, nr)}}
            prev = (nl, nr)

    def led(self, first, last, title, sub, rows, steps, unit="万石", tag=TAG_NUM):
        prev = None
        for k, n in enumerate(range(first, last + 1)):
            c = steps[k]
            self.out[self.sid(n)] = {"template": "ledger", "giu_hinh": prev == c,
                                     "data": {"title": title, "sub": sub, "tag": tag, "unit": unit, "show_total": False,
                                              "toi": True, "total_label": "", "rows": [list(r) for r in rows[:c]]}}
            prev = c

    def day(self, first, last, title, sub, stops):
        for k, n in enumerate(range(first, last + 1)):
            self.out[self.sid(n)] = {"template": "day", "giu_hinh": k > 0,
                                     "data": {"title": title, "sub": sub, "tag": TAG_NUM, "chara": False, "toi": True,
                                              "stops": stops}}

    # ------------------------------------------------------------ thẻ chương và ghi canh.json
    def finish(self, opening):
        for chuong, first_id in self.first.items():
            head, name = chuong.split(":", 1)
            num = int(re.search(r"Chương (\d+)", head).group(1))
            card = opening if num == 1 else {"no": f"第{num}章", "title": name.strip()}
            self.out[first_id]["data"]["the_chuong"] = card
            self.out[first_id]["giu_hinh"] = False
        path = self.dir / "motion" / "canh.json"
        skel = json.loads(path.read_text("utf-8"))
        cues = {s["id"]: s["goi_y_hinh"][0] if s["goi_y_hinh"] else "" for s in self.scenes}
        ids = {s["id"] for s in skel["canh"]}
        missing = [s["id"] for s in skel["canh"] if s["id"] not in self.out]
        extra = [k for k in self.out if k not in ids]
        if missing or extra:
            sys.exit(f"thiếu cảnh: {missing}\ncảnh thừa: {extra}")
        problems = 0
        for sc in skel["canh"]:
            spec = self.out[sc["id"]]
            sc["template"], sc["data"], sc["giu_hinh"] = spec["template"], spec["data"], bool(spec["giu_hinh"])
            sc["nguon"] = sorted(set(re.findall(r"F\d+", cues[sc["id"]])))
            errs = mau_motion.check_scene(sc)
            if sc["template"] in mau_motion.NEEDS_SOURCE and not sc["nguon"]:
                errs.append("thiếu mã nguồn")
            for e in errs:
                problems += 1
                print(sc["id"], sc["template"], "-", e)
        if problems:
            sys.exit(f"{problems} lỗi, chưa ghi canh.json")
        path.write_text(json.dumps(skel, ensure_ascii=False, indent=1), "utf-8")
        print("đã ghi", len(skel["canh"]), "cảnh:", dict(Counter(s["template"] for s in skel["canh"])),
              "| giữ hình:", sum(1 for s in skel["canh"] if s["giu_hinh"]),
              "| thẻ chương:", sum(1 for s in skel["canh"] if s["data"].get("the_chuong")))
