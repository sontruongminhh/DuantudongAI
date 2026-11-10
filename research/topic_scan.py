"""So sánh các hướng chủ đề bằng YouTube Data API v3.

  python research/topic_scan.py       (cần YOUTUBE_API_KEY trong tệp .env)

Lưu ý khi đọc số liệu: API không có lượng tìm kiếm, và search.list trả về video top theo view,
nên đây là so sánh tương đối giữa các hướng, không phải quy mô thị trường.
"""
import collections
import hashlib
import json
import os
import re
import statistics as st
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
CACHE = HERE / "cache"
OUT = HERE / "data"
API = "https://www.googleapis.com/youtube/v3/"
MIN_MINUTES = 8
SMALL_CHANNEL = 100_000
HIT_VIEWS = 100_000
NEW_CHANNEL_DAYS = 548  # 18 tháng

NICHES = {
    "Sinh tồn lạnh, vùng cực": {
        "queries": ["how did people survive winter history", "arctic expedition survival story history",
                    "how did vikings survive winter"],
        "title": r"winter|cold|freez|frozen|arctic|antarctic|polar|snow|ice\b|blizzard|-\d+\s*°|−\d+"},
    "Biển, đắm tàu": {
        "queries": ["shipwreck survival true story history", "how did sailors survive at sea history",
                    "lighthouse keepers history survive"],
        "title": r"sea\b|sailor|ship|shipwreck|ocean|lighthouse|whaler|pirate|castaway|voyage|navy"},
    "Núi, độ cao": {
        "queries": ["how did people survive mountains history", "himalaya sherpa history survival documentary",
                    "alpine monks history winter"],
        "title": r"mountain|everest|himalaya|sherpa|alps|alpine|altitude|andes|tibet"},
    "Đoàn thám hiểm mất tích": {
        "queries": ["lost expedition mystery documentary", "vanished expedition history what happened",
                    "doomed expedition true story"],
        "title": r"expedition|vanish|lost|disappear|doomed|missing|mystery"},
    "Một ngày thời xưa": {
        "queries": ["what did medieval people do all day", "daily life in medieval times", "a day in the life ancient"],
        "title": r"day|daily|life|lived?|what did|actually"},
    "Lịch sử ru ngủ": {
        "queries": ["boring history for sleep", "history documentary to fall asleep to", "sleepy history bedtime"],
        "title": r"sleep|bedtime|asleep|boring|relax"},
    "Nghề xưa khắc nghiệt": {
        "queries": ["worst jobs in history", "most dangerous jobs in history documentary", "brutal jobs medieval"],
        "title": r"job|work|profession|trade|miner|whaler|keeper|career"},
    "Khai hoang, miền Tây": {
        "queries": ["how did pioneers survive winter", "frontier life history documentary", "donner party history"],
        "title": r"pioneer|frontier|settler|wild west|homestead|oregon|donner|cabin|prairie|gold rush"},
    "Văn minh bí ẩn": {
        "queries": ["lost civilization documentary", "ancient mysteries documentary", "history of ancient civilization"],
        "title": r"civili[sz]ation|ancient|mystery|lost|empire|ruin|egypt|maya|inca"},
    "Đời lính": {
        "queries": ["how did soldiers survive in war history", "life of a soldier history documentary",
                    "roman legion daily life"],
        "title": r"soldier|legion|trench|army|knight|warrior|samurai|troops"},
    "Thảm họa lịch sử": {
        "queries": ["worst disaster in history documentary", "historic disaster explained", "forgotten disaster history"],
        "title": r"disaster|catastrophe|tragedy|collapse|eruption|flood|sinking|explosion"},
    "Sống sót thời tiền sử": {
        "queries": ["how long would you survive prehistoric", "how did ancient humans survive", "ice age humans survive"],
        "title": r"prehistoric|ice age|stone age|caveman|ancient humans?|early humans?|neanderthal"},
}


class Quota(Exception):
    pass


