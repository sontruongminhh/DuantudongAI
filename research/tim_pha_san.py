r"""Tìm gia tộc / doanh nhân Nhật đã phá sản hoặc biến mất mà người Nhật đang quan tâm (loạt 「なぜ消えたのか」).

  .venv\Scripts\python.exe -I research\tim_pha_san.py

Dùng lại cách đo của research\tim_nguoi.py (Wikipedia 12 tháng, đà tăng, Wikidata, Commons, YouTube), thêm:
- Trang công ty / ngân hàng / gia tộc ("tc"): không kiểm năm mất, tên tìm YouTube là tên trang bỏ phần ngoặc.
- YouTube API hết hạn mức thì chuyển sang yt-dlp tìm kiếm (không có ngày đăng nên "180 ngày" để trống).
  Lỗi API chỉ in mã trạng thái, không in đường dẫn (đường dẫn có khóa).
Kết quả: research\data\tim_pha_san_<ngày>.json và .md.
"""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tim_nguoi as tn  # noqa: E402

# (tên trang ja.wikipedia, gia tộc / công ty và cách kết thúc, loại: "ng" người, "tc" tổ chức)
UNG_VIEN = [
    # Thương gia thời Edo bị tịch thu hoặc lụi tàn
    ("淀屋", "淀屋・1705年闕所", "tc"), ("淀屋常安", "淀屋", "ng"), ("紀伊國屋文左衛門", "紀文・没落", "ng"),
    ("奈良屋茂左衛門", "奈良茂・没落", "ng"), ("銭屋五兵衛", "銭五・1852年闕所", "ng"),
    ("天王寺屋五兵衛", "天王寺屋・両替商", "ng"), ("鴻池善右衛門", "鴻池・両替商", "ng"), ("鴻池財閥", "鴻池", "tc"),
    ("本間光丘", "本間家", "ng"),
    # Minh Trị: đổ vỡ sớm
    ("小野組", "1874年破綻", "tc"), ("島田組", "1874年破綻", "tc"), ("田中平八", "糸平・天下の糸平", "ng"),
    ("雨宮敬次郎", "甲州財閥・鉄道", "ng"), ("若尾逸平", "若尾財閥・若尾銀行", "ng"), ("平沼専蔵", "平沼銀行", "ng"),
    ("今村清之助", "今村銀行", "ng"), ("松本重太郎", "百三十銀行・1904年破綻", "ng"),
    ("高田慎蔵", "高田商会・1925年破綻", "ng"), ("高田商会", "1925年破綻", "tc"),
    # Đại Chính – đầu Chiêu Hòa: thành kim, khủng hoảng 1920 và 1927
    ("岩下清周", "北浜銀行・1914年破綻", "ng"), ("北浜銀行", "1914年破綻", "tc"),
    ("茂木惣兵衛", "茂木商店・1920年破綻", "ng"), ("石井定七", "1922年破綻", "ng"),
    ("山本唯三郎", "船成金・没落", "ng"), ("鈴木久五郎", "株成金・没落", "ng"), ("乾新兵衛", "乾汽船", "ng"),
    ("内田信也", "内田汽船・船成金", "ng"), ("山下亀三郎", "山下汽船", "ng"),
    ("渡辺治右衛門", "東京渡辺銀行・1927年破綻", "ng"), ("東京渡辺銀行", "1927年破綻・昭和金融恐慌", "tc"),
    ("松方巌", "十五銀行・1927年休業", "ng"), ("十五銀行", "1927年休業", "tc"),
    ("松方幸次郎", "川崎造船所・1927年経営危機", "ng"), ("川崎正蔵", "川崎造船所", "ng"),
    ("星一", "星製薬・没落", "ng"), ("星製薬", "没落", "tc"), ("鈴木藤三郎", "日本精製糖・日糖事件", "ng"),
    ("武藤山治 (実業家)", "鐘紡", "ng"), ("福沢桃介", "大同電力", "ng"), ("片倉兼太郎", "片倉製糸", "ng"),
    # Tài phiệt mới tan rã
    ("浅野総一郎", "浅野財閥", "ng"), ("藤田伝三郎", "藤田組", "ng"), ("久原房之助", "久原財閥", "ng"),
    ("鮎川義介", "日産コンツェルン", "ng"), ("野口遵", "日窒コンツェルン", "ng"), ("森矗昶", "森コンツェルン", "ng"),
    ("中島知久平", "中島飛行機", "ng"), ("大河内正敏", "理研コンツェルン", "ng"),
    # Sau chiến tranh
    ("安宅英一", "安宅産業・1977年消滅", "ng"), ("安宅産業", "1977年消滅", "tc"),
    ("横井英樹", "ホテルニュージャパン・1982年火災", "ng"), ("ホテルニュージャパン", "1982年火災", "tc"),
    ("小佐野賢治", "国際興業", "ng"), ("中内功", "ダイエー", "ng"), ("ダイエー", "2004年再生機構", "tc"),
    ("水島廣雄", "そごう・2000年破綻", "ng"), ("そごう", "2000年破綻", "tc"),
    ("和田一夫", "ヤオハン・1997年破綻", "ng"), ("ヤオハン", "1997年破綻", "tc"),
    ("河本重次郎", "三光汽船・1985年破綻", "ng"), ("三光汽船", "1985年破綻", "tc"),
    ("井植歳男", "三洋電機", "ng"), ("林原健", "林原・2011年破綻", "ng"),
    ("高橋治則", "イ・アイ・イ・バブル崩壊", "ng"), ("イ・アイ・イ・インターナショナル", "バブル崩壊", "tc"),
    ("渡辺喜太郎", "麻布建物・バブル崩壊", "ng"), ("佐佐木吉之助", "桃源社・バブル崩壊", "ng"),
    ("秀和", "バブル崩壊", "tc"),
]
DA_LAM = {"大倉喜八郎", "安田善次郎", "堤清二", "永田雅一", "金子直吉", "鈴木よね"}


