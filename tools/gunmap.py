"""Đọc shapefile ranh giới (郡地図) bằng Python thuần, đơn giản hóa và xuất ra tệp JS cho mẫu cảnh ban_do.

  python tools/gunmap.py <tệp.shp> <thư_mục_ra> [--id TRƯỜNG] [--ten TRƯỜNG] [--nhom TRƯỜNG] [--dung-sai 0.02] [--khung TÂY NAM ĐÔNG BẮC] [--gop CU=MOI ...]

Không cần thư viện ngoài. Đọc .shp (đa giác) và .dbf cạnh nó. Tọa độ giả định là kinh độ, vĩ độ (độ).
Tệp ra: ban_do_map.js (window.BANDO) và ban_do_map.json (danh sách trường để đối chiếu).
"""
import argparse
import json
import math
import struct
import sys
from pathlib import Path

BOX_W, BOX_H = 700, 620


def read_dbf(path, encoding=None):
    """Danh sách bản ghi (dict) của tệp .dbf. Tự chọn mã hóa: .cpg cạnh tệp, rồi utf-8, rồi cp932."""
    path = Path(path)
    raw = path.read_bytes()
    n_rec, head_len, rec_len = struct.unpack("<xxxxIHH", raw[:12])
    fields, pos = [], 32
    while raw[pos] != 0x0D:
        name = raw[pos:pos + 11].split(b"\x00")[0].decode("ascii", "replace")
        fields.append((name, chr(raw[pos + 11]), raw[pos + 16]))
        pos += 32
    encs = [encoding] if encoding else []
    cpg = path.with_suffix(".cpg")
    if cpg.is_file():
        encs.append(cpg.read_text("ascii", "ignore").strip() or "utf-8")
    encs += ["utf-8", "cp932"]
    for enc in encs:
        try:
            return _records(raw, head_len, rec_len, n_rec, fields, enc), enc
        except (UnicodeDecodeError, LookupError):
            continue
    raise ValueError("Không đọc được mã hóa của " + path.name)


def _records(raw, head_len, rec_len, n_rec, fields, enc):
    out = []
    for i in range(n_rec):
        rec = raw[head_len + i * rec_len: head_len + (i + 1) * rec_len]
        if not rec or rec[0:1] == b"*":
            out.append(None)
            continue
        row, off = {}, 1
        for name, _kind, size in fields:
            row[name] = rec[off:off + size].decode(enc).strip()
            off += size
        out.append(row)
    return out


def read_shp(path):
    """Mỗi bản ghi là danh sách vòng (ring); vòng là danh sách (x, y). Bản ghi rỗng là []."""
    raw = Path(path).read_bytes()
    if struct.unpack(">i", raw[:4])[0] != 9994:
        raise ValueError("Không phải tệp shapefile")
    pos, out = 100, []
    while pos + 8 <= len(raw):
        _num, words = struct.unpack(">ii", raw[pos:pos + 8])
        body = raw[pos + 8: pos + 8 + words * 2]
        pos += 8 + words * 2
        kind = struct.unpack("<i", body[:4])[0]
        if kind == 0:
            out.append([])
            continue
        if kind not in (5, 15, 25):
            raise ValueError(f"Loại hình {kind} chưa hỗ trợ (cần đa giác)")
        n_parts, n_pts = struct.unpack("<ii", body[36:44])
        parts = list(struct.unpack(f"<{n_parts}i", body[44:44 + 4 * n_parts]))
        base = 44 + 4 * n_parts
        pts = [struct.unpack("<dd", body[base + 16 * k: base + 16 * k + 16]) for k in range(n_pts)]
        parts.append(n_pts)
        out.append([pts[parts[k]:parts[k + 1]] for k in range(n_parts)])
    return out


def simplify(points, tol):
    """Douglas-Peucker không đệ quy. tol cùng đơn vị với tọa độ."""
    if len(points) < 4 or tol <= 0:
        return list(points)
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        (ax, ay), (bx, by) = points[a], points[b]
        dx, dy = bx - ax, by - ay
        norm = math.hypot(dx, dy)
        best, idx = -1.0, -1
        for i in range(a + 1, b):
            px, py = points[i]
            d = abs(dy * (px - ax) - dx * (py - ay)) / norm if norm else math.hypot(px - ax, py - ay)
            if d > best:
                best, idx = d, i
        if best > tol:
            keep[idx] = True
            stack += [(a, idx), (idx, b)]
    return [p for p, k in zip(points, keep) if k]


def _inside(rings, bbox):
    pts = [p for r in rings for p in r]
    cx, cy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
    return bbox[0] <= cx <= bbox[2] and bbox[1] <= cy <= bbox[3]


