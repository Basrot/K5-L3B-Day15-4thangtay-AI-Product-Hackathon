"""Dịch vụ SQLite cho giao diện demo CBC cục bộ."""

import json
import sqlite3
import os
from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from .agent import answer
from .tools import compare_cbc, compare_cbc_reports
from .references import reference_mode


def _comparison_key(report):
    """Normalize harmless JSON number/string representation differences for equality checks."""
    if not report:
        return report
    normalized = dict(report)
    normalized["rows"] = []
    for raw in report.get("rows", []):
        row = dict(raw)
        for key in ("value", "ref_low", "ref_high"):
            if row.get(key) is not None:
                row[key] = str(row[key])
        normalized["rows"].append(row)
    return normalized


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
                    specimen_date TEXT,
                    revision INTEGER NOT NULL DEFAULT 0,
                    owner_id TEXT,
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
                CREATE TABLE IF NOT EXISTS report_shares (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    patient_id TEXT NOT NULL,
                    doctor_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    revoked_at TEXT,
                    UNIQUE(session_id, doctor_id, created_at)
                );
                CREATE INDEX IF NOT EXISTS idx_report_shares_patient ON report_shares(patient_id, revoked_at);
                CREATE INDEX IF NOT EXISTS idx_report_shares_doctor ON report_shares(doctor_id, revoked_at);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_report_shares_active_pair
                    ON report_shares(session_id, doctor_id) WHERE revoked_at IS NULL;
                CREATE TABLE IF NOT EXISTS report_share_audit (
                    id INTEGER PRIMARY KEY,
                    share_id TEXT NOT NULL,
                    actor_id TEXT NOT NULL,
                    action TEXT NOT NULL CHECK (action IN ('shared', 'viewed', 'revoked')),
                    created_at TEXT NOT NULL
                );
            """)
            session_columns = {row["name"] for row in db.execute("PRAGMA table_info(sessions)")}
            if "owner_id" not in session_columns:
                db.execute("ALTER TABLE sessions ADD COLUMN owner_id TEXT")
            if "specimen_date" not in session_columns:
                db.execute("ALTER TABLE sessions ADD COLUMN specimen_date TEXT")
            db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_owner ON sessions(owner_id)")

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

    @staticmethod
    def _revoke_session_shares(db, session_id, now):
        shares = db.execute(
            "SELECT id, patient_id FROM report_shares WHERE session_id = ? AND revoked_at IS NULL",
            (session_id,),
        ).fetchall()
        db.execute("UPDATE report_shares SET revoked_at = ? WHERE session_id = ? AND revoked_at IS NULL",
                   (now, session_id))
        db.executemany(
            "INSERT INTO report_share_audit(share_id, actor_id, action, created_at) VALUES (?, ?, 'revoked', ?)",
            [(share["id"], share["patient_id"], now) for share in shares],
        )

    def assign_unowned_sessions(self, owner_id):
        with self._connection() as db:
            db.execute("UPDATE sessions SET owner_id = ? WHERE owner_id IS NULL", (owner_id,))

    def create_session(self, owner_id=None):
        session_id = uuid4().hex
        with self._connection() as db:
            db.execute("INSERT INTO sessions(id, owner_id) VALUES (?, ?)", (session_id, owner_id))
        return session_id

    def get_session(self, session_id, owner_id=None):
        with self._connection() as db:
            if owner_id is None:
                row = db.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
            else:
                row = db.execute("SELECT * FROM sessions WHERE id = ? AND owner_id = ?",
                                 (session_id, owner_id)).fetchone()
        if row is None:
            raise KeyError("Không tìm thấy phiên CBC.")
        report = json.loads(row["report"]) if row["report"] else None
        if report is not None and "specimen_date" not in report:
            report["specimen_date"] = row["specimen_date"]
        return {"session_id": row["id"], "revision": row["revision"],
                "specimen_date": row["specimen_date"], "report": report}

    def confirm_report(self, session_id, report, *, confirmed, expected_revision, owner_id=None):
        if confirmed is not True:
            raise ValueError("Xác nhận thông tin trên phiếu trước khi lưu.")
        comparison = compare_cbc(report)
        if comparison["status"] != "ok":
            raise ValueError(" ".join(comparison["issues"]))
        # Chỉ lưu các trường có trong hợp đồng, bỏ các khóa dư từ ảnh/OCR.
        fields = (("analyte", "value", "unit") if comparison["reference_mode"] == "study" else
                  ("analyte", "value", "unit", "ref_low", "ref_high", "ref_unit"))
        cleaned = {key: report[key] for key in ("pregnancy_status", "adult_confirmed", "gestational_age")}
        specimen_date = report.get("specimen_date")
        cleaned["specimen_date"] = specimen_date.isoformat() if hasattr(specimen_date, "isoformat") else specimen_date
        cleaned["rows"] = [{key: row.get(key) for key in fields} for row in report["rows"]]
        # Pin the selected mode for both new and legacy reports so that a
        # repeated confirmation compares against the same canonical report.
        cleaned["reference_mode"] = comparison["reference_mode"]
        if comparison["reference_mode"] == "study":
            cleaned["reference_version"] = comparison["reference_version"]
        cleaned["analysis_snapshot"] = {
            key: comparison[key] for key in (
                "rows", "gestational_age", "trimester", "reference_mode",
                "reference_version", "reference_source", "reference_note",
            ) if key in comparison
        }
        # Return the same JSON-compatible values that will be read back from
        # SQLite (notably lists instead of tuples in reference metadata).
        cleaned = json.loads(json.dumps(cleaned, ensure_ascii=False))
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            if owner_id is None:
                current = db.execute("SELECT report, revision, specimen_date FROM sessions WHERE id = ?", (session_id,)).fetchone()
            else:
                current = db.execute("SELECT report, revision, specimen_date FROM sessions WHERE id = ? AND owner_id = ?",
                                     (session_id, owner_id)).fetchone()
            if current is None:
                raise KeyError("Không tìm thấy phiên CBC.")
            existing = json.loads(current["report"]) if current["report"] else None
            if existing:
                normalized_existing = dict(existing)
                normalized_existing.setdefault("specimen_date", current["specimen_date"])
                normalized_existing.setdefault("reference_mode", reference_mode(existing))
            else:
                normalized_existing = None
            if _comparison_key(normalized_existing) == _comparison_key(cleaned):
                return {**comparison, "session": {"session_id": session_id,
                        "revision": current["revision"], "specimen_date": current["specimen_date"], "report": existing}}
            existing_without_snapshot = dict(normalized_existing) if normalized_existing else None
            cleaned_without_snapshot = dict(cleaned)
            if existing_without_snapshot is not None:
                existing_without_snapshot.pop("analysis_snapshot", None)
                existing_without_date = dict(existing_without_snapshot)
                existing_without_date.pop("specimen_date", None)
            else:
                existing_without_date = None
            cleaned_without_snapshot.pop("analysis_snapshot", None)
            cleaned_without_date = dict(cleaned_without_snapshot)
            cleaned_without_date.pop("specimen_date", None)
            existing_mode = reference_mode(existing) if existing else None
            old_analysis_snapshot = existing.get("analysis_snapshot") if existing else None
            snapshot_reference_is_current = (
                existing is not None and (
                    old_analysis_snapshot == cleaned.get("analysis_snapshot")
                    or (old_analysis_snapshot is None and (
                        existing_mode == "lab"
                        or existing.get("reference_version") == comparison.get("reference_version")
                    ))
                )
            )
            date_only_change = (
                _comparison_key(existing_without_date) == _comparison_key(cleaned_without_date)
                and snapshot_reference_is_current
            )
            if current["revision"] != expected_revision:
                raise ValueError("Phiếu đã thay đổi. Hãy tải lại dữ liệu trước khi xác nhận.")
            if owner_id is None:
                cursor = db.execute(
                    "UPDATE sessions SET report = ?, specimen_date = ?, revision = revision + 1 WHERE id = ?",
                    (json.dumps(cleaned, ensure_ascii=False), cleaned["specimen_date"], session_id),
                )
            else:
                cursor = db.execute(
                    "UPDATE sessions SET report = ?, specimen_date = ?, revision = revision + 1 WHERE id = ? AND owner_id = ?",
                    (json.dumps(cleaned, ensure_ascii=False), cleaned["specimen_date"], session_id, owner_id),
                )
            if cursor.rowcount != 1:
                raise KeyError("Không tìm thấy phiên CBC.")
            self._revoke_session_shares(db, session_id, datetime.now(timezone.utc).isoformat(timespec="seconds"))
            if date_only_change:
                db.execute(
                    "UPDATE messages SET revision = ? WHERE session_id = ? AND revision = ?",
                    (current["revision"] + 1, session_id, current["revision"]),
                )
            else:
                db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            snapshot = {"session_id": session_id, "revision": current["revision"] + 1,
                        "specimen_date": cleaned["specimen_date"], "report": cleaned}
        return {**comparison, "session": snapshot}

    def list_reports(self, owner_id):
        """Return confirmed report summaries for one authenticated account only."""
        with self._connection() as db:
            rows = db.execute(
                "SELECT id, report, revision, specimen_date FROM sessions "
                "WHERE owner_id = ? AND report IS NOT NULL", (owner_id,)
            ).fetchall()
        reports = []
        for row in rows:
            report = json.loads(row["report"])
            reports.append({
                "session_id": row["id"],
                "revision": row["revision"],
                "specimen_date": row["specimen_date"],
                "gestational_age": report.get("gestational_age"),
                "rows": [{key: item.get(key) for key in ("analyte", "value", "unit")}
                         for item in report.get("rows", [])],
            })
        reports.sort(key=lambda item: (item["specimen_date"] or "", item["session_id"]), reverse=True)
        reports.sort(key=lambda item: item["specimen_date"] is None)
        return reports

    def compare_saved_reports(self, prior_session_id, current_session_id, owner_id):
        """Compare two confirmed CBC reports owned by the same account."""
        with self._connection() as db:
            rows = db.execute(
                "SELECT id, report, specimen_date FROM sessions "
                "WHERE owner_id = ? AND id IN (?, ?)",
                (owner_id, prior_session_id, current_session_id),
            ).fetchall()
        by_id = {row["id"]: row for row in rows}
        prior = by_id.get(prior_session_id)
        current = by_id.get(current_session_id)
        if (prior is None or current is None or prior["report"] is None or current["report"] is None):
            raise KeyError("Không tìm thấy phiếu CBC đã xác nhận.")
        if prior_session_id == current_session_id:
            raise ValueError("Chọn hai phiếu CBC khác nhau để so sánh.")
        if not prior["specimen_date"] or not current["specimen_date"]:
            raise ValueError("Cả hai phiếu cần có ngày lấy mẫu để so sánh theo thời gian.")
        if prior["specimen_date"] >= current["specimen_date"]:
            raise ValueError("Phiếu hiện tại cần có ngày lấy mẫu muộn hơn phiếu trước.")
        return compare_cbc_reports(
            json.loads(prior["report"]), json.loads(current["report"]),
            prior["specimen_date"], current["specimen_date"],
        )

    def invalidate_report(self, session_id, *, expected_revision, owner_id=None):
        """Gọi ngay khi người dùng sửa form hoặc chọn ảnh khác."""
        with self._connection() as db:
            if owner_id is None:
                cursor = db.execute(
                    "UPDATE sessions SET report = NULL, specimen_date = NULL, revision = revision + 1 WHERE id = ? AND revision = ?",
                    (session_id, expected_revision),
                )
            else:
                cursor = db.execute(
                    "UPDATE sessions SET report = NULL, specimen_date = NULL, revision = revision + 1 WHERE id = ? AND owner_id = ? AND revision = ?",
                    (session_id, owner_id, expected_revision),
                )
            if cursor.rowcount != 1:
                raise ValueError("Phiếu đã thay đổi hoặc phiên đã bị xóa.")
            self._revoke_session_shares(db, session_id, datetime.now(timezone.utc).isoformat(timespec="seconds"))
            db.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        return {"session_id": session_id, "revision": expected_revision + 1, "report": None}

    def ask(self, session_id, question, *, expected_revision, request_id=None, owner_id=None):
        if not isinstance(question, str) or not question.strip() or len(question) > 1000:
            raise ValueError("Nhập câu hỏi dài từ 1 đến 1000 ký tự.")
        if request_id is None:
            request_id = uuid4().hex
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            raise ValueError("request_id phải là chuỗi từ 1 đến 128 ký tự.")
        session = self.get_session(session_id, owner_id)
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

        recent_history = self.recent_history(
            session_id, session["revision"], owner_id=owner_id, limit=8
        )
        result = answer(
            json.dumps({"report": session["report"], "question": question}, ensure_ascii=False),
            confirmed=True,
            history=recent_history,
        )
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            if owner_id is None:
                current = db.execute("SELECT revision FROM sessions WHERE id = ?", (session_id,)).fetchone()
            else:
                current = db.execute("SELECT revision FROM sessions WHERE id = ? AND owner_id = ?",
                                     (session_id, owner_id)).fetchone()
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

    def recent_history(self, session_id, revision, *, owner_id=None, limit=8):
        """Return a bounded tail of prior turns from this session revision only."""
        with self._connection() as db:
            query = """SELECT m.question, m.result FROM messages m
                       JOIN sessions s ON s.id = m.session_id AND s.revision = m.revision
                       WHERE m.session_id = ? AND m.revision = ?"""
            params = [session_id, revision]
            if owner_id is not None:
                query += " AND s.owner_id = ?"
                params.append(owner_id)
            query += " ORDER BY m.id DESC LIMIT ?"
            params.append(max(0, min(int(limit), 8)))
            rows = db.execute(query, params).fetchall()
        turns = []
        for row in reversed(rows):
            result = json.loads(row["result"])
            turns.append({
                "question": row["question"][:500],
                "output": str(result.get("output", ""))[:500],
            })
        return turns

    def history(self, session_id, owner_id=None):
        with self._connection() as db:
            if owner_id is None:
                rows = db.execute(
                    """SELECT m.question, m.result, m.created_at FROM messages m
                       JOIN sessions s ON s.id = m.session_id AND s.revision = m.revision
                       WHERE m.session_id = ? ORDER BY m.id""", (session_id,)
                ).fetchall()
            else:
                rows = db.execute(
                    """SELECT m.question, m.result, m.created_at FROM messages m
                       JOIN sessions s ON s.id = m.session_id AND s.revision = m.revision
                       WHERE m.session_id = ? AND s.owner_id = ? ORDER BY m.id""", (session_id, owner_id)
                ).fetchall()
        return [{"question": row["question"], "result": json.loads(row["result"]),
                 "created_at": row["created_at"]} for row in rows]

    def delete_session(self, session_id, owner_id=None):
        with self._connection() as db:
            if owner_id is None:
                db.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
            else:
                db.execute("DELETE FROM sessions WHERE id = ? AND owner_id = ?", (session_id, owner_id))

    def share_report(self, session_id, patient_id, doctor_id):
        now = datetime.now(timezone.utc)
        share_id = uuid4().hex
        created_at = now.isoformat(timespec="seconds")
        expires_at = (now + timedelta(days=30)).isoformat(timespec="seconds")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            report = db.execute("SELECT report FROM sessions WHERE id = ? AND owner_id = ?",
                                (session_id, patient_id)).fetchone()
            if report is None or report["report"] is None:
                raise KeyError("Chỉ có thể chia sẻ phiếu đã xác nhận của chính bạn.")
            db.execute("""
                UPDATE report_shares SET revoked_at = ?
                WHERE session_id = ? AND doctor_id = ? AND revoked_at IS NULL AND expires_at <= ?
            """, (created_at, session_id, doctor_id, created_at))
            active = db.execute("""
                SELECT id FROM report_shares
                WHERE session_id = ? AND doctor_id = ? AND revoked_at IS NULL
            """, (session_id, doctor_id)).fetchone()
            if active:
                raise ValueError("Phiếu này đã được chia sẻ với bác sĩ. Thu hồi quyền hiện tại trước khi cấp lại.")
            db.execute("""
                INSERT INTO report_shares(id, session_id, patient_id, doctor_id, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (share_id, session_id, patient_id, doctor_id, created_at, expires_at))
            db.execute("INSERT INTO report_share_audit(share_id, actor_id, action, created_at) VALUES (?, ?, 'shared', ?)",
                       (share_id, patient_id, created_at))
        return {"share_id": share_id, "session_id": session_id, "doctor_id": doctor_id,
                "created_at": created_at, "expires_at": expires_at, "revoked_at": None}

    def list_report_shares(self, patient_id):
        with self._connection() as db:
            rows = db.execute("""
                SELECT rs.id AS share_id, rs.session_id, rs.created_at, rs.expires_at, rs.revoked_at,
                       u.email AS doctor_email, d.full_name AS doctor_name, d.specialty,
                       (SELECT MAX(a.created_at) FROM report_share_audit a
                        WHERE a.share_id = rs.id AND a.action = 'viewed') AS last_viewed_at,
                       (SELECT COUNT(*) FROM report_share_audit a
                        WHERE a.share_id = rs.id AND a.action = 'viewed') AS access_count
                FROM report_shares rs JOIN users u ON u.id = rs.doctor_id
                JOIN doctor_profiles d ON d.user_id = rs.doctor_id
                WHERE rs.patient_id = ? ORDER BY rs.created_at DESC
            """, (patient_id,)).fetchall()
        return [dict(row) for row in rows]

    def revoke_report_share(self, share_id, patient_id):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute("""
                UPDATE report_shares SET revoked_at = ?
                WHERE id = ? AND patient_id = ? AND revoked_at IS NULL
            """, (now, share_id, patient_id))
            if cursor.rowcount != 1:
                raise KeyError("Không tìm thấy quyền chia sẻ còn hiệu lực.")
            db.execute("INSERT INTO report_share_audit(share_id, actor_id, action, created_at) VALUES (?, ?, 'revoked', ?)",
                       (share_id, patient_id, now))

    def list_doctor_shared_reports(self, doctor_id):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connection() as db:
            rows = db.execute("""
                SELECT rs.id AS share_id, rs.session_id, rs.created_at AS shared_at, rs.expires_at,
                       s.specimen_date, p.email AS patient_email, p.display_name AS patient_name,
                       json_extract(s.report, '$.gestational_age') AS gestational_age,
                       json_array_length(json_extract(s.report, '$.rows')) AS row_count
                FROM report_shares rs JOIN sessions s ON s.id = rs.session_id
                JOIN users p ON p.id = rs.patient_id
                WHERE rs.doctor_id = ? AND rs.revoked_at IS NULL AND rs.expires_at > ? AND s.report IS NOT NULL
                ORDER BY s.specimen_date DESC, rs.created_at DESC
            """, (doctor_id, now)).fetchall()
        return [dict(row) for row in rows]

    def get_doctor_shared_report(self, share_id, doctor_id):
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connection() as db:
            db.execute("BEGIN IMMEDIATE")
            row = db.execute("""
                SELECT rs.id AS share_id, rs.session_id, rs.expires_at, s.revision, s.specimen_date,
                       s.report, p.display_name AS patient_name, p.email AS patient_email
                FROM report_shares rs JOIN sessions s ON s.id = rs.session_id
                JOIN users p ON p.id = rs.patient_id
                WHERE rs.id = ? AND rs.doctor_id = ? AND rs.revoked_at IS NULL
                  AND rs.expires_at > ? AND s.report IS NOT NULL
            """, (share_id, doctor_id, now)).fetchone()
            if row is None:
                raise KeyError("Phiếu không tồn tại hoặc quyền xem đã hết hạn/được thu hồi.")
            db.execute("INSERT INTO report_share_audit(share_id, actor_id, action, created_at) VALUES (?, ?, 'viewed', ?)",
                       (share_id, doctor_id, now))
        return {"share_id": row["share_id"], "session_id": row["session_id"],
                "revision": row["revision"], "specimen_date": row["specimen_date"],
                "expires_at": row["expires_at"], "patient": {"name": row["patient_name"], "email": row["patient_email"]},
                "report": json.loads(row["report"])}
