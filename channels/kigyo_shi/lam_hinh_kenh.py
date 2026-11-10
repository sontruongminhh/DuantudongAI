"""Avatar (800x800) và ảnh bìa (2560x1440) của kênh 日本一の終わり方. Chạy: .venv\\Scripts\\python.exe channels\\kigyo_shi\\lam_hinh_kenh.py

Biểu tượng: chữ 「一」 làm đường chân trời, mặt trời vàng lặn sau nét chữ ("số một đang lặn").
Ảnh bìa: vùng an toàn của YouTube là 1546x423 ở giữa (x 507–2053, y 508–931); tên kênh và câu giới thiệu nằm trong đó.
Ảnh nền chỉ dùng ảnh phạm vi công cộng trên Wikimedia Commons (không cần ghi tác giả), lấy từ các lần chạy.
Kết quả: channels/kigyo_shi/assets/avatar.png, banner.jpg
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = HERE / "assets"
PROJ = OUT / "du_an_hinh"
HF = "hyperframes@0.8.231"

# Ảnh nền (tất cả Public domain theo credit.json của từng lần chạy)
ANH = {
    "honsha": ROOT / "runs/20261104-suzuki-shoten/motion/anh/honsha_shoshitsu_1918.jpg",   # 鈴木商店本店 焼失 1918
    "kanebo": ROOT / "runs/20261104-kanebo/motion/anh/kanebo_tokyo_1908.jpg",              # 鐘紡東京工場 1908
    "kobe": ROOT / "runs/20261104-suzuki-shoten/motion/anh/kobe_bund_1885.jpg",            # 神戸 海岸通 1885頃 (Farsari)
    "toritsuke": ROOT / "runs/20261104-suzuki-shoten/motion/anh/toritsuke_1927.jpg",       # 取り付け騒ぎ 1927
}

AI, NIGHT, CREAM, GOLD = "#1f3a5f", "#101826", "#f4efe4", "#e2b65a"


def emblem(size):
    """Mặt trời lặn sau chữ 一. size: cạnh hình vuông (px)."""
    s = size
    return f"""<svg width="{s}" height="{s}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
<defs>
 <radialGradient id="sun" cx="50%" cy="60%" r="55%"><stop offset="0" stop-color="#ffe7a6"/><stop offset=".55" stop-color="{GOLD}"/>
  <stop offset="1" stop-color="#b9832c"/></radialGradient>
 <linearGradient id="sea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e2b65a" stop-opacity=".35"/>
  <stop offset="1" stop-color="#e2b65a" stop-opacity="0"/></linearGradient>
 <clipPath id="up"><rect x="0" y="0" width="100" height="58"/></clipPath>
</defs>
<circle cx="50" cy="58" r="25" fill="url(#sun)" clip-path="url(#up)"/>
<rect x="30" y="62" width="40" height="2.2" rx="1" fill="url(#sea)"/>
<rect x="36" y="68" width="28" height="1.8" rx=".9" fill="url(#sea)"/>
<rect x="42" y="73" width="16" height="1.4" rx=".7" fill="url(#sea)"/>
<path d="M14 57.2 Q30 53.6 50 54.4 Q70 55.2 84 53.4 Q88.5 53 89 55.6 Q89.3 58.4 85 59.4 Q68 61.8 50 61 Q31 60.4 16 62.2 Q11.6 62.6 11.4 59.8 Q11.3 57.8 14 57.2 Z"
 fill="{CREAM}"/>
</svg>"""


BASE_CSS = f"""*{{margin:0;padding:0;box-sizing:border-box}}
#root{{position:relative;overflow:hidden;font-family:"Noto Serif JP",serif;background:{NIGHT}}}
.abs{{position:absolute}}"""


def page(cid, w, h, body, css=""):
    return f"""<!doctype html><html lang="ja"><head><meta charset="UTF-8"/><meta name="viewport" content="width={w}, height={h}"/>