def build(shp, dbf, id_field=None, name_field=None, group_field=None, tol=0.02, box=(BOX_W, BOX_H), bbox=None, merge=None,
          keep=None, clip_rings=False):
    """Trả về dict BANDO: kích thước hộp, danh sách feature {id, name, g, d}.

    bbox = (kinh_tây, vĩ_nam, kinh_đông, vĩ_bắc): bỏ hình có tâm nằm ngoài khung (đảo xa), và khung bản đồ co theo phần còn lại.
    clip_rings: với bbox, bỏ từng vòng (đảo) có tâm ngoài khung, thay vì giữ hay bỏ cả hình. Dùng khi một quận có chuỗi đảo xa.
    keep = tập tên nhóm (sau khi gộp): chỉ giữ các nhóm này, ví dụ chỉ các quốc Cửu Châu. Khung bản đồ co theo phần giữ lại.
    """
    shapes = read_shp(shp)
    rows, enc = read_dbf(dbf)
    if len(rows) != len(shapes):
        raise ValueError(f"Số hình ({len(shapes)}) khác số bản ghi thuộc tính ({len(rows)})")
    if bbox and clip_rings:
        shapes = [[r for r in s if r and _inside([r], bbox)] if s else [] for s in shapes]
    elif bbox:
        shapes = [s if s and _inside(s, bbox) else [] for s in shapes]
    if keep and group_field:
        grp = lambda r: (merge or {}).get(r.get(group_field, ""), r.get(group_field, "")) if r else None
        shapes = [s if grp(r) in keep else [] for s, r in zip(shapes, rows)]
    xs = [x for rings in shapes for ring in rings for x, _ in ring]
    ys = [y for rings in shapes for ring in rings for _, y in ring]
    if not xs:
        raise ValueError("Không có hình nào")
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    k = math.cos(math.radians((y0 + y1) / 2))          # co kinh độ theo vĩ độ giữa
    scale = min(box[0] / ((x1 - x0) * k), box[1] / (y1 - y0))
    ox = (box[0] - (x1 - x0) * k * scale) / 2
    oy = (box[1] - (y1 - y0) * scale) / 2
    feats = []
    for n, (rings, row) in enumerate(zip(shapes, rows)):
        if not rings or row is None:
            continue
        parts = []
        for ring in rings:
            pts = simplify(ring, tol)
            if len(pts) < 4:
                continue
            xy = [(ox + (x - x0) * k * scale, oy + (y1 - y) * scale) for x, y in pts]
            parts.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in xy) + "Z")
        if parts:
            feats.append({"id": row.get(id_field) or str(n), "name": row.get(name_field, "") if name_field else "",
                          "g": (merge or {}).get(row.get(group_field, ""), row.get(group_field, "")) if group_field else "", "d": "".join(parts)})
    return {"w": box[0], "h": box[1], "features": feats, "encoding": enc}


def write(bando, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    text = json.dumps(bando, ensure_ascii=False, separators=(",", ":"))
    (out_dir / "ban_do_map.js").write_text("window.BANDO=" + text + ";\n", encoding="utf-8")
    index = [{k: f[k] for k in ("id", "name", "g")} for f in bando["features"]]
    (out_dir / "ban_do_map.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    return out_dir / "ban_do_map.js"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("shp")
    ap.add_argument("out")
    ap.add_argument("--id")
    ap.add_argument("--ten")
    ap.add_argument("--nhom")
    ap.add_argument("--khung", nargs=4, type=float, metavar=("TÂY", "NAM", "ĐÔNG", "BẮC"), help="bỏ hình có tâm ngoài khung (độ)")
    ap.add_argument("--gop", nargs="*", default=[], metavar="CU=MOI", help="gộp nhóm, ví dụ 陸前国=陸奥国")
    ap.add_argument("--cat-dao", action="store_true", help="với --khung: bỏ từng đảo ngoài khung, không bỏ cả quận")
    ap.add_argument("--chi-nhom", nargs="*", default=None, metavar="NHOM", help="chỉ giữ các nhóm này, ví dụ 筑前国 筑後国 ...")
    ap.add_argument("--dung-sai", type=float, default=0.02, help="độ (kinh/vĩ), 0,02 độ là khoảng 2 km")
    a = ap.parse_args()
    shp = Path(a.shp)
    bando = build(shp, shp.with_suffix(".dbf"), a.id, a.ten, a.nhom, a.dung_sai, bbox=a.khung, merge=dict(x.split("=", 1) for x in a.gop),
                  keep=set(a.chi_nhom) if a.chi_nhom else None, clip_rings=a.cat_dao)
    path = write(bando, a.out)
    pts = sum(f["d"].count("L") for f in bando["features"])
    print(f"{len(bando['features'])} hình, {pts} điểm, mã hóa {bando['encoding']}, tệp {path.stat().st_size / 1e6:.2f} MB → {path}")


if __name__ == "__main__":
    main()
