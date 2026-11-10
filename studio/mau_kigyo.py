"""Mẫu cảnh motion của kênh 4 (lịch sử công ty): ảnh tư liệu, số lớn, biểu đồ, niên biểu, bản đồ chấm điểm, trích dẫn.

Mỗi cảnh in dòng 出典 (data.src) ở góc trên trái. Chừa 120 px ở đáy cho dải phụ đề (dung.phu_de_kieu: dai_den).
Chữ trong data đã được mau_motion.build thoát ký tự HTML. Ảnh nằm ở assets/anh (sao từ motion/anh của lần chạy).
Đăng ký vào mau_motion.TEMPLATES ở cuối mau_motion.py.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

VENDOR = Path(__file__).resolve().parent.parent / "motion" / "vendor" / "ne"
AI, SHU, MUTED, NIGHT, GOLD = "#1f3a5f", "#b8412c", "#7d7566", "#141a24", "#c99a3c"
SAFE_H = 600            # vùng vẽ: 1280 x 600, phần dưới cho phụ đề

K4CSS = """<style>
#root{background:#f3eee3;color:#22252b}
#root div{text-wrap:balance;line-break:strict}
.kd{position:absolute;left:0;top:0;width:1280px;height:720px;background:#f3eee3}
.kd:after{content:"";position:absolute;inset:0;background-image:radial-gradient(#d6cdb9 1.2px,transparent 1.3px);background-size:28px 28px;opacity:.6}
.kn{position:absolute;left:0;top:0;width:1280px;height:720px;background:radial-gradient(circle at 50% 38%,#1d2738 0%,#141a24 70%)}
.ksrc{position:absolute;left:18px;top:12px;font-size:17px;color:#7d7566;z-index:40;padding:2px 8px;letter-spacing:.02em}
.ksrc.dk{color:#e4e6ea;background:rgba(8,10,16,.62);border-radius:2px}
.kkari{position:absolute;right:20px;top:12px;font-size:15px;color:#fff;background:#b8412c;padding:1px 10px;border-radius:2px;z-index:40}
.kc{background:#fffdf7;border:1px solid #ddd3bf;box-shadow:0 6px 18px rgba(40,30,10,.13);border-radius:4px}
.kh{font-family:"Noto Serif JP",serif;font-weight:900;color:#1f3a5f;letter-spacing:.02em}
.ks{font-family:"Noto Serif JP",serif}
.kt{position:absolute;left:84px;top:54px;font-size:42px}
.kt small{display:block;font-family:"Noto Sans JP",sans-serif;font-weight:400;font-size:22px;color:#7d7566;margin-top:6px}
</style>"""


def _src(s, dark=False):
    t = s.get("src", "")
    if not t:
        return ""
    if not t.startswith(("出典", "画像", "資料")):
        t = "出典：" + t
    kari = '<div class="kkari">試作・仮の数値</div>' if s.get("kari") else ""
    return f'<div class="ksrc{" dk" if dark else ""}">{t}</div>{kari}'


def _title(s):
    sub = f"<small>{s['sub']}</small>" if s.get("sub") else ""
    return f'<div class="abs kh kt" id="kt">{s["title"]}{sub}</div>' if s.get("title") else ""


TITLE_JS = 'if(document.querySelector("#kt"))tl.from("#kt",{opacity:0,y:-16,duration:.5,ease:"power2.out"},.15);\n'


def _img(file, x=50, y=40, bw=False, bright=1.0):
    f = "grayscale(1) contrast(1.05) " if bw else ""
    return (f'background:#222 url(../assets/anh/{file}) {x}% {y}%/cover no-repeat;filter:{f}brightness({bright})')


# ---------------------------------------------------------------- các mẫu

def chuong(s):
    body = f"""<div class="kd"></div>
<div class="abs" style="left:0;top:0;width:1280px;height:600px;display:flex;flex-direction:column;justify-content:center;padding-left:150px">
 <div id="no" style="font-size:30px;color:{SHU};font-weight:700;letter-spacing:.3em">{s['no']}</div>
 <div id="ln" style="width:130px;height:4px;background:{SHU};margin:14px 0 18px;transform-origin:left"></div>
 <div id="tt" class="kh" style="font-size:80px;line-height:1.15">{s['title']}</div>
 <div id="yr" style="font-size:30px;color:{MUTED};margin-top:18px">{s.get('years', '')}</div></div>"""
    js = """tl.from("#no",{opacity:0,x:-30,duration:.5},.15);tl.from("#ln",{scaleX:0,duration:.5},.35);
tl.from("#tt",{opacity:0,y:30,duration:.7,ease:"power3.out"},.5);tl.from("#yr",{opacity:0,duration:.6},1.1);"""
    return body, js


PAN = {"vao": ("scale:1.0", "scale:1.12"), "ra": ("scale:1.14", "scale:1.0"),
       "trai": ("scale:1.12,x:40", "scale:1.12,x:-40"), "phai": ("scale:1.12,x:-40", "scale:1.12,x:40")}


def anh(s):
    a, b = PAN.get(s.get("pan", "vao"), PAN["vao"])
    caps = "".join(
        f'<div class="kc cap" style="display:block;width:max-content;max-width:760px;margin-bottom:10px;padding:8px 18px;'
        f'font-size:{30 if i == 0 else 25}px;font-weight:{700 if i == 0 else 400};color:{AI if i == 0 else "#22252b"}">{c}</div>'
        for i, c in enumerate(s.get("caps") or []))
    pos = "left:48px;top:62px" if s.get("cap_vi_tri", "tren") == "tren" else "left:48px;top:420px"
    body = f"""<div class="abs" style="inset:0;background:#111"></div>
<div class="abs" id="pic" style="left:0;top:0;width:1280px;height:720px;{_img(s['anh'], s.get('x', 50), s.get('y', 40), s.get('bw', False), .86)}"></div>
<div class="abs" style="inset:0;background:linear-gradient(90deg,rgba(0,0,0,.42),transparent 55%)"></div>
{_src(s, True)}<div class="abs" style="{pos}">{caps}</div>"""
    js = (f'tl.fromTo("#pic",{{{a}}},{{{b},duration:10,ease:"none"}},0);\n'
          'tl.from(".cap",{opacity:0,x:-24,duration:.5,stagger:.35},.4);\n')
    return body, js


def chan_dung(s):
    body = f"""<div class="kd"></div>{_src(s)}
<div class="abs kc" id="card" style="left:140px;top:56px;width:380px;height:500px;padding:14px">
 <div id="pic" style="width:350px;height:470px;{_img(s['anh'], s.get('x', 50), s.get('y', 25), s.get('bw', True))}"></div></div>
<div class="abs" id="nm" style="left:600px;top:150px;width:620px">
 <div style="font-size:26px;color:{SHU};font-weight:700;letter-spacing:.1em">{s.get('role', '')}</div>
 <div class="kh" style="font-size:76px;margin-top:6px">{s['name']}</div>
 <div style="font-size:30px;color:{MUTED};margin-top:2px">{s.get('years', '')}</div></div>
<div class="abs" id="nt" style="left:604px;top:390px;width:600px;font-size:29px;line-height:1.6">{s.get('note', '')}</div>"""
    js = """tl.from("#card",{opacity:0,y:24,duration:.6},.1);tl.fromTo("#pic",{scale:1.0},{scale:1.06,duration:10,ease:"none"},0);
tl.from("#nm",{opacity:0,x:30,duration:.6},.6);tl.from("#nt",{opacity:0,duration:.6},1.3);"""
    return body, js


def so_lon(s):
    body = f"""<div class="kd"></div>{_src(s)}
<div class="abs" style="left:0;top:0;width:1280px;height:600px;display:flex;flex-direction:column;justify-content:center;padding-left:130px">
 <div id="yr" style="font-size:36px;font-weight:700;color:{AI}">{s.get('year', '')}</div>
 <div id="lb" style="font-size:42px;font-weight:700;margin-top:14px">{s['label']}</div>
 <div id="num" class="ks" style="font-size:156px;font-weight:900;color:{SHU};line-height:1.1;transform-origin:left center">{s['num']}<span style="font-size:66px;margin-left:10px">{s.get('unit', '')}</span></div>
 <div id="cmp" style="font-size:32px;color:{MUTED};margin-top:6px">{s.get('compare', '')}</div></div>"""
    js = """tl.from("#yr",{opacity:0,duration:.4},.1);tl.from("#lb",{opacity:0,y:20,duration:.5},.35);
tl.from("#num",{opacity:0,scale:.85,duration:.7,ease:"back.out(1.6)"},.75);tl.from("#cmp",{opacity:0,duration:.5},1.5);"""
    return body, js


def cot(s):
    bars_d = s["bars"]
    n = len(bars_d)
    mx = max(float(v) for _, v, _ in bars_d) or 1
    w = min(150, int(820 / n))
    gap = (980 - n * w) // (n + 1)
    hi = s.get("nhan", n - 1)
    top0 = 170 if s.get("sub") else 140
    hmax = 500 - top0 - 50
    bars = ""
    for i, (lab, v, txt) in enumerate(bars_d):
        h = max(4, int(hmax * float(v) / mx))
        x = 150 + gap + i * (w + gap)
        col = SHU if i == hi else "#93a1b6"
        bars += (f'<div class="abs bar" style="left:{x}px;top:{500 - h}px;width:{w}px;height:{h}px;background:{col};transform-origin:bottom"></div>'
                 f'<div class="abs bv" style="left:{x - 50}px;top:{456 - h}px;width:{w + 100}px;text-align:center;font-size:30px;font-weight:700;color:{SHU if i == hi else "#22252b"}">{txt}</div>'
                 f'<div class="abs" style="left:{x - 50}px;top:512px;width:{w + 100}px;text-align:center;font-size:25px">{lab}</div>')
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}
<div class="abs" style="left:150px;top:500px;width:980px;height:3px;background:#22252b"></div>{bars}"""
    js = TITLE_JS + """tl.from(".bar",{scaleY:0,duration:.7,stagger:.3,ease:"power2.out"},.4);tl.from(".bv",{opacity:0,duration:.4,stagger:.3},.9);"""
    return body, js


PIE_COLORS = [SHU, AI, GOLD, "#6f8f7a", "#93a1b6", "#b9ad95"]


def tron(s):
    parts = s["parts"]
    hi = s.get("nhan", 0)
    r, cx, cy, sw = 150, 380, 340, 70
    circ = 2 * math.pi * r
    arcs, legend, acc = "", "", 0.0
    for i, (lab, pct) in enumerate(parts):
        col = SHU if i == hi else PIE_COLORS[1 + i % (len(PIE_COLORS) - 1)]
        ln = circ * float(pct) / 100
        arcs += (f'<circle class="arc" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{sw}" '
                 f'stroke-dasharray="{ln:.1f} {circ:.1f}" stroke-dashoffset="{-acc:.1f}" transform="rotate(-90 {cx} {cy})"/>')
        acc += ln
        legend += (f'<div class="lg" style="display:flex;align-items:center;margin-bottom:22px"><i style="display:inline-block;width:26px;height:26px;'
                   f'background:{col};margin-right:16px;border-radius:3px"></i><span style="font-size:32px;font-weight:{700 if i == hi else 400}">{lab}</span>'
                   f'<span class="ks" style="font-size:40px;font-weight:900;margin-left:18px;color:{SHU if i == hi else "#22252b"}">{pct}%</span></div>')
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}
<svg class="abs" width="1280" height="720" style="left:0;top:0">{arcs}</svg>
<div class="abs" style="left:640px;top:{230 if len(parts) <= 3 else 190}px">{legend}</div>"""
    js = TITLE_JS + """tl.from(".arc",{opacity:0,duration:.5,stagger:.25},.4);tl.from(".lg",{opacity:0,x:24,duration:.45,stagger:.25},.6);"""
    return body, js


def danh_sach(s):
    hi = set(s.get("nhan") or [])
    items = "".join(
        f'<div class="kc it" style="display:flex;align-items:center;margin-bottom:18px;padding:14px 26px;width:max-content;max-width:1060px">'
        f'<i style="display:inline-block;width:14px;height:14px;background:{SHU if i in hi else AI};margin-right:20px;border-radius:2px"></i>'
        f'<span style="font-size:36px;font-weight:{700 if i in hi else 500};color:{SHU if i in hi else "#22252b"}">{t}</span></div>'
        for i, t in enumerate(s["items"]))
    top = 180 if s.get("sub") else 160
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}<div class="abs" style="left:110px;top:{top}px">{items}</div>"""
    js = TITLE_JS + """tl.from(".it",{opacity:0,x:-26,duration:.5,stagger:.45,ease:"power2.out"},.45);"""
    return body, js


def nien_bieu(s):
    stops = s["stops"]
    n = len(stops)
    hi = s.get("nhan", n - 1)
    x0, x1, y = 140, 1140, 330
    step = (x1 - x0) / (n - 1) if n > 1 else 0
    marks = ""
    for i, (yr, txt) in enumerate(stops):
        x = x0 + i * step
        col = SHU if i == hi else AI
        up = i % 2 == 0
        marks += (f'<div class="abs dot" style="left:{x - 13:.0f}px;top:{y - 13}px;width:26px;height:26px;border-radius:50%;background:{col};border:4px solid #f3eee3"></div>'
                  f'<div class="abs lab" style="left:{x - 110:.0f}px;top:{y - 150 if up else y + 34}px;width:220px;text-align:center">'
                  f'<div class="ks" style="font-size:34px;font-weight:900;color:{col}">{yr}</div>'
                  f'<div style="font-size:25px;line-height:1.35;margin-top:4px;font-weight:{700 if i == hi else 400}">{txt}</div></div>')
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}
<div class="abs" id="line" style="left:{x0}px;top:{y - 2}px;width:{x1 - x0}px;height:4px;background:#22252b;transform-origin:left"></div>{marks}"""
    js = TITLE_JS + """tl.from("#line",{scaleX:0,duration:.8,ease:"power2.inOut"},.3);
tl.from(".dot",{scale:0,duration:.35,stagger:.35,ease:"back.out(2)"},.7);tl.from(".lab",{opacity:0,y:10,duration:.4,stagger:.35},.8);"""
    return body, js


def so_sanh(s):
    def side(d, x, col, cls):
        items = "".join(f'<div class="{cls}" style="font-size:30px;line-height:1.5;margin-top:10px">・{t}</div>' for t in d["items"])
        return (f'<div class="abs kc" id="{cls}c" style="left:{x}px;top:170px;width:500px;min-height:250px;padding:28px 34px 34px;border-top:8px solid {col}">'
                f'<div class="kh" style="font-size:44px;color:{col}">{d["name"]}</div>'
                f'<div style="font-size:22px;color:{MUTED};margin-top:2px">{d.get("sub", "")}</div>{items}</div>')
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}
{side(s['left'], 110, AI, 'sl')}{side(s['right'], 670, SHU, 'sr')}"""
    js = TITLE_JS + """tl.from("#slc",{opacity:0,x:-40,duration:.6},.3);tl.from("#src",{opacity:0,x:40,duration:.6},.5);
tl.from(".sl",{opacity:0,duration:.4,stagger:.35},1.0);tl.from(".sr",{opacity:0,duration:.4,stagger:.35},1.2);"""
    return body, js


@lru_cache(maxsize=None)
def _geo(name):
    return json.loads((VENDOR / f"{name}.geojson").read_text(encoding="utf-8"))["features"]


VUNG = {   # tên: (tệp, lon trái, lon phải, lat trên, lat dưới)
    "nhat_ban": ("ne_50m_admin_0_countries", 128.5, 146.5, 45.8, 30.5),
    "dong_a": ("ne_50m_admin_0_countries", 98.0, 150.0, 47.0, 5.0),
    "the_gioi": ("ne_110m_admin_0_countries", -170.0, 190.0, 76.0, -56.0),
}
MAP_BOX = (40, 40, 1200, 540)     # vùng đặt bản đồ trong khung (trái, trên, rộng, cao)


@lru_cache(maxsize=None)
def _projection(vung):
    _, l, r, t, b = VUNG[vung]
    k = math.cos(math.radians((t + b) / 2))
    bx, by, bw, bh = MAP_BOX
    sc = min(bw / ((r - l) * k), bh / (t - b))
    ox = bx + (bw - (r - l) * k * sc) / 2
    oy = by + (bh - (t - b) * sc) / 2
    return l, t, k, sc, ox, oy


def _xy(vung, lon, lat):
    l, t, k, sc, ox, oy = _projection(vung)
    return ox + (lon - l) * k * sc, oy + (t - lat) * sc


def project(vung, lon, lat):
    """Kinh độ, vĩ độ → toạ độ px trong khung 1280x720."""
    if vung == "the_gioi" and lon < -170:
        lon += 360
    return _xy(vung, lon, lat)


@lru_cache(maxsize=None)
def map_paths(vung):
    """Đường viền các nước trong vùng: [(mã ISO, chuỗi path SVG)]."""
    fname, l, r, t, b = VUNG[vung]
    out = []
    for f in _geo(fname):
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        iso = f["properties"].get("ISO_A3") or f["properties"].get("ADM0_A3", "")
        if vung == "the_gioi" and iso == "ATA":
            continue
        d = []
        for poly in polys:
            for ring in poly:
                lons = [p[0] for p in ring]
                lats = [p[1] for p in ring]
                if vung == "the_gioi":   # vòng vắt qua kinh tuyến 180 hoặc nằm hẳn ở mép trái: dời sang phải để liền
                    if max(lons) - min(lons) > 180:
                        lons = [x + 360 if x < 0 else x for x in lons]
                    elif max(lons) < -170:
                        lons = [x + 360 for x in lons]
                elif max(lons) < l - 5 or min(lons) > r + 5 or max(lats) < b - 5 or min(lats) > t + 5:
                    continue
                pts, last = [], None
                for lon, lat in zip(lons, lats):
                    x, y = _xy(vung, lon, lat)
                    if last and abs(x - last[0]) + abs(y - last[1]) < 1.2:
                        continue
                    pts.append(f"{x:.1f},{y:.1f}")
                    last = (x, y)
                if len(pts) >= 3:
                    d.append("M" + "L".join(pts) + "Z")
        if d:
            out.append((iso, "".join(d)))
    return tuple(out)


def ban_do_diem(s):
    vung = s.get("vung", "nhat_ban")
    hi = s.get("nhan", 0)
    land = '<rect width="1280" height="720" fill="#dfe6e8"/>' + "".join(
        f'<path d="{d}" fill="{"#d8c9a6" if iso == "JPN" else "#efe9dc"}" stroke="{"#a8946a" if iso == "JPN" else "#c9bea6"}" stroke-width="1.2"/>'
        for iso, d in map_paths(vung))
    pts = ""
    for i, p in enumerate(s["points"]):
        name, lon, lat = p[0], float(p[1]), float(p[2])
        x, y = project(vung, lon, lat)
        col = SHU if i == hi else AI
        left = len(p) > 3 and p[3] == "trai"
        pts += (f'<div class="abs pt" style="left:{x - 11:.0f}px;top:{y - 11:.0f}px;width:22px;height:22px;border-radius:50%;background:{col};'
                f'border:3px solid #fffdf7;box-shadow:0 0 0 2px {col}55"></div>'
                f'<div class="abs kc pl" style="{"right:" + f"{1280 - x + 20:.0f}" if left else "left:" + f"{x + 20:.0f}"}px;top:{y - 22:.0f}px;padding:4px 14px;'
                f'font-size:26px;font-weight:700;white-space:nowrap;color:{col}">{name}</div>')
    body = f"""<div class="kd"></div>
<svg class="abs" id="map" width="1280" height="720" style="left:0;top:0">{land}</svg>
{_src(s)}{_title(s)}{pts}
<div class="abs" style="right:24px;top:{570}px;font-size:14px;color:{MUTED}">地図：Natural Earth</div>"""
    js = TITLE_JS + """tl.from("#map",{opacity:0,duration:.6},0);tl.from(".pt",{scale:0,duration:.35,stagger:.35,ease:"back.out(2.2)"},.6);
tl.from(".pl",{opacity:0,x:-10,duration:.35,stagger:.35},.75);"""
    return body, js


def luoi_anh(s):
    items = s["items"]
    n = len(items)
    cols, rows = n, 1        # một hàng: ảnh sản phẩm, chân dung đứng dọc
    top0 = 150 if s.get("title") else 70
    cw = (1120 - (cols - 1) * 24) // cols
    ch = 585 - top0
    cells = ""
    for i, it in enumerate(items):
        f, lab = it[0], it[1]
        c, r = i % cols, i // cols
        x, y = 80 + c * (cw + 24), top0 + r * (ch + 24)
        cells += (f'<div class="abs kc cell" style="left:{x}px;top:{y}px;width:{cw}px;height:{ch}px;padding:10px;overflow:hidden">'
                  f'<div style="width:{cw - 20}px;height:{ch - 64}px;{_img(f, 50, 45)}"></div>'
                  f'<div style="font-size:26px;font-weight:700;text-align:center;margin-top:8px;color:{AI}">{lab}</div></div>')
    body = f"""<div class="kd"></div>{_src(s)}{_title(s)}{cells}"""
    js = TITLE_JS + """tl.from(".cell",{opacity:0,y:24,duration:.5,stagger:.3,ease:"power2.out"},.3);"""
    return body, js


def bon_the(s):
    pos = [(140, 140), (800, 140), (140, 400), (800, 400)]
    cards = "".join(f'<div class="abs kc bt" style="left:{x}px;top:{y}px;width:340px;height:110px;display:flex;align-items:center;'
                    f'justify-content:center;font-size:32px;font-weight:700;color:{AI}">{t}</div>'
                    for (x, y), t in zip(pos, s["items"]))
    lines = "".join(f'<line class="ar" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{MUTED}" stroke-width="3" stroke-dasharray="8 7"/>'
                    for x1, y1, x2, y2 in ((480, 195, 560, 270), (800, 195, 720, 270), (480, 455, 560, 380), (800, 455, 720, 380)))
    body = f"""<div class="kd"></div>{_src(s)}
<svg class="abs" width="1280" height="720" style="left:0;top:0">{lines}</svg>
<div class="abs" id="ctr" style="left:520px;top:225px;width:240px;height:200px;border-radius:12px;background:{AI};color:#fff;display:flex;
 align-items:center;justify-content:center;text-align:center;font-family:'Noto Serif JP',serif;font-weight:900;font-size:40px;line-height:1.25;padding:10px">{s['center']}</div>{cards}"""
    js = """tl.from("#ctr",{scale:.6,opacity:0,duration:.6,ease:"back.out(1.8)"},.2);tl.from(".bt",{opacity:0,scale:.9,duration:.45,stagger:.3},.7);
tl.from(".ar",{opacity:0,duration:.4,stagger:.3},.9);"""
    return body, js


def trich_dan(s):
    cards = "".join(
        f'<div class="kc q" style="margin-bottom:16px;padding:14px 28px;width:max-content;max-width:1000px;'
        f'{"font-size:24px;color:" + MUTED if i == 0 else "font-size:38px;font-weight:700;font-family:Noto Serif JP,serif"}">{c}</div>'
        for i, c in enumerate(s["lines"]))
    body = f"""<div class="kn"></div>{_src(s, True)}
<div class="abs" style="left:0;top:0;width:1280px;height:600px;display:flex;flex-direction:column;justify-content:center;padding-left:150px">{cards}</div>"""
    js = """tl.from(".q",{opacity:0,y:18,duration:.55,stagger:.55,ease:"power2.out"},.3);"""
    return body, js


def cau_hoi(s):
    lines = "".join(f'<div class="ql" style="margin-bottom:10px">{t}</div>' for t in s["lines"])
    body = f"""<div class="kn"></div>{_src(s, True)}
<div class="abs ks" style="left:0;top:0;width:1280px;height:600px;display:flex;flex-direction:column;justify-content:center;align-items:center;
 text-align:center;color:#f4efe4;font-size:66px;font-weight:900;line-height:1.3">{lines}
 <div id="ul" style="width:160px;height:4px;background:{GOLD};margin-top:22px;transform-origin:center"></div></div>"""
    js = """tl.from(".ql",{opacity:0,y:26,duration:.7,stagger:.5,ease:"power3.out"},.3);tl.from("#ul",{scaleX:0,duration:.6},1.2);"""
    return body, js


TEMPLATES_K4 = {"chuong": chuong, "anh": anh, "chan_dung": chan_dung, "so_lon": so_lon, "cot": cot, "tron": tron,
                "danh_sach": danh_sach, "nien_bieu": nien_bieu, "so_sanh": so_sanh, "ban_do_diem": ban_do_diem,
                "luoi_anh": luoi_anh, "bon_the": bon_the, "trich_dan": trich_dan, "cau_hoi": cau_hoi}
SCHEMA_K4 = {
    "chuong": ("no", "title"), "anh": ("anh", "src"), "chan_dung": ("anh", "name", "src"),
    "so_lon": ("label", "num", "src"), "cot": ("title", "bars", "src"), "tron": ("title", "parts", "src"),
    "danh_sach": ("title", "items", "src"), "nien_bieu": ("title", "stops", "src"), "so_sanh": ("title", "left", "right", "src"),
    "ban_do_diem": ("points", "src"), "luoi_anh": ("items", "src"), "bon_the": ("center", "items", "src"),
    "trich_dan": ("lines", "src"), "cau_hoi": ("lines",),
}
# Mẫu mang số liệu hoặc dữ kiện: phải có mã F trong nguon
NEEDS_SOURCE_K4 = {"so_lon", "cot", "tron", "danh_sach", "nien_bieu", "so_sanh", "ban_do_diem", "trich_dan", "chan_dung"}


def wlen(text):
    return sum(0.55 if ord(c) < 128 else 1.0 for c in str(text))


def _too_long(label, text, limit):
    return [f"{label} \"{text}\" dài {wlen(text):.1f} ký tự, tối đa {limit}"] if wlen(text) > limit else []


def check_k4(t, d, anh_co=None):
    """Lỗi dữ liệu riêng của mẫu kênh 4. anh_co: tập tên ảnh có trong motion/anh (None thì không kiểm)."""
    e = []
    e += _too_long("src", d.get("src", ""), 64)
    files = []
    if t == "chuong":
        e += _too_long("title", d["title"], 13)
    if t == "anh":
        files.append(d["anh"])
        caps = d.get("caps") or []
        if len(caps) > 3:
            e.append("caps tối đa 3 dòng")
        for c in caps:
            e += _too_long("caps", c, 24)
        if d.get("pan", "vao") not in PAN:
            e.append(f"pan phải là một trong {', '.join(PAN)}")
    if t == "chan_dung":
        files.append(d["anh"])
        e += _too_long("name", d["name"], 8) + _too_long("role", d.get("role", ""), 22) + _too_long("note", d.get("note", ""), 40)
    if t == "so_lon":
        e += _too_long("num+unit", str(d["num"]) + d.get("unit", ""), 9) + _too_long("label", d["label"], 22)
        e += _too_long("compare", d.get("compare", ""), 34)
    if t == "cot":
        b = d["bars"]
        if not (isinstance(b, list) and 2 <= len(b) <= 6 and all(isinstance(x, list) and len(x) == 3 and isinstance(x[1], (int, float)) and x[1] >= 0 for x in b)):
            e.append("bars phải có 2 đến 6 mục [nhãn, số không âm, chữ hiện trên cột]")
        else:
            for lab, _, txt in b:
                e += _too_long("nhãn cột", lab, 8 if len(b) <= 4 else 6) + _too_long("chữ trên cột", txt, 9 if len(b) <= 4 else 6)
    if t == "tron":
        p = d["parts"]
        if not (isinstance(p, list) and 2 <= len(p) <= 5 and all(isinstance(x, list) and len(x) == 2 and isinstance(x[1], (int, float)) for x in p)):
            e.append("parts phải có 2 đến 5 mục [nhãn, phần trăm]")
        elif abs(sum(x[1] for x in p) - 100) > 1.5:
            e.append(f"parts cộng lại {sum(x[1] for x in p):g}%, phải khoảng 100%")
        else:
            for lab, _ in p:
                e += _too_long("nhãn", lab, 9)
    if t == "danh_sach":
        it = d["items"]
        if not 2 <= len(it) <= 5:
            e.append("items phải có 2 đến 5 ý")
        for x in it:
            e += _too_long("ý", x, 26)
    if t == "nien_bieu":
        st = d["stops"]
        if not (isinstance(st, list) and 3 <= len(st) <= 6 and all(isinstance(x, list) and len(x) == 2 for x in st)):
            e.append("stops phải có 3 đến 6 mục [năm, việc]")
        else:
            for yr, txt in st:
                e += _too_long("năm", yr, 7) + _too_long("việc", txt, 16)
    if t == "so_sanh":
        for k in ("left", "right"):
            sd = d[k]
            if not (isinstance(sd, dict) and sd.get("name") and 1 <= len(sd.get("items") or []) <= 4):
                e.append(f"{k} cần name và 1 đến 4 ý")
                continue
            e += _too_long(f"{k}.name", sd["name"], 10) + sum((_too_long(f"{k}: ý", x, 14) for x in sd["items"]), [])
    if t == "ban_do_diem":
        if d.get("vung", "nhat_ban") not in VUNG:
            e.append(f"vung phải là một trong {', '.join(VUNG)}")
        pts = d["points"]
        if not (isinstance(pts, list) and 1 <= len(pts) <= 6 and all(isinstance(p, list) and len(p) >= 3 and isinstance(p[1], (int, float)) and isinstance(p[2], (int, float)) for p in pts)):
            e.append("points phải có 1 đến 6 mục [tên, kinh độ, vĩ độ]")
        else:
            for p in pts:
                e += _too_long("địa điểm", p[0], 10)
                _, l, r, tp, bt = VUNG.get(d.get("vung", "nhat_ban"), VUNG["nhat_ban"])
                if not (l <= p[1] + (360 if p[1] < -170 else 0) <= r and bt <= p[2] <= tp):
                    e.append(f"{p[0]} ({p[1]}, {p[2]}) nằm ngoài vùng bản đồ")
    if t == "luoi_anh":
        it = d["items"]
        if not (isinstance(it, list) and 2 <= len(it) <= 4 and all(isinstance(x, list) and len(x) == 2 for x in it)):
            e.append("items phải có 2 đến 4 mục [tên ảnh, nhãn]")
        else:
            files += [x[0] for x in it]
            e += sum((_too_long("nhãn", x[1], 12 if len(it) <= 2 else 10) for x in it), [])
    if t == "bon_the":
        if len(d["items"]) != 4:
            e.append("items phải có đúng 4 thẻ")
        e += sum((_too_long("thẻ", x, 9) for x in d["items"]), []) + _too_long("center", d["center"], 10)
    if t == "trich_dan":
        ln = d["lines"]
        if not 2 <= len(ln) <= 4:
            e.append("lines phải có 2 đến 4 dòng (dòng đầu là tên tài liệu)")
        e += _too_long("tên tài liệu", ln[0], 40) + sum((_too_long("câu trích", x, 24) for x in ln[1:]), [])
    if t == "cau_hoi":
        if not 1 <= len(d["lines"]) <= 3:
            e.append("lines phải có 1 đến 3 dòng")
        e += sum((_too_long("dòng", x, 16) for x in d["lines"]), [])
    if anh_co is not None:
        e += [f"không có ảnh {f} trong motion/anh" for f in files if f not in anh_co]
    return e
