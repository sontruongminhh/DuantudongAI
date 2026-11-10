r"""So cách gộp dòng thành cảnh giữa hai bản script.md (trước và sau khi sửa).
Dùng: .venv\Scripts\python.exe tools\so_nhom_canh.py runs\<run>\script.truoc_soat.md runs\<run>\script.md
Khác nhau thì số cảnh trong dien_mau.py sẽ lệch: chỉnh độ dài câu tới khi in "GIỐNG"."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from studio.motion import parse_script, split_scenes  # noqa: E402


def nhom(p, limit):
    L = parse_script(Path(p).read_text(encoding="utf-8-sig"))
    return [[x["id"] for x in g] for g in split_scenes(L, limit)], {x["id"]: x["text"] for x in L}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cu, moi = sys.argv[1], sys.argv[2]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else 66
    A, _ = nhom(cu, limit)
    B, T = nhom(moi, limit)
    sa, sb = set(map(tuple, A)), set(map(tuple, B))
    lech = [g for g in B if tuple(g) not in sa]
    print(f"Cảnh: cũ {len(A)}, mới {len(B)}")
    for g in lech:
        print("  MỚI", " + ".join(f"{i}({len(T[i])} ký tự)" for i in g), T[g[0]][:30])
    for g in A:
        if tuple(g) not in sb:
            print("  CŨ ", " + ".join(g))
    print("GIỐNG" if not lech and len(A) == len(B) else "KHÁC")
    sys.exit(0 if not lech and len(A) == len(B) else 1)


if __name__ == "__main__":
    main()
