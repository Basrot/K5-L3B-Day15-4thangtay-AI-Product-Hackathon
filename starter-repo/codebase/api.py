"""HTTP interface for the shared CBC service; one process and one inference slot."""
import os
import threading
from datetime import date, datetime, timedelta, timezone
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr

from . import speech, tracing, tts, vision
from .agent import analyze_report
from .accounts import AccountError, AccountStore
from .api_auth import ensure_auth_ready, issue_access_token, issue_token, require_access
from .api_limits import BodyLimitMiddleware
from .catalog import ANALYTES, DEFAULT_UNITS, GROUPS
from .service import CBCService
from .tools import compare_cbc
from .references import study_references, SUPPORTED_ANALYTES

IMAGE_LIMIT = 10 * 1024 * 1024
WAV_LIMIT = 3 * 1024 * 1024
Text100 = Annotated[StrictStr, Field(max_length=100)]
LabValue = Text100 | StrictInt | StrictFloat | None
Revision = Annotated[StrictInt, Field(ge=0)]


class Payload(BaseModel):
    model_config = ConfigDict(extra="forbid", allow_inf_nan=False)


class LabRow(Payload):
    analyte: Annotated[StrictStr, Field(min_length=1, max_length=100)]
    value: LabValue = None
    unit: Text100 | None = None
    ref_low: LabValue = None
    ref_high: LabValue = None
    ref_unit: Text100 | None = None


class Report(Payload):
    reference_mode: Literal["study", "lab"] | None = None
    reference_version: Annotated[StrictStr, Field(min_length=1, max_length=64)] | None = None
    pregnancy_status: Literal["pregnant", "not_pregnant", "unknown"] | None = None
    adult_confirmed: StrictBool | None = None
    gestational_age: Annotated[StrictStr, Field(max_length=10)] | None = None
    specimen_date: Annotated[StrictStr, Field(pattern=r"^\d{4}-\d{2}-\d{2}$")] | None = None
    rows: Annotated[list[LabRow], Field(min_length=1, max_length=8)]


class Login(Payload):
    username: Annotated[StrictStr, Field(min_length=1, max_length=100)]
    password: Annotated[StrictStr, Field(min_length=1, max_length=1000)]


class Registration(Payload):
    email: Annotated[StrictStr, Field(min_length=3, max_length=254)]
    password: Annotated[StrictStr, Field(min_length=10, max_length=1000)]


class GoogleLogin(Payload):
    credential: Annotated[StrictStr, Field(min_length=20, max_length=10000)]


class RevisionBody(Payload):
    expected_revision: Revision


class ConfirmBody(RevisionBody):
    report: Report
    confirmed: StrictBool


class ChatBody(RevisionBody):
    question: Annotated[StrictStr, Field(min_length=1, max_length=1000)]
    request_id: Annotated[StrictStr, Field(min_length=1, max_length=128)]


class SpeechBody(Payload):
    text: Annotated[StrictStr, Field(min_length=1, max_length=3000)]


def _upload(file: UploadFile, limit: int) -> bytes:
    try:
        content = file.file.read(limit + 1)
        if len(content) > limit:
            raise HTTPException(413, "Tệp vượt giới hạn kích thước.")
        if not content:
            raise HTTPException(422, "Tệp không có dữ liệu.")
        return content
    finally:
        file.file.close()


def _validate_specimen_date(value):
    if value is None:
        return
    try:
        sample_date = date.fromisoformat(value)
    except ValueError:
        raise HTTPException(422, "Ngày lấy mẫu không hợp lệ.") from None
    vietnam_today = datetime.now(timezone(timedelta(hours=7))).date()
    if sample_date > vietnam_today:
        raise HTTPException(422, "Ngày lấy mẫu không thể nằm trong tương lai.")


@contextmanager
def _operation(app: FastAPI):
    if not app.state.model_lock.acquire(blocking=False):
        raise HTTPException(429, "Máy chủ đang xử lý yêu cầu khác; hãy thử lại.", headers={"Retry-After": "1"})
    usage = {}
    tracing.begin("http")
    try:
        yield usage
    finally:
        summary, _events = tracing.end()
        usage.update(summary)
        app.state.model_lock.release()


