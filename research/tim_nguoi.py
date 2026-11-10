r"""Tìm người (nhà sáng lập, chủ gia tộc, doanh nhân đã mất) mà người Nhật đang quan tâm, để làm video tiếp theo.

  .venv\Scripts\python.exe -I research\tim_nguoi.py            (cần YOUTUBE_API_KEY trong .env)

Kế hoạch ở research\KE_HOACH_TIM_NGUOI.md. Mỗi ứng viên trong UNG_VIEN được đo:
1. Wikipedia tiếng Nhật (Wikimedia REST API, không cần khóa): lượt xem 12 tháng (11/2025–10/2026), đà tăng
   = 3 tháng gần nhất so với trung bình 9 tháng trước.
2. Wikidata: còn sống hay đã mất (người còn sống bị loại), năm sinh / mất (tìm năm tròn 2027).
3. Ảnh: ảnh đại diện trang ja.wikipedia có nằm trên Commons không (Commons = giấy phép tự do).
4. YouTube Data API: 50 video liên quan nhất có tên người trong tiêu đề: view cao nhất, số video ≥10 vạn,
   số video đăng trong 180 ngày (cung) và view tốt nhất trong 180 ngày (cầu hiện tại).
Điểm (0–100) chỉ để xếp hạng; người dùng chọn. Mỗi người tốn khoảng 101 đơn vị quota (hạn mức 10.000/ngày).
Kết quả: research\data\tim_nguoi_<ngày>.json và .md. Chạy lại dùng bộ nhớ đệm research\cache\.
"""
import json
import math
import re
import sys
import time
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from quet_thi_truong import goi  # noqa: E402  (YouTube API có bộ nhớ đệm)

UA = {"User-Agent": "kenh4-research/0.1 (personal research script)"}
NGAY = datetime.now(timezone.utc)
TU, DEN = "20251101", "20261031"
OUT = HERE / "data"

# (tên trang ja.wikipedia, công ty / gia tộc, loạt: "消" = đã biến mất, "続" = vẫn còn)
UNG_VIEN = [
    ("渋沢栄一", "第一国立銀行・500社", "続"), ("岩崎弥太郎", "三菱", "続"), ("岩崎弥之助", "三菱", "続"),
    ("岩崎小弥太", "三菱", "続"), ("住友友純", "住友", "続"), ("広瀬宰平", "住友・別子銅山", "続"),
    ("伊庭貞剛", "住友", "続"), ("広岡浅子", "加島屋・大同生命", "続"), ("五代友厚", "大阪商法会議所", "続"),
    ("益田孝", "三井物産", "続"), ("團琢磨", "三井合名", "続"), ("中上川彦次郎", "三井銀行", "続"),
    ("古河市兵衛", "古河財閥", "続"), ("浅野総一郎", "浅野財閥", "消"), ("藤田伝三郎", "藤田組", "消"),
    ("松方幸次郎", "川崎造船所", "消"), ("川崎正蔵", "川崎造船所", "消"), ("中島知久平", "中島飛行機", "消"),
    ("鮎川義介", "日産コンツェルン", "消"), ("野口遵", "日窒コンツェルン", "消"), ("久原房之助", "久原財閥", "消"),
    ("森矗昶", "森コンツェルン", "消"), ("大河内正敏", "理研コンツェルン", "消"), ("根津嘉一郎", "東武・根津財閥", "続"),
    ("小林一三", "阪急・宝塚", "続"), ("五島慶太", "東急", "続"), ("堤康次郎", "西武", "続"),
    ("福沢桃介", "大同電力", "消"), ("松永安左エ門", "電力王", "続"), ("出光佐三", "出光興産", "続"),
    ("松下幸之助", "パナソニック", "続"), ("井植歳男", "三洋電機", "消"), ("早川徳次", "シャープ", "続"),
    ("本田宗一郎", "ホンダ", "続"), ("井深大", "ソニー", "続"), ("盛田昭夫", "ソニー", "続"),
    ("豊田佐吉", "豊田自動織機", "続"), ("豊田喜一郎", "トヨタ自動車", "続"), ("鳥井信治郎", "サントリー", "続"),
    ("竹鶴政孝", "ニッカウヰスキー", "続"), ("御木本幸吉", "ミキモト", "続"), ("服部金太郎", "セイコー", "続"),
    ("安藤百福", "日清食品", "続"), ("江崎利一", "江崎グリコ", "続"), ("森永太一郎", "森永製菓", "続"),
    ("鈴木三郎助", "味の素", "続"), ("石橋正二郎", "ブリヂストン", "続"), ("稲盛和夫", "京セラ・JAL", "続"),
    ("中内功", "ダイエー", "消"), ("水島廣雄", "そごう", "消"), ("和田一夫", "ヤオハン", "消"),
    ("岡田卓也", "イオン", "続"), ("正力松太郎", "読売新聞", "続"), ("小佐野賢治", "国際興業", "消"),
    ("横井英樹", "ホテルニュージャパン", "消"), ("武藤山治", "鐘紡", "消"), ("金子直吉", "鈴木商店", "消"),
    ("鈴木よね", "鈴木商店", "消"), ("安宅英一", "安宅産業", "消"), ("山下亀三郎", "山下汽船", "消"),
    ("内田信也", "内田汽船", "消"), ("河本重次郎", "三光汽船", "消"), ("野村徳七", "野村財閥", "続"),
    ("鴻池善右衛門", "鴻池", "消"), ("紀伊國屋文左衛門", "紀文", "消"), ("淀屋常安", "淀屋", "消"),
    ("本間光丘", "本間家", "消"), ("茂木佐平治", "キッコーマン", "続"), ("大谷米太郎", "ホテルニューオータニ", "続"),
    ("大林芳五郎", "大林組", "続"), ("鹿島岩吉", "鹿島建設", "続"), ("田中久重", "東芝", "続"),
    ("大倉和親", "TOTO・日本陶器", "続"), ("森村市左衛門", "森村グループ", "続"), ("波多野鶴吉", "グンゼ", "続"),
    ("片倉兼太郎", "片倉製糸", "消"), ("林原健", "林原", "消"),
]
DA_LAM = {"大倉喜八郎", "安田善次郎", "三井高利", "堤清二", "永田雅一", "金子直吉", "鈴木よね"}