def api_key():
    """Lấy khóa từ biến môi trường, không có thì đọc tệp .env ở thư mục dự án."""
    key = os.environ.get("YOUTUBE_API_KEY")
    env_file = HERE.parent / ".env"
    if not key and env_file.is_file():
        for line in env_file.read_text(encoding="utf-8-sig").splitlines():
            name, _, value = line.partition("=")
            if name.strip() == "YOUTUBE_API_KEY":
                key = value.strip().strip("\"'")
    if not key:
        sys.exit("Thiếu YOUTUBE_API_KEY trong biến môi trường hoặc tệp .env")
    return key


class YT:
    def __init__(self, key):
        self.session = requests.Session()
        self.session.headers["X-Goog-Api-Key"] = key  # khóa không nằm trong URL, cache hay log
        self.calls = collections.Counter()
        CACHE.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def cache_path(endpoint, params):
        raw = json.dumps([datetime.now().strftime("%Y-%m-%d"), endpoint, sorted(params.items())], ensure_ascii=False)
        return CACHE / (hashlib.sha1(raw.encode()).hexdigest() + ".json")

    def get(self, endpoint, **params):
        path = self.cache_path(endpoint, params)
        if path.exists():
            return json.loads(path.read_text("utf-8"))
        r = self.session.get(API + endpoint, params=params, timeout=30)
        self.calls[endpoint] += 1
        if not r.ok:
            err = r.json().get("error", {}) if "json" in r.headers.get("content-type", "") else {}
            reason = (err.get("errors") or [{}])[0].get("reason", "")
            if "quota" in reason.lower() or "rateLimit" in reason:
                raise Quota(reason)
            raise RuntimeError(f"{endpoint}: HTTP {r.status_code} {reason} {err.get('message', '')[:200]}")
        data = r.json()
        path.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
        return data

    def search(self, q, after):
        return [i["id"]["videoId"] for i in self.get(
            "search", part="id", type="video", q=q, order="viewCount", publishedAfter=after, regionCode="US",
            relevanceLanguage="en", maxResults=50, videoDuration="any").get("items", [])]

    def batched(self, endpoint, part, ids):
        ids, out = list(ids), []
        for i in range(0, len(ids), 50):
            out += self.get(endpoint, part=part, id=",".join(ids[i:i + 50]), maxResults=50).get("items", [])
        return out


def minutes(iso):
    m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return d * 1440 + h * 60 + mi + s / 60


def parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def is_english(title):
    letters = re.findall(r"[^\W\d_]", title)
    return bool(letters) and sum(c.isascii() for c in letters) / len(letters) > 0.9


