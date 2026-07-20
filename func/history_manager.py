# func/history_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import json
import sqlite3
import shutil
import subprocess
import logging
from datetime import datetime
from contextlib import closing
from typing import List, Dict, Any, Optional

from variables.constants import HISTORY_PATH, HISTORY_FILE

logger = logging.getLogger(__name__)


class HistoryManager:
    """مدیریت تاریخچه با دیتابیس SQLite و context manager"""

    def __init__(self):
        self.db_path = HISTORY_FILE
        self.history_path = HISTORY_PATH
        self._ensure_folders()
        self._init_db()

    def _ensure_folders(self) -> None:
        os.makedirs(self.history_path, exist_ok=True)

    def _init_db(self) -> None:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS history (
                        id TEXT PRIMARY KEY,
                        original_name TEXT NOT NULL,
                        history_file TEXT NOT NULL,
                        history_path TEXT NOT NULL,
                        save_path TEXT,
                        date_added TEXT NOT NULL,
                        metadata TEXT
                    )
                ''')
                conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Error initializing history DB: {e}")
            raise

    def add_to_history(self, file_info: Dict[str, Any]) -> bool:
        """
        افزودن فایل به تاریخچه با بررسی کامل وجود فایل و مسیر
        بازگشت True در صورت موفقیت، False در صورت خطا
        """
        try:
            src = file_info.get('save_path')
            if not src:
                logger.error("No save_path provided in file_info")
                return False

            if not os.path.exists(src):
                parent_dir = os.path.dirname(src)
                logger.warning(
                    f"Source file not found: {src}. "
                    f"Parent dir exists: {os.path.exists(parent_dir) if parent_dir else 'N/A'}, "
                    f"Parent dir is dir: {os.path.isdir(parent_dir) if parent_dir else 'N/A'}"
                )
                return False

            if not os.path.isfile(src):
                logger.warning(f"Path is not a file: {src}")
                return False

            # بررسی فضای خالی دیسک (اختیاری)
            try:
                file_size = os.path.getsize(src)
                if file_size == 0:
                    logger.warning(f"Source file is empty: {src}")
                    return False
            except OSError as e:
                logger.warning(f"Could not get file size: {e}")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = os.path.basename(src)
            history_file = f"{timestamp}_{file_name}"
            history_full_path = os.path.join(self.history_path, history_file)

            # کپی فایل
            try:
                shutil.copy2(src, history_full_path)
                logger.info(f"Copied to history: {history_full_path}")
            except (shutil.Error, OSError) as e:
                logger.error(f"Failed to copy file to history: {e}")
                return False

            # ذخیره متادیتا
            metadata_json = json.dumps(file_info.get('metadata', {}), ensure_ascii=False)

            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO history (id, original_name, history_file, history_path, save_path, date_added, metadata) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (timestamp, file_name, history_file, history_full_path, src,
                     datetime.now().strftime("%Y-%m-%d %H:%M"), metadata_json)
                )
                conn.commit()
            return True

        except (sqlite3.Error, json.JSONEncodeError) as e:
            logger.exception(f"Database error in add_to_history: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error in add_to_history: {e}")
            return False

    def load_history(self) -> List[Dict[str, Any]]:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT id, original_name, history_file, history_path, save_path, date_added, metadata "
                    "FROM history ORDER BY date_added DESC"
                )
                rows = cursor.fetchall()
                history = []
                for row in rows:
                    metadata = {}
                    if row[6]:
                        try:
                            metadata = json.loads(row[6])
                        except json.JSONDecodeError:
                            logger.warning(f"Invalid JSON in metadata for {row[0]}")
                    history.append({
                        'id': row[0],
                        'original_name': row[1],
                        'history_file': row[2],
                        'history_path': row[3],
                        'save_path': row[4],
                        'date_added': row[5],
                        'metadata': metadata
                    })
                return history
        except sqlite3.Error as e:
            logger.error(f"Error loading history: {e}")
            return []

    def remove_from_history(self, item_id: str) -> bool:
        try:
            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT history_file FROM history WHERE id = ?", (item_id,))
                row = cursor.fetchone()
                if row:
                    file_path = os.path.join(self.history_path, row[0])
                    if os.path.exists(file_path):
                        try:
                            os.remove(file_path)
                            logger.info(f"Removed history file: {file_path}")
                        except OSError as e:
                            logger.warning(f"Could not remove history file: {e}")
                    cursor.execute("DELETE FROM history WHERE id = ?", (item_id,))
                    conn.commit()
                    return True
            return False
        except (sqlite3.Error, OSError) as e:
            logger.error(f"Error removing from history: {e}")
            return False

    def clear_all_history(self) -> bool:
        try:
            items = self.load_history()
            for item in items:
                file_path = os.path.join(self.history_path, item['history_file'])
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

            with closing(sqlite3.connect(self.db_path)) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()
            logger.info("All history cleared")
            return True
        except (sqlite3.Error, OSError) as e:
            logger.error(f"Error clearing history: {e}")
            return False

    @staticmethod
    def open_file_location(item: Dict[str, Any]) -> bool:
        """باز کردن مسیر فایل در File Explorer"""
        folder = None
        save_path = item.get('save_path')
        history_path = item.get('history_path')
        if save_path and os.path.exists(save_path):
            folder = os.path.dirname(save_path)
        elif history_path and os.path.exists(history_path):
            folder = os.path.dirname(history_path)
        if folder and os.path.exists(folder):
            try:
                subprocess.Popen(['explorer', os.path.normpath(folder)])
                return True
            except Exception as e:
                logger.error(f"Could not open location: {e}")
        return False

    @staticmethod
    def open_file(item: Dict[str, Any]) -> bool:
        """باز کردن فایل با برنامه پیش‌فرض"""
        file_to_open = None
        save_path = item.get('save_path')
        history_path = item.get('history_path')
        if save_path and os.path.exists(save_path):
            file_to_open = save_path
        elif history_path and os.path.exists(history_path):
            file_to_open = history_path
        if file_to_open:
            try:
                subprocess.Popen(['explorer', os.path.normpath(file_to_open)])
                return True
            except Exception as e:
                logger.error(f"Could not open file: {e}")
        return False