"""Tải video lên YouTube sau Cổng 3. Video luôn được tải lên ở chế độ riêng tư."""
import json
import os
import re
import shutil
import time
import webbrowser
from pathlib import Path
from wsgiref.simple_server import WSGIRequestHandler, make_server
from wsgiref.util import request_uri

from .core import ROOT, StudioError, load_profile, read_json
from .duyet import THUMBNAIL, verify_gate
from .qc import require_qc_passed
from .seo import check_metadata

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube.force-ssl"]
KEYRING_SERVICE = "DuanTuDongAI-YouTube"
CHUNK_BYTES = 16 * 1024 * 1024
RETRIES = 5
CONSENT_TIMEOUT = 600
HANDLER_TIMEOUT = 5


def client_file(kenh=None):
    """Tệp OAuth client. Hồ sơ kênh có youtube.oauth_client_file thì dùng tệp riêng của kênh đó (mỗi kênh một dự án
    Google Cloud, hạn mức riêng), không thì dùng YOUTUBE_OAUTH_CLIENT_FILE hoặc tệp chung mặc định."""
    default = Path(os.environ.get("APPDATA", Path.home())) / "DuanTuDongAI" / "client_secret.json"
    own = None
    if kenh:
        profile_path = ROOT / "channels" / kenh / "profile.yaml"
        if profile_path.is_file():
            own = (load_profile(profile_path).get("youtube") or {}).get("oauth_client_file")
    path = Path(os.path.expandvars(own)) if own else Path(os.environ.get("YOUTUBE_OAUTH_CLIENT_FILE") or default)
    if not path.is_file():
        raise StudioError(f"Không thấy tệp OAuth client tại {path}. Xem hướng dẫn trong README")
    return path


class _QuietHandler(WSGIRequestHandler):
    timeout = HANDLER_TIMEOUT  # kết nối rỗng của trình duyệt không được giữ máy chủ quá lâu

    def log_message(self, *args):
        pass


def _redirect_server():
    """Máy chủ cục bộ nhận mã từ Google. Trả về (máy chủ, kho chứa địa chỉ nhận được)."""
    received = {}

    def app(environ, start_response):
        # Bỏ qua favicon và các yêu cầu không mang kết quả từ Google
        if environ.get("PATH_INFO") == "/" and re.search(r"(^|&)(code|error)=", environ.get("QUERY_STRING", "")):
            received["uri"] = request_uri(environ)
            start_response("200 OK", [("Content-Type", "text/plain; charset=utf-8")])
            return ["Đã nhận phản hồi từ Google. Bạn có thể đóng tab này.".encode("utf-8")]
        start_response("404 Not Found", [("Content-Type", "text/plain")])
        return [b""]

    return make_server("localhost", 0, app, handler_class=_QuietHandler), received


def _wait_for_redirect(server, received, seconds=CONSENT_TIMEOUT):
    """Bỏ qua kết nối rỗng hoặc yêu cầu lạ, đợi tới khi Google chuyển hướng về."""
    server.timeout = 5
    deadline = time.monotonic() + seconds
    while "uri" not in received:
        if time.monotonic() > deadline:
            raise StudioError(f"Quá {seconds // 60} phút chưa nhận được phản hồi từ Google. Hãy chạy lại lệnh")
        server.handle_request()
    return received["uri"]


def connect(kenh):
    """Mở trình duyệt để bạn tự đăng nhập, rồi lưu refresh token vào Windows Credential Manager."""
    import keyring
    from google_auth_oauthlib.flow import InstalledAppFlow
    from oauthlib.oauth2 import OAuth2Error
    flow = InstalledAppFlow.from_client_secrets_file(str(client_file(kenh)), SCOPES)
    server, received = _redirect_server()
    with server:
        flow.redirect_uri = f"http://localhost:{server.server_port}/"
        url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        print(f"Mở liên kết này trong Chrome của đúng hồ sơ kênh nếu trình duyệt không tự mở:\n{url}", flush=True)
        webbrowser.open(url)
        uri = _wait_for_redirect(server, received)
    try:
        flow.fetch_token(authorization_response=uri.replace("http://", "https://", 1))
    except OAuth2Error as e:
        raise StudioError(f"Google từ chối cấp quyền: {e.error}") from e
    creds = flow.credentials
    if not creds.refresh_token:
        raise StudioError("Google không trả refresh token. Hãy thu hồi quyền của ứng dụng rồi kết nối lại")
    keyring.set_password(KEYRING_SERVICE, kenh, creds.refresh_token)
    return channel_info(build_service(kenh))


def build_service(kenh):
    import keyring
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    token = keyring.get_password(KEYRING_SERVICE, kenh)
    if not token:
        raise StudioError(f"Kênh {kenh} chưa kết nối YouTube. Chạy: python -m studio ket-noi-youtube {kenh}")
    info = json.loads(client_file(kenh).read_text(encoding="utf-8"))
    info = info.get("installed") or info.get("web") or {}
    creds = Credentials(None, refresh_token=token, token_uri=info["token_uri"], client_id=info["client_id"],
                        client_secret=info["client_secret"], scopes=SCOPES)
    return build("youtube", "v3", credentials=creds, cache_discovery=False)


def channel_info(service):
    items = service.channels().list(part="id,snippet", mine=True).execute().get("items", [])
    return [{"id": c["id"], "ten": c["snippet"]["title"]} for c in items]


