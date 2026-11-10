"""Dựng bảng kênh thị trường ngách công ty / gia tộc (TSV) để dán vào Google Sheet
(https://docs.google.com/spreadsheets/d/1dvSN2W_l_AXVlP14xsw9r4d6ktqV-BnVHcdG4zgryuA, tab "Thị trường Cty-Gia tộc").
Cùng 18 cột với tab "Kênh thị trường" của kênh 2.

  python -I research/lam_bang_thi_truong.py      (sau research/quet_thi_truong.py; cần YOUTUBE_API_KEY)

Nhóm và ghi chú từng kênh nằm trong KENH bên dưới. Kênh chưa có trong dữ liệu quét thì tìm theo tên.
"""
import collections
import json
import statistics as st
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quet_thi_truong import goi, lay_video, theo_lo  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
NGAY = "20261105"
SRC = HERE / "data" / f"thi_truong_kigyo_{NGAY}.json"
OUT = HERE / "data" / f"thi_truong_kigyo_{NGAY}.tsv"
VIDEO_MAU = ["dnTI_R4d_bc", "FN1fxz8HdtU"]  # người dùng gửi 05/11/2026

NHOM = ["1. Cty biến mất「なぜ消えた」", "2. Cty biến mất「その後」", "3. Gia tộc, tài phiệt「家のその後」",
        "4. Tiểu sử doanh nhân", "5. Lịch sử cty còn sống, tài phiệt", "6. ゆっくり / しくじり企業",
        "7. Kinh tế, phá sản thời sự"]
# Kênh trùng tên với kênh nhái: chỉ định handle
HANDLE = {"看板を下ろした日": "@sayonara-company"}
KENH = {
    "看板を下ろした日": (1, "Kênh mẫu. 12 chương 30 phút, ảnh tư liệu + đồ họa giấy. カネボウ 112 vạn, 鈴木商店 69 vạn. Lập 22/10/2026."),
    "カカチャンネル": (1, "Kênh lớn lâu năm (2016), 24 phút. Làm cả công ty nước ngoài (ナイキ 131 vạn). Đăng thưa (3 video / 30 ngày)."),
    "消滅図鑑": (1, "「…はなぜ消えた？」+ hiện tại, 24 phút. 三洋電機 45 vạn. Lập 7/2026, cùng khuôn với mình."),
    "あの会社はなぜ消えた?": (1, "Cùng khuôn tiêu đề với kênh mẫu, 20 phút, đăng dày (15 / 30 ngày). ベスト電器 9,6 vạn; セゾン chỉ 1.136."),
    "企業興亡録": (1, "「10万人の会社はなぜ消えたのか」36 phút. 三洋電機 4 vạn. 30 ngày qua không đăng."),
    "歴ビズ": (1, "「ダイエーはなぜ衰退したのか」23,8 vạn; góc bài học kinh doanh, 15 phút."),
    "ビジネス戦記": (1, "Truyện doanh nghiệp kịch tính (町工場の逆転) 44 vạn; view trung vị thấp."),
    "ちび企業劇場": (1, "三洋電機 5.309; 13 sub. Bản nhái khuôn."),
    "破綻、そのあと。": (2, "「Xが消えた後、1万人の社員はどこへ？」アイワ 111 vạn. Góc người lao động và tên thương hiệu bị bán. 12 phút."),
    "消えたあとに": (2, "Lập 27/10/2026, cùng góc「その後」: レナウン 8,6 vạn sau vài ngày."),
    "消えた会社のゆくえ": (2, "Lập 28/10/2026, chép khuôn 破綻、そのあと。: 拓銀 4,7 vạn."),
    "逆転の経営史": (2, "鈴木商店に残った39人が双日を作るまで; lập 30/10/2026, còn ít view."),
    "会社の答え合わせ": (2, "Xếp hạng chuỗi cửa hàng chỉ còn tên, 30 phút; 171 sub mà 4,3 vạn view."),
    "その後の日本": (3, "「ヤオハン破綻後、和田家はどうなったのか」1,4 vạn: góc gia tộc sau phá sản, gần nhất với hướng mới của mình."),
    "その後の日本史": (3, "Lập 30/10/2026, 9 video đã 19 vạn view:「小栗上野介の妻と娘のその後」17 vạn. Khuôn「〇〇のその後。…『…』」 giống ギルド日本史."),
    "ギルド日本史": (3, "Video mẫu 05/11. Loạt「〇〇の家のその後」20 phút, 7 chương, tiêu đề có câu hỏi「なぜ…？」+ móc thời sự【新1万円札】【豊臣兄弟！】. 渋沢 7,3 vạn / 9 ngày, 四大財閥 4,9 vạn, 豊臣完子 17 vạn. Lập 9/10/2026, 1.600 sub."),
    "日本の黒歴史": (3, "Video mẫu 05/11. 278 sub nhưng「鈴木商店の女帝、鈴木よねの生涯」18 vạn: góc một người phụ nữ đứng sau tài phiệt. Các video khác vài trăm view."),
    "名家の歴史": (3, "「白洲家｜名門一族として栄えた家族に何が起きたのか」19 vạn; video 69 phút."),
    "日本一族史": (3, "「麻生家150年史｜炭鉱から巨大企業グループへ」5,8 vạn; 80 phút, gia tộc doanh nghiệp."),
    "名家のゆくえ": (3, "Có trong bảng kênh 2. Gia tộc「一族20人の運命」, sơ đồ gia hệ, view/sub rất cao."),
    "日本史のつづき": (3, "Gia tộc samurai「〇〇家のその後」(吉良家 80 vạn). Lập 3/10/2026, 1.340 sub: khuôn「家のその後」đang nổ."),
    "日本史を学べるチャンネル": (3, "「平家一族の末路」125 vạn. Khuôn「学校ですら教えてくれない…のその後」."),
    "教科書のその先": (3, "Cùng khuôn「学校ですら教えてくれない…その後」, 豊臣秀次一族 34,8 vạn; 361 sub."),
    "偉人エピソードX": (4, "Tiểu sử doanh nhân lớn, 36 phút:「岩崎弥太郎｜三菱財閥創始者の野望」38,5 vạn. 14,3 vạn sub."),
    "禁断のパイオニア列伝": (4, "「堤義明…西武王国はなぜ崩壊したのか」25 vạn; 26 phút. Người sống: cẩn thận."),
    "偉人に学ぶ人生訓": (4, "Tiểu sử chủ doanh nghiệp (スズキ 鈴木修 7,9 vạn), 55 phút."),
    "時代を支えた人々": (4, "「小倉昌男の決断」; 206 sub, view rất thấp."),
    "御社と競合の違い": (5, "「三大財閥を完全解説」54 vạn; giải thích công ty còn sống, 16 phút, 5,7 vạn sub."),
    "大企業の歴史": (5, "「伊藤忠商事160年史｜本格ドキュメンタリー」2,9 vạn; 46 phút. Lập 9/2026."),
    "100年企業TV": (5, "Doanh nghiệp trăm năm còn sống; 505 sub mà 14 vạn view."),
    "ゆっくり企業事件簿": (6, "ゆっくり「しくじり企業」: 代ゼミ 39 vạn; trung vị thấp."),
    "企業しくじり・やらかし物語": (6, "ゆっくり, 14 phút, 12/12 video đúng ngách: 自動車整備工場 25,6 vạn."),
    "オワコン対策ゆっくり研究所": (6, "ゆっくり phá sản: マイカル 1,7 vạn, 千代田生命 9.000."),
    "ぼくひぐま。": (7, "Cựu nhân viên ngân hàng giải thích vụ phá sản mới (速報), 9,3 vạn sub."),
    "盛者必衰チャンネル": (7, "「新聞はなぜ消えていくのか」: ngành đang suy, không phải công ty đã mất."),
    "マネーのからくり図解室": (7, "Đồ họa giải thích: ダイエー崩壊の裏側 29,6 vạn."),
    "柴課長の深層レポート": (7, "「レナウンはなぜ一夜で消えたのか」23 vạn; phân tích cấu trúc."),
    "夜のビジネス博物館": (7, "Thời sự doanh nghiệp + セゾン解体 255 view."),
    "セイスイチャンネル": (7, "「企業盛衰記」#104 bài ngắn 9 phút; đăng dày, view rất thấp."),
}


