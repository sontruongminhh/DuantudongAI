"""Mẫu cảnh motion 10 giây: dữ liệu cảnh → trang HTML cho HyperFrames. Không in phụ đề vào clip."""
import html
import copy
import json
W, H, FPS, DUR = 1280, 720, 24, 10

CSS = """
:root{--paper:#f6ecd8;--ink:#2a2018;--red:#c8432b;--indigo:#2f4b7c;--gold:#d99a1e;--sage:#5f8a62;--muted:#8a7a62;
--font:"Noto Sans JP",sans-serif}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:1280px;height:720px;overflow:hidden;background:var(--paper)}
#root{position:relative;width:1280px;height:720px;font-family:var(--font);color:var(--ink);background:var(--paper)}
.stage{position:absolute;left:0;top:0;width:1280px;height:720px}
.abs{position:absolute}
.band{position:absolute;left:0;top:0;width:1280px;height:14px;background:var(--red)}
.tag{position:absolute;right:28px;bottom:20px;font-size:17px;color:var(--muted);letter-spacing:.04em}
.title{position:absolute;left:64px;top:42px;font-size:46px;font-weight:700;letter-spacing:.02em}
.title small{display:block;font-size:20px;color:var(--muted);font-weight:400;margin-top:4px}
.hl{color:var(--red)}
svg text{font-family:var(--font)}
"""

BIRD = """
<svg class="abs" id="__ID__" width="__S__" height="__S__" viewBox="0 0 120 120" style="left:__X__px;top:__Y__px">
  <g stroke="#2a2018" stroke-width="3" stroke-linejoin="round" stroke-linecap="round">
    <line x1="50" y1="106" x2="48" y2="117" stroke="#e8a33d"/><line x1="70" y1="106" x2="72" y2="117" stroke="#e8a33d"/>
    <circle cx="60" cy="74" r="36" fill="#c9a27a"/>
    <ellipse cx="60" cy="86" rx="23" ry="20" fill="#f3e6cf" stroke="none"/>
    <path d="M26 78 Q14 96 40 100 Q36 88 40 76 Z" fill="#a9825a"/>
    <polygon points="92,66 108,72 92,78" fill="#e8a33d"/>
    <path d="M28 40 Q60 4 92 40 Z" fill="#e4c78a"/>
    <ellipse cx="60" cy="40" rx="46" ry="11" fill="#d9b772"/>
    <path d="M44 48 Q60 66 76 48" fill="none" stroke="#a23b27" stroke-width="2.5"/>
  </g>
  <circle cx="72" cy="66" r="4.5" fill="#2a2018"/><circle cx="73.5" cy="64.5" r="1.4" fill="#fff"/>
  <circle cx="50" cy="76" r="6" fill="#f0a38a" opacity=".8"/>
</svg>
"""


def bird(ident, x, y, size=120):
    return (BIRD.replace("__ID__", ident).replace("__S__", str(size)).replace("__X__", str(x)).replace("__Y__", str(y)))


def hook(s):
    body = f"""
<div class="band"></div>
<div class="abs" id="kicker" style="left:96px;top:130px;font-size:30px;color:var(--indigo);font-weight:700;letter-spacing:.12em">{s['kicker']}</div>
<h1 class="abs" id="q" style="left:96px;top:200px;font-size:84px;line-height:1.25;font-weight:900">
  <span class="ln">{s['line1']}</span><br><span class="ln"><span class="hl" id="hl">{s['hl']}</span>{s['line2']}</span></h1>
<div class="abs" id="ul" style="left:96px;top:432px;width:250px;height:10px;background:var(--red);transform-origin:left"></div>
{bird('bird', 930, 360, 260) if s.get('chara', True) else ''}
<div class="tag">{s.get('tag', '')}</div>"""
    js = """
tl.from("#kicker",{opacity:0,x:-40,duration:.6,ease:"power3.out"},.3);
tl.from(".ln",{opacity:0,y:50,duration:.7,stagger:.35,ease:"power3.out"},.7);
tl.from("#ul",{scaleX:0,duration:.6,ease:"power2.out"},1.7);
"""
    if s.get("chara", True):   # chara: false khi kênh chưa có nhân vật đại diện
        js += """tl.from("#bird",{x:420,opacity:0,duration:1,ease:"back.out(1.6)"},1.2);
tl.to("#bird",{y:-22,duration:.55,yoyo:true,repeat:13,ease:"sine.inOut"},2.4);
"""
    return body, js


def route(s):
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
<svg class="abs" id="map" width="1280" height="720" viewBox="0 0 1280 720" style="left:0;top:0">
  <path id="road" d="M150 560 C300 450,360 640,540 520 S780 330,900 430 S1060 210,1140 250" fill="none" stroke="#d9c9a5" stroke-width="16" stroke-linecap="round"/>
  <path id="road2" d="M150 560 C300 450,360 640,540 520 S780 330,900 430 S1060 210,1140 250" fill="none" stroke="var(--red)" stroke-width="6" stroke-linecap="round" stroke-dasharray="1 0"/>
  <g id="dots"></g>
  <g id="a"><circle cx="150" cy="560" r="16" fill="var(--indigo)"/><text x="150" y="612" font-size="30" font-weight="700" text-anchor="middle">{s['from']}</text></g>
  <g id="b"><circle cx="1140" cy="250" r="16" fill="var(--indigo)"/><text x="1140" y="206" font-size="30" font-weight="700" text-anchor="middle">{s['to']}</text></g>
</svg>
<div class="abs" style="left:64px;top:600px;font-size:34px;font-weight:700">{s['count_label']}<span id="cnt" class="hl" style="font-size:72px;margin-left:14px;font-weight:900">0</span></div>
{bird('bird', 0, 0, 90)}
<div class="tag">{s.get('tag', '')}</div>"""
    js = f"""
const road=document.getElementById("road2"),len=road.getTotalLength(),N={s['count']};
road.setAttribute("stroke-dasharray",len+" "+len);road.setAttribute("stroke-dashoffset",len);
const dots=document.getElementById("dots"),ns="http://www.w3.org/2000/svg";
for(let i=0;i<N;i++){{const p=road.getPointAtLength(len*i/(N-1));const c=document.createElementNS(ns,"circle");
 c.setAttribute("cx",p.x);c.setAttribute("cy",p.y);c.setAttribute("r",5.5);c.setAttribute("fill","#fff");c.setAttribute("stroke","#2a2018");c.setAttribute("stroke-width",2);
 c.setAttribute("class","dot");dots.appendChild(c);}}
tl.from("#a",{{scale:0,transformOrigin:"150px 560px",duration:.5,ease:"back.out(2)"}},.4);
tl.to(road,{{strokeDashoffset:0,duration:5,ease:"power1.inOut"}},1);
tl.from(".dot",{{scale:0,transformOrigin:"center",duration:.2,stagger:5/N,ease:"back.out(3)"}},1);
const o={{n:0}};tl.to(o,{{n:N,duration:5,ease:"power1.inOut",onUpdate:()=>{{document.getElementById("cnt").textContent=Math.round(o.n)}}}},1);
tl.from("#b",{{scale:0,transformOrigin:"1140px 250px",duration:.5,ease:"back.out(2)"}},5.7);
const b=document.getElementById("bird"),pt={{x:0}};
tl.to(pt,{{x:1,duration:5,ease:"power1.inOut",onUpdate:()=>{{const p=road.getPointAtLength(len*pt.x);gsap.set(b,{{x:p.x-45,y:p.y-100}})}}}},1);
tl.from("#bird",{{opacity:0,duration:.3}},1);
tl.to("#cnt",{{scale:1.12,transformOrigin:"left center",duration:.4,yoyo:true,repeat:5,ease:"sine.inOut"}},6.2);
"""
    return body, js


def plan(s):
    rooms = s["rooms"]
    rects = "".join(
        f'<g class="room"><rect x="{r[1]}" y="{r[2]}" width="{r[3]}" height="{r[4]}" fill="{r[5]}" stroke="#2a2018" stroke-width="3"/>'
        f'<text x="{r[1] + r[3] / 2}" y="{r[2] + r[4] / 2 + 8}" font-size="24" font-weight="700" text-anchor="middle">{r[0]}</text></g>'
        for r in rooms)
    futons = "".join(
        f'<rect class="fu" x="{x}" y="{y}" width="64" height="26" rx="4" fill="#fff" stroke="#8a7a62" stroke-width="2"/>'
        for x, y in [(590, 200), (670, 200), (750, 200), (880, 200), (960, 200), (1040, 200)])
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
<svg class="abs" width="1280" height="720" viewBox="0 0 1280 720" style="left:0;top:0">
  <rect id="frame" x="140" y="170" width="1000" height="420" rx="6" fill="#fbf4e4" stroke="#2a2018" stroke-width="5" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
  {rects}{futons}
</svg>
{bird('bird', 150, 515, 70)}
<div class="tag">{s.get('tag', '')}</div>"""
    js = """
tl.to("#frame",{strokeDashoffset:0,duration:1.4,ease:"power2.inOut"},.4);
tl.from(".room",{opacity:0,scale:.9,transformOrigin:"center",duration:.5,stagger:.35,ease:"back.out(1.6)"},1.4);
tl.from(".fu",{opacity:0,y:-14,duration:.3,stagger:.12},3.6);
tl.from("#bird",{opacity:0,scale:0,duration:.5,ease:"back.out(2)"},1.2);
tl.to("#bird",{x:450,duration:1.8,ease:"power1.inOut"},4.4);
tl.to("#bird",{x:620,y:-220,duration:1.6,ease:"power1.inOut"},7);
tl.to("#bird",{y:"-=12",duration:.35,yoyo:true,repeat:3,ease:"sine.inOut"},8.7);
"""
    return body, js