def ten_tim(t):
    return re.sub(r"\s*\(.*?\)", "", t)


def youtube_dlp(q):
    """Dự phòng khi hết hạn mức API: 40 kết quả tìm kiếm, có view, không có ngày đăng."""
    r = subprocess.run([shutil.which("yt-dlp") or "yt-dlp", "--flat-playlist", "-j", f"ytsearch40:{q}"],
                       capture_output=True, text=True, encoding="utf-8", timeout=180)
    vs = []
    for dong in r.stdout.splitlines():
        try:
            v = json.loads(dong)
        except ValueError:
            continue
        t = v.get("title") or ""
        if q in t:
            vs.append({"id": v.get("id"), "t": t, "kenh": v.get("channel") or v.get("uploader") or "",
                       "ngay": "", "view": int(v.get("view_count") or 0)})
    vs.sort(key=lambda v: -v["view"])
    return {"so": len(vs), "max": vs[0]["view"] if vs else 0, "top": vs[:3], "so_10van": sum(v["view"] >= 100000 for v in vs),
            "so_180": None, "max_180": 0, "top_180": [], "nguon": "yt-dlp"}


HET_HAN_MUC = False


def youtube(q):
    global HET_HAN_MUC
    if not HET_HAN_MUC:
        try:
            y = tn.youtube(q)
            y["nguon"] = "api"
            return y
        except requests.HTTPError as e:
            print(f"  YouTube API lỗi {e.response.status_code}, chuyển sang yt-dlp")
            HET_HAN_MUC = True
    return youtube_dlp(q)


def diem(x):
    y = dict(x["yt"])
    if y["so_180"] is None:      # yt-dlp không có ngày đăng: khoảng trống tính nửa điểm
        y["so_180"] = 4
    return tn.diem({**x, "yt": y})


