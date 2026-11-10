"""AI Film Studio: ghép giọng thuyết minh Genmax + phụ đề vào thư mục clip đã render (Muse...).

Cách dùng:
  python ai_film_studio.py chay  <thu_muc_du_an>                 # chạy thật, gọi Genmax
  python ai_film_studio.py chay  <thu_muc_du_an> --chi-kiem-tra  # chỉ ước lượng thời lượng, không tốn credit
  python ai_film_studio.py chay  <thu_muc_du_an> --gia-lap       # dùng giọng giả để thử căn chỉnh
  python ai_film_studio.py giong --ngon-ngu vi --prompt "giọng nam trầm kể chuyện"

Thư mục dự án:
  <thư mục clip>/ các video, xếp theo tên file (01.mp4, 02.mp4, ...); tự tìm thư mục con đầu tiên có video
  prompt.md       mục "mô tả giọng" (viết tiếng gì cũng được) + mục "toàn văn": mỗi đoạn cách 1 dòng trống = 1 clip,
                  "[3-5] ..." = đoạn đọc trải qua clip 3 đến 5. Lời viết bằng tiếng nào thì giọng & phụ đề tiếng đó.
  kich_ban.txt    (tùy chọn) dùng khi prompt chỉ có mô tả giọng
  cau_hinh.json   (tùy chọn) ghi đè DEFAULT_CONFIG
  nhac_nen.mp3    (tùy chọn) nhạc nền, tự giảm khi có lời đọc
"""
import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from genmax import SPEED_LIMITS, Genmax, GenmaxError

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}

DEFAULT_CONFIG = {
    "thu_muc_clip": None,         # để trống = thư mục con đầu tiên có video
    "file_prompt": None,          # để trống = prompt.md hoặc prompt.txt
    "file_kich_ban": None,        # để trống = lấy mục toàn văn trong prompt, không có thì kich_ban.txt
    "api_key": None,              # hoặc đặt biến môi trường GENMAX_API_KEY
    "provider": "minimax",        # minimax | elevenlabs | capcut
    "model_id": "speech-2.8-hd",  # elevenlabs: eleven_multilingual_v2
    "voice_id": None,             # để trống = tự chọn theo ngôn ngữ kịch bản + prompt.txt
    "ngon_ngu": None,             # để trống = tự nhận diện từ kịch bản (vi, en, ja, zh...)
    "toc_do": 1.0,                # tốc độ đọc cơ bản
    "toc_do_toi_da": 1.2,         # được tăng tốc tới mức này khi lời dài hơn cảnh
    "dem_dau": 0.25,              # giây im lặng trước khi bắt đầu đọc trong mỗi cảnh
    "dem_cuoi": 0.35,             # giây im lặng chừa lại cuối cảnh
    "khoang_nghi": 0.4,           # nghỉ tối thiểu giữa 2 đoạn lời liền nhau
    "lech_toi_da": 3.0,           # lời dài được tràn sang cảnh sau; đoạn sau được bắt đầu trễ tối đa chừng này giây
    "keo_cham_hinh_toi_da": 1.3,  # trễ quá mức: làm chậm hình cảnh trước tới mức này, thiếu nữa thì dừng hình
    "am_luong_goc": 0.0,          # âm thanh gốc của clip (0 = tắt)
    "am_luong_nhac": 0.15,
    "phu_de": True,               # in phụ đề lên video (luôn xuất thêm file .srt)
    "co_chu_phu_de": None,        # để trống = tự chọn theo khung hình
    "phu_de_kieu": None,          # None = chữ trắng viền đen; "dai_den" = chữ trắng trên dải đen ngang đáy khung
    "do_phan_giai": None,         # ví dụ [1920, 1080]; để trống = lấy theo clip đầu tiên
    "fps": 30,
    "song_song": 4,               # số đoạn gọi Genmax cùng lúc
    "giu_file_tam": False,        # giữ output/tmp và video_ghep.mp4 để soi lỗi
    "cach_doc": None,             # {"chữ": "cách đọc"}: chỉ thay trong lời gửi đi đọc, phụ đề giữ chữ gốc
}

# Tốc độ đọc ước lượng (ký tự/giây) để kiểm tra trước khi tốn credit
CHARS_PER_SEC = {"zh": 5.0, "yue": 5.0, "ja": 6.0, "ko": 7.0, "th": 13.0, "vi": 16.0}

LANG_NAMES = {"vi": "tiếng Việt", "en": "tiếng Anh", "ja": "tiếng Nhật", "zh": "tiếng Trung", "ko": "tiếng Hàn",
              "th": "tiếng Thái", "es": "tiếng Tây Ban Nha", "fr": "tiếng Pháp", "de": "tiếng Đức",
              "pt": "tiếng Bồ Đào Nha", "it": "tiếng Ý", "ru": "tiếng Nga", "id": "tiếng Indonesia",
              "yue": "tiếng Quảng Đông", "hi": "tiếng Hindi", "ar": "tiếng Ả Rập"}
DEFAULT_CPS = 15.0

SUB_FONT = {"zh": "Microsoft YaHei", "yue": "Microsoft YaHei", "ja": "Yu Gothic",
            "ko": "Malgun Gothic", "th": "Leelawadee UI", "hi": "Nirmala UI"}
CJK = {"zh", "yue", "ja", "ko"}


# ---------------------------------------------------------------- tiện ích

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if p.returncode != 0:
        raise RuntimeError(f"Lệnh lỗi: {' '.join(map(str, cmd))[:400]}\n{p.stderr[-1500:]}")
    return p.stdout


def probe(path):
    out = json.loads(run(["ffprobe", "-v", "error", "-show_entries",
                          "format=duration:stream=codec_type,width,height", "-of", "json", str(path)]))
    streams = out.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), {})
    return {
        "duration": float(out["format"]["duration"]),
        "width": video.get("width"),
        "height": video.get("height"),
        "has_audio": any(s.get("codec_type") == "audio" for s in streams),
    }


def natural_key(name):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", name)]