def ledger(s):
    rows = s["rows"]
    mx = max(r[1] for r in rows)
    total = sum(r[1] for r in rows)
    unit = s.get("unit", "文")
    dec = 1 if any(isinstance(r[1], float) and r[1] != int(r[1]) for r in rows) else 0   # tổng có số lẻ thì hiện 1 chữ số thập phân
    out = []
    for i, (label, val) in enumerate(rows):
        y = 190 + i * (100 if len(rows) <= 4 else 86)
        w = int(560 * val / mx)
        out.append(
            f'<div class="abs rw" style="left:90px;top:{y}px;width:1100px;height:76px">'
            f'<div class="abs" style="left:0;top:18px;width:300px;font-size:34px;font-weight:700">{label}</div>'
            f'<div class="abs" style="left:310px;top:12px;width:{560}px;height:52px;background:#e8dcc0;border-radius:8px"></div>'
            f'<div class="abs bar" data-w="{w}" style="left:310px;top:12px;width:{w}px;height:52px;background:var(--indigo);border-radius:8px;transform-origin:left"></div>'
            f'<div class="abs" style="left:890px;top:8px;width:200px;text-align:right;font-size:50px;font-weight:900"><span class="num" data-v="{val}" data-d="{min(2, len(repr(val).split('.')[1])) if isinstance(val, float) and val != int(val) else 0}">0</span><span style="font-size:28px">{unit}</span></div></div>')
    ty = 190 + len(rows) * (100 if len(rows) <= 4 else 86) + 4
    # show_total: false khi nguồn chỉ ghi khoảng giá nên không cộng tổng. kari: true chỉ cho số liệu thử, hiện dấu 仮
    tot_html = ("<div class=\"abs\" id=\"tot\" style=\"left:90px;top:" + str(ty) + "px;width:1100px;height:80px;border-top:5px solid var(--ink)\">"
                "<div class=\"abs\" style=\"left:0;top:14px;font-size:38px;font-weight:900\">" + str(s["total_label"]) + "</div>"
                "<div class=\"abs hl\" style=\"left:890px;top:6px;width:200px;text-align:right;font-size:60px;font-weight:900\">"
                "<span id=\"tn\">0</span><span style=\"font-size:30px\">" + str(unit) + "</span></div></div>") if s.get("show_total", True) else ""
    stamp_html = ("<div class=\"abs\" id=\"stamp\" style=\"left:1090px;top:26px;width:110px;height:110px;border:6px solid var(--red);"
                  "border-radius:50%;color:var(--red);font-size:46px;font-weight:900;text-align:center;line-height:98px;"
                  "transform:rotate(-14deg)\">仮</div>") if s.get("kari") else ""
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
{''.join(out)}
{tot_html}
{stamp_html}
<div class="tag">{s.get('tag', '')}</div>"""
    js = f"""
tl.from(".rw",{{opacity:0,x:-60,duration:.5,stagger:.45,ease:"power3.out"}},.5);
document.querySelectorAll(".bar").forEach((b,i)=>{{tl.from(b,{{scaleX:0,duration:.8,ease:"power2.out"}},.9+i*.45)}});
document.querySelectorAll(".num").forEach((n,i)=>{{const o={{v:0}};tl.to(o,{{v:+n.dataset.v,duration:.8,ease:"power2.out",onUpdate:()=>{{n.textContent=o.v.toFixed(+n.dataset.d)}}}},.9+i*.45)}});
"""
    if s.get("show_total", True):
        js += f"""tl.from("#tot",{{opacity:0,y:20,duration:.4}},2.6);
const t={{v:0}};tl.to(t,{{v:{total},duration:.9,ease:"power2.out",onUpdate:()=>{{document.getElementById("tn").textContent=t.v.toFixed({dec})}}}},2.7);
"""
    if s.get("kari"):
        js += 'tl.from("#stamp",{scale:2.4,opacity:0,duration:.35,ease:"power4.in"},3.8);\n'
    return body, js


def compare(s):
    def card(side, x, color):
        items = "".join(f'<div class="abs it" style="left:44px;top:{146 + i * 70}px;font-size:32px;font-weight:700;line-height:1.3"><span class="ck" style="color:{color}">✔</span> {t}</div>'
                        for i, t in enumerate(side["items"]))
        return (f'<div class="abs card" style="left:{x}px;top:170px;width:540px;height:440px;background:#fff8e8;border:5px solid {color};border-radius:18px">'
                f'<div class="abs" style="left:0;top:0;width:100%;height:100px;background:{color};border-radius:10px 10px 0 0;color:#fff;font-size:46px;font-weight:900;text-align:center;line-height:100px">{side["name"]}'
                f'<span style="font-size:24px;margin-left:12px;font-weight:400">{side["ruby"]}</span></div>{items}</div>')
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
{card(s['left'], 64, 'var(--indigo)')}{card(s['right'], 676, 'var(--red)')}
<div class="abs" id="vs" style="left:600px;top:360px;width:80px;height:80px;border-radius:50%;background:var(--ink);color:#fff;font-size:34px;font-weight:900;text-align:center;line-height:80px">VS</div>
<div class="tag">{s.get('tag', '')}</div>"""
    js = """
tl.from(".card",{opacity:0,y:60,duration:.7,stagger:.3,ease:"power3.out"},.4);
tl.from("#vs",{scale:0,rotation:-180,duration:.5,ease:"back.out(2)"},1.1);
tl.from(".it",{opacity:0,x:-30,duration:.45,stagger:.5,ease:"power2.out"},1.8);
tl.from(".ck",{scale:0,duration:.3,stagger:.5,ease:"back.out(3)"},2);
tl.fromTo("#vs",{scale:1},{scale:1.12,duration:.5,yoyo:true,repeat:9,ease:"sine.inOut",immediateRender:false},4.4);   // fromTo: không lấy cỡ 0 của bước hiện ra làm điểm đầu
"""
    return body, js


