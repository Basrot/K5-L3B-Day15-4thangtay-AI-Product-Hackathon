"""Dịch vụ SQLite cho giao diện demo CBC cục bộ."""

import json
import sqlite3
import os
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from .agent import answer
from .tools import compare_cbc


class CBCService:
    """Mỗi trình duyệt giữ session_id riêng. Phiếu mẫu được xác nhận trước khi lưu."""

    def __init__(self, db_path=None):
        self.path = Path(db_path or os.environ.get("CBC_DB_PATH") or
                         Path(__file__).resolve().parents[1] / "runtime" / "cbc.sqlite3")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    report TEXT,
                    revision INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    revision INTEGER NOT NULL,
                    request_id TEXT NOT NULL,
                    question TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(session_id, revision, request_id)
                );
            """)

    @contextmanager
    def _connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        db.execute("PRAGMA secure_delete = ON")
        try:
            with db:
                yield db
        finally:
            db.close()

    def create_session(self):
        session_id = uuid4().hex
        with self._connection() as db:
            db.execute("INSERT INTO sessions(id) VALUES (?)", (session_id,))
        return session_id

    def get_session(self, session_id):
        with self._connection() as db:
            row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            raise KeyError("Không tìm thấy phiên CBC.")
        return {"session_id": row["id"], "revision": row["revision"],
                "report": json.loads(row["report"]) if row["report"] else None}

    def confirm_report(self, session_id, report, *, confirmed, expected_revision):
        if confirmed is not True:
            raise ValueError("Xác nhận thông tin trên phiếu trước khi lưu.")
        comparison = compare_cbc(report)
        if comparison["status"] != "ok":
            raise ValueError(" ".join(comparison["issues"]))
        # Chỉ lưu các trường có trong hợp đồng, bỏ các khóa dư từ ảnh/OCR.
        fields = ("analyte", "value", "unit", "ref_low", "ref_high", "ref_unit")
        cleaned = {key: report[key] for key in ("pregnancy_status", "adult_confirmed", "gestational_age")}
        cleaned["rows"] = [{key: row[key] for key in fields} for row in report["rows"]]
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT report, revision FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if current is None:
                raise KeyError("Không tìm thấy phiên CBC.")
            if current["report"] and json.loads(current["report"]) == cleaned:
                return comparison
            if current["revision"] != expected_revision:
                raise ValueError("Phiếu đã thay đổi. Hãy tải lại dữ liệu trước khi xác nhận.")
            cursor = db.execute(
                "UPDATE sessions SET report = ?, revision = revision + 1 WHERE id = ?",
                (json.dumps(cleaned, ensure_ascii=False), session_id),
            )
            if cursor.rowcount != 1:
                raise KeyError("Không tìm thấy phiên CBC.")
            db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        return comparison

    def invalidate_report(self, session_id, *, expected_revision):
        """Gọi ngay khi người dùng sửa form hoặc chọn ảnh khác."""
        with self._connection() as db:
            cursor = db.execute(
                "UPDATE sessions SET report = NULL, revision = revision + 1 WHERE id = ? AND revision = ?",
                (session_id, expected_revision),
            )
            if cursor.rowcount != 1:
                raise ValueError("Phiếu đã thay đổi hoặc phiên đã bị xóa.")
            db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))

    def ask(self, session_id, question, *, expected_revision, request_id=None):
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            raise ValueError("Nhập câu hỏi dài từ 1 đến 1000 ký tự.")
        if request_id is None:
            request_id = uuid4().hex
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            raise ValueError("request_id phải là chuỗi từ 1 đến 128 ký tự.")
        session = self.get_session(session_id)
        if session["revision"] != expected_revision:
            raise ValueError("Phiếu đã thay đổi. Hãy tải lại dữ liệu trước khi hỏi.")
        if session["report"] is None:
            raise ValueError("Xác nhận phiếu CBC trước khi hỏi.")
        question = question.strip()
        with self._connection() as db:
            cached = db.execute(
                "SELECT question, result FROM messages WHERE session_id = ? AND revision = ? AND request_id = ?",
                (session_id, session["revision"], request_id),
            ).fetchone()
        if cached:
            if cached["question"] != question:
                raise ValueError("request_id đã được dùng cho câu hỏi khác.")
            return json.loads(cached["result"])

        result = answer(json.dumps({"report": session["report"], "question": question}, ensure_ascii=False))
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            current = db.execute("SELECT revision FROM sessions WHERE id = ?", (session_id,)).fetchone()
            if current is None or current["revision"] != session["revision"]:
                raise ValueError("Phiếu đã thay đổi trong khi trả lời. Hãy gửi lại câu hỏi.")
            db.execute(
                "INSERT OR IGNORE INTO messages(session_id, revision, request_id, question, result) VALUES (?,?,?,?,?)",
                (session_id, session["revision"], request_id, question, json.dumps(result, ensure_ascii=False)),
            )
            stored = db.execute(
                "SELECT question, result FROM messages WHERE session_id = ? AND revision = ? AND request_id = ?",
                (session_id, session["revision"], request_id),
            ).fetchone()
            if stored["question"] != question:
                raise ValueError("request_id đã được dùng cho câu hỏi khác.")
        return json.loads(stored["result"])

    def history(self, session_id):
        with self._connection() as db:
            rows = db.execute(
                """SELECT m.question, m.result, m.created_at FROM messages m
                   JOIN sessions s ON s.id = m.session_id AND s.revision = m.revision
                   WHERE m.session_id = ? ORDER BY m.id""", (session_id,)
            ).fetchall()
        return [{"question": row["question"], "result": json.loads(row["result"]),
                 "created_at": row["created_at"]} for row in rows]

    def delete_session(self, session_id):
        with self._connection() as db:
            db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
