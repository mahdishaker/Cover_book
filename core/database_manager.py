# core/database_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import sqlite3
import os
import logging
from datetime import datetime
from contextlib import closing
from typing import Optional, List, Dict, Any

from variables.constants import HERE

logger = logging.getLogger(__name__)


class DatabaseManager:
    """مدیریت دیتابیس اصلی برنامه با context manager"""

    def __init__(self):
        self.db_path = os.path.join(HERE, 'CB_data/app_data.db')
        self._init_db()

    def _init_db(self) -> None:
        """ایجاد جداول مورد نیاز"""
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS feedbacks (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        rating INTEGER NOT NULL,
                        comment TEXT,
                        suggestions TEXT,
                        created_at TEXT NOT NULL,
                        cover_type TEXT,
                        sent_to_server BOOLEAN DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS cover_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        cover_type TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        duration INTEGER,
                        success BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        user_id INTEGER PRIMARY KEY,
                        theme_color TEXT,
                        language TEXT,
                        auto_play_tutorial BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def add_feedback(self, user_id: Optional[int], rating: int,
                     comment: str = '', suggestions: str = '',
                     cover_type: str = '') -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO feedbacks (user_id, rating, comment, suggestions, created_at, cover_type) "
                    "VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, rating, comment, suggestions, datetime.now().isoformat(), cover_type)
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding feedback: {e}")
            return False

    def get_feedbacks(self, user_id: Optional[int] = None, limit: int = 100) -> List[tuple]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute(
                        "SELECT * FROM feedbacks WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                        (user_id, limit)
                    )
                else:
                    cursor.execute("SELECT * FROM feedbacks ORDER BY created_at DESC LIMIT ?", (limit,))
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting feedbacks: {e}")
            return []

    def add_cover_stat(self, user_id: Optional[int], cover_type: str,
                       duration: int, success: bool = True) -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO cover_stats (user_id, cover_type, created_at, duration, success) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (user_id, cover_type, datetime.now().isoformat(), duration, success)
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error adding cover stat: {e}")
            return False

    def get_cover_stats(self, user_id: Optional[int] = None) -> List[tuple]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                if user_id:
                    cursor.execute(
                        "SELECT cover_type, COUNT(*) as count, AVG(duration) as avg_duration "
                        "FROM cover_stats WHERE user_id = ? GROUP BY cover_type",
                        (user_id,)
                    )
                else:
                    cursor.execute(
                        "SELECT cover_type, COUNT(*) as count, AVG(duration) as avg_duration "
                        "FROM cover_stats GROUP BY cover_type"
                    )
                return cursor.fetchall()
        except sqlite3.Error as e:
            logger.error(f"Error getting cover stats: {e}")
            return []

    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT theme_color, language, auto_play_tutorial FROM user_preferences WHERE user_id = ?",
                    (user_id,)
                )
                row = cursor.fetchone()
                if row:
                    return {
                        'theme_color': row[0],
                        'language': row[1],
                        'auto_play_tutorial': bool(row[2])
                    }
        except sqlite3.Error as e:
            logger.error(f"Error getting user preferences: {e}")
        return None

    def save_user_preferences(self, user_id: int, theme_color: Optional[str] = None,
                              language: Optional[str] = None,
                              auto_play_tutorial: Optional[bool] = None) -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                current = self.get_user_preferences(user_id)
                if current:
                    cursor.execute(
                        "UPDATE user_preferences SET theme_color = COALESCE(?, theme_color), "
                        "language = COALESCE(?, language), auto_play_tutorial = COALESCE(?, auto_play_tutorial) "
                        "WHERE user_id = ?",
                        (theme_color, language, auto_play_tutorial, user_id)
                    )
                else:
                    cursor.execute(
                        "INSERT INTO user_preferences (user_id, theme_color, language, auto_play_tutorial) "
                        "VALUES (?, ?, ?, ?)",
                        (user_id, theme_color, language, auto_play_tutorial)
                    )
                conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Error saving user preferences: {e}")
            return False