def day(s):
    stops = s["stops"]
    chara = s.get("chara", True)   # chara: false thì không có chim và mặt trời (kênh chưa có nhân vật đại diện)
    sun = '<circle id="sun" cx="170" cy="250" r="34" fill="var(--gold)"/>' if chara else ""
    xs = [170 + i * 313 for i in range(len(stops))]
    items = "".join(
        f'<div class="abs st" style="left:{x - 145}px;top:430px;width:290px;text-align:center">'
        f'<div style="font-size:54px;font-weight:900;color:{c}">{t[0]}</div><div style="font-size:28px;font-weight:700;margin-top:8px;line-height:1.35">{t[1]}</div></div>'
        for x, t, c in zip(xs, stops, ["var(--gold)", "var(--sage)", "var(--red)", "var(--indigo)"]))
    nodes = "".join(f'<circle class="nd" cx="{x}" cy="380" r="14" fill="#fff" stroke="#2a2018" stroke-width="5"/>' for x in xs)
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
<svg class="abs" width="1280" height="720" viewBox="0 0 1280 720" style="left:0;top:0">
  <line x1="170" y1="380" x2="1109" y2="380" stroke="#d9c9a5" stroke-width="12" stroke-linecap="round"/>
  <line id="prog" x1="170" y1="380" x2="1109" y2="380" stroke="var(--red)" stroke-width="12" stroke-linecap="round" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>
  {nodes}
  {sun}
</svg>
{items}
{bird('bird', 110, 290, 90) if s.get('chara', True) else ''}
<div class="tag">{s.get('tag', '')}</div>"""
    js = f"""
const xs={xs};
tl.to("#prog",{{strokeDashoffset:0,duration:6,ease:"none"}},.8);
tl.from(".nd",{{scale:0,transformOrigin:"center",duration:.3,stagger:.5}},.4);
xs.forEach((x,i)=>{{tl.from(document.querySelectorAll(".st")[i],{{opacity:0,y:30,duration:.5}},.8+i*2)}});
"""
    if s.get("chara", True):
        js += """tl.to("#bird",{x:xs[3]-xs[0],duration:6,ease:"none"},.8);
tl.fromTo("#bird",{y:0},{y:-10,duration:.3,yoyo:true,repeat:19,ease:"sine.inOut"},.8);
"""
    if chara:
        js += f"""tl.to("#sun",{{attr:{{cx:xs[3]}},duration:6,ease:"none"}},.8);
tl.to("#sun",{{attr:{{cy:200}},duration:3,yoyo:true,repeat:1,ease:"sine.inOut"}},.8);
tl.to("#sun",{{fill:"#4a5e8c",duration:1.2}},5.4);
"""
    return body, js


def ban_do(s):
    """Bản đồ tô màu theo thế lực qua các mốc năm. Hình lấy từ assets/ban_do_map.js (tools/gunmap.py tạo)."""
    pal = s["palette"]
    snaps = s["snapshots"]
    base = s.get("base") or {}   # trạng thái đã có từ cảnh trước: hiện ngay, không chạy hoạt ảnh
    # Khóa trong owners là tên quốc ("日向国") hoặc "quốc/quận" ("日向国/北諸県郡"). Quận ghi đè màu của cả quốc.
    # Số đếm ở chú giải chỉ đếm quốc, không đếm quận. an_so: các thế lực không hiện thanh và số (ví dụ màu chỉ dùng cho quận).
    hide = set(s.get("an_so") or [])
    bx = s.get("map_box") or [40, 96, 700, 620]   # vị trí và cỡ khung bản đồ trên màn hình [trái, trên, rộng, cao]
    counts = []
    for sn in [{"owners": base}] + list(snaps):
        c = {k: 0 for k in pal}
        for key, owner in sn["owners"].items():
            if "/" not in key:
                c[owner] += 1
        counts.append(c)
    cnt0, counts = counts[0], counts[1:]
    peak = s.get("peak") or max(max(c.values()) for c in counts + [cnt0]) or 1
    pitch = min(46, 340 // len(pal))
    rows = "".join(
        f'<div class="lg" id="lg{i}" style="top:{i * pitch}px"><span class="chip" style="background:{v[0]}"></span>'
        f'<span class="nm">{v[1]}</span><span class="bar"{hid}><i id="bar{i}"></i></span><b id="num{i}"{hid}>0</b></div>'
        for i, (k, v) in enumerate(pal.items()) for hid in [' style="visibility:hidden"' if k in hide else ''])
    body = f"""
