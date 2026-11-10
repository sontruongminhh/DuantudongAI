"""Quét thị trường ngách "công ty / gia tộc / tài phiệt Nhật đã biến mất" bằng YouTube Data API v3.

  python -I research/quet_thi_truong.py            (cần YOUTUBE_API_KEY trong .env)

Cách làm: tìm video dài (từ 4 phút, đăng trong 6 tháng, tiếng Nhật) theo các từ khóa dưới, cộng các
video hạt giống người dùng gửi, gom theo kênh. Mỗi kênh lấy 30 video mới nhất để tính view trung vị,
video top, tỷ lệ view/sub. Chỉ giữ kênh có ít nhất 3 video đúng ngách (hoặc là hạt giống).
Kết quả: research/data/thi_truong_kigyo_<ngày>.json. Dựng bảng: research/lam_bang_thi_truong.py.
Tốn khoảng 5.000 đơn vị quota (mỗi lần search 100), lần chạy lại dùng bộ nhớ đệm research/cache/.
"""
import hashlib
import json
import re
import statistics as st
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CACHE = HERE / "cache"
OUT = HERE / "data"
API = "https://www.googleapis.com/youtube/v3/"
NGAY = datetime.now(timezone.utc).strftime("%Y%m%d")

TU_KHOA = [
    "なぜ消えた 会社", "なぜ消えたのか 企業", "倒産 なぜ", "破綻 その後", "消えた企業",
    "財閥 その後", "財閥 解体", "家のその後", "一族のその後", "創業者 生涯", "創業家 没落",
    "財閥 創業者", "女帝 商店", "日本一の会社 消えた", "名門企業 消滅", "老舗 倒産 理由",
    "実業家 生涯", "大富豪 末路", "百貨店 なぜ消えた", "映画会社 倒産", "商社 破綻",
    "経営破綻 解説", "企業 栄枯盛衰", "社史",
]
# Video người dùng gửi hoặc đã biết là đối thủ (05/11/2026)
HAT_GIONG = ["dnTI_R4d_bc", "FN1fxz8HdtU"]
# Kênh luôn giữ (đã theo dõi trước đó), tìm theo handle
KENH_THEO_DOI = ["@sayonara-company"]

NGACH = re.compile(r"会社|企業|財閥|倒産|破綻|創業|社長|商店|一族|家の|経営|百貨店|ブランド|メーカー|銀行|商社|"
                   r"実業家|富豪|コンツェルン|グループ|消えた|没落|その後|生涯")


def khoa():
    for dong in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if dong.startswith("YOUTUBE_API_KEY="):
            return dong.split("=", 1)[1].strip()
    sys.exit("Thiếu YOUTUBE_API_KEY trong .env")


KEY = khoa()


def goi(duong, **ts):
    CACHE.mkdir(exist_ok=True)
    ma = hashlib.sha1((duong + json.dumps(ts, sort_keys=True)).encode()).hexdigest()[:16]
    f = CACHE / f"{duong}_{ma}.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    r = requests.get(API + duong, params={**ts, "key": KEY}, timeout=30)
    r.raise_for_status()
    f.write_text(r.text, encoding="utf-8")
    return r.json()


def theo_lo(ids, n=50):
    ids = list(ids)
    for i in range(0, len(ids), n):
        yield ids[i:i + n]


def giay(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * k for x, k in zip(m.groups(), (3600, 60, 1))) if m else 0


def lay_video(ids):
    ra = {}
    for lo in theo_lo(ids):
        for v in goi("videos", part="snippet,statistics,contentDetails", id=",".join(lo)).get("items", []):
            ra[v["id"]] = {
                "id": v["id"], "tieu_de": v["snippet"]["title"], "kenh_id": v["snippet"]["channelId"],
                "kenh": v["snippet"]["channelTitle"], "ngay": v["snippet"]["publishedAt"][:10],
                "view": int(v["statistics"].get("viewCount", 0)), "like": int(v["statistics"].get("likeCount", 0)),
                "binh_luan": int(v["statistics"].get("commentCount", 0)), "giay": giay(v["contentDetails"].get("duration")),
            }
    return ra


