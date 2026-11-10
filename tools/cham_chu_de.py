"""Chấm điểm chủ đề cho kênh 4: nhu cầu người xem, đối thủ đã làm chưa, ảnh có giấy phép, tư liệu.

  python tools/cham_chu_de.py research/ung_vien.json [research/cham_chu_de.json]

Với mỗi ứng viên {ten, nguoi, commons[]}:
- YouTube (yt-dlp, không cần khóa): 15 kết quả đầu của "{ten}" và "{ten} なぜ消えた". Ghi view cao nhất, số video ≥10 vạn view,
  số video kiểu "消えた/倒産/破綻/崩壊/解体/没落" (đối thủ cùng ngách), và kênh mẫu 看板を下ろした日 đã làm chưa.
- Wikimedia Commons: số tệp PD/CC0/CC BY/CC BY-SA khớp các từ trong commons[], và có chân dung người chính không.
- J-STAGE (số bài), 国会会議録 (số lượt nhắc).
Điểm (0–100) chỉ là gợi ý xếp hạng; người dùng chọn.
"""
import json
import math
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

UA = {"User-Agent": "kenh4-research/0.1 (personal research script)"}
NICHE = re.compile(r"消え|倒産|破綻|崩壊|解体|没落|転落|末路|なぜ|しくじり|失敗|衰退")
FREE = re.compile(r"public domain|cc0|cc by|pd-|パブリック", re.I)
KANBAN = "看板を下ろした日"


def get(url, timeout=40):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode("utf-8", "replace")


def youtube(q, n=15):
    r = subprocess.run(["yt-dlp", "--flat-playlist", "--playlist-end", str(n), "--encoding", "utf-8", "--print",
                        "%(view_count)s\t%(channel)s\t%(title)s", f"ytsearch{n}:{q}"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"})
    out = []
    for ln in r.stdout.splitlines():
        p = ln.split("\t")
        if len(p) == 3:
            v = int(p[0]) if p[0].isdigit() else 0
            out.append({"view": v, "kenh": p[1], "tieu_de": p[2]})
    return out


COMMONS_LOCK = __import__("threading").Lock()


def commons(terms):
    """Gọi lần lượt (khóa chung), nghỉ giữa các lần: Commons trả 429 khi gọi song song."""
    files = {}
    for t in terms:
        p = {"action": "query", "generator": "search", "gsrsearch": t, "gsrnamespace": 6, "gsrlimit": 30, "prop": "imageinfo",
             "iiprop": "extmetadata", "iiextmetadatafilter": "LicenseShortName", "format": "json"}
        d = None
        for attempt in range(4):
            with COMMONS_LOCK:
                try:
                    d = json.loads(get("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p)))
                except Exception:
                    d = None
                __import__("time").sleep(1.2 if d else 5 * (attempt + 1))
            if d is not None:
                break
        if d is None:
            continue
        for pg in ((d.get("query") or {}).get("pages") or {}).values():
            lic = (((pg.get("imageinfo") or [{}])[0].get("extmetadata") or {}).get("LicenseShortName") or {}).get("value", "")
            title = pg["title"]
            if FREE.search(lic) and not title.lower().endswith((".pdf", ".djvu", ".svg", ".ogg", ".webm")):
                files[title] = lic
    return files


def jstage(q):
    try:
        x = get("https://api.jstage.jst.go.jp/searchapi/do?service=3&count=1&text=" + urllib.parse.quote(q))
        m = re.search(r"<opensearch:totalResults>(\d+)", x)
        return int(m.group(1)) if m else 0
    except Exception:
        return -1


def kokkai(q):
    try:
        j = json.loads(get("https://kokkai.ndl.go.jp/api/speech?maximumRecords=1&recordPacking=json&any=" + urllib.parse.quote(q)))
        return int(j.get("numberOfRecords") or 0)
    except Exception:
        return -1


def one(c):
    vids = {}
    for q in (c["ten"], c["ten"] + " なぜ消えた"):
        for v in youtube(q):
            vids[v["tieu_de"]] = v
    keys = [c["ten"]] + c.get("ten_khac", [])
    # chỉ tính video có tên chủ đề trong tiêu đề (bỏ kết quả liên quan lỏng của YouTube)
    vids = sorted((v for v in vids.values() if any(k in v["tieu_de"] for k in keys)), key=lambda v: -v["view"])
    niche = [v for v in vids if NICHE.search(v["tieu_de"])]
    files = commons(c["commons"])
    person = commons([c["nguoi"]]) if c.get("nguoi") else {}
    r = {**c, "view_max": vids[0]["view"] if vids else 0, "so_video_10van": sum(v["view"] >= 100_000 for v in vids),
         "doi_thu": [f"{v['view']:,} | {v['kenh']} | {v['tieu_de'][:50]}" for v in niche[:4]],
         "doi_thu_10van": sum(v["view"] >= 100_000 for v in niche), "kenh_mau_da_lam": any(KANBAN in v["kenh"] for v in vids),
         "anh": len(files), "anh_nguoi": len(person), "jstage": jstage(c["ten"]), "kokkai": kokkai(c["ten"])}
    # Điểm: nhu cầu (view cao nhất) 40, ít đối thủ 25, ảnh 20, tư liệu 15
    demand = min(40, max(0, (math.log10(r["view_max"] + 1) - 3) * 13.3))
    comp = 25 - 8 * r["doi_thu_10van"] - (25 if r["kenh_mau_da_lam"] else 0)
    img = min(14, r["anh"] / 3) + (6 if r["anh_nguoi"] else 0)
    src = min(8, r["jstage"] / 6) + min(7, r["kokkai"] / 15)
    r["diem"] = round(max(0, demand) + max(0, comp) + img + max(0, src))
    return r


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cands = json.loads(Path(sys.argv[1]).read_text("utf-8"))
    out = Path(sys.argv[2] if len(sys.argv) > 2 else "research/cham_chu_de.json")
    with ThreadPoolExecutor(6) as ex:
        res = list(ex.map(one, cands))
    res.sort(key=lambda r: -r["diem"])
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), "utf-8")
    print(f"{'Điểm':>4} {'Chủ đề':<12} {'View max':>10} {'≥10v':>4} {'ĐT≥10v':>6} {'Mẫu':>3} {'Ảnh':>4} {'Người':>5} {'J-ST':>5} {'Quốc hội':>8}")
    for r in res:
        print(f"{r['diem']:>4} {r['ten']:<12} {r['view_max']:>10,} {r['so_video_10van']:>4} {r['doi_thu_10van']:>6} "
              f"{'có' if r['kenh_mau_da_lam'] else '':>3} {r['anh']:>4} {r['anh_nguoi']:>5} {r['jstage']:>5} {r['kokkai']:>8}")


if __name__ == "__main__":
    main()
