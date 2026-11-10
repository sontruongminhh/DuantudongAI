"""Client gọi API Genmax (tài liệu: https://genmax.io/docs).

Luồng tạo giọng của Genmax là bất đồng bộ:
  POST /v1/text-to-speech/{voice_id}  -> trả về task id (status: pending)
  GET  /v1/history/{id}               -> hỏi lại tới khi status = completed, lấy result.audio_url
"""
import os
import time
from urllib.parse import urlparse

import requests

BASE_URL = "https://api.genmax.io"

# Mã ISO -> tên ngôn ngữ MiniMax dùng để lọc giọng (MiniMax lọc theo tên đầy đủ).
MINIMAX_LANG = {
    "vi": "Vietnamese", "en": "English", "zh": "Chinese (Mandarin)", "yue": "Chinese (Cantonese)",
    "ja": "Japanese", "ko": "Korean", "th": "Thai", "id": "Indonesian", "ms": "Malay",
    "fr": "French", "de": "German", "es": "Spanish", "pt": "Portuguese", "it": "Italian",
    "ru": "Russian", "ar": "Arabic", "hi": "Hindi", "tr": "Turkish", "nl": "Dutch",
    "pl": "Polish", "uk": "Ukrainian", "fil": "Filipino", "tl": "Filipino",
}

# Giới hạn tốc độ đọc theo tài liệu Genmax.
SPEED_LIMITS = {"elevenlabs": (0.7, 1.2), "minimax": (0.5, 2.0), "capcut": (0.5, 2.0)}


class GenmaxError(Exception):
    pass


class Genmax:
    def __init__(self, api_key=None, timeout=60):
        self.api_key = api_key or os.environ.get("GENMAX_API_KEY")
        if not self.api_key:
            raise GenmaxError("Thiếu API key: đặt biến môi trường GENMAX_API_KEY "
                              "hoặc điền \"api_key\" trong cau_hinh.json")
        self.session = requests.Session()
        self.session.headers["xi-api-key"] = self.api_key
        self.timeout = timeout

    def _request(self, method, path, **kwargs):
        for attempt in range(5):
            try:
                r = self.session.request(method, BASE_URL + path, timeout=self.timeout, **kwargs)
            except (requests.Timeout, requests.ConnectionError):
                # Chỉ thử lại lệnh đọc. POST tạo giọng thử lại có thể tạo trùng task (tốn credit hai lần)
                if method != "GET" or attempt == 4:
                    raise
                time.sleep(3 * 2 ** attempt)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(2 * 2 ** attempt)  # bị giới hạn tốc độ / lỗi server: chờ rồi thử lại
                continue
            if r.status_code >= 400:
                raise GenmaxError(f"{method} {path} -> HTTP {r.status_code}: {r.text[:300]}")
            return r.json() if r.content else None
        raise GenmaxError(f"{method} {path}: thử lại 5 lần vẫn lỗi (HTTP {r.status_code})")

    # ---------- Giọng đọc ----------

    def voices(self, provider, lang=None, gender=None, search=None, max_pages=10):
        """Trả danh sách giọng đã chuẩn hóa: voice_id, name, gender, age, language, description."""
        if provider == "minimax":
            out, page = [], 1
            params = {"page_size": 100}
            if lang:
                params["language"] = MINIMAX_LANG.get(lang, lang)
            if gender:
                params["gender"] = gender.capitalize()
            if search:
                params["search"] = search
            while page <= max_pages:
                data = self._request("GET", "/v1/minimax/system-voices", params={**params, "page": page})
                for v in data.get("voice_list", []):
                    tags = v.get("tag_list") or []
                    out.append({
                        "voice_id": v["voice_id"],
                        "name": v.get("voice_name", ""),
                        "gender": next((t.lower() for t in tags if t.lower() in ("male", "female")), ""),
                        "age": " ".join(t for t in tags if "young" in t.lower() or "aged" in t.lower()
                                        or "old" in t.lower() or "senior" in t.lower()),
                        "language": params.get("language", ""),
                        "description": " ".join([v.get("description") or "", *tags]),
                        "preview": v.get("sample_audio"),
                    })
                if not data.get("has_more"):
                    break
                page += 1
            return out

        if provider == "elevenlabs":
            params = {"page_size": 100}
            if search:
                params["search"] = search
            data = self._request("GET", "/v1/default-voices", params=params)
            out = []
            for v in data.get("voices", []):
                verified = [x.get("language_id") for x in v.get("verified_languages") or []]
                if gender and (v.get("gender") or "").lower() != gender.lower():
                    continue
                out.append({
                    "voice_id": v["voice_id"],
                    "name": v.get("name", ""),
                    "gender": (v.get("gender") or "").lower(),
                    "age": v.get("age") or "",
                    "language": ",".join(verified) or v.get("language", ""),
                    "description": " ".join(filter(None, [v.get("description"), v.get("use_case"),
                                                          v.get("descriptive"), v.get("accent")])),
                    "preview": v.get("preview_url"),
                    # Giọng có xác minh đúng ngôn ngữ thì phát âm chuẩn hơn
                    "verified_for_lang": bool(lang and lang in verified),
                })
            return out

        raise GenmaxError(f"Chưa hỗ trợ tự chọn giọng cho provider '{provider}'. "
                          "Hãy điền voice_id trong cau_hinh.json.")

    # ---------- Tạo giọng ----------

    def tts(self, text, voice_id, lang, provider="minimax", model_id=None, speed=1.0, extra_settings=None):
        lo, hi = SPEED_LIMITS.get(provider, (0.5, 2.0))
        body = {
            "text": text,
            "provider": provider,
            "language_code": lang,  # Genmax tự đổi mã ISO sang tên ngôn ngữ cho MiniMax
            "voice_settings": {"speed": round(min(max(speed, lo), hi), 3), **(extra_settings or {})},
        }
        if model_id:
            body["model_id"] = model_id
        task = self._request("POST", f"/v1/text-to-speech/{voice_id}", json=body)
        return self.wait(task["id"])

    def wait(self, task_id, poll=2.0, timeout=900):
        start = time.time()
        while True:
            h = self._request("GET", f"/v1/history/{task_id}")
            status = h.get("status")
            if status == "completed":
                if not (h.get("result") or {}).get("audio_url"):
                    raise GenmaxError(f"Task {task_id} xong nhưng không có audio_url")
                return h
            if status == "failed":
                raise GenmaxError(f"Task {task_id} lỗi: {h.get('error')}")
            if time.time() - start > timeout:
                raise GenmaxError(f"Task {task_id} quá {timeout}s chưa xong (status={status})")
            time.sleep(poll)

    def download(self, url, path):
        # Chỉ gửi API key khi tải từ chính máy chủ Genmax
        host = urlparse(url).hostname or ""
        getter = self.session.get if host.endswith("genmax.io") else requests.get
        for attempt in range(4):   # tải tệp giọng hay bị quá thời gian (video リッカー: đứt ở đoạn 93/235)
            try:
                r = getter(url, timeout=180)
                r.raise_for_status()
                break
            except (requests.Timeout, requests.ConnectionError):
                if attempt == 3:
                    raise
                time.sleep(5 * 2 ** attempt)
        with open(path, "wb") as f:
            f.write(r.content)