def main():
    ds = [u for u in UNG_VIEN if u[0] not in DA_LAM]
    ten = [u[0] for u in ds]
    info = tn.wiki_info(ten)
    nam = tn.wikidata_nam([i["qid"] for i in info.values()])
    commons = tn.tren_commons([i["anh"] for i in info.values()])
    kq, loai = [], []
    for t, mo_ta, kieu in ds:
        i = info[t]
        if not i["trang"]:
            loai.append((t, "không có trang ja.wikipedia"))
            continue
        sinh, mat = nam.get(i["qid"], (None, None))
        if kieu == "ng" and not mat:
            loai.append((t, "còn sống hoặc không rõ năm mất"))
            continue
        pv = tn.luot_xem(i["trang"])
        if len(pv) < 6:
            loai.append((t, f"thiếu dữ liệu lượt xem (trang {i['trang']})"))
            continue
        gan, truoc = sum(pv[-3:]) / 3, sum(pv[:-3]) / max(len(pv) - 3, 1)
        x = {"ten": t, "trang": i["trang"], "mo_ta": mo_ta, "kieu": kieu, "sinh": sinh if kieu == "ng" else None,
             "mat": mat if kieu == "ng" else None, "pv12": sum(pv), "pv_thang": pv,
             "da_tang": round(gan / truoc, 2) if truoc else 1.0, "anh": i["anh"],
             "co_anh": bool(i["anh"] and i["anh"].replace(" ", "_") in commons),
             "nam_tron": [n for n in (sinh, mat) if kieu == "ng" and n and (2027 - n) % 50 == 0 and 2027 - n > 0],
             "yt": youtube(ten_tim(t))}
        x["diem"] = diem(x)
        kq.append(x)
        y = x["yt"]
        print(f"{t}: {x['pv12']:,} lượt, ×{x['da_tang']}, YT max {y['max']:,} ({y['nguon']}), điểm {x['diem']}")
    kq.sort(key=lambda x: -x["diem"])
    ngay = tn.NGAY.strftime("%Y%m%d")
    tn.OUT.mkdir(exist_ok=True)
    (tn.OUT / f"tim_pha_san_{ngay}.json").write_text(json.dumps({"ngay": ngay, "kq": kq, "loai": loai}, ensure_ascii=False, indent=1), encoding="utf-8")
    dong = [f"# Gia tộc / doanh nhân đã phá sản hoặc biến mất: xếp hạng quan tâm ({ngay})", "",
            "Điểm như `tim_nguoi.py`: Wikipedia 30 + YouTube 30 + đà tăng 10 + khoảng trống 15 + ảnh Commons 10 + năm tròn 2027 5. "
            "Loại: ng = trang người, tc = trang công ty / ngân hàng / gia tộc.", "",
            "| # | Điểm | Tên | Kết thúc | Loại | Wiki 12 tháng | Đà tăng | YouTube cao nhất | Video ≥10 vạn | Video 180 ngày | Ảnh | Năm tròn |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for n, x in enumerate(kq, 1):
        y = x["yt"]
        ten_hien = x["ten"] + (f" ({x['sinh']}–{x['mat']})" if x["kieu"] == "ng" else "")
        so180 = "?" if y["so_180"] is None else f"{y['so_180']} ({y['max_180']:,})"
        dong.append(f"| {n} | {x['diem']} | {ten_hien} | {x['mo_ta']} | {x['kieu']} | {x['pv12']:,} | ×{x['da_tang']} | {y['max']:,} | "
                    f"{y['so_10van']} | {so180} | {'có' if x['co_anh'] else 'không'} | {', '.join(map(str, x['nam_tron']))} |")
    dong += ["", "## Bị loại", ""] + [f"- {t}: {l}" for t, l in loai]
    dong += ["", "## Video nhiều view của 20 tên đầu", ""]
    for x in kq[:20]:
        dong.append(f"**{x['ten']}**")
        for v in x["yt"]["top"] + x["yt"]["top_180"]:
            dong.append(f"- {v['view']:,} | {v['ngay']} | {v['kenh']} | {v['t']}")
        dong.append("")
    (tn.OUT / f"tim_pha_san_{ngay}.md").write_text("\n".join(dong), encoding="utf-8")
    print(f"\nĐã ghi research/data/tim_pha_san_{ngay}.md ({len(kq)} tên, loại {len(loai)})")


if __name__ == "__main__":
    main()
