"""Kịch bản v2 → shotlist.json + prompts.md. Mỗi dòng lời đọc là một cảnh, mỗi cảnh có bản thiết kế 5 trường.

  python tools/make_shotlist.py videos/001_barentsz_1596 --style A
  python tools/make_shotlist.py videos/001_barentsz_1596 --export-lines      # đầu vào cho tầng 4 (AI thiết kế hình)
  python tools/make_shotlist.py videos/001_barentsz_1596 --durations voice/durations.json

- Thiết kế hình lấy từ blueprint_visual.json (do AI viết theo prompts/04_thiet_ke_hinh.md) nếu có;
  cảnh nào chưa có thì máy tự điền bản mặc định từ dòng [HÌNH] và mã nhịp.
- Thông tin riêng của video (bối cảnh, độ chính xác lịch sử, ảnh tham chiếu) nằm trong video.json;
  cảnh nào ở bối cảnh khác (Amsterdam, năm 1871…) thì ghi đè bằng trường "setting" / "accuracy" trong thiết kế hình.
- Thời lượng lấy từ file giọng thật nếu có (--durations, {id cảnh: giây}); nếu không thì ước theo 160 từ/phút.
"""
import argparse
import json
import re
from pathlib import Path

WPM = 160
MIN_SHOT_SEC = 2.5
MAX_CLIPS = 15
STYLES = {
    "A": "Hand-painted gouache storybook illustration, soft visible brush texture, slightly simplified shapes, "
         "cold steel-blue and teal exterior tones, warm amber and orange firelight interiors, gentle rim lighting, "
         "cozy but serious mood, 16:9",
    "B": "Cinematic semi-realistic digital matte painting, dramatic volumetric light, deep cold blue shadows against "
         "warm amber firelight, fine texture and atmospheric haze, documentary film still, 16:9",
    "C": "Hand-inked line art with loose watercolor wash, crosshatching inspired by 16th-century copperplate "
         "engravings, limited palette of icy blue, sepia and warm orange accents, aged paper texture, 16:9",
}
PACE = re.compile(r"^\[(NARRATIVE|TENSION|EPIC)\]\s*(.+)$")
ANGLES = {"EPIC": ["Wide establishing shot, held still"],
          "TENSION": ["Close-up", "Extreme close-up detail", "Low-angle close shot"],
          "NARRATIVE": ["Medium shot", "Wide shot", "Over-the-shoulder shot", "Medium close-up", "High-angle shot"]}
MOTION = {"EPIC": ["slow_zoom_out"], "TENSION": ["push_in"], "NARRATIVE": ["pan_right", "zoom_in", "pan_left", "zoom_out"]}
PAUSE_AFTER = {"NARRATIVE": 0.25, "TENSION": 0.4, "EPIC": 0.8}
CLIP_HINT = r"storm|squeez|blasting|rising|collapsing|steam|smoke|snow piled|drifting|edge of sun|full round sun|rowing|tunnel|ice slabs"
INTERIOR = r"interior|inside|box bed|hut,|in the hut|hearth|lamp|table|cabin|room|fire|bed"


def visual_type(cue):
    c = cue.lower()
    if c.startswith("map"):
        return "map"
    if c.startswith(("diagram", "science graphic", "simple science graphic", "cutaway diagram")):
        return "diagram"
    if "journal page" in c:
        return "engraving_1598"
    if "museum" in c:
        return "illustration"
    if "viewer prompt card" in c:
        return "card"
    if "cutaway" in c:
        return "cutaway"
    return "illustration"


def parse(script_md):
    """Trả về các dòng lời đọc kèm chương, nhãn Saga, beat, cue, âm thanh và khoảng lặng ngay trước dòng."""
    body = script_md.split("## Kịch bản", 1)[1].split("## Bảng nguồn", 1)[0]
    out, chapter, saga, cue, sounds, silence = [], None, None, None, [], 0.0
    ci, bi, li = -1, 0, 0
    for raw in body.splitlines():
        s = raw.strip()
        if s.startswith("### "):
            ci, bi = ci + 1, 0
            chapter = s[4:]
            saga = chapter.split(" · Chương")[0]
        elif s.startswith("[HÌNH:"):
            bi, li = bi + 1, 0
            cue = s[len("[HÌNH:"):].rstrip("]").strip()
        elif s.startswith("((SILENCE"):
            m = re.search(r"([\d.]+)\s*s", s)
            silence += float(m.group(1)) if m else 1.0
        elif s.startswith("(("):
            sounds.append(s.strip("()").strip())
        elif PACE.match(s):
            li += 1
            pace, text = PACE.match(s).groups()
            out.append({"id": f"c{ci:02d}_b{bi:02d}_l{li:02d}", "chapter": chapter, "saga": saga, "cue": cue,
                        "pace": pace, "text": text, "sound": sounds, "silence_before": silence, "beat": (ci, bi)})
            sounds, silence = [], 0.0
    return out


