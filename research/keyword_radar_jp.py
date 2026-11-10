"""Quét từ khóa tiếng Nhật cho kênh lịch sử, đời sống xưa, bằng YouTube Data API v3 và gợi ý tìm kiếm.

  python research/keyword_radar_jp.py                        (cần YOUTUBE_API_KEY trong tệp .env)
  python research/keyword_radar_jp.py --cache <publishedAfter>   (chỉ đọc kết quả tìm kiếm đã lưu trong ngày, không tốn hạn mức tìm kiếm)
  python research/keyword_radar_jp.py --after <publishedAfter>   (dùng lại mốc cũ để các tìm kiếm đã lưu không bị gọi lại)

Mỗi từ khóa tốn 100 đơn vị hạn mức. API v3 không có lượng tìm kiếm và search.list xếp theo view,
nên đây là so sánh tương đối giữa các từ khóa, có thiên lệch về video thắng.
"""
import collections
import json
import re
import statistics as st
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from topic_scan import OUT, YT, Quota, api_key, minutes, parse

DAYS = 365
MIN_MINUTES = 5
HIT_VIEWS = 50_000
SMALL_CHANNEL = 50_000
NEW_CHANNEL_DAYS = 548  # 18 tháng
SUGGEST = "https://suggestqueries.google.com/complete/search"

KEYWORDS = {
    "A. Edo mùa đông, ban đêm": [
        "江戸時代 冬", "江戸時代 暖房", "江戸時代 夜 暮らし", "江戸時代 布団", "昔の日本 冬 暖房", "日本人 寝床 歴史",
    ],
    "B. Nhà ở, đi đường": [
        "江戸 長屋 暮らし", "江戸時代 旅籠", "江戸時代 旅 費用", "江戸時代 街道 旅", "木賃宿 江戸",
    ],
    "C. Đời sống thường ngày Edo": [
        "江戸時代 風呂", "江戸時代 トイレ", "江戸時代 食事 庶民", "江戸時代 一日", "江戸時代 物価", "江戸時代 仕事 庶民",
    ],
    "D. Chiến Quốc": [
        "戦国時代 暮らし", "戦国 足軽 食事", "戦国 大軍 野営", "戦国時代 農民 生活",
    ],
    "E. Người nước ngoài nhìn Nhật": [
        "外国人が見た日本 江戸", "宣教師 フロイス 戦国", "イザベラ・バード 日本奥地紀行", "シーボルト 日本 見た", "ペリー 来航 日本人 驚いた",
    ],
    "F. Châu Âu bằng tiếng Nhật": [
        "中世ヨーロッパ 暮らし", "中世ヨーロッパ 雑学", "中世ヨーロッパ 冬",
    ],
    "G. Dạng hình ảnh": [
        "図解 日本史", "歴史 図解 解説", "歴史 アニメーション 解説",
    ],
    "H. Ru ngủ": [
        "歴史 睡眠用",
    ],
    "I. Tiền, nghề, thời khác": [
        "江戸時代 生活費", "江戸時代 給料", "江戸 職人 暮らし", "平安時代 庶民 暮らし", "昭和 暮らし 昔", "アイヌ 暮らし 冬",
    ],
}
JA_CHAR = re.compile(r"[぀-ヿ一-鿿]")


def is_japanese(title):
    letters = re.findall(r"[^\W\d_]", title)
    return bool(letters) and len(JA_CHAR.findall(title)) / len(letters) > 0.3


class JPYT(YT):
    cache_only = False

    def search(self, q, after):
        """Nghỉ giữa các lệnh gọi thật. Bị giới hạn tốc độ thì chờ rồi thử lại. Chế độ cache chỉ đọc kết quả đã lưu."""
        params = dict(part="id", type="video", q=q, order="viewCount", publishedAfter=after, regionCode="JP",
                      relevanceLanguage="ja", maxResults=50, videoDuration="any")
        if self.cache_only and not self.cache_path("search", params).exists():
            return None
        for wait in (30, None):
            calls = self.calls["search"]
            try:
                ids = [i["id"]["videoId"] for i in self.get("search", **params).get("items", [])]
            except Quota as e:
                if str(e) != "rateLimitExceeded" or wait is None:
                    raise
                time.sleep(wait)
                continue
            if self.calls["search"] != calls:
                time.sleep(2)
            return ids


def suggestions(session, seed):
    r = session.get(SUGGEST, params={"client": "firefox", "ds": "yt", "q": seed, "hl": "ja", "gl": "JP"}, timeout=20)
    r.raise_for_status()
    return json.loads(r.content.decode("utf-8", "replace"))[1]