def create_app(db_path=None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application):
        service = CBCService(db_path)
        accounts = AccountStore(service.path)
        admin = accounts.ensure_admin(os.environ.get("APP_USERNAME", "demo"), os.environ.get("APP_PASSWORD", ""))
        if admin:
            service.assign_unowned_sessions(admin["id"])
        application.state.service = service
        application.state.accounts = accounts
        yield

    application = FastAPI(title="CBC Assistant API", version="1.0.0", lifespan=lifespan)
    application.state.model_lock = threading.Lock()
    application.add_middleware(BodyLimitMiddleware, max_bytes=11 * 1024 * 1024)
    origins = [origin.strip() for origin in os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",") if origin.strip()]
    for origin in origins:
        parsed = urlsplit(origin)
        if ("*" in origin or parsed.scheme not in ("http", "https") or not parsed.hostname
                or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password):
            raise ValueError("CORS_ORIGINS chỉ nhận origin http/https chính xác, không wildcard hoặc đường dẫn.")
    application.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False,
                               allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                               allow_headers=["Authorization", "Content-Type"], expose_headers=["Retry-After"])

    @application.exception_handler(KeyError)
    async def missing(_request, _exception):
        return JSONResponse(status_code=404, content={"detail": "Không tìm thấy phiên CBC."})

    @application.exception_handler(ValueError)
    async def invalid(_request, exception):
        message = str(exception)
        stale = any(term in message for term in ("đã thay đổi", "request_id đã được dùng"))
        return JSONResponse(status_code=409 if stale else 422, content={"detail": message})

    @application.exception_handler(RuntimeError)
    async def upstream(_request, _exception):
        return JSONResponse(status_code=502, content={"detail": "Dịch vụ AI hoặc âm thanh chưa phản hồi. Hãy thử lại sau."})

    @application.get("/health")
    def health():
        return {"status": "ok"}

    @application.post("/v1/auth/login")
    def login(body: Login):
        accounts = application.state.accounts
        user = accounts.authenticate_password(body.username, body.password)
        if user is None:
            # Retain the exact legacy account behavior when the database has
            # not yet been initialized by the application lifespan.
            return issue_token(body.username, body.password)
        return issue_access_token(user)

    @application.post("/v1/auth/register", status_code=201)
    def register(body: Registration):
        ensure_auth_ready()
        try:
            user = application.state.accounts.register(body.email, body.password)
        except AccountError as exception:
            raise HTTPException(exception.status_code, str(exception)) from None
        return issue_access_token(user)

    @application.post("/v1/auth/google")
    def google_login(body: GoogleLogin):
        client_id = os.environ.get("GOOGLE_CLIENT_ID", "").strip()
        if not client_id:
            raise HTTPException(503, "Đăng nhập Google chưa được cấu hình trên server.")
        try:
            from google.auth.transport.requests import Request as GoogleRequest
            from google.oauth2 import id_token

            identity = id_token.verify_oauth2_token(body.credential, GoogleRequest(), client_id)
        except Exception:
            raise HTTPException(401, "Không xác thực được tài khoản Google.") from None
        if identity.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            raise HTTPException(401, "Token Google không hợp lệ.")
        if identity.get("email_verified") is not True or not identity.get("sub") or not identity.get("email"):
            raise HTTPException(401, "Tài khoản Google cần có email đã xác minh.")
        ensure_auth_ready()
        accounts = application.state.accounts
        user = accounts.get_by_google_sub(identity["sub"])
        if user is None:
            try:
                user = accounts.create_google_user(identity["email"], identity.get("name", ""), identity["sub"])
            except AccountError as exception:
                raise HTTPException(exception.status_code, str(exception)) from None
        return issue_access_token(user)

    router = APIRouter(prefix="/v1", dependencies=[Depends(require_access)])

    @router.get("/catalog")
    def catalog():
        return [{"code": code, "name": ANALYTES[code], "unit": DEFAULT_UNITS[code], "group": GROUPS[code]}
                for code in SUPPORTED_ANALYTES]

    @router.get("/references")
    def references(gestational_age: Annotated[str, Query(min_length=1, max_length=10)]):
        return study_references(gestational_age)

    @router.get("/reports/history")
    def report_history(user: dict = Depends(require_access)):
        return {"reports": application.state.service.list_reports(user["id"])}

    @router.get("/reports/history/{prior_session_id}/compare")
    def compare_report_history(prior_session_id: str, current_session_id: Annotated[str, Query(min_length=1, max_length=128)],
                               user: dict = Depends(require_access)):
        try:
            return application.state.service.compare_saved_reports(
                prior_session_id, current_session_id, user["id"])
        except KeyError:
            raise HTTPException(404, "Không tìm thấy phiếu CBC đã xác nhận.") from None
        except ValueError as exception:
            raise HTTPException(422, str(exception)) from None

    @router.post("/reports/validate")
    def validate(body: Report):
        _validate_specimen_date(body.specimen_date)
        with _operation(application):
            return compare_cbc(body.model_dump())

    @router.post("/reports/extract")
    def extract(file: UploadFile):
        content = _upload(file, IMAGE_LIMIT)
        with _operation(application):
            return vision.extract_report(content, file.content_type or "")

    @router.post("/speech/transcribe")
    def transcribe(file: UploadFile):
        content = _upload(file, WAV_LIMIT)
        with _operation(application):
            return {"text": speech.transcribe_wav(content)}

    @router.post("/speech/synthesize", response_class=Response, responses={200: {"content": {"audio/wav": {"schema": {"type": "string", "format": "binary"}}}}})
    def synthesize(body: SpeechBody):
        with _operation(application):
            audio = tts.synthesize_wav(body.text)
        return Response(audio, media_type="audio/wav")

    @router.post("/sessions", status_code=201)
    def create_session(user: dict = Depends(require_access)):
        service = application.state.service
        session_id = service.create_session(user["id"])
        return service.get_session(session_id, user["id"])

    @router.get("/sessions/{session_id}")
    def get_session(session_id: str, user: dict = Depends(require_access)):
        return application.state.service.get_session(session_id, user["id"])

    @router.delete("/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str, user: dict = Depends(require_access)):
        service = application.state.service
        service.get_session(session_id, user["id"])
        service.delete_session(session_id, user["id"])
        return Response(status_code=204)

    @router.put("/sessions/{session_id}/report")
    def confirm(session_id: str, body: ConfirmBody, user: dict = Depends(require_access)):
        _validate_specimen_date(body.report.specimen_date)
        service = application.state.service
        with _operation(application):
            saved = service.confirm_report(session_id, body.report.model_dump(), confirmed=body.confirmed,
                                           expected_revision=body.expected_revision, owner_id=user["id"])
            state = saved["session"]
            return {**state, "analysis": analyze_report(state["report"], confirmed=True)}

    @router.post("/sessions/{session_id}/invalidate")
    def invalidate(session_id: str, body: RevisionBody, user: dict = Depends(require_access)):
        service = application.state.service
        service.get_session(session_id, user["id"])
        return service.invalidate_report(session_id, expected_revision=body.expected_revision, owner_id=user["id"])

    @router.get("/sessions/{session_id}/analysis")
    def analysis(session_id: str, expected_revision: Annotated[int, Query(ge=0)],
                 user: dict = Depends(require_access)):
        state = application.state.service.get_session(session_id, user["id"])
        if state["revision"] != expected_revision:
            raise HTTPException(409, "Phiếu đã thay đổi. Hãy tải lại dữ liệu.")
        if state["report"] is None:
            raise HTTPException(422, "Xác nhận phiếu CBC trước khi xem phân tích.")
        with _operation(application):
            return analyze_report(state["report"], confirmed=True)

    @router.get("/sessions/{session_id}/history")
    def history(session_id: str, user: dict = Depends(require_access)):
        service = application.state.service
        service.get_session(session_id, user["id"])
        return {"messages": service.history(session_id, user["id"])}

    @router.post("/sessions/{session_id}/chat")
    def chat(session_id: str, body: ChatBody, user: dict = Depends(require_access)):
        with _operation(application) as usage:
            result = application.state.service.ask(session_id, body.question, expected_revision=body.expected_revision,
                                                    request_id=body.request_id, owner_id=user["id"])
        return {**result, "usage": usage, "revision": body.expected_revision}

    application.include_router(router)
    return application


app = create_app()