def tim_kenh(ten):
    kq = goi("search", part="snippet", q=ten, type="channel", maxResults=5, regionCode="JP")
    for it in kq.get("items", []):
        if it["snippet"]["title"].startswith(ten):
            return it["snippet"]["channelId"]
    return None


def chi_so(cid):
    c = goi("channels", part="snippet,statistics,contentDetails", id=cid)["items"][0]
    up = c["contentDetails"]["relatedPlaylists"]["uploads"]
    pl = goi("playlistItems", part="contentDetails,snippet", playlistId=up, maxResults=50)
    gio_dang = {x["contentDetails"]["videoId"]: x["contentDetails"].get("videoPublishedAt", "") for x in pl.get("items", [])}
    vs = lay_video(gio_dang)
    dai = sorted([v for v in vs.values() if v["giay"] >= 240], key=lambda v: v["ngay"], reverse=True)
    now = datetime.now(timezone.utc)
    d30 = (now - timedelta(days=30)).strftime("%Y-%m-%d")
    d10 = (now - timedelta(days=10)).strftime("%Y-%m-%d")
    moi = [v for v in dai if v["ngay"] >= d30]
    cu = [v for v in dai if v["ngay"] < d10][:20]
    nhip = None
    if len(dai) >= 2:
        a = datetime.fromisoformat(dai[-1]["ngay"]); b = datetime.fromisoformat(dai[0]["ngay"])
        nhip = round((b - a).days / (len(dai) - 1), 1)
    gio = collections.Counter()
    for v in dai[:20]:
        t = gio_dang.get(v["id"])
        if t:
            gio[f"{(int(t[11:13]) + 9) % 24}時"] += 1
    top = max(dai, key=lambda v: v["view"]) if dai else None
    return {
        "id": cid, "ten": c["snippet"]["title"], "handle": c["snippet"].get("customUrl", ""),
        "lap": c["snippet"]["publishedAt"][:10], "sub": int(c["statistics"].get("subscriberCount", 0) or 0),
        "tong_view": int(c["statistics"].get("viewCount", 0)), "so_video": int(c["statistics"].get("videoCount", 0)),
        "video_30n": len(moi), "view_30n": sum(v["view"] for v in moi),
        "view_tb": round(st.mean([v["view"] for v in cu])) if cu else None,
        "view_tv": round(st.median([v["view"] for v in cu])) if cu else None,
        "nhip": nhip, "dai_tb": round(st.mean([v["giay"] for v in dai]) / 60) if dai else 0,
        "gio": gio.most_common(2), "top": top,
    }


