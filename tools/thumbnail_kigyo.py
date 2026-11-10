"""Thumbnail kênh 4: ảnh nền trụ sở (đen trắng, phủ chàm), chân dung đen trắng bên phải, tên công ty, chữ hỏi lớn, dải dưới.

  python tools/thumbnail_kigyo.py runs/<run>            đọc runs/<run>/publish/thumb.json, ghi publish/thumbnail.jpg

thumb.json:
  {"ten": "カネボウ", "kicker": "戦前の売上日本一", "hoi": ["なぜ", "消えた？"], "duoi": "国家予算の1割を売り上げたのに…",
   "chan_dung": "muto_sanji.jpg", "cd_x": 50, "cd_y": 20, "nen": "kanebo_tokyo.jpg", "nen_x": 50, "nen_y": 50}
Ảnh lấy từ runs/<run>/motion/anh. Màu riêng của kênh (chàm, trắng, vàng kim), không dùng đỏ–vàng của kênh mẫu.
"""
import html
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GSAP = ROOT / "motion" / "vendor" / "gsap.min.js"
HF = "hyperframes@0.8.231"

PAGE = """<!doctype html><html lang="ja"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1280, height=720"/>
<script src="../assets/gsap.min.js"></script><style>
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1280px;height:720px;overflow:hidden;background:#0d1626}
#root{position:relative;width:1280px;height:720px;font-family:"Noto Sans JP",sans-serif;overflow:hidden}
.a{position:absolute}
.bg{left:0;top:0;width:1280px;height:720px;background:url(../assets/anh/__NEN__) __NX__% __NY__%/cover no-repeat;filter:grayscale(1) contrast(1.1) brightness(.55)}
.tint{left:0;top:0;width:1280px;height:720px;background:linear-gradient(90deg,rgba(13,22,38,.92) 0%,rgba(13,22,38,.7) 48%,rgba(13,22,38,.25) 100%)}
.cd{right:0;top:0;width:560px;height:720px;background:url(../assets/anh/__CD__) __CX__% __CY__%/cover no-repeat;
 filter:grayscale(1) contrast(1.15) brightness(1.05);-webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 30%);mask-image:linear-gradient(90deg,transparent 0%,#000 30%)}
.ten{left:46px;top:40px;background:#f4efe4;color:#132443;font-weight:900;font-size:64px;padding:6px 26px 10px;border-radius:4px;
 font-family:"Noto Serif JP",serif;box-shadow:0 6px 18px rgba(0,0,0,.45)}
.kick{left:50px;top:150px;color:#e9d39a;font-size:36px;font-weight:700;letter-spacing:.04em;text-shadow:0 2px 6px #000}
.q{left:40px;top:198px;font-family:"Noto Serif JP",serif;font-weight:900;font-size:150px;line-height:1.02;color:#fff;
 -webkit-text-stroke:6px #0d1626;paint-order:stroke fill;text-shadow:0 8px 24px rgba(0,0,0,.6)}
.q .g{color:#f2c75c}
.duoi{left:0;top:592px;width:1280px;height:128px;background:linear-gradient(90deg,#132443 0%,#1f3a5f 70%,rgba(31,58,95,.85) 100%);
 border-top:5px solid #c99a3c;display:flex;align-items:center;padding-left:48px;color:#fff;font-size:54px;font-weight:900;letter-spacing:.02em}
</style></head><body>
<div id="root" data-composition-id="T" data-start="0" data-duration="1" data-width="1280" data-height="720" data-fps="24">
<div id="stage" class="clip" data-start="0" data-duration="1" data-track-index="0" style="position:absolute;inset:0">
<div class="a bg"></div><div class="a tint"></div><div class="a cd"></div>
<div class="a ten">__TEN__</div><div class="a kick">__KICK__</div>
<div class="a q">__Q__</div>
<div class="a duoi">__DUOI__</div></div></div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});tl.to("#root",{opacity:1,duration:1});
window.__timelines["T"]=tl;tl.seek(0);</script></body></html>"""