def get_json(url, params=None):
    for lan in range(4):
        r = requests.get(url, params=params, headers=UA, timeout=40)
        if r.status_code == 429:
            time.sleep(5 * (lan + 1))
            continue
        return r
    return r


def wiki_info(titles):
    """Tên trang thật (theo chuyển hướng), mã Wikidata, ảnh đại diện."""
    out = {}
    for i in range(0, len(titles), 40):
        r = get_json("https://ja.wikipedia.org/w/api.php", {
            "action": "query", "format": "json", "redirects": 1, "titles": "|".join(titles[i:i + 40]),
            "prop": "pageprops|pageimages", "piprop": "name", "ppprop": "wikibase_item"}).json()["query"]
        doi = {x["from"]: x["to"] for x in r.get("normalized", []) + r.get("redirects", [])}
        trang = {p["title"]: p for p in r["pages"].values()}
        for t in titles[i:i + 40]:
            thuc = doi.get(doi.get(t, t), doi.get(t, t))
            p = trang.get(thuc, {})
            out[t] = {"trang": thuc if "missing" not in p else None,
                      "qid": p.get("pageprops", {}).get("wikibase_item"), "anh": p.get("pageimage")}
    return out


def tren_commons(files):
    co = set()
    files = [f for f in files if f]
    for i in range(0, len(files), 40):
        r = get_json("https://commons.wikimedia.org/w/api.php", {
            "action": "query", "format": "json", "titles": "|".join("File:" + f for f in files[i:i + 40])}).json()
        for p in r["query"]["pages"].values():
            if "missing" not in p:
                co.add(p["title"].split(":", 1)[1].replace(" ", "_"))
    return co


def wikidata_nam(qids):
    out = {}
    qids = [q for q in qids if q]
    for i in range(0, len(qids), 40):
        r = get_json("https://www.wikidata.org/w/api.php", {
            "action": "wbgetentities", "format": "json", "ids": "|".join(qids[i:i + 40]), "props": "claims"}).json()
        for q, e in r.get("entities", {}).items():
            def nam(p):
                try:
                    return int(e["claims"][p][0]["mainsnak"]["datavalue"]["value"]["time"][1:5])
                except (KeyError, IndexError, ValueError):
                    return None
            out[q] = (nam("P569"), nam("P570"))
    return out


def luot_xem(trang):
    url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/ja.wikipedia/all-access/user/"
           f"{urllib.parse.quote(trang.replace(' ', '_'), safe='')}/monthly/{TU}/{DEN}")
    r = get_json(url)
    if not r.ok:
        return []
    return [i["views"] for i in r.json().get("items", [])]


def youtube(ten):
    ho = ten[:2]
    r = goi("search", part="snippet", q=ten, type="video", maxResults=50, relevanceLanguage="ja", regionCode="JP")
    ids = [it["id"]["videoId"] for it in r.get("items", []) if it["id"].get("videoId")]
    vs = []
    if ids:
        r = goi("videos", part="snippet,statistics,contentDetails", id=",".join(ids))
        for v in r["items"]:
            t = v["snippet"]["title"]
            if ten in t or (len(ten) >= 4 and ho in t and ten[-2:] in t):
                vs.append({"id": v["id"], "t": t, "kenh": v["snippet"]["channelTitle"],
                           "ngay": v["snippet"]["publishedAt"][:10], "view": int(v["statistics"].get("viewCount", 0))})
    moc = (NGAY - timedelta(days=180)).strftime("%Y-%m-%d")
    gan = [v for v in vs if v["ngay"] >= moc]
    vs.sort(key=lambda v: -v["view"])
    return {"so": len(vs), "max": vs[0]["view"] if vs else 0, "top": vs[:3], "so_10van": sum(v["view"] >= 100000 for v in vs),
            "so_180": len(gan), "max_180": max((v["view"] for v in gan), default=0),
            "top_180": sorted(gan, key=lambda v: -v["view"])[:2]}