def srt_time(t):
    ms = int(round(max(t, 0) * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


# ---------------------------------------------------------------- ngôn ngữ & giọng

VI_CHARS = set("ăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ")


SCRIPTS = {  # bảng chữ -> regex
    "kana": r"[぀-ヿ]", "han": r"[一-鿿]", "hangul": r"[가-힯]",
    "thai": r"[฀-๿]", "cyrillic": r"[Ѐ-ӿ]", "arabic": r"[؀-ۿ]",
    "devanagari": r"[ऀ-ॿ]", "latin": r"[A-Za-zÀ-ɏḀ-ỿ]",
}


def detect_language(text):
    """Ngôn ngữ của lời đọc, tính theo bảng chữ chiếm đa số (vài tên riêng nước ngoài không làm nhận nhầm)."""
    count = {k: len(re.findall(rx, text)) for k, rx in SCRIPTS.items()}
    cjk = count["kana"] + count["han"]
    groups = {"cjk": cjk, **{k: v for k, v in count.items() if k not in ("kana", "han")}}
    main = max(groups, key=groups.get)
    if main == "cjk":
        return "ja" if count["kana"] >= cjk * 0.1 else "zh"
    if main in ("hangul", "thai", "arabic", "devanagari"):
        return {"hangul": "ko", "thai": "th", "arabic": "ar", "devanagari": "hi"}[main]
    if main == "latin" and sum(c in VI_CHARS for c in text.lower()) >= max(3, count["latin"] * 0.02):
        return "vi"
    try:
        from langdetect import DetectorFactory, detect
        DetectorFactory.seed = 0
        return detect(text).split("-")[0]
    except Exception:
        return "ru" if main == "cyrillic" else "en"


# Tên các ngôn ngữ viết bằng nhiều thứ tiếng, để đọc câu kiểu "đọc bằng tiếng Nhật", "Language: Japanese", "日本語で"
LANG_KEYWORDS = {
    "vi": ["tiếng việt", "vietnamese", "ベトナム語", "越南语", "越南語", "베트남어", "vietnamita", "vietnamien"],
    "en": ["tiếng anh", "english", "英語", "英语", "영어", "inglés", "anglais"],
    "ja": ["tiếng nhật", "japanese", "日本語", "日语", "일본어", "japonés", "japonais"],
    "zh": ["tiếng trung", "tiếng hoa", "chinese", "mandarin", "中国語", "中文", "普通话", "汉语", "중국어", "chino",
           "chinois"],
    "yue": ["tiếng quảng đông", "cantonese", "広東語", "粤语", "粵語", "광동어"],
    "ko": ["tiếng hàn", "korean", "韓国語", "韩语", "한국어", "coreano", "coréen"],
    "th": ["tiếng thái", "thai", "タイ語", "泰语", "태국어", "ภาษาไทย", "tailandés"],
    "es": ["tiếng tây ban nha", "spanish", "español", "スペイン語", "西班牙语", "스페인어", "espagnol"],
    "fr": ["tiếng pháp", "french", "français", "フランス語", "法语", "프랑스어", "francés"],
    "de": ["tiếng đức", "german", "deutsch", "ドイツ語", "德语", "독일어", "alemán", "allemand"],
    "pt": ["tiếng bồ đào nha", "portuguese", "português", "ポルトガル語", "葡萄牙语", "포르투갈어", "portugués"],
    "it": ["tiếng ý", "italian", "italiano", "イタリア語", "意大利语", "이탈리아어", "italien"],
    "ru": ["tiếng nga", "russian", "русский", "ロシア語", "俄语", "러시아어", "ruso", "russe"],
    "id": ["tiếng indonesia", "indonesian", "bahasa indonesia", "インドネシア語", "印尼语", "인도네시아어"],
    "hi": ["tiếng hindi", "tiếng ấn", "hindi", "हिन्दी", "ヒンディー語", "印地语", "힌디어"],
    "ar": ["tiếng ả rập", "arabic", "العربية", "アラビア語", "阿拉伯语", "아랍어", "árabe", "arabe"],
}
# Từ đứng trước/sau tên ngôn ngữ để chắc đó là yêu cầu đọc bằng tiếng đó (tránh khớp nhầm "English fallback")
LANG_LABEL = r"(?:ngôn ngữ|language|言語|语言|語言|언어|idioma|langue|sprache)\s*[:：=]?\s*"
LANG_VERB = (r"(?:^|(?<=[\s(（,、:：]))(?:đọc|giọng|lời|thuyết minh|voice|narration|narrator|read|speak|spoken|"
             r"dub|voz|voix|in|en|em|auf|bằng)\s+(?:bằng\s+|in\s+)?")
LANG_AFTER = r"\s*(?:で|の(?:ナレーション|音声|声|語り)|로|으로|配音|旁白|朗读|voice|narrat|speaker)"


def requested_language(text):
    """Ngôn ngữ mà prompt yêu cầu rõ ràng (vd 'đọc bằng tiếng Nhật', 'Language: English', '日本語で'), không có thì None."""
    t = text.lower()
    for code, names in LANG_KEYWORDS.items():
        for name in names:
            n = re.escape(name)
            if re.search(rf"{LANG_LABEL}{n}|{LANG_VERB}{n}|(?:用|以){n}|{n}{LANG_AFTER}", t):
                return code
    return None


# Đặc điểm giọng: (từ khóa trong prompt, viết bằng nhiều thứ tiếng; từ khóa trong mô tả giọng của Genmax, tiếng Anh).
# Prompt viết bằng tiếng gì cũng được: Việt, Anh, Nhật, Trung, Hàn, Tây Ban Nha, Pháp, Thái.
VOICE_TRAITS = {
    "female": (["giọng nữ", "phụ nữ", "cô gái", "female", "woman", "girl", "女性", "女声", "女の", "여성", "여자",
                "mujer", "femenin", "femme", "féminin", "หญิง"], []),
    "male": (["giọng nam", "nam giới", "đàn ông", "chàng trai", "male", "man", "boy", "男性", "男声", "男の", "남성",
              "남자", "hombre", "masculin", "homme", "ชาย"], []),
    "young": (["trẻ", "young", "teen", "youth", "若い", "若者", "青年", "少年", "年轻", "젊은", "청년", "joven",
               "jeune", "วัยรุ่น"], ["young", "youth", "teen", "boy", "girl", "kid", "innocent"]),
    "mature": (["trung niên", "lớn tuổi", "già", "mature", "middle-aged", "elderly", "old", "中年", "年配", "壮年",
                "老年", "成熟", "중년", "노인", "maduro", "mûr", "âgé", "40代", "50代", "40s", "50s"],
               ["mature", "middle", "senior", "old", "elder", "uncle", "veteran"]),
    "deep": (["trầm", "deep", "low", "低音", "中低音", "低い声", "低沉", "浑厚", "저음", "낮은", "grave", "profund"],
             ["deep", "low", "baritone", "bass", "resonant", "magnetic"]),
    "calm": (["điềm tĩnh", "bình tĩnh", "từ tốn", "calm", "steady", "落ち着", "穏やか", "淡々", "冷静", "沉稳", "平静",
              "차분", "침착", "tranquil", "calme", "serein"], ["calm", "steady", "composed", "measured", "relaxed"]),
    "narration": (["kể chuyện", "thuyết minh", "tài liệu", "narrat", "documentary", "storytell", "ナレーター",
                   "ナレーション", "ドキュメンタリー", "語り", "纪录片", "旁白", "解说", "내레이션", "다큐", "documental",
                   "narrador", "documentaire", "narrateur", "สารคดี"],
                  ["narrat", "documentary", "storytell", "audiobook"]),
    "news": (["tin tức", "thời sự", "news", "broadcast", "ニュース", "報道", "公共放送", "アナウンサー", "新闻", "播音",
              "뉴스", "아나운서", "noticias", "journal", "ข่าว"], ["news", "broadcast", "anchor", "announcer"]),
    "serious": (["nghiêm túc", "căng thẳng", "serious", "authoritative", "緊張", "真剣", "重厚", "严肃", "진지",
                 "serio", "sérieux"], ["serious", "authoritative", "grave", "solemn"]),
    "intellectual": (["phân tích", "trí thức", "analytical", "intellectual", "知的", "分析", "理性", "知性", "지적",
                      "analítico", "analytique"], ["intellectual", "analytical", "rational", "precise"]),
    "warm": (["ấm", "warm", "温か", "暖か", "温暖", "따뜻", "cálid", "chaleureu"], ["warm"]),
    "clear": (["rõ ràng", "clear", "articulate", "明瞭", "はっきり", "清晰", "명확", "또렷", "clara", "clair"],
              ["clear", "crisp", "articulate"]),
    "powerful": (["mạnh mẽ", "hùng hồn", "powerful", "epic", "力強", "迫力", "雄厚", "有力", "힘있", "강렬", "potente",
                  "puissant"], ["powerful", "strong", "epic", "commanding"]),
    "gentle": (["nhẹ nhàng", "dịu dàng", "gentle", "soft", "優し", "柔らか", "温柔", "부드러", "suave", "doux"],
               ["gentle", "soft", "soothing", "tender"]),
    "cheerful": (["vui tươi", "hài hước", "sôi động", "cheerful", "funny", "energetic", "明るい", "元気", "活泼",
                  "欢快", "밝은", "alegre", "joyeux"], ["cheerful", "bright", "lively", "energetic", "playful"]),
    # Phong cách theo chủ đề
    "horror": (["kinh dị", "rùng rợn", "bí ẩn", "ma quái", "horror", "creepy", "mysterious", "spooky", "ホラー",
                "怖い", "不気味", "ミステリー", "恐怖", "悬疑", "神秘", "공포", "미스터리", "terror", "misterio",
                "horreur", "mystère", "สยองขวัญ"], ["horror", "creepy", "mysterious", "eerie", "dark", "sinister"]),
    "kids": (["thiếu nhi", "trẻ em", "trẻ con", "hoạt hình", "cổ tích", "kids", "children", "cartoon", "fairy tale",
              "子供向け", "童話", "アニメ", "儿童", "童话", "动画", "어린이", "동화", "infantil", "enfants"],
             ["kid", "child", "cartoon", "cute", "fairy", "animated"]),
    "inspiring": (["truyền cảm hứng", "động lực", "khích lệ", "motivational", "inspiring", "inspirational",
                   "感動", "励まし", "モチベーション", "励志", "激励", "동기부여", "감동", "motivador", "inspirant"],
                  ["inspir", "motivat", "uplifting", "passionate"]),
    "romantic": (["lãng mạn", "ngọt ngào", "tình cảm", "romantic", "sweet", "loving", "ロマンチック", "甘い", "浪漫",
                  "甜美", "로맨틱", "달콤", "romántic", "romantique"], ["romantic", "sweet", "tender", "intimate"]),
    "whisper": (["thì thầm", "asmr", "whisper", "囁き", "ささやき", "耳语", "低语", "속삭", "susurr", "chuchot"],
                ["whisper", "asmr", "breathy", "hushed"]),
    "sports": (["thể thao", "bình luận", "hào hứng", "sports", "commentat", "excited", "hype", "実況", "スポーツ",
                "解説者", "体育", "解说员", "激动", "스포츠", "중계", "deportiv", "sportif"],
               ["sport", "commentat", "excited", "hype", "dynamic", "energetic"]),
    "sad": (["buồn", "u sầu", "xúc động", "sad", "melanchol", "emotional", "悲しい", "切ない", "感傷", "悲伤", "伤感",
             "슬픈", "애절", "triste", "mélancol"], ["sad", "melanchol", "emotional", "sorrow", "tender"]),
    "meditation": (["thiền", "thư giãn", "chữa lành", "meditation", "relaxing", "soothing", "healing", "瞑想",
                    "癒し", "リラックス", "冥想", "治愈", "放松", "명상", "힐링", "meditación", "relajante", "méditation"],
                   ["soothing", "calm", "meditat", "healing", "relax", "gentle"]),
    "commercial": (["quảng cáo", "bán hàng", "review", "advert", "commercial", "promo", "広告", "セールス",
                    "广告", "带货", "광고", "publicidad", "publicité"], ["advert", "commercial", "promo", "sales",
                                                                       "persuasive"]),
    "fast": (["nhanh", "dồn dập", "fast", "quick", "brisk", "速い", "早口", "テンポよく", "快速", "语速快", "빠른",
              "rápid", "rapide"], ["fast", "quick", "brisk", "rapid", "energetic"]),
    "slow": (["chậm rãi", "từ từ", "slow", "unhurried", "ゆっくり", "遅め", "缓慢", "慢慢", "천천히", "lento", "lent"],
             ["slow", "unhurried", "deliberate", "leisurely"]),
    # Giọng vùng miền: khớp với nhãn giọng của Genmax (vd EN-British, EN-US)
    "accent_north_vi": (["miền bắc", "giọng bắc", "hà nội", "northern vietnamese"], ["north", "hanoi"]),
    "accent_south_vi": (["miền nam", "giọng sài gòn", "sài gòn", "southern vietnamese"], ["south", "saigon"]),
    "accent_british": (["giọng anh-anh", "british", "uk accent", "イギリス", "英式", "영국"],
                       ["british", "uk", "england", "london"]),
    "accent_american": (["giọng mỹ", "anh mỹ", "american", "us accent", "アメリカ英語", "美式", "미국"],
                        ["american", "us", "general american"]),
    "accent_australian": (["giọng úc", "australian", "aussie", "オーストラリア", "澳洲", "호주"],
                          ["australian", "aussie"]),
    "accent_kansai": (["関西弁", "kansai", "osaka", "大阪弁"], ["kansai", "osaka"]),
    "accent_latam": (["latino", "mexicano", "latinoamerican", "latin american"], ["latin", "mexic", "latam"]),
    "accent_brazil": (["brasileiro", "brazilian", "brasil"], ["brazil", "brasil"]),
}
OPPOSITE_TRAIT = {"young": "mature", "mature": "young", "calm": "cheerful", "cheerful": "calm",
                  "fast": "slow", "slow": "fast", "kids": "horror"}
TRAIT_WEIGHT = {"young": 2, "mature": 2, "narration": 2, "horror": 2, "kids": 2, "whisper": 2, "sports": 2}
TRAIT_WEIGHT.update({t: 3 for t in VOICE_TRAITS if t.startswith("accent_")})


def _has_word(text, word):
    """Tiếng Latin: so khớp đầu từ (từ ngắn phải khớp nguyên từ, để 'male' không khớp 'female').
    Chữ Nhật/Trung/Hàn/Thái: so khớp chuỗi con."""
    if word.isascii():
        end = r"\b" if len(word) <= 4 else ""
        return re.search(rf"\b{re.escape(word)}{end}", text) is not None
    return word in text


def analyze_voice_prompt(prompt):
    """Đọc mô tả giọng (bất kỳ thứ tiếng nào) -> giới tính, các đặc điểm, tốc độ đọc."""
    p = prompt.lower()
    found = [t for t, (words, _) in VOICE_TRAITS.items() if any(_has_word(p, w) for w in words)]
    gender = None
    if "female" in found and "male" not in found:
        gender = "female"
    elif "male" in found and "female" not in found:
        gender = "male"
    traits = [t for t in found if t not in ("male", "female")]
    m = (re.search(r"(\d+(?:[.,]\d+)?)\s*(?:倍|x|×|lần|배)", p)
         or re.search(r"(?:x|×|speed|tốc độ|速度)\s*[:=]?\s*(\d+(?:[.,]\d+)?)", p))
    speed = float(m[1].replace(",", ".")) if m else None
    if speed is not None and not 0.5 <= speed <= 2.0:
        speed = None
    return {"gender": gender, "traits": traits, "speed": speed}


def prompt_gender(prompt):
    return analyze_voice_prompt(prompt)["gender"]


def rank_voices(voices, prompt, long_script=False):
    """Chấm điểm giọng theo mô tả. long_script: lời dài so với video -> tránh giọng đọc chậm."""
    wanted = analyze_voice_prompt(prompt)
    if long_script and "slow" not in wanted["traits"] and "fast" not in wanted["traits"]:
        wanted["traits"].append("fast")
    ranked = []
    for v in voices:
        desc = f"{v['name']} {v['description']} {v['age']}".lower()
        score, why = 0, []
        if wanted["gender"]:
            if v["gender"] == wanted["gender"]:
                score += 5
                why.append(wanted["gender"])
            elif v["gender"]:
                score -= 10
        for trait in wanted["traits"]:
            if any(_has_word(desc, w) for w in VOICE_TRAITS[trait][1]):
                score += TRAIT_WEIGHT.get(trait, 1)
                why.append(trait)
            opposite = OPPOSITE_TRAIT.get(trait)
            if opposite and opposite not in wanted["traits"] and \
                    any(_has_word(desc, w) for w in VOICE_TRAITS[opposite][1]):
                score -= 2
                why.append(f"-{opposite}")
        if v.get("verified_for_lang"):
            score += 3
            why.append("đúng ngôn ngữ")
        ranked.append((score, why, v))
    ranked.sort(key=lambda x: -x[0])
    return ranked


def pick_voice(client, cfg, lang, prompt, long_script=False):
    """Trả (provider, model_id, voice_id, mô tả). Không có giọng MiniMax cho ngôn ngữ này thì chuyển sang ElevenLabs."""
    if cfg["voice_id"]:
        return cfg["provider"], cfg["model_id"], cfg["voice_id"], "voice_id trong cau_hinh.json"
    provider, model = cfg["provider"], cfg["model_id"]
    voices = client.voices(provider, lang=lang, gender=prompt_gender(prompt))
    if not voices and provider == "minimax":
        print(f"  MiniMax không có giọng cho '{lang}', chuyển sang ElevenLabs multilingual")
        provider, model = "elevenlabs", "eleven_multilingual_v2"
        voices = client.voices(provider, lang=lang)
    if not voices:
        raise GenmaxError(f"Không tìm thấy giọng nào cho ngôn ngữ '{lang}'")
    ranked = rank_voices(voices, prompt, long_script)
    if long_script:
        print("  Lời đọc dài so với video: ưu tiên giọng đọc nhanh, tránh giọng chậm")
    print("  Top giọng phù hợp (muốn cố định thì chép voice_id vào cau_hinh.json):")
    for score, why, v in ranked[:5]:
        print(f"    [{score:>3}] {v['voice_id']:<18} {v['name'][:40]:<40} {', '.join(why)}")
        if v.get("preview"):
            print(f"          nghe thử: {v['preview']}")
    best = ranked[0][2]
    return provider, model, best["voice_id"], best["name"]


# ---------------------------------------------------------------- prompt

VOICE_HEADING = re.compile(r"giọng|voice|style|phong cách|声|音色|ボイス|목소리|음성|voz|voix|เสียง", re.I)
SCRIPT_HEADING = re.compile(r"kịch bản|toàn văn|lời đọc|lời thoại|lời bình|lời thuyết minh|nội dung|script|"
                            r"full text|narration text|transcript|台本|原稿|本文|脚本|文稿|旁白稿|대본|원고|guion|texte|"
                            r"บท", re.I)
# Dòng nhãn kiểu "Giọng: ...", "**Voice:**", "1. Kịch bản：" (không cần markdown #)
LABEL_LINE = re.compile(r"^\s*(?:\d+[.)]\s*)?(?:\*\*)?(?P<label>[^:：\n*]{1,40}?)(?:\*\*)?\s*[:：]\s*(?:\*\*)?"
                        r"\s*(?P<rest>.*)$")


def _paragraphs(body):
    """Các đoạn văn của 1 mục, bỏ bảng, gạch đầu dòng, khối code và dòng kẻ."""
    body = re.sub(r"```.*?```", "", body, flags=re.S)
    keep = [ln for ln in body.splitlines() if not re.match(r"\s*(\||[-*] |---|>)", ln)]
    return [p.strip() for p in re.split(r"\n\s*\n", "\n".join(keep)) if p.strip()]


def _sections(text):
    """Chia prompt thành các mục (tiêu đề, nội dung). Tiêu đề là dòng markdown '#',
    hoặc dòng nhãn 'Giọng: ...' / 'Kịch bản:' có chữ giống tiêu đề giọng hay kịch bản."""
    sections, heading, body = [], None, []
    for line in text.splitlines():
        md = re.match(r"^\s*#{1,6}\s+(.*)$", line)
        label = LABEL_LINE.match(line) if not md else None
        if label and not (VOICE_HEADING.search(label["label"]) or SCRIPT_HEADING.search(label["label"])):
            label = None
        if md or label:
            if heading is not None:
                sections.append((heading, "\n".join(body)))
            heading = md[1].strip() if md else label["label"].strip()
            body = [] if md else [label["rest"]]
        elif heading is not None:
            body.append(line)
    if heading is not None:
        sections.append((heading, "\n".join(body)))
    return sections


def parse_prompt(text):
    """Tách prompt thành (mô tả giọng, lời đọc). Không phụ thuộc chủ đề hay thứ tiếng của prompt.

    - Có mục/nhãn: mục "giọng/voice/声..." là mô tả giọng; mục "kịch bản/toàn văn/script/台本..."
      (hoặc mục có nhiều đoạn văn nhất) là lời đọc, mỗi đoạn cách nhau 1 dòng trống = 1 cảnh.
    - Không có mục: đoạn đầu là mô tả giọng nếu nó đúng là mô tả giọng (có giới tính/đặc điểm),
      các đoạn còn lại là lời đọc. Chỉ 1 đoạn thì coi là mô tả giọng, lời đọc lấy từ kich_ban.txt.
    """
    sections = _sections(text)
    if not sections:
        blocks = _paragraphs(text)
        if len(blocks) == 1:
            return blocks[0], None
        first = analyze_voice_prompt(blocks[0])
        looks_like_voice = len(blocks[0]) < 400 and (first["gender"] or len(first["traits"]) >= 2)
        if looks_like_voice:
            return blocks[0], "\n\n".join(blocks[1:]) if len(blocks) > 1 else None
        return "", "\n\n".join(blocks) if blocks else None

    voice = next((re.sub(r"```[^\n]*", "", body).strip() for heading, body in sections
                  if VOICE_HEADING.search(heading) and not SCRIPT_HEADING.search(heading) and body.strip()), "")
    candidates = [(len(_paragraphs(body)), bool(SCRIPT_HEADING.search(heading)), body)
                  for heading, body in sections
                  if SCRIPT_HEADING.search(heading) or not VOICE_HEADING.search(heading)]
    candidates = [c for c in candidates if c[0] >= 1]
    if not candidates:
        return voice, None
    # Ưu tiên mục có tiêu đề kiểu "kịch bản", rồi tới mục có nhiều đoạn nhất
    n, _, body = max(candidates, key=lambda c: (c[1], c[0]))
    return voice, "\n\n".join(_paragraphs(body))


# ---------------------------------------------------------------- kịch bản

NO_SPACE_CHAR = re.compile(r"[　-ヿ一-鿿＀-￯]")  # chữ Nhật/Trung viết liền


def join_lines(block):
    """Nối các dòng của 1 đoạn, giữ nguyên chữ: tiếng Nhật/Trung nối liền, tiếng khác nối bằng 1 dấu cách."""
    out = ""
    for line in (ln.strip() for ln in block.splitlines()):
        if not line:
            continue
        if out and not (NO_SPACE_CHAR.match(out[-1]) and NO_SPACE_CHAR.match(line[0])):
            out += " "
        out += line
    return out


def parse_script(text, n_clips):
    segments, next_clip = [], 1
    for block in re.split(r"\n\s*\n", text.strip()):
        m = re.match(r"\s*\[(\d+)(?:\s*-\s*(\d+))?\]\s*", block)
        if m:
            start, end = int(m[1]), int(m[2] or m[1])
            block = block[m.end():]
        else:
            start = end = next_clip
        content = join_lines(block)
        if not content:
            continue
        if start < next_clip:
            raise ValueError(f"Đoạn \"{content[:40]}...\" bắt đầu ở clip {start} nhưng clip này đã có lời")
        if end < start or end > n_clips:
            raise ValueError(f"Đoạn \"{content[:40]}...\" trỏ tới clip {start}-{end}, nhưng chỉ có {n_clips} clip")
        segments.append({"clips": [start, end], "text": content})
        next_clip = end + 1
    return segments


# Chữ Nhật/Trung không có khoảng trắng: khi không có dấu phẩy thì cắt sau trợ từ để không đứt giữa từ
SOFT_BREAKS = {"ja": "はがをにでともへ", "zh": "的了在和是"}


def split_caption(text, max_chars, lang=None):
    chunks = []
    soft = SOFT_BREAKS.get(lang, "")
    # Dấu chấm trong số thập phân (1.5兆円, 11.9%) không phải hết câu
    for sentence in re.split(r"(?<=[!?…。！？])\s*|(?<=\.)(?!\d)\s*", text):
        s = sentence.strip()
        # Câu CJK chỉ dài hơn một chút thì để 1 dòng, tránh dòng sau chỉ còn vài chữ
        limit = max_chars * 1.3 if lang in CJK else max_chars
        while len(s) > limit:
            # Chia đều câu dài thành các dòng gần bằng nhau, ưu tiên cắt ở dấu phẩy rồi tới khoảng trắng/trợ từ
            target = len(s) / math.ceil(len(s) / max_chars)
            seps = [i for i, ch in enumerate(s[:max_chars]) if ch in ",，、;； " + soft and i > max_chars * 0.3]
            if seps:
                cut = min(seps, key=lambda i: abs(i + 1 - target) - (4 if s[i] in ",，、;；" else 0))
                piece = s[:cut + 1]
            else:
                piece = s[:round(target)]
            chunks.append(piece.strip())
            s = s[len(piece):].strip()
        if s:
            chunks.append(s)
    return chunks


# ---------------------------------------------------------------- tạo giọng

class VoiceMaker:
    """mode: "that" = gọi Genmax, "gia_lap" = tiếng bíp, "uoc_luong" = chỉ tính thời lượng, không tạo file.

    Lời đọc được gửi tới Genmax như trong prompt, chỉ thay các mục trong cfg["cach_doc"] (xem doc_theo_bang).
    """

    def __init__(self, out_dir, lang, mode, client=None, provider=None, model=None, voice_id=None):
        self.dir = out_dir / "voice"
        self.lang, self.mode, self.client = lang, mode, client
        self.provider, self.model, self.voice_id = provider, model, voice_id
        if mode != "uoc_luong":
            self.dir.mkdir(parents=True, exist_ok=True)

    def make(self, text, speed):
        if self.mode == "uoc_luong":
            return None, len(text) / CHARS_PER_SEC.get(self.lang, DEFAULT_CPS) / speed
        key = json.dumps([self.mode, self.provider, self.model, self.voice_id, self.lang, text, round(speed, 3)])
        wav = self.dir / f"{hashlib.sha1(key.encode()).hexdigest()[:16]}.wav"
        if not wav.exists():  # đã tạo rồi thì dùng lại, không tốn credit lần nữa
            if self.mode == "gia_lap":
                dur = len(text) / CHARS_PER_SEC.get(self.lang, DEFAULT_CPS) / speed
                run(["ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=330:sample_rate=48000",
                     "-af", "volume=0.15", "-t", f"{dur:.3f}", "-ac", "2", str(wav)])
            else:
                task = self.client.tts(text, self.voice_id, self.lang, self.provider, self.model, speed)
                raw = wav.with_suffix(".mp3")
                self.client.download(task["result"]["audio_url"], raw)
                # Cắt khoảng lặng đầu/cuối để đo đúng thời lượng lời
                trim = "silenceremove=start_periods=1:start_threshold=-50dB"
                run(["ffmpeg", "-y", "-i", str(raw), "-af", f"{trim},areverse,{trim},areverse",
                     "-ar", "48000", "-ac", "2", str(wav)])
                raw.unlink()
        return wav, probe(wav)["duration"]


def doc_theo_bang(text, bang):
    """Thay tên riêng bằng cách đọc (ví dụ 新発田 -> しばた) trong một lượt; khóa dài được ưu tiên."""
    if not bang:
        return text
    pattern = re.compile("|".join(re.escape(k) for k in sorted(bang, key=len, reverse=True) if k))
    return pattern.sub(lambda m: bang[m.group(0)], text)


def synth_segment(seg, clip_durs, cfg, maker):
    """Tạo giọng 1 đoạn. Chỉ tăng tốc đọc khi riêng đoạn này đã dài hơn cảnh của nó + độ trễ cho phép,
    để giọng giữ đều tốc độ; phần dài vừa phải sẽ được tràn sang cảnh sau ở bước layout()."""
    s, e = seg["clips"]
    allow = max(sum(clip_durs[s - 1:e]) - cfg["dem_dau"] - cfg["dem_cuoi"] + cfg["lech_toi_da"], 0.5)
    _, hi = SPEED_LIMITS.get(maker.provider or "minimax", (0.5, 2.0))
    max_speed = min(cfg["toc_do_toi_da"], hi)

    speed = cfg["toc_do"]
    voice_text = doc_theo_bang(seg["text"], cfg.get("cach_doc"))
    wav, dur = maker.make(voice_text, speed)
    for _ in range(2):
        if dur <= allow or speed >= max_speed - 1e-3:
            break
        speed = min(speed * dur / allow * 1.03, max_speed)
        wav, dur = maker.make(voice_text, speed)
    seg.update(audio=wav.name if wav else None, audio_dur=round(dur, 3), speed=round(speed, 3))
    if voice_text != seg["text"]:
        seg["loi_giong"] = voice_text
    return seg


def layout(segments, clip_durs, cfg, extend=True):
    """Xếp các đoạn lời nối tiếp nhau trên timeline.

    Mỗi đoạn bắt đầu ở đầu cảnh của nó (+dem_dau), hoặc muộn hơn nếu đoạn trước còn đang đọc.
    Nếu phải trễ quá lech_toi_da giây thì kéo dài hình của cảnh cuối đoạn trước cho đủ.
    Trả về số giây cần kéo dài thêm cho từng clip; ghi voice_start, lag vào từng đoạn.
    """
    extra = [0.0] * len(clip_durs)
    prev_end, prev_last = None, None
    for seg in segments:
        s, e = seg["clips"]
        ideal = sum(clip_durs[:s - 1]) + sum(extra[:s - 1]) + cfg["dem_dau"]
        if prev_end is not None:
            need = prev_end + cfg["khoang_nghi"] - (ideal + cfg["lech_toi_da"])
            if need > 0 and extend:
                extra[prev_last] += need
                ideal += need
            start = max(ideal, prev_end + cfg["khoang_nghi"])
        else:
            start = ideal
        seg["voice_start"] = round(start, 3)
        seg["lag"] = round(start - ideal, 3)
        prev_end, prev_last = start + seg["audio_dur"], e - 1
    # Đoạn cuối phải đọc xong trước khi hết video
    tail = prev_end + cfg["dem_cuoi"] - (sum(clip_durs) + sum(extra))
    if tail > 0 and extend:
        extra[prev_last] += tail
    return extra


def stretch_freeze(duration, extra, max_slow):
    """Kéo dài clip thêm `extra` giây: làm chậm trước (tối đa max_slow), thiếu nữa thì dừng khung cuối."""
    if extra <= 0:
        return 1.0, 0.0
    stretch = min((duration + extra) / duration, max_slow)
    return round(stretch, 4), round(duration + extra - duration * stretch, 3)


# ---------------------------------------------------------------- dựng video

def normalize_clip(src, info, dst, size, fps, stretch, freeze, orig_vol):
    w, h = size
    vf = (f"setpts={stretch:.5f}*PTS,scale={w}:{h}:force_original_aspect_ratio=decrease,"
          f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1,fps={fps}")
    if freeze > 0:
        vf += f",tpad=stop_mode=clone:stop_duration={freeze:.3f}"
    target = info["duration"] * stretch + freeze
    cmd = ["ffmpeg", "-y", "-i", str(src)]
    if info["has_audio"] and orig_vol > 0:
        cmd += ["-filter:a", f"atempo={1 / stretch:.5f},volume={orig_vol},apad", "-map", "0:a:0"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "1:a"]
    cmd += ["-filter:v", vf, "-map", "0:v:0", "-t", f"{target:.3f}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(fps),
            "-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "192k", str(dst)]
    run(cmd)


def render_final(out_dir, segments, total, music, cfg, lang, size, burn_subs):
    """Gộp video đã nối + các đoạn giọng (đặt đúng mốc) + nhạc nền (tự giảm khi có lời) + phụ đề."""
    inputs = ["-i", "video_ghep.mp4"]
    for seg in segments:
        inputs += ["-i", f"voice/{seg['audio']}"]
    if music:
        inputs += ["-stream_loop", "-1", "-i", str(music)]

    parts = []
    for i, seg in enumerate(segments, start=1):
        ms = int(seg["voice_start"] * 1000)
        parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}:all=1[v{i}]")
    labels = "".join(f"[v{i}]" for i in range(1, len(segments) + 1))
    parts.append(f"{labels}amix=inputs={len(segments)}:normalize=0[voices]")
    mix = ["[base]", "[voices]"]
    if music:
        m = len(segments) + 1
        parts[-1] = parts[-1].replace("[voices]", "[voices_all]")
        parts.append("[voices_all]asplit[voices][duck]")
        parts.append(f"[{m}:a]aresample=48000,aformat=channel_layouts=stereo,volume={cfg['am_luong_nhac']}[mus]")
        parts.append("[mus][duck]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=500[musd]")
        mix.append("[musd]")
    # Tiếng gốc của video ghép thường ngắn hơn hình (mỗi clip hụt vài chục ms, video dài hụt cả chục giây).
    # amix lấy độ dài theo luồng này, nên phải kéo dài bằng khoảng lặng tới hết video, không thì câu cuối và nhạc bị cắt.
    # Khi tắt tiếng gốc (am_luong_goc = 0) thì dùng nền im lặng tự tạo đúng độ dài video: luồng tiếng của video ghép
    # có mốc thời gian lệch nên apad vẫn bị cắt sớm (video リッカー: mất 8 giây cuối).
    if not cfg.get("am_luong_goc"):
        parts.append(f"anullsrc=r=48000:cl=stereo:d={total:.3f}[base]")
    else:
        parts.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,apad=whole_dur={total:.3f}[base]")
    parts.append(f"{''.join(mix)}amix=inputs={len(mix)}:normalize=0:duration=first,"
                 "loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    w, h = size
    if burn_subs:
        font = SUB_FONT.get(lang, "Arial")
        fs = cfg["co_chu_phu_de"] or (10 if h > w else 16)
        if cfg.get("phu_de_kieu") == "dai_den":
            # dải đen cao 1/6 khung (120 px ở 720p), chữ trắng không viền nằm giữa dải
            style = (f"FontName={font},FontSize={fs},Bold=0,PrimaryColour=&H00FFFFFF,"
                     "OutlineColour=&H00000000,BorderStyle=1,Outline=0,Shadow=0,MarginV=18")
            parts.append(f"[0:v]drawbox=x=0:y=ih-ih/6:w=iw:h=ih/6:color=black@0.82:t=fill,"
                         f"subtitles=filename=final.srt:force_style='{style}'[vout]")
        else:
            style = (f"FontName={font},FontSize={fs},Bold=1,PrimaryColour=&H00FFFFFF,"
                     "OutlineColour=&H00000000,BorderStyle=1,Outline=1.6,Shadow=0,MarginV=22")
            parts.append(f"[0:v]subtitles=filename=final.srt:force_style='{style}'[vout]")
        vmap = ["-map", "[vout]", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p"]
    else:
        vmap = ["-map", "0:v", "-c:v", "copy"]

    # Chuỗi lọc ghi ra tệp và nạp bằng "-/filter_complex": video dài (hàng trăm đoạn lời) làm dòng lệnh
    # vượt giới hạn 32.767 ký tự của Windows (WinError 206)
    (Path(out_dir) / "bo_loc_am_thanh.txt").write_text(";\n".join(parts), encoding="utf-8")
    run(["ffmpeg", "-y", *inputs, "-/filter_complex", "bo_loc_am_thanh.txt", *vmap,
         "-map", "[aout]", "-c:a", "aac", "-b:a", "192k", "-t", f"{total:.3f}",
         "-movflags", "+faststart", "final.mp4"], cwd=out_dir)


# ---------------------------------------------------------------- lệnh chính

def find_clip_dir(project, name):
    """Thư mục clip ghi trong cấu hình, không có thì lấy thư mục con đầu tiên chứa video."""
    def has_video(d):
        return any(p.suffix.lower() in VIDEO_EXT for p in d.iterdir())
    if name and (project / name).is_dir():
        return project / name
    subdirs = sorted((d for d in project.iterdir() if d.is_dir() and d.name != "output"),
                     key=lambda d: natural_key(d.name))
    return next((d for d in subdirs if has_video(d)), project if has_video(project) else None)


def find_file(project, *names):
    return next((project / n for n in names if n and (project / n).is_file()), None)


def prepare(clip_dir, prompt_file, cfg, user_keys=(), script_file=None):
    """Đọc clip + prompt, phân tích ngôn ngữ và giọng. Dùng chung cho dòng lệnh và cửa sổ ứng dụng."""
    clip_dir = Path(clip_dir)
    if not clip_dir.is_dir():
        raise ValueError(f"Không thấy thư mục video: {clip_dir}")
    clip_paths = sorted((p for p in clip_dir.iterdir() if p.suffix.lower() in VIDEO_EXT),
                        key=lambda p: natural_key(p.name))
    if not clip_paths:
        raise ValueError(f"Thư mục {clip_dir} không có video nào (.mp4, .mov, .mkv, .webm)")
    print(f"[1/6] Đọc {len(clip_paths)} clip trong {clip_dir.name}")
    infos = [probe(p) for p in clip_paths]
    clip_durs = [i["duration"] for i in infos]

    # Prompt: mô tả giọng + (nếu có) toàn bộ lời đọc. Ngôn ngữ của lời đọc quyết định giọng và phụ đề.
    prompt_file = Path(prompt_file) if prompt_file else None
    prompt_text = prompt_file.read_text(encoding="utf-8-sig") if prompt_file else ""
    voice_prompt, script = parse_prompt(prompt_text)
    script_source = prompt_file.name if script else None
    if script_file:
        script, script_source = Path(script_file).read_text(encoding="utf-8-sig"), Path(script_file).name
    if not script:
        raise ValueError("Không thấy lời đọc: thêm mục toàn văn/kịch bản vào file prompt")
    segments = parse_script(script, len(clip_paths))
    wanted = analyze_voice_prompt(voice_prompt)
    if wanted["speed"] and "toc_do" not in user_keys:
        cfg["toc_do"] = wanted["speed"]
    covered = {c for seg in segments for c in range(seg["clips"][0], seg["clips"][1] + 1)}
    print(f"[2/6] Phân tích prompt {prompt_file.name if prompt_file else '(không có)'}")
    print(f"  Lời đọc: {len(segments)} đoạn lấy từ {script_source}, "
          f"{len(clip_paths) - len(covered)} clip không có lời")

    # Ngôn ngữ: cấu hình > ngôn ngữ thật của lời đọc. Prompt có ghi ngôn ngữ thì đối chiếu để cảnh báo.
    meta = prompt_text
    for para in script.split("\n\n"):
        meta = meta.replace(para.strip(), "")
    asked, written = requested_language(meta), detect_language(script)
    if asked == "yue" and written == "zh":
        written = "yue"  # chữ Hán đọc bằng giọng Quảng Đông
    lang = cfg["ngon_ngu"] or written
    name = LANG_NAMES.get(lang, lang)
    note = "theo cấu hình" if cfg["ngon_ngu"] else "nhận từ lời đọc"
    if asked == lang:
        note += ", khớp với ngôn ngữ prompt yêu cầu"
    print(f"  Ngôn ngữ: {name} ({note}) -> giọng đọc và phụ đề {name}")
    if asked and asked != lang:
        print(f"  ! Prompt yêu cầu {LANG_NAMES.get(asked, asked)} nhưng lời đọc đang viết bằng "
              f"{LANG_NAMES.get(written, written)}. Tool đọc theo {name}; muốn ra "
              f"{LANG_NAMES.get(asked, asked)} thì cần dịch lời đọc sang tiếng đó trước.")
    print(f"  Giọng mong muốn: {wanted['gender'] or 'không rõ giới tính'}, "
          f"{', '.join(wanted['traits']) or 'không có đặc điểm'}, tốc độ x{cfg['toc_do']}")
    est = sum(len(sg["text"]) for sg in segments) / CHARS_PER_SEC.get(lang, DEFAULT_CPS) / cfg["toc_do"]
    return {
        "clip_paths": clip_paths, "infos": infos, "clip_durs": clip_durs, "segments": segments,
        "voice_prompt": voice_prompt, "lang": lang, "wanted": wanted,
        "long_script": est > 0.9 * sum(clip_durs), "est_voice": est,
    }


def run_pipeline(clip_dir, prompt_file, out_dir, cfg, mode="that", user_keys=(), script_file=None, music=None):
    """Toàn bộ quy trình. mode: "that" (gọi Genmax), "gia_lap" (tiếng bíp), "kiem_tra" (chỉ ước lượng).
    Trả về đường dẫn final.mp4 (hoặc None khi chỉ kiểm tra)."""
    ctx = prepare(clip_dir, prompt_file, cfg, user_keys, script_file)
    clip_paths, infos, clip_durs = ctx["clip_paths"], ctx["infos"], ctx["clip_durs"]
    segments, lang = ctx["segments"], ctx["lang"]
    out_dir = Path(out_dir)

    if mode == "kiem_tra":
        if cfg["api_key"] or os.environ.get("GENMAX_API_KEY"):
            print("[3/6] Chọn giọng (chỉ xem danh sách, không tốn credit)")
            _, _, voice_id, voice_desc = pick_voice(Genmax(cfg["api_key"]), cfg, lang, ctx["voice_prompt"],
                                                    ctx["long_script"])
            print(f"  -> {voice_desc} ({voice_id})")
        print("  Ước lượng thời lượng lời theo số ký tự (không gọi Genmax)")
        maker = VoiceMaker(out_dir, lang, "uoc_luong")
        voice_desc = "ước lượng"
    elif mode == "gia_lap":
        print("[3/6] Chế độ giả lập: dùng tiếng bíp thay giọng thật")
        maker = VoiceMaker(out_dir, lang, "gia_lap")
        voice_desc = "giả lập"
    else:
        client = Genmax(cfg["api_key"])
        print("[3/6] Chọn giọng")
        provider, model, voice_id, voice_desc = pick_voice(client, cfg, lang, ctx["voice_prompt"],
                                                           ctx["long_script"])
        print(f"  -> {voice_desc} ({provider}/{voice_id})")
        maker = VoiceMaker(out_dir, lang, "that", client, provider, model, voice_id)

    print(f"[4/6] Tạo giọng & xếp lời lên timeline ({len(segments)} đoạn)")
    with ThreadPoolExecutor(cfg["song_song"]) as pool:
        segments = list(pool.map(lambda sg: synth_segment(sg, clip_durs, cfg, maker), segments))
    extra = layout(segments, clip_durs, cfg)
    adjust = [stretch_freeze(d, x, cfg["keo_cham_hinh_toi_da"]) for d, x in zip(clip_durs, extra)]

    faster = [sg for sg in segments if sg["speed"] != cfg["toc_do"]]
    voice_total = sum(sg["audio_dur"] for sg in segments)
    print(f"  Tổng lời {voice_total:.0f}s / hình {sum(clip_durs):.0f}s; "
          f"{len(faster)} đoạn phải đọc nhanh hơn; trễ lớn nhất {max(sg['lag'] for sg in segments):.1f}s")
    for sg in faster:
        print(f"    đọc nhanh x{sg['speed']}: clip {sg['clips'][0]}-{sg['clips'][1]}")
    for k, x in enumerate(extra):
        if x > 0:
            print(f"    kéo dài clip {clip_paths[k].name}: +{x:.1f}s "
                  f"(chậm x{adjust[k][0]}, dừng hình {adjust[k][1]}s)")
    print(f"  Video dự kiến dài {sum(clip_durs) + sum(extra):.1f}s, kéo dài hình tổng {sum(extra):.1f}s")
    if mode == "kiem_tra":
        return None

    print("[5/6] Chuẩn hóa & nối clip")
    (out_dir / "tmp").mkdir(parents=True, exist_ok=True)
    first = infos[0]
    size = cfg["do_phan_giai"] or [first["width"] // 2 * 2, first["height"] // 2 * 2]
    norm = [out_dir / "tmp" / f"clip_{i + 1:03d}.mp4" for i in range(len(clip_paths))]
    with ThreadPoolExecutor(3) as pool:
        list(pool.map(lambda i: normalize_clip(clip_paths[i], infos[i], norm[i], size, cfg["fps"],
                                               adjust[i][0], adjust[i][1], cfg["am_luong_goc"]),
                      range(len(clip_paths))))
    # Đo lại thời lượng thật sau chuẩn hóa rồi xếp lại mốc lời, để không bị trôi dần qua nhiều clip
    real = [probe(p)["duration"] for p in norm]
    starts = [sum(real[:i]) for i in range(len(real))]
    total = sum(real)
    layout(segments, real, cfg, extend=False)
    (out_dir / "tmp" / "list.txt").write_text(
        "".join(f"file 'clip_{i + 1:03d}.mp4'\n" for i in range(len(norm))), encoding="utf-8")
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "tmp/list.txt", "-c", "copy", "video_ghep.mp4"],
        cwd=out_dir)

    # Phụ đề: chia câu thành dòng ngắn, thời gian mỗi dòng tỉ lệ theo số ký tự
    w, h = size
    max_chars = (12 if h > w else 20) if lang in CJK else (28 if h > w else 45)
    srt, n = [], 0
    for seg in segments:
        chunks = split_caption(seg["text"], max_chars, lang)
        weight = sum(len(c) for c in chunks)
        t = seg["voice_start"]
        for c in chunks:
            d = seg["audio_dur"] * len(c) / weight
            n += 1
            srt.append(f"{n}\n{srt_time(t)} --> {srt_time(t + d)}\n{c}\n")
            t += d
    (out_dir / "final.srt").write_text("\n".join(srt), encoding="utf-8")

    print("[6/6] Trộn âm thanh & xuất video")
    render_final(out_dir, segments, total, Path(music) if music else None, cfg, lang, size, cfg["phu_de"])

    timeline = {
        "ngon_ngu": lang, "giong": voice_desc, "do_phan_giai": size, "tong_thoi_luong": round(total, 3),
        "clips": [{"file": p.name, "goc": round(i["duration"], 3), "cham_hinh": adjust[k][0],
                   "dung_hinh": adjust[k][1], "bat_dau": round(starts[k], 3), "thoi_luong": round(real[k], 3)}
                  for k, (p, i) in enumerate(zip(clip_paths, infos))],
        "doan_loi": segments,
    }
    (out_dir / "timeline.json").write_text(json.dumps(timeline, ensure_ascii=False, indent=2), encoding="utf-8")
    if not cfg["giu_file_tam"]:
        shutil.rmtree(out_dir / "tmp", ignore_errors=True)
        (out_dir / "video_ghep.mp4").unlink(missing_ok=True)
    print(f"Xong: {out_dir / 'final.mp4'}  ({total:.1f}s)")
    return out_dir / "final.mp4"


def cmd_run(args):
    project = Path(args.du_an).resolve()
    user_cfg = {}
    if (project / "cau_hinh.json").exists():
        user_cfg = json.loads((project / "cau_hinh.json").read_text(encoding="utf-8-sig"))
    cfg = {**DEFAULT_CONFIG, **user_cfg}

    clip_dir = find_clip_dir(project, cfg["thu_muc_clip"])
    if not clip_dir:
        raise ValueError(f"Không thấy thư mục video nào trong {project}")
    prompt_file = find_file(project, args.prompt or cfg["file_prompt"], "prompt.md", "prompt.txt")
    if args.prompt and (not prompt_file or prompt_file.name != Path(args.prompt).name):
        raise ValueError(f"Không thấy file prompt {args.prompt} trong {project}")
    script_file = find_file(project, cfg["file_kich_ban"]) if cfg["file_kich_ban"] else None
    if not script_file and (not prompt_file or not parse_prompt(prompt_file.read_text(encoding="utf-8-sig"))[1]):
        script_file = find_file(project, "kich_ban.txt")
    music = find_file(project, "nhac_nen.mp3", "nhac_nen.wav", "nhac_nen.m4a")
    mode = "kiem_tra" if args.chi_kiem_tra else "gia_lap" if args.gia_lap else "that"
    run_pipeline(clip_dir, prompt_file, project / (args.output or "output"), cfg, mode,
                 user_keys=user_cfg.keys(), script_file=script_file, music=music)


def cmd_voices(args):
    client = Genmax(args.api_key)
    voices = client.voices(args.provider, lang=args.ngon_ngu, gender=prompt_gender(args.prompt or ""))
    for score, why, v in rank_voices(voices, args.prompt or "")[:args.so_luong]:
        print(f"[{score:>3}] {v['voice_id']:<28} {v['name'][:30]:<30} {v['gender']:<7} "
              f"{v['description'][:70]}")
        if v.get("preview"):
            print(f"      nghe thử: {v['preview']}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="AI Film Studio: ghép giọng Genmax vào clip video")
    sub = ap.add_subparsers(dest="lenh", required=True)

    r = sub.add_parser("chay", help="Dựng video từ thư mục dự án")
    r.add_argument("du_an")
    r.add_argument("--gia-lap", action="store_true", help="Dùng giọng giả, không gọi Genmax")
    r.add_argument("--chi-kiem-tra", action="store_true", help="Chỉ ước lượng thời lượng, không dựng")
    r.add_argument("--prompt", help="File prompt trong thư mục dự án (mặc định prompt.md / prompt.txt)")
    r.add_argument("--output", help="Thư mục kết quả trong thư mục dự án (mặc định output)")
    r.set_defaults(func=cmd_run)

    v = sub.add_parser("giong", help="Liệt kê giọng Genmax theo ngôn ngữ")
    v.add_argument("--ngon-ngu", default="vi")
    v.add_argument("--provider", default="minimax")
    v.add_argument("--prompt", default="")
    v.add_argument("--so-luong", type=int, default=15)
    v.add_argument("--api-key")
    v.set_defaults(func=cmd_voices)

    args = ap.parse_args()
    try:
        args.func(args)
    except (GenmaxError, ValueError, RuntimeError) as e:
        sys.exit(f"LỖI: {e}")


if __name__ == "__main__":
    main()