<div class="band"></div>
<div class="title">{s['title']}<small>{s['sub']}</small></div>
<svg class="abs" id="mapsvg" width="{bx[2]}" height="{bx[3]}" viewBox="0 0 700 620" style="left:{bx[0]}px;top:{bx[1]}px;overflow:visible"></svg>
<div class="abs" id="yr" style="left:790px;top:96px;font-size:132px;font-weight:900;letter-spacing:.02em;line-height:1">0</div>
<div class="abs" id="lab" style="left:796px;top:240px;font-size:34px;font-weight:700;color:var(--indigo)">&nbsp;</div>
<div class="abs" id="legend" style="left:796px;top:316px;width:440px">{rows}</div>
<style>.lg{{position:absolute;left:0;width:440px;height:{max(pitch - 4, 24)}px;font-size:26px;font-weight:700;display:flex;align-items:center;gap:12px}}
.chip{{width:22px;height:22px;border-radius:4px;flex:none}}.nm{{width:124px;flex:none}}
.bar{{flex:1;height:14px;background:#e6dcc4;border-radius:7px;overflow:hidden}}.bar i{{display:block;height:14px;width:0;background:var(--ink);border-radius:7px}}
.lg b{{width:48px;text-align:right;font-size:26px}}.reg{{stroke:#f6ecd8;stroke-width:.5}}.title{{z-index:2}}</style>
<div class="tag">{s.get('tag', '')}</div>
<script src="../assets/ban_do_map.js"></script>"""
    owners_by = [sn["owners"] for sn in snaps]
    js = f"""
const B=window.BANDO,ns="http://www.w3.org/2000/svg",svg=document.getElementById("mapsvg"),FS=[];
B.features.forEach(f=>{{const p=document.createElementNS(ns,"path");p.setAttribute("d",f.d);p.setAttribute("class","reg");
 p.setAttribute("fill","#d9cfb8");svg.appendChild(p);FS.push({{p:p,g:f.g,k:f.g+"/"+f.name}});}});
const RES=o=>FS.map(f=>f.k in o?o[f.k]:(f.g in o?o[f.g]:null));
const PAL={json.dumps(list(pal.values()), ensure_ascii=False)},OWN={json.dumps(owners_by, ensure_ascii=False)},
 YEARS={json.dumps([sn["year"] for sn in snaps])},LABS={json.dumps([sn.get("label", "") for sn in snaps], ensure_ascii=False)},
 CNT={json.dumps([list(c.values()) for c in counts])},PEAK={peak},KEYS={json.dumps(list(pal.keys()), ensure_ascii=False)},
 BASE={json.dumps(base, ensure_ascii=False)},CNT0={json.dumps(list(cnt0.values()))},HAS=Object.keys(BASE).length>0,GRAY="#d9cfb8";
const R0=RES(BASE),RK=OWN.map(RES);
R0.forEach((o,i)=>{{if(o!==null)FS[i].p.setAttribute("fill",PAL[KEYS.indexOf(o)][0])}});
CNT0.forEach((c,i)=>{{document.getElementById("bar"+i).style.width=(100*c/PEAK)+"%";document.getElementById("num"+i).textContent=c}});
const yr=document.getElementById("yr"),lab=document.getElementById("lab"),st={{y:YEARS[0]}};yr.textContent=YEARS[0];lab.textContent=LABS[0]||"\\u00a0";
if(!HAS){{tl.from("#mapsvg",{{opacity:0,duration:.6}},0);tl.from("#yr",{{opacity:0,y:-20,duration:.5}},.3);}}
const T0=HAS?0.2:0.9,STEP=(9-T0)/YEARS.length;
YEARS.forEach((y,k)=>{{const t=T0+k*STEP,prev=k?RK[k-1]:R0,cur=RK[k],byColor={{}},gone=[];
 cur.forEach((o,i)=>{{if(o===prev[i])return;if(o===null)gone.push(FS[i].p);else (byColor[o]=byColor[o]||[]).push(FS[i].p);}});
 for(const o in byColor){{tl.to(byColor[o],{{fill:PAL[KEYS.indexOf(o)][0],duration:.55,ease:"power1.inOut"}},t);}}
 if(gone.length){{tl.to(gone,{{fill:GRAY,duration:.55,ease:"power1.inOut"}},t);}}
 tl.to(st,{{y:y,duration:.7,ease:"power1.inOut",onUpdate:()=>{{yr.textContent=Math.round(st.y)}}}},t);
 tl.call(()=>{{lab.textContent=LABS[k]||"\\u00a0"}},null,t+.3);
 CNT[k].forEach((c,i)=>{{tl.to("#bar"+i,{{width:(100*c/PEAK)+"%",duration:.6,ease:"power1.out"}},t);
  const o={{n:k?CNT[k-1][i]:CNT0[i]}};tl.to(o,{{n:c,duration:.6,onUpdate:()=>{{document.getElementById("num"+i).textContent=Math.round(o.n)}}}},t);}});
}});
"""
    return body, js


# ---------------------------------------------------------------- bản đồ kiểu điện ảnh (ban_do2)
# Học cách trình bày của các kênh bản đồ lịch sử Nhật: bản đồ phủ khung trên nền tối, huy hiệu tên nhà ngay trên bản đồ,
# khung năm lớn ở góc, thanh thời gian ở trên, vùng ảnh hưởng đánh sọc, bụi sáng trôi. Màu và bố cục là của kênh mình
# (xanh đêm, hoa văn sóng, chữ kem và vàng), không dùng mặt trời đỏ hay nền đen của kênh khác.
DARK = {"bg": "#0e1830", "land": "#27334d", "edge": "#0e1830", "cream": "#f3e7cc", "gold": "#e2b65a", "muted": "#8f9bb5"}

BAN_DO2_CSS = """
#root{background:__BG__}
.serif{font-family:"Noto Serif JP",serif}
.lg2{display:flex;align-items:center;gap:8px;color:__CREAM__;font-size:19px;font-weight:700}
.ch2{width:18px;height:18px;border-radius:3px;flex:none;border:1px solid rgba(243,231,204,.5)}
.reg2{stroke:__EDGE__;stroke-width:.45}
.tk{position:absolute;top:-5px;transform:translateX(-50%)}.tk i{display:block;width:2px;height:12px;background:__MUTED__;margin:0 auto}
.tk span{position:absolute;top:-24px;left:50%;transform:translateX(-50%);white-space:nowrap;color:__MUTED__;font-size:15px}
.mk{position:absolute;transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center}
.mk b{width:54px;height:54px;border-radius:50%;background:__BG__;border:3px solid var(--c);color:__CREAM__;font-size:28px;line-height:48px;
 text-align:center;font-family:"Noto Serif JP",serif;font-weight:900;box-shadow:0 0 0 3px rgba(14,24,48,.6),0 4px 10px rgba(0,0,0,.5)}
.mk em{font-style:normal;margin-top:4px;background:rgba(14,24,48,.85);color:__CREAM__;font-size:22px;font-weight:900;padding:1px 10px;
 border-radius:3px;font-family:"Noto Serif JP",serif;white-space:nowrap}
.dust{position:absolute;width:3px;height:3px;border-radius:50%;background:#f3e7cc}
"""

BAN_DO2_JS = r"""
const B=window.BANDO,ns="http://www.w3.org/2000/svg",svg=document.getElementById("mapsvg"),G=document.getElementById("regs"),FS=[];
B.features.forEach(f=>{const p=document.createElementNS(ns,"path");p.setAttribute("d",f.d);p.setAttribute("class","reg2");
 p.setAttribute("fill",LAND);G.appendChild(p);FS.push({p:p,g:f.g,k:f.g+"/"+f.name});});
const RES=o=>FS.map(f=>f.k in o?o[f.k]:(f.g in o?o[f.g]:null));
const fillOf=o=>{const i=KEYS.indexOf(o),v=PAL[i];return v.length>3&&v[3]?"url(#st"+i+")":v[0]};
const R0=RES(BASE),RK=OWN.map(RES);
R0.forEach((o,i)=>{if(o!==null)FS[i].p.setAttribute("fill",fillOf(o))});
// máy quay: khung quanh các quốc/quận được nêu, giữ đúng tỉ lệ khung hình, chừa lề
function cam(keys){if(!keys||!keys.length)return [0,0,700,620];let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;
 FS.forEach(f=>{if(keys.includes(f.g)||keys.includes(f.k)){const b=f.p.getBBox();x0=Math.min(x0,b.x);y0=Math.min(y0,b.y);x1=Math.max(x1,b.x+b.width);y1=Math.max(y1,b.y+b.height);}});
 if(x0>x1)return [0,0,700,620];let w=(x1-x0)*1.3,h=(y1-y0)*1.3;const r=BW/BH;if(w/h<r)w=h*r;else h=w/r;
 return [(x0+x1)/2-w/2,(y0+y1)/2-h/2,w,h]}
const CAM=FOCUS?cam(FOCUS):[0,0,700,620],CAM0=FOCUS0?cam(FOCUS0):CAM;
svg.setAttribute("viewBox",CAM0.join(" "));
const scr=(x,y,c)=>{const k=Math.min(BW/c[2],BH/c[3]);return [(BW-c[2]*k)/2+(x-c[0])*k,(BH-c[3]*k)/2+(y-c[1])*k]};
const yr=document.getElementById("yr"),lab=document.getElementById("lab"),st={y:YEARS[0]};yr.textContent=YEARS[0];
const pct=y=>Math.max(0,Math.min(1,(y-TF)/Math.max(TT-TF,1)))*100;
gsap.set("#tlbar",{width:pct(YEARS[0])+"%"});gsap.set("#tldot",{left:pct(YEARS[0])+"%"});
// bụi sáng trôi chậm; vị trí theo hạt giống cố định nên mọi lần render giống nhau
const D=document.getElementById("dusts");let sd=7;const rnd=()=>(sd=(sd*9301+49297)%233280)/233280;
for(let i=0;i<34;i++){const d=document.createElement("div");d.className="dust";d.style.left=(rnd()*1280)+"px";d.style.top=(rnd()*720)+"px";
 d.style.opacity=.15+rnd()*.45;D.appendChild(d);tl.to(d,{y:-30-rnd()*60,x:(rnd()-.5)*40,duration:10,ease:"none"},0);}
if(!HAS){tl.from(G,{opacity:0,duration:.8},0);}
const MOVE=CAM0.join()!==CAM.join();
if(MOVE){const o={t:0};tl.to(o,{t:1,duration:2.2,ease:"power2.inOut",onUpdate:()=>{svg.setAttribute("viewBox",CAM0.map((v,i)=>v+(CAM[i]-v)*o.t).join(" "))}},.2);}
const T0=(HAS?0.3:1.0)+(MOVE?2.2:0),STEP=(8.4-T0)/YEARS.length;
// huy hiệu: ở mảnh gần trọng tâm các mảnh của nhà đó, rồi đẩy các huy hiệu chồng nhau ra xa
const MK=document.getElementById("marks"),mkEl={};
function place(res,c){const acc={};res.forEach((o,i)=>{if(o===null)return;const b=FS[i].p.getBBox(),a=b.width*b.height+1e-6,
 q={x:b.x+b.width/2,y:b.y+b.height/2,a:a};(acc[o]=acc[o]||[]).push(q)});const out={};
 for(const o in acc){const L=acc[o],A=L.reduce((s,q)=>s+q.a,0),cx=L.reduce((s,q)=>s+q.x*q.a,0)/A,cy=L.reduce((s,q)=>s+q.y*q.a,0)/A;
  let best=L[0],bd=1e18;L.forEach(q=>{const d=(q.x-cx)**2+(q.y-cy)**2-q.a*.15;if(d<bd){bd=d;best=q}});out[o]=scr(best.x,best.y,c);}
 // nhà nằm ngoài khung nhìn của máy quay: không đặt huy hiệu (trước đây bị dồn vào mép khung)
 for(const o in out){const p=out[o];if(p[0]<-10||p[0]>BW+10||p[1]<-10||p[1]>BH+10)delete out[o];}
 const ks=Object.keys(out).filter(o=>PAL[KEYS.indexOf(o)][2]);
 for(let it=0;it<40;it++)for(let i=0;i<ks.length;i++)for(let j=i+1;j<ks.length;j++){const a=out[ks[i]],b=out[ks[j]];
  let dx=b[0]-a[0],dy=b[1]-a[1],d=Math.hypot(dx,dy)||1;if(d<100){const m=(100-d)/2;dx/=d;dy/=d;a[0]-=dx*m;a[1]-=dy*m;b[0]+=dx*m;b[1]+=dy*m;}}
 for(const o in out){out[o][0]=Math.max(40,Math.min(BW-40,out[o][0]));out[o][1]=Math.max(36,Math.min(BH-50,out[o][1]));}
 return out}
function marker(o){const i=KEYS.indexOf(o),v=PAL[i];if(!v[2])return null;if(mkEl[o])return mkEl[o];const m=document.createElement("div");
 m.className="mk";m.style.setProperty("--c",v[0]);m.innerHTML="<b>"+v[2]+"</b><em>"+v[1]+"</em>";m.style.opacity=0;MK.appendChild(m);mkEl[o]=m;return m}
const P0=place(R0,CAM0),P0e=place(R0,CAM);
for(const o in P0){const m=marker(o);if(!m)continue;m.style.left=P0[o][0]+"px";m.style.top=P0[o][1]+"px";m.style.opacity=1;m.dataset.on=1;
 if(MOVE){if(P0e[o])tl.to(m,{left:P0e[o][0],top:P0e[o][1],duration:2.2,ease:"power2.inOut"},.2);
  else tl.to(m,{opacity:0,duration:.8},.2);}}
YEARS.forEach((y,k)=>{const t=T0+k*STEP,prev=k?RK[k-1]:R0,cur=RK[k],byColor={},gone=[];
 cur.forEach((o,i)=>{if(o===prev[i])return;if(o===null)gone.push(FS[i].p);else (byColor[o]=byColor[o]||[]).push(FS[i].p);});
 for(const o in byColor){tl.to(byColor[o],{fill:fillOf(o),duration:.7,ease:"power1.inOut"},t);}
 if(gone.length){tl.to(gone,{fill:LAND,duration:.7,ease:"power1.inOut"},t);}
 tl.to(st,{y:y,duration:.8,ease:"power1.inOut",onUpdate:()=>{yr.textContent=Math.round(st.y)}},t);
 tl.to("#tlbar",{width:pct(y)+"%",duration:.8,ease:"power1.inOut"},t);tl.to("#tldot",{left:pct(y)+"%",duration:.8,ease:"power1.inOut"},t);
 tl.call(()=>{lab.textContent=LABS[k]||" ";document.getElementById("wa").textContent=WAS[k]},null,t+.3);
 const P=place(cur,CAM);
 for(const o in mkEl){if(!(o in P))tl.to(mkEl[o],{opacity:0,scale:.6,duration:.4},t);}
 for(const o in P){const m=marker(o);if(!m)continue;
  if(!m.dataset.on){m.dataset.on=1;m.style.left=P[o][0]+"px";m.style.top=P[o][1]+"px";
   tl.fromTo(m,{opacity:0,scale:.4},{opacity:1,scale:1,duration:.5,ease:"back.out(2)"},t+.4);}
  else tl.to(m,{left:P[o][0],top:P[o][1],opacity:1,scale:1,duration:.7,ease:"power1.inOut"},t);}
});
if(document.getElementById("note"))tl.from("#note",{opacity:0,y:20,duration:.5},T0+.6);
if(document.getElementById("person"))tl.from("#person",{opacity:0,x:40,duration:.6,ease:"power2.out"},T0+.3);
"""


def ban_do2(s):
    pal = s["palette"]                    # {khóa: [màu, tên, chữ trên huy hiệu (rỗng: không huy hiệu), sọc (true/false)]}
    snaps = s["snapshots"]
    base = s.get("base") or {}
    tl_from, tl_to = (s.get("timeline") or [snaps[0]["year"], snaps[-1]["year"]])[:2]
    marks = s.get("marks") or []          # [[năm, nhãn]] trên thanh thời gian
    bx = s.get("map_box") or [330, 40, 900, 660]
    focus = s.get("focus")                # danh sách quốc/quận để máy quay nhìn vào; focus0 khác focus thì máy quay di chuyển
    focus0 = s.get("focus0")
    note = s.get("note")
    person = s.get("person")              # {anh: {file, x, y, z} hoặc không có, name, role}: thẻ nhân vật ở góc phải
    D = DARK
    stripe = "background-image:repeating-linear-gradient(135deg,rgba(14,24,48,.6) 0 3px,transparent 3px 7px)"
    used = set(base.values()) | {o for sn in snaps for o in sn["owners"].values()}   # chú giải chỉ có các nhà xuất hiện trong cảnh
    shown = [v for k, v in pal.items() if k in used]
    two = len(shown) > 6
    legend = "".join(f'<div class="lg2" style="{"width:128px;font-size:17px" if two else ""}"><span class="ch2" style="background-color:{v[0]};{stripe if len(v) > 3 and v[3] else ""}"></span>{v[1]}</div>'
                     for v in shown)
    span = max(tl_to - tl_from, 1)
    ticks = "".join(f'<div class="tk" style="left:{(y - tl_from) / span * 100:.2f}%"><i></i><span{"" if n % 2 == 0 else ' style="top:16px"'}>{lab}</span></div>'
                    for n, (y, lab) in enumerate(marks))
    note_html = (f'<div class="abs" id="note" style="right:{290 if person else 36}px;bottom:150px;width:470px;background:rgba(14,24,48,.9);border:1.5px solid {D["gold"]};'
                 f'border-radius:4px;padding:12px 20px 14px"><div style="color:{D["gold"]};font-size:20px;font-weight:700;letter-spacing:.08em">{note["title"]}</div>'
                 f'<div style="color:{D["cream"]};font-size:27px;font-weight:700;margin-top:4px;line-height:1.35">{"<br>".join(note["lines"])}</div></div>') if note else ""
    pats = "".join(f'<pattern id="st{i}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                   f'<rect width="7" height="7" fill="{D["land"]}"/><rect width="3.4" height="7" fill="{v[0]}"/></pattern>' for i, v in enumerate(pal.values()))
    css = (BAN_DO2_CSS.replace("__BG__", D["bg"]).replace("__CREAM__", D["cream"]).replace("__EDGE__", D["edge"])
           .replace("__MUTED__", D["muted"]))
    era = (f'<span style="background:#c8432b;color:#fff;font-size:20px;font-weight:700;padding:2px 10px;border-radius:2px">{s["era"]}</span>'
           if s.get("era") else "")
    body = f"""<style>{css}</style>
<svg class="abs" width="1280" height="720" style="left:0;top:0">
 <defs><pattern id="wave" width="48" height="24" patternUnits="userSpaceOnUse">
  <path d="M0 24a24 24 0 0 1 48 0M12 24a12 12 0 0 1 24 0" fill="none" stroke="#18264a" stroke-width="2"/></pattern></defs>
 <rect width="1280" height="720" fill="url(#wave)"/></svg>
<svg class="abs" id="mapsvg" width="{bx[2]}" height="{bx[3]}" viewBox="0 0 700 620" style="left:{bx[0]}px;top:{bx[1]}px;overflow:visible">
 <defs>{pats}</defs><g id="regs"></g></svg>
<div class="abs" id="marks" style="left:{bx[0]}px;top:{bx[1]}px;width:{bx[2]}px;height:{bx[3]}px"></div>
<svg class="abs" width="1280" height="720" style="left:0;top:0"><defs><radialGradient id="vig" cx="62%" cy="52%" r="72%">
 <stop offset="55%" stop-color="#0e1830" stop-opacity="0"/><stop offset="100%" stop-color="#050a16" stop-opacity=".8"/></radialGradient></defs>
 <rect width="1280" height="720" fill="url(#vig)"/></svg>
<div id="dusts"></div>
<div class="abs serif" style="left:48px;top:36px;border-left:5px solid #c8432b;padding-left:14px;color:{D['cream']};font-size:30px;font-weight:900">{s['chapter']}</div>
<div class="abs serif" id="yr" style="left:44px;top:82px;font-size:118px;font-weight:900;line-height:1.05;background:linear-gradient(180deg,#fff3d1 10%,{D['gold']} 55%,#9c7428);-webkit-background-clip:text;background-clip:text;color:transparent">0</div>
<div class="abs serif" style="left:298px;top:150px;color:{D['gold']};font-size:40px;font-weight:900">年</div>
<div class="abs" style="left:50px;top:214px;display:flex;gap:10px;align-items:center"><span class="serif" id="wa" style="color:{D['cream']};font-size:24px;font-weight:700">{snaps[0].get('wareki', s.get('wareki', ''))}</span>{era}</div>
<div class="abs" id="lab" style="left:50px;top:258px;color:{D['gold']};font-size:26px;font-weight:700">&nbsp;</div>
<div class="abs" style="left:50px;top:312px;width:270px;display:flex;flex-wrap:wrap;flex-direction:{'row' if two else 'column'};gap:9px">{legend}</div>
<div class="abs" style="left:560px;top:50px;width:660px;height:4px;background:#2c3a5c;border-radius:2px">{ticks}
 <div class="abs" style="left:-14px;top:12px;color:{D['muted']};font-size:15px">{tl_from}</div>
 <div class="abs" style="right:-14px;top:12px;color:{D['muted']};font-size:15px">{tl_to}</div>
 <div class="abs" id="tlbar" style="left:0;top:0;height:4px;width:0;background:{D['gold']};border-radius:2px"></div>
 <div class="abs" id="tldot" style="left:0;top:-6px;width:16px;height:16px;margin-left:-8px;border-radius:50%;background:{D['gold']};box-shadow:0 0 12px {D['gold']}"></div></div>
{note_html}
{person_card(person, 40) if person else ''}
<div class="abs" style="left:48px;bottom:16px;color:{D['muted']};font-size:15px">{s.get('tag', '')}</div>
<script src="../assets/ban_do_map.js"></script>"""
    consts = (f"const PAL={json.dumps(list(pal.values()), ensure_ascii=False)},KEYS={json.dumps(list(pal.keys()), ensure_ascii=False)},"
              f"OWN={json.dumps([sn['owners'] for sn in snaps], ensure_ascii=False)},YEARS={json.dumps([sn['year'] for sn in snaps])},"
              f"LABS={json.dumps([sn.get('label', '') for sn in snaps], ensure_ascii=False)},BASE={json.dumps(base, ensure_ascii=False)},"
              f"HAS=Object.keys(BASE).length>0,LAND={json.dumps(D['land'])},TF={tl_from},TT={tl_to},"
              f"WAS={json.dumps([sn.get('wareki', s.get('wareki', '')) for sn in snaps], ensure_ascii=False)},FOCUS={json.dumps(focus, ensure_ascii=False)},FOCUS0={json.dumps(focus0, ensure_ascii=False)},BW={bx[2]},BH={bx[3]};")
    return body, consts + BAN_DO2_JS


# ---------------------------------------------------------------- ảnh, thẻ chương, đối đầu (kiểu điện ảnh)
WAVE_BG = """<svg class="abs" width="1280" height="720" style="left:0;top:0"><defs><pattern id="wave" width="48" height="24" patternUnits="userSpaceOnUse">
<path d="M0 24a24 24 0 0 1 48 0M12 24a12 12 0 0 1 24 0" fill="none" stroke="#18264a" stroke-width="2"/></pattern></defs>
<rect width="1280" height="720" fill="url(#wave)"/></svg>"""

# Tông tối cho các mẫu cũ (ledger, compare, day) khi data có "toi": true
DARK_THEME = """<style>:root{--paper:#0e1830;--ink:#f3e7cc;--indigo:#4a7fd0;--red:#d9463a;--gold:#e2b65a;--sage:#5fb37a;--muted:#8f9bb5}
html,body,#root{background:#0e1830}.band{background:linear-gradient(90deg,#c8432b,#e2b65a);height:6px}
.title{font-family:"Noto Serif JP",serif;font-weight:900}.title small{font-family:"Noto Sans JP",sans-serif}
#vs{background:linear-gradient(180deg,#f3d58a,#b8862f)!important;color:#0e1830!important}</style>"""


def portrait(a, w, h, extra=""):
    """Khung chân dung: a = {file, x, y, z} (điểm canh %, độ phóng). Ảnh nằm ở assets/anh."""
    return (f'<div class="abs" style="width:{w}px;height:{h}px;border:3px solid #e2b65a;border-radius:4px;'
            f'background:#1b2540 url(../assets/anh/{a["file"]}) {a.get("x", 50)}% {a.get("y", 30)}%/{a.get("z", 1.6) * 100:.0f}% auto no-repeat;'
            f'box-shadow:0 0 0 4px rgba(14,24,48,.7),0 10px 30px rgba(0,0,0,.6);{extra}"></div>')


def chapter_overlay(c):
    """Thẻ chương phủ lên cảnh đầu của chương, mờ dần sau khoảng 2 giây."""
    body = (f'<div class="abs" id="chap" style="left:0;top:0;width:1280px;height:720px;background:#0e1830;z-index:50">{WAVE_BG}'
            f'<div class="abs" style="left:0;top:250px;width:1280px;text-align:center;color:#e2b65a;font-size:30px;letter-spacing:.3em;'
            f'font-family:\'Noto Serif JP\',serif;font-weight:700">— {c["no"]} —</div>'
            f'<div class="abs" id="chapt" style="left:0;top:300px;width:1280px;text-align:center;font-size:92px;font-weight:900;'
            f'font-family:\'Noto Serif JP\',serif;background:linear-gradient(180deg,#fff3d1 10%,#e2b65a 55%,#9c7428);-webkit-background-clip:text;'
            f'background-clip:text;color:transparent">{c["title"]}</div>'
            f'<div class="abs" style="left:440px;top:430px;width:400px;height:2px;background:linear-gradient(90deg,transparent,#e2b65a,transparent)"></div>'
            f'<div class="abs" style="left:0;top:448px;width:1280px;text-align:center;color:#c9d2e6;font-size:26px">{c.get("sub", "")}</div></div>')
    js = ('tl.from("#chapt",{opacity:0,y:20,duration:.6,ease:"power2.out"},0);'
          'tl.to("#chap",{opacity:0,duration:.6,ease:"power1.in"},1.9);\n')
    return body, js


def doi_dau(s):
    """Màn đối đầu: nền chia hai màu, chân dung hoặc huy hiệu, chữ VS vàng, các dòng thông tin, thanh so số (stats)."""
    L, R = s["left"], s["right"]
    cl, cr = L.get("color", "#3f7fd9"), R.get("color", "#d9463a")

    def side(d, cx, color, ident):
        if d.get("anh"):
            pic = portrait(d["anh"], 190, 240, f"left:{cx - 95}px;top:92px")
        else:
            pic = (f'<div class="abs" style="left:{cx - 95}px;top:110px;width:190px;height:190px;border-radius:50%;background:#0e1830;'
                   f'border:6px solid {color};box-shadow:0 0 0 6px rgba(14,24,48,.6),0 0 40px {color}55;color:#f3e7cc;font-size:108px;'
                   f'line-height:176px;text-align:center;font-family:\'Noto Serif JP\',serif;font-weight:900">{d.get("badge", d["name"][0])}</div>')
        items = "".join(f'<div class="it2 {ident}" style="font-size:24px;font-weight:700;color:#f3e7cc;margin-top:2px">{t}</div>' for t in d["items"])
        return (pic + f'<div class="abs" style="left:{cx - 300}px;top:344px;width:600px;text-align:center">'
                f'<div style="display:inline-block;background:{color};color:#fff;font-size:20px;font-weight:700;padding:2px 12px;border-radius:2px">{d.get("role", "")}</div>'
                f'<div style="font-family:\'Noto Serif JP\',serif;font-size:54px;font-weight:900;color:#fff;line-height:1.15;text-shadow:0 3px 12px rgba(0,0,0,.6)">{d["name"]}</div>'
                f'{items}</div>')
    stats = s.get("stats") or []      # [[nhãn, số trái, số phải, chữ trái, chữ phải]]
    st_html = ""
    if stats:
        rows = ""
        for i, (lab, a, b, ta, tb) in enumerate(stats):
            m = max(a, b) or 1
            rows += (f'<div class="abs" style="left:0;top:{i * 40}px;width:1040px;height:36px">'
                     f'<div class="abs" style="left:0;width:230px;text-align:right;color:#f3e7cc;font-size:24px;font-weight:700;white-space:nowrap">{ta}</div>'
                     f'<div class="abs sb" style="left:{250 + 230 - int(230 * a / m)}px;top:10px;width:{int(230 * a / m)}px;height:16px;background:{cl};transform-origin:right"></div>'
                     f'<div class="abs" style="left:480px;width:80px;text-align:center;color:#e2b65a;font-size:20px;font-weight:700">{lab}</div>'
                     f'<div class="abs sb" style="left:560px;top:10px;width:{int(230 * b / m)}px;height:16px;background:{cr};transform-origin:left"></div>'
                     f'<div class="abs" style="left:810px;width:230px;color:#f3e7cc;font-size:24px;font-weight:700;white-space:nowrap">{tb}</div></div>')
        st_html = (f'<div class="abs" id="stats" style="left:120px;top:{628 - 40 * len(stats)}px;width:1040px;height:{40 * len(stats)}px;'
                   f'">{rows}</div>')
    body = f"""<style>#root{{background:#0e1830}}</style>
<div class="abs" style="left:0;top:0;width:1280px;height:720px;background:linear-gradient(115deg,{cl}cc 0%,#0e1830 46%,#0e1830 54%,{cr}cc 100%)"></div>
{WAVE_BG.replace('stroke="#18264a"', 'stroke="#ffffff" stroke-opacity=".05"')}
<div class="abs" style="left:0;top:0;width:1280px;height:720px;background:radial-gradient(circle at 50% 40%,transparent 30%,rgba(5,10,22,.75) 100%)"></div>
<div class="abs" style="left:0;top:22px;width:1280px;text-align:center;color:#e2b65a;font-family:'Noto Serif JP',serif;font-size:34px;font-weight:900;letter-spacing:.12em">— {s['title']} —</div>
<div class="abs" style="left:0;top:66px;width:1280px;text-align:center;color:#a9b4cc;font-size:20px">{s.get('sub', '')}</div>
<div id="L">{side(L, 320, cl, 'l')}</div><div id="R">{side(R, 960, cr, 'r')}</div>
<div class="abs" id="vs" style="left:540px;top:170px;width:200px;text-align:center;font-family:'Noto Serif JP',serif;font-size:140px;font-weight:900;line-height:1;
 background:linear-gradient(180deg,#fff3d1 10%,#e2b65a 55%,#8c6420);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 18px rgba(226,182,90,.45))">VS</div>
{st_html}
<div class="abs" style="left:40px;bottom:12px;color:#8f9bb5;font-size:15px">{s.get('tag', '')}</div>"""
    js = """
tl.from("#L",{opacity:0,x:-80,duration:.7,ease:"power3.out"},.2);
tl.from("#R",{opacity:0,x:80,duration:.7,ease:"power3.out"},.35);
tl.fromTo("#vs",{scale:2.2,opacity:0},{scale:1,opacity:1,duration:.5,ease:"power4.in",immediateRender:false},.9);
tl.from(".it2.l",{opacity:0,y:14,duration:.4,stagger:.45},1.5);tl.from(".it2.r",{opacity:0,y:14,duration:.4,stagger:.45},1.7);
tl.from(".sb",{scaleX:0,duration:.8,stagger:.15,ease:"power2.out"},2.4);
tl.fromTo("#vs",{scale:1},{scale:1.06,duration:.6,yoyo:true,repeat:7,ease:"sine.inOut",immediateRender:false},3.4);
"""
    return body, js


def person_card(p, right):
    """Thẻ nhân vật trên bản đồ: chân dung (nếu có) và tên."""
    pic = portrait(p["anh"], 200, 250, "left:0;top:0") if p.get("anh") else ""
    top = 262 if p.get("anh") else 0
    return (f'<div class="abs" id="person" style="right:{right}px;top:{250 if p.get("anh") else 470}px;width:206px;height:340px">{pic}'
            f'<div class="abs" style="left:-20px;top:{top}px;width:246px;text-align:center">'
            f'<div style="display:inline-block;background:#c8432b;color:#fff;font-size:17px;font-weight:700;padding:1px 10px;border-radius:2px">{p.get("role", "")}</div>'
            f'<div style="font-family:\'Noto Serif JP\',serif;font-size:34px;font-weight:900;color:#f3e7cc;text-shadow:0 2px 8px #000">{p["name"]}</div></div></div>')


# Đặt timeline ở trạng thái cuối và khóa các lệnh tua, để mọi khung hình của cảnh đều là trạng thái cuối
HOLD_JS = """
{const N=tl.duration(),tt=tl.totalTime.bind(tl);tt(N);const f=function(){return tt(N)};tl.seek=f;tl.time=f;tl.totalTime=f;tl.progress=f;tl.totalProgress=f;}
"""

TEMPLATES = {"hook": hook, "route": route, "plan": plan, "ledger": ledger, "compare": compare, "day": day, "ban_do": ban_do, "ban_do2": ban_do2, "doi_dau": doi_dau}

PAGE = """<!doctype html>
<html lang="ja"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1280, height=720"/>
<script src="../assets/gsap.min.js"></script>
<style>__CSS__</style></head><body>
<div id="root" data-composition-id="__ID__" data-start="0" data-duration="__DUR__" data-width="1280" data-height="720" data-fps="__FPS__">
<div id="stage" class="stage clip" data-start="0" data-duration="__DUR__" data-track-index="0">__BODY__</div></div>
<script>
window.__timelines=window.__timelines||{};
const tl=gsap.timeline({paused:true});
__JS__
{const N=tl.duration(),K=Math.min(1,(__DUR__-.3)/N);if(K<1)tl.getChildren(false,true,true).forEach(c=>{c.startTime(c.startTime()*K);c.timeScale(1/K)});}
__POST__
window.__timelines["__ID__"]=tl;tl.seek(0);
</script></body></html>"""


SCHEMA = {
    "hook": ("kicker", "line1", "hl", "line2"),
    "route": ("title", "sub", "from", "to", "count", "count_label"),
    "plan": ("title", "sub", "rooms"),
    "ledger": ("title", "sub", "rows", "total_label"),
    "compare": ("title", "sub", "left", "right"),
    "day": ("title", "sub", "stops"),
    "ban_do": ("title", "sub", "palette", "snapshots"),
    "ban_do2": ("chapter", "palette", "snapshots"),
    "doi_dau": ("title", "left", "right"),
}
# Mẫu có số liệu hoặc dữ kiện lịch sử: phải ghi mã nguồn (nguon) của dữ kiện trong nguon.md
NEEDS_SOURCE = {"route", "plan", "ledger", "compare", "day", "ban_do", "ban_do2", "doi_dau"}

# Mẫu của kênh 4 (lịch sử công ty), xem studio/mau_kigyo.py
from .mau_kigyo import K4CSS, NEEDS_SOURCE_K4, SCHEMA_K4, TEMPLATES_K4, check_k4  # noqa: E402
TEMPLATES.update(TEMPLATES_K4)
SCHEMA.update(SCHEMA_K4)
NEEDS_SOURCE |= NEEDS_SOURCE_K4


def check_scene(sc, anh_co=None):
    """Trả về danh sách lỗi của dữ liệu một cảnh. Danh sách rỗng nghĩa là dựng được.
    anh_co: tên các ảnh có trong motion/anh (để kiểm mẫu kênh 4 dùng ảnh)."""
    t = sc.get("template")
    if t not in SCHEMA:
        return [f"mẫu \"{t}\" không có, các mẫu hiện có: {', '.join(SCHEMA)}"]
    data = sc.get("data") or {}
    required = [k for k in SCHEMA[t] if not (t == "ledger" and k == "total_label" and data.get("show_total") is False)]
    errors = [f"thiếu trường {k}" for k in required if data.get(k) in (None, "", [])]
    if errors:
        return errors
    if t == "route" and not (isinstance(data["count"], int) and 2 <= data["count"] <= 120):
        errors.append("count phải là số nguyên từ 2 đến 120")
    if t == "plan":
        rooms = data["rooms"]
        if not all(isinstance(r, list) and len(r) == 6 and all(isinstance(x, (int, float)) for x in r[1:5]) for r in rooms):
            errors.append("mỗi phòng trong rooms phải là [tên, x, y, rộng, cao, màu]")
    if t == "ledger":
        rows = data["rows"]
        if not all(isinstance(r, list) and len(r) == 2 and isinstance(r[1], (int, float)) and r[1] > 0 for r in rows):
            errors.append("mỗi dòng trong rows phải là [nhãn, số dương]")
        elif not 1 <= len(rows) <= 5:
            errors.append("rows phải có từ 1 đến 5 dòng")
    if t == "compare":
        for side in ("left", "right"):
            s = data[side]
            if not isinstance(s, dict) or not s.get("name") or not s.get("ruby") or not 1 <= len(s.get("items") or []) <= 4:
                errors.append(f"{side} cần name, ruby và 1 đến 4 mục trong items")
    if t == "day":
        stops = data["stops"]
        if not (isinstance(stops, list) and len(stops) == 4 and all(isinstance(x, list) and len(x) == 2 for x in stops)):
            errors.append("stops phải có đúng 4 mục [mốc, việc]")
    if t in ("ban_do", "ban_do2"):
        errors += check_ban_do(data, 16 if t == "ban_do2" else 12)
    if t == "doi_dau":
        for side in ("left", "right"):
            d = data[side]
            if not isinstance(d, dict) or not d.get("name") or not 1 <= len(d.get("items") or []) <= 4:
                errors.append(f"{side} cần name và 1 đến 4 mục trong items")
            elif wlen(d["name"]) > 7 or any(wlen(i) > 15 for i in d["items"]):
                errors.append(f"{side}: name tối đa 7 ký tự, mỗi mục tối đa 15")
        if not all(isinstance(r, list) and len(r) == 5 for r in data.get("stats") or []):
            errors.append("stats: mỗi dòng là [nhãn, số trái, số phải, chữ trái, chữ phải]")
    if t in SCHEMA_K4:
        errors += check_k4(t, data, anh_co)
    return errors or check_length(t, data)


def check_ban_do(data, max_houses=12):
    pal, snaps = data["palette"], data["snapshots"]
    if not (isinstance(pal, dict) and 1 <= len(pal) <= max_houses and all(
            isinstance(v, list) and 2 <= len(v) <= 4 and str(v[0]).startswith("#") for v in pal.values())):
        return [f"palette phải là {{mã: [màu #hex, tên]}} với 1 đến {max_houses} thế lực"]
    if not (isinstance(snaps, list) and 1 <= len(snaps) <= 12):
        return ["snapshots phải có từ 1 đến 12 mốc"]
    errors, last = [], None
    for i, sn in enumerate(snaps, 1):
        if not (isinstance(sn, dict) and isinstance(sn.get("year"), int) and isinstance(sn.get("owners"), dict)):
            errors.append(f"mốc {i} cần year (số nguyên) và owners {{nhóm: thế lực}} (owners có thể rỗng)")
            continue
        if last is not None and sn["year"] <= last:
            errors.append(f"mốc {i}: năm {sn['year']} phải lớn hơn năm trước ({last})")
        last = sn["year"]
        errors += [f"mốc {i}: thế lực \"{o}\" không có trong palette" for o in set(sn["owners"].values()) if o not in pal]
    box = data.get("map_box")
    if box is not None and not (isinstance(box, list) and len(box) == 4 and all(isinstance(x, (int, float)) for x in box)):
        errors.append("map_box phải là [trái, trên, rộng, cao]")
    base = data.get("base") or {}
    if not isinstance(base, dict):
        errors.append("base phải là {nhóm: thế lực}")
    else:
        errors += [f"base: thế lực \"{o}\" không có trong palette" for o in set(base.values()) if o not in pal]
    return errors


# Độ rộng tối đa (tính theo ký tự toàn chiều rộng) để chữ không tràn khung 1280x720. Đo theo cách mẫu bố trí, không đo theo font thật.
# Ký tự ASCII (số, chữ latin) tính 0,55.


def wlen(text):
    return sum(0.55 if ord(c) < 128 else 1.0 for c in str(text))


MAX_LEN = {"title": 22, "sub": 34, "tag": 60, "kicker": 24, "from": 6, "to": 6, "count_label": 8}


def check_length(t, data):
    errors = []
    for key, limit in MAX_LEN.items():
        value = data.get(key)
        if isinstance(value, str) and wlen(value) > limit:
            errors.append(f"{key} dài {wlen(value):.1f} ký tự, tối đa {limit}")
    if t == "hook":
        for text, name in ((data["line1"], "line1"), (data["hl"] + data["line2"], "hl + line2")):
            if wlen(text) > 10:
                errors.append(f"{name} dài {wlen(text):.1f} ký tự, tối đa 10 (chữ lớn 84 px, nhân vật chiếm bên phải)")
    if t == "ledger":
        errors += [f"nhãn \"{r[0]}\" dài {wlen(r[0]):.1f} ký tự, tối đa 9" for r in data["rows"] if wlen(str(r[0])) > 9]
    if t == "compare":
        for side in ("left", "right"):
            s = data[side]
            if wlen(s["name"]) > 6 or wlen(s["ruby"]) > 10:
                errors.append(f"{side}: name tối đa 6 ký tự, ruby tối đa 10")
            errors += [f"{side}: mục \"{i}\" dài {wlen(i):.1f} ký tự, tối đa 14" for i in s["items"] if wlen(i) > 14]
    if t == "day":
        errors += [f"mốc \"{x[1]}\" dài {wlen(x[1]):.1f} ký tự, tối đa 10" for x in data["stops"] if wlen(x[1]) > 10]
    if t == "plan":
        errors += [f"phòng \"{r[0]}\" dài {wlen(r[0]):.1f} ký tự, tối đa 6" for r in data["rooms"] if wlen(str(r[0])) > 6]
    if t == "ban_do":
        errors += [f"thế lực \"{v[1]}\" dài {wlen(v[1]):.1f} ký tự, tối đa 4" for v in data["palette"].values() if wlen(v[1]) > 4]
        errors += [f"nhãn mốc \"{sn.get('label')}\" dài {wlen(sn.get('label', '')):.1f} ký tự, tối đa 12"
                   for sn in data["snapshots"] if wlen(sn.get("label", "")) > 12]
    return errors


def _escape(obj):
    if isinstance(obj, str):
        return html.escape(obj, quote=True)
    if isinstance(obj, list):
        return [_escape(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _escape(v) for k, v in obj.items()}
    return obj


def build(scene, duration=None):
    """Trang HTML của một cảnh. scene: {id, template, data}. Chữ trong dữ liệu được thoát ký tự HTML.

    Các mẫu được thiết kế cho DUR giây. Cảnh ngắn hơn thì hoạt ảnh được nén cho vừa (chừa 0,3 giây cuối để dừng hình),
    cảnh đủ dài thì giữ nguyên nhịp."""
    data = _escape(copy.deepcopy(scene.get("data") or {}))
    body, js = TEMPLATES[scene["template"]](data)
    if scene["template"] in TEMPLATES_K4:
        body = K4CSS + body
    if data.get("toi") and scene["template"] in ("ledger", "compare", "day"):   # tông tối cho mẫu cũ
        body = DARK_THEME + WAVE_BG + body.replace("#fff8e8", "#16223f").replace("#e8dcc0", "#2c3a5c").replace("#d9c9a5", "#2c3a5c")
    if data.get("the_chuong") and not scene.get("giu_hinh"):   # thẻ chương phủ lên cảnh đầu chương
        cb, post = chapter_overlay(data["the_chuong"])
        body = body + cb
    else:
        post = ""
    if scene.get("giu_hinh"):
        js += HOLD_JS   # cảnh tiếp theo của một beat: hiện ngay trạng thái cuối của hoạt ảnh, không chạy lại
    return (PAGE.replace("__CSS__", CSS).replace("__ID__", scene["id"]).replace("__DUR__", f"{duration or DUR:g}")
            .replace("__FPS__", str(FPS)).replace("__BODY__", body).replace("__JS__", js).replace("__POST__", post))