def diem(x):
    """Cầu (Wikipedia + YouTube) 60, đà tăng 10, khoảng trống (ít video gần đây so với cầu) 15, ảnh 10, năm tròn 5."""
    pv = max(x["pv12"], 1)
    cau_wiki = min(math.log10(pv) / 6, 1)           # 100 vạn lượt / năm = đủ điểm
    cau_yt = min(math.log10(max(x["yt"]["max"], 1)) / 6.3, 1)  # 200 vạn view = đủ điểm
    tang = min(max((x["da_tang"] - 0.8) / 0.8, 0), 1)  # ≥1,6 lần = đủ điểm
    cung = x["yt"]["so_180"]
    trong = 1 / (1 + cung / 4)                       # 0 video gần đây = 1, 4 video = 0,5
    nam_tron = 1 if x["nam_tron"] else 0
    return round(30 * cau_wiki + 30 * cau_yt + 10 * tang + 15 * trong + 10 * x["co_anh"] + 5 * nam_tron, 1)


def main():
    ten = [t for t, _, _ in UNG_VIEN if t not in DA_LAM]
    meta = {t: (c, l) for t, c, l in UNG_VIEN}
    info = wiki_info(ten)
    nam = wikidata_nam([i["qid"] for i in info.values()])
    commons = tren_commons([i["anh"] for i in info.values()])
    kq, loai = [], []
    for t in ten:
        i = info[t]
        if not i["trang"]:
            loai.append((t, "không có trang ja.wikipedia"))
            continue
        sinh, mat = nam.get(i["qid"], (None, None))
        if not mat:
            loai.append((t, "còn sống hoặc không rõ năm mất"))
            continue
        pv = luot_xem(i["trang"])
        if len(pv) < 6:
            loai.append((t, "thiếu dữ liệu lượt xem"))
            continue
        gan, truoc = sum(pv[-3:]) / 3, sum(pv[:-3]) / max(len(pv) - 3, 1)
        x = {"ten": t, "trang": i["trang"], "cong_ty": meta[t][0], "loat": meta[t][1], "sinh": sinh, "mat": mat,
             "pv12": sum(pv), "pv_thang": pv, "da_tang": round(gan / truoc, 2) if truoc else 1.0,
             "anh": i["anh"], "co_anh": bool(i["anh"] and i["anh"].replace(" ", "_") in commons),
             "nam_tron": [n for n in (sinh, mat) if n and (2027 - n) % 50 == 0 and 2027 - n > 0],
             "yt": youtube(t)}
        x["diem"] = diem(x)
        kq.append(x)
        print(f"{t}: {x['pv12']:,} lượt, ×{x['da_tang']}, YT max {x['yt']['max']:,}, 180 ngày {x['yt']['so_180']} video, điểm {x['diem']}")
    kq.sort(key=lambda x: -x["diem"])
    OUT.mkdir(exist_ok=True)
    ngay = NGAY.strftime("%Y%m%d")
    (OUT / f"tim_nguoi_{ngay}.json").write_text(json.dumps({"ngay": ngay, "kq": kq, "loai": loai}, ensure_ascii=False, indent=1), encoding="utf-8")
    dong = [f"# Xếp hạng người nên làm video ({ngay})", "",
            "Điểm: cầu Wikipedia 30 + cầu YouTube 30 + đà tăng 10 + khoảng trống 15 + chân dung Commons 10 + năm tròn 2027 5.", "",
            "| # | Điểm | Người | Công ty / gia tộc | Loạt | Lượt xem Wiki 12 tháng | Đà tăng | YouTube cao nhất | Video ≥10 vạn | Video 180 ngày (view tốt nhất) | Ảnh | Năm tròn 2027 |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, x in enumerate(kq, 1):
        y = x["yt"]
        dong.append(f"| {n} | {x['diem']} | {x['ten']} ({x['sinh']}–{x['mat']}) | {x['cong_ty']} | {x['loat']} | {x['pv12']:,} | ×{x['da_tang']} | "
                    f"{y['max']:,} | {y['so_10van']} | {y['so_180']} ({y['max_180']:,}) | {'có' if x['co_anh'] else 'không'} | "
                    f"{', '.join(str(v) for v in x['nam_tron']) or ''} |")
    dong += ["", "## Bị loại", ""] + [f"- {t}: {ly_do}" for t, ly_do in loai]
    dong += ["", "## Video nhiều view của 15 người đầu", ""]
    for x in kq[:15]:
        dong.append(f"**{x['ten']}**")
        for v in x["yt"]["top"] + x["yt"]["top_180"]:
            dong.append(f"- {v['view']:,} | {v['ngay']} | {v['kenh']} | {v['t']}")
        dong.append("")
    (OUT / f"tim_nguoi_{ngay}.md").write_text("\n".join(dong), encoding="utf-8")
    print(f"\nĐã ghi research/data/tim_nguoi_{ngay}.md ({len(kq)} người, loại {len(loai)})")


if __name__ == "__main__":
    main()
