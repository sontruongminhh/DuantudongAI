r"""Tìm cảnh có độ dài định trước (planned_sec) dài hơn clip đã render, để render lại.

  .venv\Scripts\python.exe tools\tim_lam_lai.py runs\<run>                  (in danh sách)
  .venv\Scripts\python.exe tools\tim_lam_lai.py runs\<run> runs\<run>\lam_lai.txt   (ghi ra tệp)

Dùng sau lần dựng đầu + nap-motion + dung-canh (QUY_TRINH bước 7). Tệp ghi ra dùng cho
`tools\ve_song_song.py runs\<run> --so-luong 10 --lam-lai $(cat runs\<run>\lam_lai.txt)`.
Chạy lại sau nhan-clip --ghi-de: phải in 0 cảnh. Cần ffprobe.
"""
import json
import subprocess
import sys
from pathlib import Path

DU = 0.05  # giây, sai số cho phép


def do_dai(p: Path) -> float:
    if not p.is_file():
        return 0.0
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def tim(run: Path) -> list[str]:
    canh = json.loads((run / "scenes.json").read_text(encoding="utf-8"))["canh"]
    return [s["id"] for s in canh if s["planned_sec"] > do_dai(run / "clips" / f"{s['id']}.mp4") + DU]


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    bad = tim(Path(sys.argv[1]))
    print(f"{len(bad)} cảnh dài hơn clip")
    if len(sys.argv) > 2:
        Path(sys.argv[2]).write_text(" ".join(bad), encoding="utf-8")
    elif bad:
        print(" ".join(bad))


if __name__ == "__main__":
    main()
