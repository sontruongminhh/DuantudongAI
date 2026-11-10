"""Kiểm thử bộ đọc shapefile (tools/gunmap.py) và mẫu cảnh ban_do. Không cần PyYAML."""
import json
import math
import random
import struct
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))
import gunmap  # noqa: E402
from studio import mau_motion  # noqa: E402


def write_shp(path, polygons, fields=("ID", "NAME", "GRP"), rows=None, enc="utf-8"):
    """Ghi shapefile đa giác (mỗi phần tử polygons là danh sách vòng) và .dbf, .cpg để thử."""
    recs, boxes = b"", []
    for i, rings in enumerate(polygons, 1):
        pts = [p for r in rings for p in r]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        starts, n = [], 0
        for r in rings:
            starts.append(n)
            n += len(r)
        body = struct.pack("<i4d2i", 5, min(xs), min(ys), max(xs), max(ys), len(rings), n)
        body += struct.pack(f"<{len(rings)}i", *starts) + b"".join(struct.pack("<dd", *p) for p in pts)
        recs += struct.pack(">2i", i, len(body) // 2) + body
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    total = 100 + len(recs)
    allx = [b[0] for b in boxes] + [b[2] for b in boxes]
    ally = [b[1] for b in boxes] + [b[3] for b in boxes]
    head = struct.pack(">7i", 9994, 0, 0, 0, 0, 0, total // 2) + struct.pack("<2i8d", 1000, 5, min(allx), min(ally), max(allx), max(ally), 0, 0, 0, 0)
    Path(path).write_bytes(head + recs)
    rows = rows or [(str(i), f"郡{i}", "G1") for i in range(1, len(polygons) + 1)]
    size = 24
    rec_len = 1 + size * len(fields)
    hdr = struct.pack("<4B I H H 20x", 3, 126, 1, 1, len(rows), 33 + 32 * len(fields), rec_len)
    desc = b"".join(f.encode().ljust(11, b"\x00") + b"C" + b"\x00" * 4 + bytes([size, 0]) + b"\x00" * 14 for f in fields)
    data = b"".join(b" " + b"".join(str(v).encode(enc).ljust(size)[:size] for v in row) for row in rows)
    Path(path).with_suffix(".dbf").write_bytes(hdr + desc + b"\x0d" + data + b"\x1a")
    Path(path).with_suffix(".cpg").write_text("UTF-8" if enc == "utf-8" else "SHIFT_JIS", encoding="ascii")


def square(x, y, s=1.0):
    return [(x, y), (x, y + s), (x + s, y + s), (x + s, y), (x, y)]


def test_read_back_shapes_and_attributes(tmp_path):
    write_shp(tmp_path / "a.shp", [[square(130, 33)], [square(131, 33), square(133, 35, .5)]],
              rows=[("1", "福岡", "筑前"), ("2", "佐賀", "肥前")])
    shapes = gunmap.read_shp(tmp_path / "a.shp")
    rows, enc = gunmap.read_dbf(tmp_path / "a.dbf")
    assert [len(s) for s in shapes] == [1, 2] and shapes[0][0][0] == (130.0, 33.0)
    assert rows[1]["NAME"] == "佐賀" and rows[0]["GRP"] == "筑前" and enc.lower().replace("-", "") == "utf8"


def test_dbf_shift_jis_is_read(tmp_path):
    write_shp(tmp_path / "b.shp", [[square(130, 33)]], rows=[("1", "福岡", "筑前")], enc="cp932")
    rows, enc = gunmap.read_dbf(tmp_path / "b.dbf")
    assert rows[0]["NAME"] == "福岡" and enc.lower().startswith(("shift", "cp932", "sjis"))


def test_simplify_drops_collinear_points_only():
    line = [(0, 0), (1, 0.001), (2, 0), (3, 0.0005), (4, 0)]
    assert gunmap.simplify(line, 0.01) == [(0, 0), (4, 0)]
    bent = [(0, 0), (1, 1), (2, 0)]
    assert gunmap.simplify(bent, 0.1) == bent


def test_build_fits_box_and_keeps_group(tmp_path):
    write_shp(tmp_path / "c.shp", [[square(130, 33, 2)], [square(133, 35, 2)]],
              rows=[("1", "A郡", "甲"), ("2", "B郡", "乙")])
    b = gunmap.build(tmp_path / "c.shp", tmp_path / "c.dbf", "ID", "NAME", "GRP")
    assert [f["g"] for f in b["features"]] == ["甲", "乙"]
    nums = [float(v) for f in b["features"] for v in f["d"].replace("M", " ").replace("L", " ").replace("Z", " ").split()]
    assert 0 <= min(nums) and max(nums) <= max(b["w"], b["h"]) + 1


def test_bbox_drops_far_islands_and_refits(tmp_path):
    write_shp(tmp_path / "e.shp", [[square(130, 33)], [square(135, 35)], [square(128, 26)]],
              rows=[("1", "A", "甲"), ("2", "B", "乙"), ("3", "琉球", "丙")])
    full = gunmap.build(tmp_path / "e.shp", tmp_path / "e.dbf", "ID", "NAME", "GRP")
    cut = gunmap.build(tmp_path / "e.shp", tmp_path / "e.dbf", "ID", "NAME", "GRP", bbox=(129, 30, 146, 46))
    assert len(full["features"]) == 3 and [f["id"] for f in cut["features"]] == ["1", "2"]
    assert cut["features"][0]["d"] != full["features"][0]["d"]  # khung co lại nên tọa độ đổi


def test_merge_renames_groups(tmp_path):
    write_shp(tmp_path / "f.shp", [[square(130, 33)], [square(131, 33)]], rows=[("1", "A", "陸前国"), ("2", "B", "岩代国")])
    b = gunmap.build(tmp_path / "f.shp", tmp_path / "f.dbf", "ID", "NAME", "GRP", merge={"陸前国": "陸奥国", "岩代国": "陸奥国"})
    assert {f["g"] for f in b["features"]} == {"陸奥国"}


def test_ban_do_year_starts_at_first_snapshot():
    assert "yr.textContent=YEARS[0]" in mau_motion.build(scene())


def test_write_makes_js_and_index(tmp_path):
    write_shp(tmp_path / "d.shp", [[square(130, 33)]])
    path = gunmap.write(gunmap.build(tmp_path / "d.shp", tmp_path / "d.dbf", "ID", "NAME", "GRP"), tmp_path / "out")
    text = path.read_text("utf-8")
    assert text.startswith("window.BANDO=") and json.loads(text[len("window.BANDO="):-2])["features"]
    assert (tmp_path / "out" / "ban_do_map.json").is_file()


def test_not_a_shapefile_is_rejected(tmp_path):
    (tmp_path / "x.shp").write_bytes(b"x" * 200)
    with pytest.raises(ValueError):
        gunmap.read_shp(tmp_path / "x.shp")


GOOD = {"title": "戦国の勢力図", "sub": "応仁の乱から大坂の陣まで",
        "palette": {"oda": ["#c8432b", "織田"], "tok": ["#2f4b7c", "徳川"]},
        "snapshots": [{"year": 1560, "label": "桶狭間", "owners": {"A": "oda", "B": "tok"}},
                      {"year": 1600, "label": "関ヶ原", "owners": {"A": "tok", "B": "tok"}}]}


def scene(**over):
    data = json.loads(json.dumps(GOOD))
    data.update(over)
    return {"id": "S001", "template": "ban_do", "data": data}


def test_ban_do_good_scene_has_no_errors_and_builds():
    assert mau_motion.check_scene(scene()) == []
    page = mau_motion.build(scene())
    assert "ban_do_map.js" in page and "window.__timelines" in page and "1560" in page


def test_ban_do_rejects_bad_data():
    assert any("palette" in e for e in mau_motion.check_scene(scene(palette={})))
    assert any("snapshots" in e for e in mau_motion.check_scene(scene(snapshots=[])))
    s = scene()
    s["data"]["snapshots"][1]["year"] = 1500
    assert any("phải lớn hơn" in e for e in mau_motion.check_scene(s))
    s = scene()
    s["data"]["snapshots"][0]["owners"]["A"] = "mori"
    assert any("không có trong palette" in e for e in mau_motion.check_scene(s))


def test_ban_do_length_limits():
    s = scene()
    s["data"]["palette"]["oda"][1] = "織田信長一族"
    assert any("tối đa 4" in e for e in mau_motion.check_scene(s))
    s = scene()
    s["data"]["snapshots"][0]["label"] = "あ" * 13
    assert any("tối đa 12" in e for e in mau_motion.check_scene(s))


def test_ban_do_needs_source():
    assert "ban_do" in mau_motion.NEEDS_SOURCE


def test_ban_do_base_peak_and_empty_owners():
    s = scene(base={"A": "oda"}, peak=9)
    assert mau_motion.check_scene(s) == []
    page = mau_motion.build(s)
    assert 'BASE={"A": "oda"}' in page and "PEAK=9" in page and "HAS=Object.keys(BASE).length>0" in page
    assert mau_motion.check_scene(scene(snapshots=[{"year": 1560, "label": "x", "owners": {}}])) == []
    assert any("base" in e for e in mau_motion.check_scene(scene(base={"A": "mori"})))
    assert any("base" in e for e in mau_motion.check_scene(scene(base=[1])))


def test_ban_do_repaints_provinces_that_leave_the_map():
    assert "GRAY" in mau_motion.build(scene(base={"A": "oda"}))


def test_day_and_hook_without_mascot():
    stops = [["1", "あ"], ["2", "い"], ["3", "う"], ["4", "え"]]
    day = mau_motion.build({"id": "S001", "template": "day", "data": {"title": "t", "sub": "s", "stops": stops, "chara": False}})
    assert 'id="bird"' not in day and 'id="sun"' not in day and '"#sun"' not in day
    day = mau_motion.build({"id": "S001", "template": "day", "data": {"title": "t", "sub": "s", "stops": stops}})
    assert 'id="bird"' in day and 'id="sun"' in day
    hook = {"kicker": "k", "line1": "あ", "hl": "い", "line2": "う"}
    assert 'id="bird"' not in mau_motion.build({"id": "S001", "template": "hook", "data": {**hook, "chara": False}})
    assert 'id="bird"' in mau_motion.build({"id": "S001", "template": "hook", "data": hook})


def test_ledger_shows_decimals_only_on_rows_that_have_them():
    page = mau_motion.build({"id": "S001", "template": "ledger", "data": {
        "title": "t", "sub": "s", "total_label": "x", "show_total": False, "unit": "万石", "rows": [["a", 112], ["b", 29.8]]}})
    assert 'data-v="112" data-d="0"' in page and 'data-v="29.8" data-d="1"' in page


def test_keep_groups_and_clip_far_island_rings(tmp_path):
    # quận 1 có một đảo xa (vòng thứ hai); quận 2 thuộc nhóm khác
    write_shp(tmp_path / "k.shp", [[square(130, 33), square(129, 28, .3)], [square(132, 34)]],
              rows=[("1", "川辺郡", "薩摩国"), ("2", "大島郡", "周防国")])
    b = gunmap.build(tmp_path / "k.shp", tmp_path / "k.dbf", "ID", "NAME", "GRP", bbox=(128, 30, 133, 35),
                     keep={"薩摩国"}, clip_rings=True)
    assert [f["g"] for f in b["features"]] == ["薩摩国"]
    assert b["features"][0]["d"].count("M") == 1     # đảo ngoài khung bị bỏ, quận vẫn còn


def test_ban_do_county_keys_override_province_and_are_not_counted():
    s = scene(palette={"a": ["#c8432b", "島津"], "b": ["#e2826d", "諸県郡"]}, an_so=["b"],
              snapshots=[{"year": 1587, "label": "国分け", "owners": {"薩摩国": "a", "日向国/北諸県郡": "b"}}])
    assert mau_motion.check_scene(s) == []
    page = mau_motion.build(s)
    assert 'f.k in o?o[f.k]' in page and "CNT=[[1, 0]]" in page
    assert page.count('style="visibility:hidden"') == 2    # thanh và số của 諸県郡 bị ẩn


def test_ban_do_map_box():
    page = mau_motion.build(scene(map_box=[90, 148, 632, 560]))
    assert 'width="632" height="560" viewBox="0 0 700 620" style="left:90px;top:148px' in page
    assert any("map_box" in e for e in mau_motion.check_scene(scene(map_box=[1, 2])))


def test_compare_vs_pulse_starts_from_full_size():
    side = {"name": "甲", "ruby": "こう", "items": ["あ"]}
    page = mau_motion.build({"id": "S001", "template": "compare", "data": {"title": "t", "sub": "s", "left": side, "right": side}})
    assert 'tl.fromTo("#vs",{scale:1}' in page and "immediateRender:false" in page


def test_doi_dau_builds_with_portrait_badge_and_stats():
    L = {"name": "大友氏", "role": "豊後", "items": ["3万とも4万とも"], "anh": {"file": "otomo_sorin.jpg", "x": 45, "y": 18, "z": 2}}
    R = {"name": "島津氏", "role": "薩摩", "items": ["島津義久"], "badge": "島"}
    sc = {"id": "S001", "template": "doi_dau", "data": {"title": "耳川の戦い", "left": L, "right": R, "stats": [["兵", 40000, 30000, "3〜4万", "?"]]}}
    assert mau_motion.check_scene(sc) == []
    page = mau_motion.build(sc)
    assert "../assets/anh/otomo_sorin.jpg" in page and ">島</div>" in page and 'id="stats"' in page
    bad = {"id": "S001", "template": "doi_dau", "data": {"title": "t", "left": {"name": "x", "items": []}, "right": R}}
    assert mau_motion.check_scene(bad)


def test_chapter_overlay_dark_theme_and_person_card():
    rows = [["a", 1]]
    led = {"id": "S001", "template": "ledger", "data": {"title": "t", "sub": "s", "rows": rows, "total_label": "", "show_total": False,
                                                        "toi": True, "the_chuong": {"no": "第5章", "title": "耳川の戦い"}}}
    page = mau_motion.build(led)
    assert "--paper:#0e1830" in page and 'id="chap"' in page and "#e8dcc0" not in page
    held = dict(led, giu_hinh=True)
    assert 'id="chap"' not in mau_motion.build(held)
    p = scene(person={"name": "大友宗麟", "role": "豊後", "anh": {"file": "otomo_sorin.jpg"}}, chapter="t")
    p["template"] = "ban_do2"
    assert 'id="person"' in mau_motion.build(p)