def so(x):
    return str(x).replace(".", ",")


def main():
    data = json.loads(SRC.read_text("utf-8"))
    theo_ten = {k["ten"]: k["kenh_id"] for k in data["kenh"]}
    theo_handle = {k["handle"].lower(): k["kenh_id"] for k in data["kenh"] if k["handle"]}
    rows, thieu = [], []
    for ten, (n, note) in KENH.items():
        cid = (theo_handle.get(HANDLE[ten].lower()) if ten in HANDLE else None) or theo_ten.get(ten)             or next((i for t, i in theo_ten.items() if t.startswith(ten)), None) or tim_kenh(ten)
        if not cid:
            thieu.append(ten)
            continue
        rows.append((n, chi_so(cid), note))
    rows.sort(key=lambda x: (x[0], -(x[1]["top"]["view"] if x[1]["top"] else 0)))
    head = ["STT", "Nhóm dạng", "Kênh", "Link", "Ngày lập", "Sub", "Tổng view", "Số video",
            "Video dài đăng 30 ngày", "View của các video đó", "View TB / video (20 video, ≥10 ngày)",
            "View trung vị", "Nhịp đăng (ngày/video)", "Độ dài TB (phút)", "Giờ đăng hay dùng (JST)",
            "Video nhiều view nhất (trong 50 video mới)", "View video đó", "Ghi chú"]
    lines = ["\t".join(head)]
    for i, (n, r, note) in enumerate(rows, 1):
        link = f"https://www.youtube.com/{r['handle']}" if r["handle"] else f"https://www.youtube.com/channel/{r['id']}"
        top = r["top"]
        cells = [i, NHOM[n - 1], r["ten"].strip(), link, r["lap"], r["sub"], r["tong_view"], r["so_video"],
                 r["video_30n"], r["view_30n"], r["view_tb"] or "", r["view_tv"] or "",
                 so(r["nhip"]) if r["nhip"] is not None else "", r["dai_tb"],
                 ", ".join(f"{h} ({c})" for h, c in r["gio"]),
                 top["tieu_de"].replace("\t", " ") if top else "", top["view"] if top else "", note]
        lines.append("\t".join(str(c) for c in cells))
    lines += ["", "", "\t".join(["", "Tóm tắt theo nhóm", "Số kênh", "Tổng view video đăng 30 ngày",
                                 "Trung vị view TB / video", "Trung vị độ dài (phút)", "Số kênh lập năm 2026"])]
    for gi, g in enumerate(NHOM, 1):
        rs = [r for n, r, _ in rows if n == gi]
        if not rs:
            continue
        tb = [r["view_tb"] for r in rs if r["view_tb"]]
        lines.append("\t".join(str(c) for c in ["", g, len(rs), sum(r["view_30n"] for r in rs),
                                                round(st.median(tb)) if tb else "",
                                                round(st.median(r["dai_tb"] for r in rs)),
                                                sum(r["lap"] >= "2026" for r in rs)]))
    lines += ["", "", "\t".join(["", f"Video mẫu ({NGAY})", "Kênh", "Link", "Ngày đăng", "Độ dài (phút)", "View",
                                 "View/ngày", "Like", "Bình luận", "Sub kênh", "Tiêu đề"])]
    now = datetime.now(timezone.utc).date()
    vm = lay_video(VIDEO_MAU)
    subs = {r["id"]: r["sub"] for _, r, _ in rows}
    for vid in VIDEO_MAU:
        o = vm[vid]
        ngay = max(1, (now - datetime.fromisoformat(o["ngay"]).date()).days)
        lines.append("\t".join(str(c) for c in ["", "", o["kenh"], "https://youtu.be/" + vid, o["ngay"],
                                                so(round(o["giay"] / 60, 1)), o["view"], round(o["view"] / ngay),
                                                o["like"], o["binh_luan"], subs.get(o["kenh_id"], ""), o["tieu_de"]]))
    OUT.write_text("\n".join(lines), "utf-8")
    print(len(rows), "kênh; không tìm thấy:", thieu)
    print("Đã ghi", OUT)


if __name__ == "__main__":
    main()
