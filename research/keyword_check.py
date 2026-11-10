"""Kiểm tra từ khóa ứng viên: video top 12 tháng và gợi ý tìm kiếm.

  python research/keyword_check.py    (cần YOUTUBE_API_KEY trong tệp .env)

API v3 không có lượng tìm kiếm. Gợi ý tìm kiếm chỉ cho biết cụm từ có người tìm, không cho biết bao nhiêu.
"""
import json
import re
import statistics as st
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_scan import MIN_MINUTES, OUT, YT, api_key, is_english, minutes

TOP_N = 20
KEYWORDS = [
    "how did people survive winter", "how did people stay warm before electricity",
    "how did people sleep in winter before heating", "how did ice age humans survive", "life in the ice age",
    "how did medieval people survive winter", "how did samurai survive winter", "how did roman soldiers survive winter",
    "how did vikings survive winter", "how did people survive arctic winter", "castle in winter medieval life",
    "ice age history for sleep",
]
SEEDS = ["how did people survive", "how did people stay warm", "how did people sleep before", "how did ice age",
         "life in the ice age", "how did medieval people", "before central heating", "how did samurai",
         "survive winter history", "history for sleep ice age"]
SUGGEST = "https://suggestqueries.google.com/complete/search"


def suggestions(session, seed):
    r = session.get(SUGGEST, params={"client": "firefox", "ds": "yt", "q": seed, "hl": "en", "gl": "US"}, timeout=20)
    r.raise_for_status()
    return json.loads(r.content.decode("utf-8", "replace"))[1]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.now(timezone.utc)
    after = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    yt = YT(api_key())
    results = []
    for kw in KEYWORDS:
        ids = yt.search(kw, after)
        vids = [v for v in yt.batched("videos", "snippet,statistics,contentDetails", ids)
                if minutes(v["contentDetails"].get("duration")) >= MIN_MINUTES and is_english(v["snippet"]["title"])][:TOP_N]
        if not vids:
            results.append({"tu_khoa": kw, "so_video": 0})
            continue
        chans = {c["id"]: c for c in yt.batched("channels", "statistics", {v["snippet"]["channelId"] for v in vids})}
        sub = lambda v: int(chans.get(v["snippet"]["channelId"], {}).get("statistics", {}).get("subscriberCount", 0) or 0)
        view = lambda v: int(v["statistics"].get("viewCount", 0))
        words = [w for w in re.findall(r"[a-z]+", kw.lower()) if len(w) > 3]
        exact = sum(all(w in v["snippet"]["title"].lower() for w in words) for v in vids)
        results.append({
            "tu_khoa": kw, "so_video": len(vids), "view_tv": st.median(view(v) for v in vids),
            "video_100k": sum(view(v) >= 100_000 for v in vids),
            "kenh_nho_100k": sum(view(v) >= 100_000 and sub(v) < 100_000 for v in vids),
            "sub_tv": st.median(sub(v) for v in vids), "khop_tieu_de": exact,
            "video_tot": max(((view(v), v["snippet"]["title"][:70]) for v in vids))})

    session = requests.Session()
    suggested = {}
    for seed in SEEDS:
        try:
            suggested[seed] = suggestions(session, seed)
        except (requests.RequestException, ValueError, IndexError) as e:
            suggested[seed] = [f"LỖI: {type(e).__name__}"]

    (OUT / f"keyword_check_{now.strftime('%Y%m%d')}.json").write_text(
        json.dumps({"ngay": now.isoformat(), "tu_khoa": results, "goi_y": suggested}, ensure_ascii=False, indent=1), "utf-8")
    print(f"Lệnh gọi API thật: {dict(yt.calls)}")
    print("Từ khóa | video | view TV | >=100k | kênh nhỏ >=100k | sub TV | khớp tiêu đề")
    for r in sorted(results, key=lambda x: -x.get("view_tv", 0)):
        if r["so_video"]:
            print(f"{r['tu_khoa']} | {r['so_video']} | {r['view_tv']:,.0f} | {r['video_100k']} | {r['kenh_nho_100k']} | "
                  f"{r['sub_tv']:,.0f} | {r['khop_tieu_de']}")
    for seed, items in suggested.items():
        print(f"[{seed}] " + "; ".join(items[:8]))


if __name__ == "__main__":
    main()
