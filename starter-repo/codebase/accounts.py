"""Persistent local accounts for the Railway CBC API."""

import hashlib
import hmac
import os
import re
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4


class AccountError(ValueError):
    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if len(email) > 254 or not re.fullmatch(r"[^@\s]{1,64}@[^@\s.]+(?:\.[^@\s.]+)+", email):
        raise AccountError(422, "Nhập địa chỉ email hợp lệ.")
    return email


def _password_hash(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode("utf-8"), salt=salt, n=2**14, r=8, p=1, dklen=64)
    return "$".join(("scrypt", "16384", "8", "1", salt.hex(), digest.hex()))


def _password_matches(password: str, stored: str) -> bool:
    try:
        algorithm, n, r, p, salt_hex, digest_hex = stored.split("$")
        if algorithm != "scrypt":
            return False
        digest = hashlib.scrypt(password.encode("utf-8"), salt=bytes.fromhex(salt_hex),
                                n=int(n), r=int(r), p=int(p), dklen=len(bytes.fromhex(digest_hex)))
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError, MemoryError):
        return False


class AccountStore:
    """Owns account records in the same SQLite database as CBC sessions."""

    def __init__(self, db_path):
        self.path = Path(db_path)
        with self._connection() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT UNIQUE,
                    email TEXT UNIQUE COLLATE NOCASE,
                    display_name TEXT NOT NULL DEFAULT '',
                    password_hash TEXT,
                    google_sub TEXT UNIQUE,
                    role TEXT NOT NULL DEFAULT 'user' CHECK (role IN ('admin', 'user')),
                    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
                CREATE INDEX IF NOT EXISTS idx_users_google_sub ON users(google_sub);
                CREATE TABLE IF NOT EXISTS doctor_profiles (
                    user_id TEXT PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                    full_name TEXT NOT NULL,
                    license_number TEXT NOT NULL,
                    specialty TEXT NOT NULL,
                    workplace TEXT NOT NULL DEFAULT '',
                    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'rejected')),
                    reviewed_by TEXT,
                    reviewed_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)

    @contextmanager
    def _connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    @staticmethod
    def _public(row):
        if row is None:
            return None
        return {"id": row["id"], "username": row["username"], "email": row["email"],
                "display_name": row["display_name"], "role": row["role"],
                "is_active": bool(row["is_active"])}

    def ensure_admin(self, username: str, password: str):
        if not username or not password:
            return None
        admin_id = "admin-" + hashlib.sha256(username.encode("utf-8")).hexdigest()[:24]
        encoded_password = _password_hash(password)
        with self._connection() as db:
            db.execute("UPDATE users SET is_active = 0 WHERE role = 'admin' AND username != ?", (username,))
            db.execute("""
                INSERT INTO users(id, username, display_name, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, 'admin', 1)
                ON CONFLICT(username) DO UPDATE SET
                    password_hash = excluded.password_hash,
                    role = 'admin', is_active = 1
            """, (admin_id, username, username, encoded_password))
            row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return self._public(row)

    def register(self, email: str, password: str):
        email = normalize_email(email)
        if len(password) < 10 or len(password) > 1000:
            raise AccountError(422, "Mật khẩu cần có ít nhất 10 ký tự.")
        try:
            with self._connection() as db:
                db.execute("INSERT INTO users(id, email, display_name, password_hash) VALUES (?, ?, ?, ?)",
                           (uuid4().hex, email, email.split("@", 1)[0], _password_hash(password)))
                row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        except sqlite3.IntegrityError:
            raise AccountError(409, "Email này đã được đăng ký. Hãy đăng nhập hoặc dùng Google đã liên kết.") from None
        return self._public(row)

    def authenticate_password(self, username_or_email: str, password: str):
        identifier = username_or_email.strip()
        with self._connection() as db:
            row = db.execute("""
                SELECT * FROM users WHERE is_active = 1 AND
                    (username = ? OR email = ? COLLATE NOCASE)
            """, (identifier, identifier.lower())).fetchone()
        if row is None or not row["password_hash"] or not _password_matches(password, row["password_hash"]):
            return None
        return self._public(row)

    def get_by_id(self, user_id: str):
        with self._connection() as db:
            row = db.execute("SELECT * FROM users WHERE id = ? AND is_active = 1", (user_id,)).fetchone()
        return self._public(row)

    def get_by_username(self, username: str):
        with self._connection() as db:
            row = db.execute("SELECT * FROM users WHERE username = ? AND is_active = 1", (username,)).fetchone()
        return self._public(row)

    def get_by_google_sub(self, google_sub: str):
        with self._connection() as db:
            row = db.execute("SELECT * FROM users WHERE google_sub = ? AND is_active = 1", (google_sub,)).fetchone()
        return self._public(row)

    def link_google_account(self, email: str, google_sub: str):
        """Link a Google-verified email to an existing account with the same email."""
        email = normalize_email(email)
        try:
            with self._connection() as db:
                row = db.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE AND is_active = 1",
                                 (email,)).fetchone()
                if row is None:
                    return None
                if row["google_sub"] and row["google_sub"] != google_sub:
                    raise AccountError(409, "Email này đã liên kết với tài khoản Google khác.")
                db.execute("UPDATE users SET google_sub = ? WHERE id = ?", (google_sub, row["id"]))
                row = db.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()
        except sqlite3.IntegrityError:
            raise AccountError(409, "Tài khoản Google này đã được liên kết với người dùng khác.") from None
        return self._public(row)

    def create_google_user(self, email: str, display_name: str, google_sub: str):
        email = normalize_email(email)
        try:
            with self._connection() as db:
                db.execute("INSERT INTO users(id, email, display_name, google_sub) VALUES (?, ?, ?, ?)",
                           (uuid4().hex, email, display_name[:200], google_sub))
                row = db.execute("SELECT * FROM users WHERE google_sub = ?", (google_sub,)).fetchone()
        except sqlite3.IntegrityError:
            raise AccountError(409, "Email này đã có tài khoản. Hãy đăng nhập bằng mật khẩu đã đăng ký.") from None
        return self._public(row)

    def submit_doctor_request(self, user_id: str, full_name: str, license_number: str,
                              specialty: str, workplace: str = ""):
        values = [value.strip() for value in (full_name, license_number, specialty, workplace)]
        full_name, license_number, specialty, workplace = values
        if not full_name or not license_number or not specialty:
            raise AccountError(422, "Nhập họ tên, số giấy phép hành nghề và chuyên khoa.")
        if len(full_name) > 200 or len(license_number) > 100 or len(specialty) > 150 or len(workplace) > 200:
            raise AccountError(422, "Thông tin đăng ký bác sĩ vượt quá độ dài cho phép.")
        with self._connection() as db:
            account = db.execute("SELECT id, google_sub FROM users WHERE id = ? AND is_active = 1", (user_id,)).fetchone()
            if account is None:
                raise AccountError(404, "Không tìm thấy tài khoản.")
            if not account["google_sub"]:
                raise AccountError(422, "Để đăng ký cổng bác sĩ, hãy đăng nhập bằng Google để xác nhận email trước.")
            current = db.execute("SELECT status FROM doctor_profiles WHERE user_id = ?", (user_id,)).fetchone()
            if current and current["status"] == "active":
                raise AccountError(409, "Tài khoản bác sĩ đã được xác minh; liên hệ quản trị viên để cập nhật hồ sơ.")
            db.execute("""
                INSERT INTO doctor_profiles(user_id, full_name, license_number, specialty, workplace)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET full_name = excluded.full_name,
                    license_number = excluded.license_number, specialty = excluded.specialty,
                    workplace = excluded.workplace, status = 'pending', reviewed_by = NULL, reviewed_at = NULL
            """, (user_id, full_name, license_number, specialty, workplace))
        return self.get_doctor_profile(user_id)

    def get_doctor_profile(self, user_id: str):
        with self._connection() as db:
            row = db.execute("""
                SELECT d.user_id, d.full_name, d.license_number, d.specialty, d.workplace,
                       d.status, d.reviewed_at, u.email
                FROM doctor_profiles d JOIN users u ON u.id = d.user_id
                WHERE d.user_id = ? AND u.is_active = 1
            """, (user_id,)).fetchone()
        return dict(row) if row else None

    def list_pending_doctors(self):
        with self._connection() as db:
            rows = db.execute("""
                SELECT d.user_id, d.full_name, d.license_number, d.specialty, d.workplace,
                       d.created_at, u.email
                FROM doctor_profiles d JOIN users u ON u.id = d.user_id
                WHERE d.status = 'pending' AND u.is_active = 1 ORDER BY d.created_at
            """).fetchall()
        return [dict(row) for row in rows]

    def review_doctor(self, user_id: str, reviewer_id: str, approved: bool):
        with self._connection() as db:
            cursor = db.execute("""
                UPDATE doctor_profiles SET status = ?, reviewed_by = ?, reviewed_at = CURRENT_TIMESTAMP,
                    license_number = ''
                WHERE user_id = ? AND status = 'pending'
            """, ("active" if approved else "rejected", reviewer_id, user_id))
            if cursor.rowcount != 1:
                raise AccountError(404, "Không tìm thấy hồ sơ bác sĩ đang chờ duyệt.")
        return self.get_doctor_profile(user_id)

    def get_verified_doctor_by_email(self, email: str):
        with self._connection() as db:
            row = db.execute("""
                SELECT u.id, u.email, d.full_name, d.specialty, d.workplace
                FROM users u JOIN doctor_profiles d ON d.user_id = u.id
                WHERE lower(u.email) = lower(?) AND u.is_active = 1 AND u.google_sub IS NOT NULL AND d.status = 'active'
            """, (email.strip(),)).fetchone()
        return dict(row) if row else None