# Kiểu "noi_bat" (05/11/2026, sau khi so với 18 thumbnail nhiều view của ngách): chữ móc rất to viền dày,
# nền giữ màu tông ấm, mặt to sát khung, dải dưới vàng kim (khác dải đỏ của kênh mẫu).
PAGE_NOI_BAT = """<!doctype html><html lang="ja"><head><meta charset="UTF-8"/><meta name="viewport" content="width=1280, height=720"/>
<script src="../assets/gsap.min.js"></script><style>
*{margin:0;padding:0;box-sizing:border-box}html,body{width:1280px;height:720px;overflow:hidden;background:#0b1220}
#root{position:relative;width:1280px;height:720px;font-family:"Noto Sans JP",sans-serif;overflow:hidden}
.a{position:absolute}
.bg{left:0;top:0;width:1280px;height:720px;background:url(../assets/anh/__NEN__) __NX__% __NY__%/cover no-repeat;
 filter:__BGF__}
.tint{left:0;top:0;width:1280px;height:720px;background:linear-gradient(90deg,__TINT__ 0%,__TINT2__ 42%,rgba(8,14,28,.05) 76%),
 radial-gradient(ellipse at 70% 45%,rgba(0,0,0,0) 40%,rgba(0,0,0,.55) 100%)}
.cd{right:-20px;top:0;width:600px;height:600px;background:url(../assets/anh/__CD__) __CX__% __CY__%/__CZ__% auto no-repeat;
 filter:grayscale(1) sepia(.18) contrast(1.3) brightness(1.08);
 -webkit-mask-image:linear-gradient(90deg,transparent 0%,#000 22%),linear-gradient(0deg,transparent 0%,#000 12%);-webkit-mask-composite:source-in;
 mask-image:linear-gradient(90deg,transparent 0%,#000 22%);mask-composite:intersect}
.ten{left:40px;top:30px;background:#f4efe4;color:#0b1a36;font-weight:900;font-size:__TS__px;padding:2px 22px 8px;border-radius:4px;
 font-family:"Noto Serif JP",serif;box-shadow:0 6px 18px rgba(0,0,0,.5)}
.hero{left:34px;top:128px;font-family:"Noto Serif JP",serif;font-weight:900;font-size:__HS__px;line-height:1.08;color:__MM__;
 -webkit-text-stroke:12px #070c18;paint-order:stroke fill;text-shadow:0 6px 0 #070c18,0 10px 26px rgba(0,0,0,.7);letter-spacing:-.02em}
.q{left:34px;top:__QT__px;font-family:"Noto Serif JP",serif;font-weight:900;font-size:__QS__px;line-height:1;color:__MH__;
 -webkit-text-stroke:12px #070c18;paint-order:stroke fill;text-shadow:0 6px 0 #070c18,0 0 30px rgba(255,190,40,.45);letter-spacing:-.03em}
.duoi{left:0;top:600px;width:1280px;height:120px;background:__DN__;
 border-top:6px solid #070c18;display:flex;align-items:center;padding-left:40px;color:__DC__;font-size:58px;font-weight:900;letter-spacing:.01em}
</style></head><body>
<div id="root" data-composition-id="T" data-start="0" data-duration="1" data-width="1280" data-height="720" data-fps="24">
<div id="stage" class="clip" data-start="0" data-duration="1" data-track-index="0" style="position:absolute;inset:0">
<div class="a bg"></div><div class="a tint"></div><div class="a cd"></div>
<div class="a ten">__TEN__</div><div class="a hero">__HERO__</div><div class="a q">__Q__</div>
<div class="a duoi">__DUOI__</div></div></div>
<script>window.__timelines=window.__timelines||{};const tl=gsap.timeline({paused:true});tl.to("#root",{opacity:1,duration:1});
window.__timelines["T"]=tl;tl.seek(0);</script></body></html>"""


TONG = {  # tông nền: bộ lọc ảnh, màu phủ đậm (trái) và màu phủ giữa
    "am": ("sepia(.3) saturate(1.4) contrast(1.15) brightness(.78)", "rgba(8,14,28,.9)", "rgba(8,14,28,.62)"),
    "do": ("sepia(.6) saturate(2.2) hue-rotate(-18deg) contrast(1.2) brightness(.7)", "rgba(40,6,4,.9)", "rgba(60,10,6,.55)"),
    "mau": ("saturate(1.25) contrast(1.1) brightness(.85)", "rgba(8,14,28,.88)", "rgba(8,14,28,.5)"),
}
DUOI = {"vang": ("linear-gradient(90deg,#ffd75e 0%,#f2b93a 60%,#e2a22c 100%)", "#0b1a36"),
        "cham": ("linear-gradient(90deg,#0b1a36 0%,#1c3664 100%)", "#ffd75e"),
        "trang": ("linear-gradient(90deg,#fbf7ee 0%,#efe6d2 100%)", "#8e1b12")}