def group_shots(lines, durations):
    """Mỗi dòng là một cảnh; dòng ngắn dưới MIN_SHOT_SEC được gộp với dòng sau trong cùng beat."""
    shots, cur = [], []
    for i, ln in enumerate(lines):
        ln["est"] = (durations or {}).get(ln["id"]) or len(ln["text"].split()) / WPM * 60
        cur.append(ln)
        nxt = lines[i + 1] if i + 1 < len(lines) else None
        short = sum(x["est"] for x in cur) < MIN_SHOT_SEC
        if not (short and nxt and nxt["beat"] == ln["beat"] and ln["pace"] != "EPIC"):
            shots.append(cur)
            cur = []
    return shots


def default_blueprint(shot_lines, first_in_beat, n_in_beat, video):
    ln = shot_lines[0]
    pace = max((x["pace"] for x in shot_lines), key=lambda p: {"EPIC": 2, "TENSION": 1, "NARRATIVE": 0}[p])
    kind = visual_type(ln["cue"]) if first_in_beat else "illustration"
    angle = ANGLES[pace][n_in_beat % len(ANGLES[pace])]
    subject = ln["cue"] if first_in_beat else f"{ln['cue']}; a different moment of the same scene matching: \"{ln['text'][:120]}\""
    low = (ln["cue"] + " " + ln["text"]).lower()
    atmos = ", ".join(x for k, x in [("snow", "drifting snow"), ("smoke", "smoke haze"), ("frost", "frost crystals"),
                                     ("ice", "ice glinting"), ("fire", "floating embers"), ("breath", "visible breath vapor"),
                                     ("storm", "blowing snow streaks"), ("dark", "deep shadows")] if k in low) or "still cold air, faint drifting snow"
    lighting = ("warm amber firelight against cold blue shadows" if re.search(INTERIOR, low)
                else "cold steel-blue and teal light, pale polar sky")
    refs = sorted(r for r, rx in video.get("ref_keywords", {}).items() if re.search(rx, ln["cue"], re.I))
    return {"primary_visual": kind, "subject_action": subject, "atmosphere": atmos, "shot_angle": angle,
            "lighting_palette": lighting, "refs": refs, "motion": None, "pace": pace}


def build(vd, style, durations=None):
    video = json.loads((vd / "video.json").read_text("utf-8"))
    lines = parse((vd / "script.md").read_text("utf-8"))
    groups = group_shots(lines, durations)
    ai = {}
    if (vd / "blueprint_visual.json").exists():
        ai = {b["id"]: b for b in json.loads((vd / "blueprint_visual.json").read_text("utf-8"))}

    shots, t, beat_count = [], 0.0, {}
    for g in groups:
        sid = g[0]["id"] if len(g) == 1 else f"{g[0]['id']}-{g[-1]['id'][-2:]}"
        n_in_beat = beat_count.get(g[0]["beat"], 0)
        beat_count[g[0]["beat"]] = n_in_beat + 1
        bp = default_blueprint(g, n_in_beat == 0, n_in_beat, video)
        source = "auto"
        if sid in ai:
            bp.update({k: v for k, v in ai[sid].items() if k != "id" and v is not None})
            source = "ai"
        pause = sum(PAUSE_AFTER[x["pace"]] for x in g)
        dur = sum(x["est"] for x in g) + pause
        t += g[0]["silence_before"]
        prompt = (f"{STYLES[style]}. {bp['shot_angle']}. {bp['subject_action']}. {bp['atmosphere']}. "
                  f"{bp['lighting_palette']}. Setting: {bp.get('setting') or video['setting']}. {bp.get('accuracy') or video['accuracy']}.")
        shots.append({
            "id": sid, "lines": [x["id"] for x in g], "chapter": g[0]["chapter"], "saga": g[0]["saga"],
            "pace": bp["pace"], "narration": " ".join(x["text"] for x in g),
            "start": round(t, 2), "duration": round(dur, 2), "silence_before": g[0]["silence_before"],
            "pause_after": round(pause, 2), "type": bp["primary_visual"], "blueprint": bp, "blueprint_source": source,
            "prompt": prompt, "refs": bp["refs"], "motion": MOTION[bp["pace"]][n_in_beat % len(MOTION[bp["pace"]])],
            "sound": [s for x in g for s in x["sound"]], "cue": g[0]["cue"],
        })
        t += dur

    # chọn tối đa MAX_CLIPS cảnh làm clip AI: AI đã chỉ định trước, rồi đến cảnh đầu beat có chuyển động mạnh
    clips = [s for s in shots if s["type"] == "ai_clip"]
    for s in shots:
        if len(clips) >= MAX_CLIPS:
            break
        if s not in clips and s["blueprint_source"] == "auto" and s["type"] == "illustration" \
                and s["id"].endswith("_l01") and re.search(CLIP_HINT, s["cue"], re.I):
            s["type"] = "ai_clip"
            clips.append(s)
    for s in clips:
        s["video_prompt"] = (s["blueprint"].get("motion") or
                             f"Animate this exact image. Primary: {s['blueprint']['subject_action'].rstrip('.')}, moving subtly. "
                             "Physics: slow, heavy, natural motion. Environment: snow, smoke or firelight drifting. "
                             "Slow calm camera; characters keep their faces and clothing; no morphing.")
    return lines, shots


