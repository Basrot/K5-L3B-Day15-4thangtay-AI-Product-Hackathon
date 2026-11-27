"""HTTP interface for the shared CBC service; one process and one inference slot."""
import os
import threading
from contextlib import asynccontextmanager, contextmanager
from typing import Annotated, Literal
from urllib.parse import urlsplit

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, Response, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, StrictBool, StrictFloat, StrictInt, StrictStr

from . import speech, tracing, tts, vision
from .agent import analyze_report
from .api_auth import issue_token, require_access
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
    rows: Annotated[list[LabRow], Field(min_length=1, max_length=8)]


class Login(Payload):
    username: Annotated[StrictStr, Field(min_length=1, max_length=100)]
    password: Annotated[StrictStr, Field(min_length=1, max_length=1000)]


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
        application.state.service = CBCService(db_path)
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
        return issue_token(body.username, body.password)

    router = APIRouter(prefix="/v1", dependencies=[Depends(require_access)])

    @router.get("/catalog")
    def catalog():
        return [{"code": code, "name": ANALYTES[code], "unit": DEFAULT_UNITS[code], "group": GROUPS[code]}
                for code in SUPPORTED_ANALYTES]

    @router.get("/references")
    def references(gestational_age: Annotated[str, Query(min_length=1, max_length=10)]):
        return study_references(gestational_age)

    @router.post("/reports/validate")
    def validate(body: Report):
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
    def create_session():
        service = application.state.service
        return service.get_session(service.create_session())

    @router.get("/sessions/{session_id}")
    def get_session(session_id: str):
        return application.state.service.get_session(session_id)

    @router.delete("/sessions/{session_id}", status_code=204)
    def delete_session(session_id: str):
        service = application.state.service
        service.get_session(session_id)
        service.delete_session(session_id)
        return Response(status_code=204)

    @router.put("/sessions/{session_id}/report")
    def confirm(session_id: str, body: ConfirmBody):
        service = application.state.service
        with _operation(application):
            saved = service.confirm_report(session_id, body.report.model_dump(), confirmed=body.confirmed,
                                           expected_revision=body.expected_revision)
            state = saved["session"]
            return {**state, "analysis": analyze_report(state["report"])}

    @router.post("/sessions/{session_id}/invalidate")
    def invalidate(session_id: str, body: RevisionBody):
        service = application.state.service
        service.get_session(session_id)
        return service.invalidate_report(session_id, expected_revision=body.expected_revision)

    @router.get("/sessions/{session_id}/analysis")
    def analysis(session_id: str, expected_revision: Annotated[int, Query(ge=0)]):
        state = application.state.service.get_session(session_id)
        if state["revision"] != expected_revision:
            raise HTTPException(409, "Phiếu đã thay đổi. Hãy tải lại dữ liệu.")
        if state["report"] is None:
            raise HTTPException(422, "Xác nhận phiếu CBC trước khi xem phân tích.")
        with _operation(application):
            return analyze_report(state["report"])

    @router.get("/sessions/{session_id}/history")
    def history(session_id: str):
        service = application.state.service
        service.get_session(session_id)
        return {"messages": service.history(session_id)}

    @router.post("/sessions/{session_id}/chat")
    def chat(session_id: str, body: ChatBody):
        with _operation(application) as usage:
            result = application.state.service.ask(session_id, body.question, expected_revision=body.expected_revision,
                                                    request_id=body.request_id)
        return {**result, "usage": usage, "revision": body.expected_revision}

    application.include_router(router)
    return application


app = create_app()