def collect(yt, now):
    after_year = (now - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    after_quarter = (now - timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%SZ")
    found = collections.defaultdict(set)
    for name, cfg in NICHES.items():
        for q in cfg["queries"]:
            for after in (after_year, after_quarter):
                for vid in yt.search(q, after):
                    found[vid].add(name)
    videos = yt.batched("videos", "snippet,statistics,contentDetails", found)
    channels = {c["id"]: c for c in yt.batched(
        "channels", "snippet,statistics", {v["snippet"]["channelId"] for v in videos})}
    rows = []
    for v in videos:
        sn, stats = v["snippet"], v["statistics"]
        ch = channels.get(sn["channelId"])
        dur = minutes(v["contentDetails"]["duration"])
        if not ch or dur < MIN_MINUTES or not is_english(sn["title"]):
            continue
        published = parse(sn["publishedAt"])
        views = int(stats.get("viewCount", 0))
        age = max((now - published).total_seconds() / 86400, 1)
        for name in found[v["id"]]:
            if re.search(NICHES[name]["title"], sn["title"], re.I):
                rows.append({
                    "huong": name, "id": v["id"], "tieu_de": sn["title"], "kenh": sn["channelTitle"],
                    "kenh_id": sn["channelId"], "sub": int(ch["statistics"].get("subscriberCount", 0) or 0),
                    "tuoi_kenh_ngay": (now - parse(ch["snippet"]["publishedAt"])).days, "view": views,
                    "view_ngay": views / age, "tuoi_ngay": age, "phut": round(dur, 1),
                    "ngay_dang": sn["publishedAt"][:10], "binh_luan": int(stats.get("commentCount", 0) or 0)})
    return rows


def summarize(rows):
    out = []
    for name in NICHES:
        g = [r for r in rows if r["huong"] == name]
        if not g:
            out.append({"huong": name, "so_video": 0})
            continue
        recent = [r for r in g if r["tuoi_ngay"] <= 90]
        by_channel = collections.Counter()
        for r in g:
            by_channel[r["kenh"]] += r["view"]
        total = sum(by_channel.values()) or 1
        small_hits = [r for r in g if r["sub"] < SMALL_CHANNEL and r["view"] >= HIT_VIEWS]
        new_hits = [r for r in g if r["tuoi_kenh_ngay"] <= NEW_CHANNEL_DAYS and r["view"] >= HIT_VIEWS]
        out.append({
            "huong": name, "so_video": len(g), "so_kenh": len(by_channel),
            "view_trung_vi": round(st.median(r["view"] for r in g)),
            "view_ngay_trung_vi": round(st.median(r["view_ngay"] for r in g)),
            "video_90_ngay": len(recent),
            "view_ngay_90_trung_vi": round(st.median(r["view_ngay"] for r in recent)) if recent else 0,
            "ty_le_hit_kenh_nho": round(len(small_hits) / len(g), 3),
            "so_kenh_nho_co_hit": len({r["kenh"] for r in small_hits}),
            "so_kenh_moi_co_hit": len({r["kenh"] for r in new_hits}),
            "top3_chiem": round(sum(v for _, v in by_channel.most_common(3)) / total, 3),
            "phut_trung_vi": round(st.median(r["phut"] for r in g), 1),
            "kenh_nho_vi_du": sorted({(r["kenh"], r["sub"]) for r in small_hits}, key=lambda x: x[1])[:6],
            "video_tot": [(r["tieu_de"], r["view"], r["kenh"], r["sub"]) for r in
                          sorted(g, key=lambda r: -r["view"])[:5]],
        })
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.now(timezone.utc)
    yt = YT(api_key())
    try:
        rows = collect(yt, now)
    except Quota as e:
        sys.exit(f"Hết hạn mức ({e}). Kết quả đã lấy được vẫn nằm trong cache, chạy lại sau.")
    except RuntimeError as e:
        sys.exit(f"LỖI: {e}")
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%d")
    summary = summarize(rows)
    (OUT / f"topic_scan_{stamp}.json").write_text(
        json.dumps({"ngay": now.isoformat(), "tong_hop": summary, "video": rows}, ensure_ascii=False, indent=1), "utf-8")
    print(f"Lệnh gọi API thật: {dict(yt.calls)} · {len(rows)} dòng video")
    head = "Hướng | video | kênh | view TV | view/ngày TV | 90 ngày: video, view/ngày TV | hit kênh nhỏ % (số kênh) | kênh mới có hit | top3 | phút"
    print(head)
    for s in sorted(summary, key=lambda x: -x.get("view_ngay_90_trung_vi", 0)):
        if not s["so_video"]:
            print(s["huong"], "| không có dữ liệu")
            continue
        print(f"{s['huong']} | {s['so_video']} | {s['so_kenh']} | {s['view_trung_vi']:,} | {s['view_ngay_trung_vi']:,} | "
              f"{s['video_90_ngay']}, {s['view_ngay_90_trung_vi']:,} | {s['ty_le_hit_kenh_nho']:.0%} ({s['so_kenh_nho_co_hit']}) | "
              f"{s['so_kenh_moi_co_hit']} | {s['top3_chiem']:.0%} | {s['phut_trung_vi']}")


if __name__ == "__main__":
    main()