def write_prompts_md(path, shots, style):
    kinds = {}
    for s in shots:
        kinds[s["type"]] = kinds.get(s["type"], 0) + 1
    lines = [f"# Prompt tạo hình · phong cách {style}", "",
             f"Tổng {len(shots)} cảnh · " + " · ".join(f"{k} {v}" for k, v in sorted(kinds.items())), "",
             "Lưu kết quả vào `assets/` đúng tên `<id>.png` (ảnh) hoặc `<id>.mp4` (clip).", ""]
    chapter = None
    for s in shots:
        if s["chapter"] != chapter:
            chapter = s["chapter"]
            lines += [f"## {chapter}", ""]
        lines.append(f"**{s['id']}** · {s['type']} · [{s['pace']}] · {s['duration']}s · tham chiếu: {', '.join(s['refs']) or '—'}"
                     + (" · thiết kế: AI" if s["blueprint_source"] == "ai" else ""))
        lines.append(f"> {s['narration']}")
        lines.append(f"```\n{s['prompt']}\n```")
        if s.get("video_prompt"):
            lines.append(f"Clip: `{s['video_prompt']}`")
        if s["sound"]:
            lines.append(f"Âm thanh: {' · '.join(s['sound'])}")
        lines.append("")
    path.write_text("\n".join(lines), "utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_dir", type=Path)
    ap.add_argument("--style", default="A", choices=STYLES)
    ap.add_argument("--durations", type=Path, help="JSON {id dòng: giây} từ file giọng đọc")
    ap.add_argument("--export-lines", action="store_true", help="xuất lines_for_blueprint.json cho tầng 4")
    a = ap.parse_args()
    durations = json.loads(a.durations.read_text("utf-8")) if a.durations else None
    lines, shots = build(a.video_dir, a.style, durations)
    if a.export_lines:
        export = [{"id": s["id"], "chapter": s["chapter"], "saga": s["saga"], "pace": s["pace"],
                   "beat_cue": s["cue"], "narration": s["narration"]} for s in shots]
        (a.video_dir / "lines_for_blueprint.json").write_text(json.dumps(export, ensure_ascii=False, indent=1), "utf-8")
        print(f"Đã xuất {len(export)} cảnh → lines_for_blueprint.json")
    (a.video_dir / "shotlist.json").write_text(json.dumps({"style": a.style, "shots": shots}, ensure_ascii=False, indent=1), "utf-8")
    write_prompts_md(a.video_dir / "prompts.md", shots, a.style)
    total = shots[-1]["start"] + shots[-1]["duration"]
    kinds = {}
    for s in shots:
        kinds[s["type"]] = kinds.get(s["type"], 0) + 1
    ai_n = sum(s["blueprint_source"] == "ai" for s in shots)
    print(f"{len(lines)} dòng → {len(shots)} cảnh · {total / 60:.1f} phút (gồm khoảng nghỉ) · {kinds} · thiết kế AI: {ai_n}/{len(shots)}")


if __name__ == "__main__":
    main()