<script src="../assets/gsap.min.js"></script><style>{BASE_CSS}html,body{{width:{w}px;height:{h}px;overflow:hidden;background:{NIGHT}}}
#root{{width:{w}px;height:{h}px}}{css}</style></head><body>
<div id="root" data-composition-id="{cid}" data-start="0" data-duration="1" data-width="{w}" data-height="{h}" data-fps="24">
<div class="clip" data-start="0" data-duration="1" data-track-index="0" style="position:absolute;inset:0">{body}</div></div>
<script>window.__timelines=window.__timelines||{{}};const tl=gsap.timeline({{paused:true}});tl.to("#root",{{opacity:1,duration:1}});
window.__timelines["{cid}"]=tl;tl.seek(0);</script></body></html>"""


def avatar():
    body = f"""<div class="abs" style="inset:0;background:radial-gradient(circle at 50% 42%,#2a4a73 0%,{AI} 38%,{NIGHT} 78%)"></div>
<div class="abs" style="left:40px;top:40px">{emblem(720)}</div>"""
    return page("AVATAR", 800, 800, body)


def banner():
    def img(key, x, y, w, h, op, pos="50% 50%"):
        return (f'<div class="abs" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;background:url(../assets/anh/{key}.jpg) {pos}/cover;'
                f'filter:grayscale(1) contrast(1.05);opacity:{op};'
                f'-webkit-mask-image:linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent);'
                f'mask-image:linear-gradient(90deg,transparent,#000 22%,#000 78%,transparent)"></div>')
    body = f"""{img('kobe', -150, 0, 1150, 1440, .34)}{img('kanebo', 700, 0, 1160, 1440, .26, '50% 40%')}
{img('honsha', 1560, 0, 1150, 1440, .34, '40% 50%')}
<div class="abs" style="inset:0;background:radial-gradient(ellipse 62% 48% at 50% 50%,rgba(16,24,38,.93) 0%,rgba(16,24,38,.86) 55%,rgba(16,24,38,.55) 100%)"></div>
<div class="abs" style="left:0;top:0;width:2560px;height:1440px;background:linear-gradient(180deg,rgba(31,58,95,.35),transparent 40%,transparent 60%,rgba(31,58,95,.35))"></div>
<div class="abs" style="left:530px;top:520px">{emblem(330)}</div>
<div class="abs" style="left:880px;top:555px">
 <div style="font-size:128px;font-weight:900;color:{CREAM};letter-spacing:.04em;line-height:1"><span style="color:{GOLD}">日本一</span>の終わり方</div>
 <div style="width:760px;height:3px;background:linear-gradient(90deg,{GOLD},transparent);margin:34px 0 28px"></div>
 <div style="font-family:'Noto Sans JP',sans-serif;font-size:46px;font-weight:700;color:#e9e1cf;letter-spacing:.06em">かつて日本一だった会社は、なぜ消えたのか。</div>
 <div style="font-family:'Noto Sans JP',sans-serif;font-size:34px;color:#aeb6c4;margin-top:22px;letter-spacing:.05em">資料と数字でたどる、日本の企業史</div>
</div>"""
    return page("BANNER", 2560, 1440, body)


def render(cid, html, w, h, out):
    (PROJ / "scenes").mkdir(parents=True, exist_ok=True)
    (PROJ / "scenes" / f"{cid}.html").write_text(html, encoding="utf-8")
    env = os.environ.copy()
    env["PATH"] = r"C:\Program Files\nodejs" + os.pathsep + env.get("PATH", "")
    env.setdefault("PRODUCER_PAGE_NAVIGATION_TIMEOUT_MS", "240000")
    npx = shutil.which("npx.cmd", path=env["PATH"]) or "npx"
    mp4 = PROJ / f"{cid}.mp4"
    subprocess.run([npx, "--yes", HF, "render", "-c", f"scenes/{cid}.html", "-o", str(mp4), "--fps", "24"], cwd=PROJ, env=env,
                   check=True, capture_output=True)
    args = ["-q:v", "2"] if out.suffix == ".jpg" else []
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", "0.5", "-i", str(mp4), "-frames:v", "1", *args, str(out)], check=True)
    print(out, out.stat().st_size // 1024, "KB")


def main():
    (PROJ / "assets" / "anh").mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / "motion" / "vendor" / "gsap.min.js", PROJ / "assets" / "gsap.min.js")
    for f in (ROOT / "motion" / "mau_du_an").iterdir():
        shutil.copy2(f, PROJ / f.name)
    for k, p in ANH.items():
        shutil.copy2(p, PROJ / "assets" / "anh" / f"{k}.jpg")
    render("AVATAR", avatar(), 800, 800, OUT / "avatar.png")
    render("BANNER", banner(), 2560, 1440, OUT / "banner.jpg")


if __name__ == "__main__":
    main()