def main():
    sau = (datetime.now(timezone.utc) - timedelta(days=183)).strftime("%Y-%m-%dT00:00:00Z")
    tim = {}
    for tk in TU_KHOA:
        for dai in ("medium", "long"):
            kq = goi("search", part="snippet", q=tk, type="video", videoDuration=dai, order="viewCount",
                     publishedAfter=sau, regionCode="JP", relevanceLanguage="ja", maxResults=50)
            for it in kq.get("items", []):
                tim.setdefault(it["id"]["videoId"], set()).add(tk)
    print(f"{len(tim)} video từ {len(TU_KHOA)} từ khóa")
    vids = lay_video(set(tim) | set(HAT_GIONG))
    kenh_ids = {v["kenh_id"] for v in vids.values()}
    for h in KENH_THEO_DOI:
        it = goi("channels", part="id", forHandle=h).get("items", [])
        kenh_ids |= {x["id"] for x in it}
    hat_kenh = {vids[i]["kenh_id"] for i in HAT_GIONG if i in vids}

    kenh = {}
    for lo in theo_lo(kenh_ids):
        for c in goi("channels", part="snippet,statistics,contentDetails", id=",".join(lo)).get("items", []):
            kenh[c["id"]] = c
    ket = []
    for cid, c in kenh.items():
        up = c["contentDetails"]["relatedPlaylists"]["uploads"]
        try:
            pl = goi("playlistItems", part="contentDetails", playlistId=up, maxResults=30)
        except requests.HTTPError:
            continue
        gan = lay_video([x["contentDetails"]["videoId"] for x in pl.get("items", [])])
        dai = [v for v in gan.values() if v["giay"] >= 240]
        dung = [v for v in dai if NGACH.search(v["tieu_de"])]
        theo_doi = cid in hat_kenh or c["snippet"].get("customUrl", "").lower() in [h.lower() for h in KENH_THEO_DOI]
        if len(dung) < 3 and not theo_doi:
            continue
        sub = int(c["statistics"].get("subscriberCount", 0) or 0)
        top = max(dai, key=lambda v: v["view"]) if dai else None
        trung_vi = int(st.median([v["view"] for v in dai])) if dai else 0
        moi30 = [v for v in dai if v["ngay"] >= (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")]
        ket.append({
            "kenh_id": cid, "ten": c["snippet"]["title"], "handle": c["snippet"].get("customUrl", ""),
            "lap": c["snippet"]["publishedAt"][:10], "sub": sub,
            "tong_view": int(c["statistics"].get("viewCount", 0)), "so_video": int(c["statistics"].get("videoCount", 0)),
            "video_dai_gan": len(dai), "dung_ngach": len(dung), "dang_30_ngay": len(moi30),
            "view_trung_vi": trung_vi, "view_tren_sub": round(trung_vi / sub, 2) if sub else None,
            "phut_trung_vi": round(st.median([v["giay"] for v in dai]) / 60) if dai else 0,
            "top": top, "hat_giong": theo_doi,
            "video_tim_thay": sorted([v for v in vids.values() if v["kenh_id"] == cid], key=lambda v: -v["view"])[:5],
            "gan_day": sorted(dai, key=lambda v: v["ngay"], reverse=True)[:12],
        })
    ket.sort(key=lambda k: -(k["top"]["view"] if k["top"] else 0))
    OUT.mkdir(exist_ok=True)
    f = OUT / f"thi_truong_kigyo_{NGAY}.json"
    f.write_text(json.dumps({"ngay": NGAY, "tu_khoa": TU_KHOA, "hat_giong": HAT_GIONG,
                             "video_hat_giong": [vids[i] for i in HAT_GIONG if i in vids], "kenh": ket},
                            ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(kenh)} kênh, giữ {len(ket)} kênh đúng ngách → {f}")


if __name__ == "__main__":
    main()