def tokens(keyword):
    return [t[:2] for t in keyword.split() if t]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    now = datetime.now(timezone.utc)
    cache_mode = "--cache" in sys.argv
    flag = "--cache" if cache_mode else "--after" if "--after" in sys.argv else None
    after = (sys.argv[sys.argv.index(flag) + 1] if flag
             else (now - timedelta(days=DAYS)).strftime("%Y-%m-%dT00:00:00Z"))  # tròn theo ngày để cache khớp giữa các lần chạy
    yt = JPYT(api_key())
    yt.cache_only = cache_mode
    found, stopped = {}, None
    for group, kws in KEYWORDS.items():
        for kw in kws:
            try:
                vids = yt.search(kw, after)
                if vids is not None:
                    found[kw] = (group, vids)
            except Quota as e:
                stopped = f"Hết hạn mức ở từ khóa: {kw} ({e})"
                break
        if stopped:
            break

    ids = sorted({i for _, vids in found.values() for i in vids})
    videos = {v["id"]: v for v in yt.batched("videos", "snippet,statistics,contentDetails", ids)}
    chans = {c["id"]: c for c in yt.batched("channels", "snippet,statistics",
                                            sorted({v["snippet"]["channelId"] for v in videos.values()}))}

    def row(v):
        c = chans.get(v["snippet"]["channelId"], {})
        views = int(v["statistics"].get("viewCount", 0))
        subs = int(c.get("statistics", {}).get("subscriberCount", 0) or 0)
        age = max((now - parse(v["snippet"]["publishedAt"])).days, 1)
        return {"id": v["id"], "tieu_de": v["snippet"]["title"], "kenh": v["snippet"]["channelTitle"], "sub": subs,
                "view": views, "ngay_tuoi": age, "view_ngay": round(views / age),
                "ti_le_view_sub": round(views / max(subs, 1), 1), "phut": round(minutes(v["contentDetails"].get("duration")), 1),
                "tuoi_kenh_ngay": (now - parse(c["snippet"]["publishedAt"])).days if c else None}

    session = requests.Session()
    table, pool = [], {}
    for kw, (group, vids) in found.items():
        toks = tokens(kw)
        rows = []
        for i in vids:
            v = videos.get(i)
            if not v or minutes(v["contentDetails"].get("duration")) < MIN_MINUTES or not is_japanese(v["snippet"]["title"]):
                continue
            title = v["snippet"]["title"]
            if not any(t in title for t in toks):
                continue
            rows.append(row(v))
        for r in rows:
            pool[r["id"]] = r
        try:
            sug = suggestions(session, kw)
        except (requests.RequestException, ValueError, IndexError):
            sug = []
        time.sleep(0.3)
        if not rows:
            table.append({"nhom": group, "tu_khoa": kw, "so_video": 0, "goi_y": len(sug)})
            continue
        by_channel = collections.Counter()
        for r in rows:
            by_channel[r["kenh"]] += r["view"]
        hits = [r for r in rows if r["view"] >= HIT_VIEWS and r["sub"] < SMALL_CHANNEL]
        new_hits = [r for r in rows if r["view"] >= HIT_VIEWS and (r["tuoi_kenh_ngay"] or 9999) <= NEW_CHANNEL_DAYS]
        table.append({
            "nhom": group, "tu_khoa": kw, "so_video": len(rows), "so_kenh": len(by_channel), "goi_y": len(sug),
            "view_tv": round(st.median(r["view"] for r in rows)), "view_ngay_tv": round(st.median(r["view_ngay"] for r in rows)),
            "hit_kenh_nho": len({r["kenh"] for r in hits}), "hit_kenh_moi": len({r["kenh"] for r in new_hits}),
            "top3_chiem": round(sum(v for _, v in by_channel.most_common(3)) / sum(by_channel.values()), 2),
            "phut_tv": round(st.median(r["phut"] for r in rows), 1),
            "tieu_de_hoi": round(sum(bool(re.search(r"[？?]|どうやって|なぜ|なんで", r["tieu_de"])) for r in rows) / len(rows), 2),
            "video_tot": [(r["view"], r["sub"], r["kenh"], r["tieu_de"][:70]) for r in sorted(rows, key=lambda x: -x["view"])[:3]],
        })

    outliers = sorted((r for r in pool.values() if r["view"] >= HIT_VIEWS and r["sub"] <= SMALL_CHANNEL),
                      key=lambda x: -x["view"])
    (OUT / f"jp_radar_{now.strftime('%Y%m%d')}.json").write_text(json.dumps(
        {"ngay": now.isoformat(), "so_ngay": DAYS, "tu_khoa": table, "noi_troi": outliers, "video": list(pool.values()),
         "dung_som": stopped},
        ensure_ascii=False, indent=1), "utf-8")

    print(f"Lệnh gọi API thật: {dict(yt.calls)}")
    if stopped:
        print(stopped)
    print("Nhóm | từ khóa | video | kênh | gợi ý | view TV | view/ngày TV | hit kênh nhỏ | hit kênh mới | top3 | phút TV | tiêu đề hỏi")
    for t in sorted(table, key=lambda x: (-x.get("hit_kenh_nho", 0), -x.get("view_tv", 0))):
        if t["so_video"]:
            print(f"{t['nhom'][:2]} | {t['tu_khoa']} | {t['so_video']} | {t['so_kenh']} | {t['goi_y']} | {t['view_tv']:,} | "
                  f"{t['view_ngay_tv']:,} | {t['hit_kenh_nho']} | {t['hit_kenh_moi']} | {t['top3_chiem']:.0%} | {t['phut_tv']} | "
                  f"{t['tieu_de_hoi']:.0%}")
        else:
            print(f"{t['nhom'][:2]} | {t['tu_khoa']} | 0 video | gợi ý {t['goi_y']}")
    print(f"\nVideo từ kênh dưới {SMALL_CHANNEL:,} sub đạt từ {HIT_VIEWS:,} view: {len(outliers)}")
    for r in outliers[:40]:
        print(f"{r['id']} | {r['view']:,} view | {r['sub']:,} sub | x{r['ti_le_view_sub']} | {r['phut']}p | {r['ngay_tuoi']}d | "
              f"{r['kenh']} | {r['tieu_de'][:70]}")


if __name__ == "__main__":
    main()
