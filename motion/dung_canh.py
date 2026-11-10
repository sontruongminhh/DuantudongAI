"""Tạo các cảnh motion mẫu hoặc từ tệp JSON. Thư viện mẫu nằm ở studio/mau_motion.py.

  python motion/dung_canh.py <thu_muc_du_an> [tep_canh.json]

Tệp JSON: danh sách {id, template, data}. Render từng cảnh:
  npx hyperframes render -c scenes/S001.html -o out/S001.mp4 --fps 24
Với một lần chạy của studio, dùng các lệnh dung-canh và ve-canh thay cho tệp này.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.mau_motion import build  # noqa: E402

SAMPLE = [{'id': 'S001',
  'template': 'hook',
  'thu': True,
  'data': {'kicker': '江戸の旅 ─ 東海道', 'line1': '旅籠に一泊すると、', 'hl': 'いくら', 'line2': 'かかった？', 'tag': 'テスト用サンプル'}},
 {'id': 'S002',
  'template': 'route',
  'thu': True,
  'data': {'title': '東海道五十三次',
           'sub': '江戸から京都まで、宿場は全部で53',
           'from': '日本橋',
           'to': '京都',
           'count': 53,
           'count_label': '宿場の数',
           'tag': 'イメージ図（縮尺・形は実際と異なります）'}},
 {'id': 'S003',
  'template': 'plan',
  'thu': True,
  'data': {'title': '旅籠の間取り',
           'sub': '泊まる人はどこを通ったのか',
           'tag': 'イメージ図（実際の建物とは異なります）',
           'rooms': [['中庭', 140, 170, 420, 210, '#dfe9d0'],
                     ['土間', 140, 380, 220, 210, '#e8d7b5'],
                     ['帳場', 360, 380, 200, 110, '#efe0c0'],
                     ['台所', 360, 490, 200, 100, '#e8d7b5'],
                     ['相部屋', 560, 170, 290, 200, '#f0e6cd'],
                     ['相部屋', 850, 170, 290, 200, '#f0e6cd'],
                     ['食事の間', 560, 370, 290, 220, '#f6ecd8'],
                     ['風呂', 850, 370, 150, 220, '#dbe6ea'],
                     ['厠', 1000, 370, 140, 220, '#e3dcc8']]}},
 {'id': 'S004',
  'template': 'ledger',
  'thu': True,
  'data': {'kari': True, 'title': '一泊いくらかかった？',
           'sub': '旅の出費をならべてみる',
           'tag': '※数値は動作確認用の仮の値です',
           'rows': [['宿代（一泊二食）', 250], ['昼の茶屋', 60], ['わらじ', 15]],
           'total_label': '合計'}},
 {'id': 'S005',
  'template': 'compare',
  'thu': True,
  'data': {'title': '旅籠と木賃宿のちがい',
           'sub': '食事は誰が用意するのか',
           'tag': 'テスト用サンプル',
           'left': {'name': '旅籠', 'ruby': 'はたご', 'items': ['夕食と朝食がつく', '宿の人が食事を用意', '宿代は高め']},
           'right': {'name': '木賃宿', 'ruby': 'きちんやど', 'items': ['払うのは薪代だけ', '食材は持参して自炊', '宿代は安い']}}},
 {'id': 'S006',
  'template': 'day',
  'thu': True,
  'data': {'title': '旅の一日',
           'sub': '朝から夜まで',
           'tag': 'イメージ図',
           'stops': [['朝', '宿を出発'], ['昼', '茶屋で休憩'], ['夕', '次の宿場に到着'], ['夜', '食事をして就寝']]}}]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    project = Path(sys.argv[1])
    scenes = json.loads(Path(sys.argv[2]).read_text("utf-8")) if len(sys.argv) > 2 else SAMPLE
    out = project / "scenes"
    out.mkdir(parents=True, exist_ok=True)
    for sc in scenes:
        (out / f"{sc['id']}.html").write_text(build(sc), "utf-8")
    print(f"Đã tạo {len(scenes)} cảnh trong {out}")


if __name__ == "__main__":
    main()
