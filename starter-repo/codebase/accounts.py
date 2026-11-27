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
