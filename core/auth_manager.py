# core/auth_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import sqlite3
import os
import json
import secrets
import hashlib
import logging
from datetime import datetime, timedelta
from contextlib import closing
from typing import Optional, Tuple, Dict, Any
import hmac

from variables.constants import HERE

logger = logging.getLogger(__name__)

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    logger.warning("bcrypt not installed, using hashlib (less secure)")


class AuthManager:
    def __init__(self):
        self.db_path = os.path.join(HERE, 'CB_data/users.db')
        self._init_db()
        self.current_user: Optional[int] = None
        self.session_token: Optional[str] = None
        self._load_session()

    def _init_db(self) -> None:
        with closing(sqlite3.connect(self.db_path)) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    email TEXT,
                    full_name TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    is_guest BOOLEAN DEFAULT 0,
                    preferences TEXT,
                    remember_token_hash TEXT,
                    remember_expiry TEXT
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    token TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            ''')
            conn.commit()

    @staticmethod
    def _hash_password(password: str) -> str:
        if HAS_BCRYPT:
            salt = bcrypt.gensalt() # ایجاد نمک
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        else:
            salt = secrets.token_hex(32)
            combined = salt + password
            hash_obj = hashlib.sha256(combined.encode())
            return salt + ':' + hash_obj.hexdigest()

    @staticmethod
    def _verify_password(password: str, stored_hash: str) -> bool:
        if HAS_BCRYPT:
            try:
                return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
            except ValueError:
                return False
        else:
            try:
                salt, hash_value = stored_hash.split(':')
                combined = salt + password
                hash_obj = hashlib.sha256(combined.encode())
                return hmac.compare_digest(hash_obj.hexdigest(), hash_value)
            except Exception:
                return False

    def register_user(self, username: str, password: str,
                      email: Optional[str] = None,
                      full_name: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
                if cursor.fetchone():
                    return False, "Username already exists"
                password_hash = self._hash_password(password)
                created_at = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, email, full_name, created_at, is_guest) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (username, password_hash, email, full_name, created_at, False)
                )
                conn.commit()
                logger.info(f"User registered: {username}")
                return True, cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Registration error: {e}")
            return False, str(e)

    def login_user(self, username: str, password: str,
                   remember_me: bool = False) -> Tuple[bool, Any]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
                row = cursor.fetchone()
                if not row:
                    return False, "User not found"
                user_id, stored_hash = row
                if not self._verify_password(password, stored_hash):
                    return False, "Invalid password"
                cursor.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now().isoformat(), user_id)
                )
                if remember_me:
                    # توکن تصادفی، هش شده در دیتابیس ذخیره می‌شود
                    raw_token = secrets.token_urlsafe(32)
                    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
                    expiry = (datetime.now() + timedelta(days=30)).isoformat()
                    cursor.execute(
                        "UPDATE users SET remember_token_hash = ?, remember_expiry = ? WHERE id = ?",
                        (token_hash, expiry, user_id)
                    )
                    # برای ذخیره در کوکی یا فایل، فقط raw_token را نگه می‌داریم
                    self._save_remember_token(raw_token, username)
                else:
                    cursor.execute(
                        "UPDATE users SET remember_token_hash = NULL, remember_expiry = NULL WHERE id = ?",
                        (user_id,)
                    )
                conn.commit()
            token = self._create_session(user_id)
            self.current_user = user_id
            self.session_token = token
            self._save_session_info(user_id, token)
            logger.info(f"User logged in: {username}")
            return True, token
        except sqlite3.Error as e:
            logger.error(f"Login error: {e}")
            return False, str(e)

    def login_guest(self) -> Tuple[bool, Any]:
        try:
            guest_username = f"guest_{secrets.token_hex(4)}"
            guest_password = secrets.token_hex(8)
            password_hash = self._hash_password(guest_password)
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                created_at = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO users (username, password_hash, created_at, is_guest) "
                    "VALUES (?, ?, ?, ?)",
                    (guest_username, password_hash, created_at, True)
                )
                conn.commit()
                user_id = cursor.lastrowid
            token = self._create_session(user_id)
            self.current_user = user_id
            self.session_token = token
            self._save_session_info(user_id, token)
            logger.info(f"Guest logged in: {guest_username}")
            return True, token
        except Exception as e:
            logger.exception("Guest login failed")
            return False, str(e)

    def _create_session(self, user_id: int) -> str:
        token = secrets.token_urlsafe(32)
        created_at = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=12)).isoformat()
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
                cursor.execute(
                    "INSERT INTO sessions (user_id, token, created_at, expires_at) "
                    "VALUES (?, ?, ?, ?)",
                    (user_id, token, created_at, expires_at)
                )
                conn.commit()
            return token
        except sqlite3.Error as e:
            logger.error(f"Session creation error: {e}")
            raise

    def _save_session_info(self, user_id: int, token: str) -> None:
        try:
            session_file = os.path.join(HERE, 'CB_data/session.json')
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'user_id': user_id,
                    'token': token,
                    'created_at': datetime.now().isoformat()
                }, f)
        except OSError as e:
            logger.error(f"Could not save session: {e}")

    def _save_remember_token(self, raw_token: str, username: str) -> None:
        try:
            remember_file = os.path.join(HERE, 'CB_data/remember.json')
            with open(remember_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'username': username,
                    'token': raw_token,  # فقط توکن خام ذخیره می‌شود
                    'created_at': datetime.now().isoformat()
                }, f)
        except OSError as e:
            logger.error(f"Could not save remember token: {e}")

    def _load_session(self) -> bool:
        session_file = os.path.join(HERE, 'CB_data/session.json')
        if not os.path.exists(session_file):
            return self._load_remember_token()
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            created_at = datetime.fromisoformat(data.get('created_at', ''))
            if datetime.now() - created_at > timedelta(hours=12):
                return self._load_remember_token()
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT user_id, expires_at FROM sessions WHERE token = ? AND expires_at > ?",
                    (data.get('token'), datetime.now().isoformat())
                )
                row = cursor.fetchone()
                if row:
                    self.current_user = row[0]
                    self.session_token = data.get('token')
                    return True
        except (OSError, json.JSONDecodeError, sqlite3.Error) as e:
            logger.warning(f"Session load failed: {e}")
        return self._load_remember_token()

    def _load_remember_token(self) -> bool:
        remember_file = os.path.join(HERE, 'CB_data/remember.json')
        if not os.path.exists(remember_file):
            return False
        try:
            with open(remember_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            username = data.get('username')
            raw_token = data.get('token')
            if not username or not raw_token:
                return False
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id FROM users WHERE username = ? AND remember_token_hash = ? AND remember_expiry > ?",
                    (username, token_hash, datetime.now().isoformat())
                )
                row = cursor.fetchone()
                if not row:
                    return False
                user_id = row[0]
                new_token = self._create_session(user_id)
                self.current_user = user_id
                self.session_token = new_token
                self._save_session_info(user_id, new_token)
                logger.info(f"Remember token accepted for {username}")
                return True
        except (OSError, json.JSONDecodeError, sqlite3.Error) as e:
            logger.warning(f"Remember token load failed: {e}")
            return False

    def logout_user(self, clear_remember: bool = False) -> None:
        if self.session_token:
            try:
                with closing(sqlite3.connect(self.db_path)) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM sessions WHERE token = ?", (self.session_token,))
                    if clear_remember and self.current_user:
                        cursor.execute(
                            "UPDATE users SET remember_token_hash = NULL, remember_expiry = NULL WHERE id = ?",
                            (self.current_user,)
                        )
                    conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Logout error: {e}")
        session_file = os.path.join(HERE, 'CB_data/session.json')
        if os.path.exists(session_file):
            try:
                os.remove(session_file)
            except OSError:
                pass
        if clear_remember:
            remember_file = os.path.join(HERE, 'CB_data/remember.json')
            if os.path.exists(remember_file):
                try:
                    os.remove(remember_file)
                except OSError:
                    pass
        self.current_user = None
        self.session_token = None
        logger.info("User logged out")

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        if not self.current_user:
            return None
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, username, email, full_name, created_at, last_login, is_guest, preferences "
                    "FROM users WHERE id = ?", (self.current_user,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
                        'full_name': row[3],
                        'created_at': row[4],
                        'last_login': row[5],
                        'is_guest': bool(row[6]),
                        'preferences': row[7]
                    }
        except sqlite3.Error as e:
            logger.error(f"Error getting user: {e}")
        return None

    def is_authenticated(self) -> bool:
        return self.current_user is not None and self.session_token is not None

    def get_remaining_time(self) -> Optional[timedelta]:
        if not self.session_token:
            return None
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT expires_at FROM sessions WHERE token = ?",
                    (self.session_token,)
                )
                row = cursor.fetchone()
                if row:
                    expiry = datetime.fromisoformat(row[0])
                    remaining = expiry - datetime.now()
                    if remaining.total_seconds() > 0:
                        return remaining
        except (sqlite3.Error, ValueError) as e:
            logger.warning(f"Error getting remaining time: {e}")
        return None