def build_body(meta):
    """Luôn đặt private. Có lịch thì YouTube tự công khai đúng giờ đã được duyệt."""
    status = {"privacyStatus": "private", "selfDeclaredMadeForKids": meta["tre_em"],
              "containsSyntheticMedia": meta["noi_dung_tong_hop"]}
    if meta.get("lich_dang"):
        status["publishAt"] = meta["lich_dang"]
    return {
        "snippet": {"title": meta["tieu_de"], "description": meta["mo_ta"], "tags": meta.get("the") or [],
                    "categoryId": str(meta["category_id"]), "defaultLanguage": meta["ngon_ngu"],
                    "defaultAudioLanguage": meta["ngon_ngu_am_thanh"]},
        "status": status,
    }


def _named_copy(run, meta):
    """YouTube Studio hiện tên tệp gốc, nên tải lên bản có tên đã duyệt."""
    final = run.dir / "render" / "final.mp4"
    dst = run.dir / "publish" / meta["ten_tep"]
    dst.unlink(missing_ok=True)
    try:
        os.link(final, dst)
    except OSError:
        shutil.copy2(final, dst)
    return dst


def upload(run, service=None):
    """Kiểm tra lại mọi điều kiện ngay trước khi tải lên. Trả về video_id."""
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    verify_gate(run, "G3")
    verify_gate(run, "G2")
    require_qc_passed(run)
    errors = check_metadata(run)
    if errors:
        raise StudioError("Thông tin đăng tải còn lỗi:\n  " + "\n  ".join(errors))
    state = run.state
    if state.get("video_id"):
        raise StudioError(f"Lần chạy này đã tải lên video {state['video_id']}")
    channel_id = run.profile["youtube"].get("channel_id")
    if not channel_id:
        raise StudioError("Hồ sơ chưa có youtube.channel_id")

    service = service or build_service(state["kenh"])
    owned = [c["id"] for c in channel_info(service)]
    if channel_id not in owned:
        raise StudioError(f"Tài khoản đã kết nối không sở hữu kênh {channel_id}. Không tải lên")

    meta = read_json(run.dir / "publish" / "metadata.json")
    media = MediaFileUpload(str(_named_copy(run, meta)), chunksize=CHUNK_BYTES, resumable=True, mimetype="video/mp4")
    request = service.videos().insert(part="snippet,status", body=build_body(meta), media_body=media)
    response = None
    try:
        while response is None:
            progress, response = request.next_chunk(num_retries=RETRIES)
            if progress:
                print(f"  Đã tải {progress.progress():.0%}")
    except HttpError as e:
        run.log("Tải lên YouTube", "loi", chi_tiet=str(e)[:500])
        raise StudioError(f"Tải lên lỗi: {e}") from e
    video_id = response["id"]
    run.update(video_id=video_id)
    run.log("Tải lên YouTube", "ok", chi_tiet=f"video_id={video_id}")

    _finish(run, service, meta, video_id)
    return video_id


def update_metadata(run, service=None):
    """Cập nhật tiêu đề, mô tả và thẻ của video đã tải lên theo metadata.json. Không đổi quyền riêng tư."""
    errors = check_metadata(run)
    if errors:
        raise StudioError("Thông tin đăng tải còn lỗi:\n  " + "\n  ".join(errors))
    state = run.state
    video_id = state.get("video_id")
    if not video_id:
        raise StudioError("Lần chạy này chưa tải video lên")
    service = service or build_service(state["kenh"])
    meta = read_json(run.dir / "publish" / "metadata.json")
    service.videos().update(part="snippet", body={"id": video_id, "snippet": build_body(meta)["snippet"]}).execute()
    run.log("Cập nhật SEO", "ok", chi_tiet=f"video_id={video_id}")
    return video_id


def _finish(run, service, meta, video_id):
    """Các bước sau tải lên chạy độc lập: một bước lỗi không làm mất video đã tải."""
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    def step(name, call):
        try:
            call()
            run.log(name, "ok")
        except (HttpError, OSError, StudioError) as e:
            run.log(name, "loi", chi_tiet=str(e)[:500])
            print(f"  ! {name} lỗi: {e}")

    def verify():
        items = service.videos().list(part="status", id=video_id).execute().get("items", [])
        privacy = items[0]["status"]["privacyStatus"] if items else None
        if privacy != "private":
            raise StudioError(f"Video đang ở trạng thái {privacy}, cần kiểm tra ngay trong YouTube Studio")
        run.update(youtube_status=items[0]["status"])

    step("Xác nhận trạng thái riêng tư", verify)
    thumb = run.dir / THUMBNAIL
    if thumb.is_file():
        step("Đặt thumbnail", lambda: service.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(str(thumb), mimetype="image/jpeg")).execute())
    if meta.get("tai_phu_de"):
        step("Tải phụ đề", lambda: service.captions().insert(
            part="snippet", body={"snippet": {"videoId": video_id, "language": meta["ngon_ngu"], "name": ""}},
            media_body=MediaFileUpload(str(run.dir / "render" / "final.srt"),
                                       mimetype="application/octet-stream")).execute())
    if meta.get("danh_sach_phat"):
        step("Thêm vào danh sách phát", lambda: service.playlistItems().insert(
            part="snippet", body={"snippet": {"playlistId": meta["danh_sach_phat"],
                                              "resourceId": {"kind": "youtube#video", "videoId": video_id}}}).execute())