def build_noi_bat(cfg):
    """thumb.json thêm: "kieu": "noi_bat", "moc": ["大倉財閥"] (chủ ngữ rất to, 1–2 dòng, ≤ 6 ký tự mỗi dòng),
    "ten" là hộp nhãn trên cùng (≤ 16 ký tự, ví dụ 「帝国ホテル・大成建設の生みの親」).
    Chữ móc + chữ hỏi phải đúng nghĩa: thứ còn tồn tại hôm nay không được đứng làm chủ ngữ của 「なぜ消えた？」.
    "hoi": ["なぜ消えた？"], "cd_zoom": 130 (phóng mặt, % chiều rộng khung chân dung),
    "tong": am|do|mau (tông nền), "mau_moc"/"mau_hoi" (màu chữ), "duoi_mau": vang|cham|trang, "moc_co"/"hoi_co" (cỡ chữ)."""
    e = html.escape
    moc = cfg["moc"]
    dai = max(len(m) for m in moc)
    hs = cfg.get("moc_co") or (150 if len(moc) == 1 and dai <= 5 else 112 if dai <= 6 else 96)
    qt = 128 + int(hs * 1.08 * len(moc)) + 6
    return (PAGE_NOI_BAT.replace("__NEN__", cfg["nen"]).replace("__NX__", str(cfg.get("nen_x", 50)))
            .replace("__NY__", str(cfg.get("nen_y", 50))).replace("__CD__", cfg["chan_dung"])
            .replace("__CX__", str(cfg.get("cd_x", 50))).replace("__CY__", str(cfg.get("cd_y", 20)))
            .replace("__CZ__", str(cfg.get("cd_zoom", 120))).replace("__TEN__", e(cfg["ten"]))
            .replace("__TS__", str(58 if len(cfg["ten"]) <= 8 else 42)).replace("__HERO__", "<br>".join(e(m) for m in moc)).replace("__HS__", str(hs))
            .replace("__QT__", str(qt)).replace("__QS__", str(cfg.get("hoi_co", 118)))
            .replace("__Q__", "<br>".join(e(t) for t in cfg["hoi"])).replace("__DUOI__", e(cfg["duoi"]))
            .replace("__BGF__", TONG[cfg.get("tong", "am")][0]).replace("__TINT__", TONG[cfg.get("tong", "am")][1])
            .replace("__TINT2__", TONG[cfg.get("tong", "am")][2]).replace("__MM__", cfg.get("mau_moc", "#fff"))
            .replace("__MH__", cfg.get("mau_hoi", "#ffcf3f")).replace("__DN__", DUOI[cfg.get("duoi_mau", "vang")][0])
            .replace("__DC__", DUOI[cfg.get("duoi_mau", "vang")][1]))


def build(cfg):
    if cfg.get("kieu") == "noi_bat":
        return build_noi_bat(cfg)
    e = html.escape
    lines = cfg["hoi"]
    q = "<br>".join((f'<span class="g">{e(t)}</span>' if i == len(lines) - 1 else e(t)) for i, t in enumerate(lines))
    return (PAGE.replace("__NEN__", cfg["nen"]).replace("__NX__", str(cfg.get("nen_x", 50))).replace("__NY__", str(cfg.get("nen_y", 50)))
            .replace("__CD__", cfg["chan_dung"]).replace("__CX__", str(cfg.get("cd_x", 50))).replace("__CY__", str(cfg.get("cd_y", 20)))
            .replace("__TEN__", e(cfg["ten"])).replace("__KICK__", e(cfg.get("kicker", ""))).replace("__Q__", q)
            .replace("__DUOI__", e(cfg["duoi"])))


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    run = Path(sys.argv[1]).resolve()
    ten_cfg = sys.argv[2] if len(sys.argv) > 2 else "thumb.json"  # thử phương án: thumb_A.json -> thumbnail_A.jpg
    cfg = json.loads((run / "publish" / ten_cfg).read_text(encoding="utf-8"))
    proj = run / "publish" / "thumb_du_an"
    (proj / "scenes").mkdir(parents=True, exist_ok=True)
    (proj / "assets" / "anh").mkdir(parents=True, exist_ok=True)
    shutil.copy2(GSAP, proj / "assets" / "gsap.min.js")
    for f in (ROOT / "motion" / "mau_du_an").iterdir():
        shutil.copy2(f, proj / f.name)
    for key in ("nen", "chan_dung"):
        shutil.copy2(run / "motion" / "anh" / cfg[key], proj / "assets" / "anh" / cfg[key])
    (proj / "scenes" / "T.html").write_text(build(cfg), encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs" + os.pathsep + env.get("PATH", "")
    npx = shutil.which("npx.cmd", path=env["PATH"]) or "npx"
    mp4 = proj / "T.mp4"
    subprocess.run([npx, "--yes", HF, "render", "-c", "scenes/T.html", "-o", str(mp4), "--fps", "24"], cwd=proj, env=env,
                   check=True, capture_output=True)
    out = run / "publish" / ten_cfg.replace("thumb", "thumbnail").replace(".json", ".jpg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(mp4), "-frames:v", "1", "-q:v", "2", str(out)], check=True)
    print(out, out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
