# core/theme_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import json
import os
import logging
import threading
from typing import Optional

from variables.constants import CONFIG_FILE, DEFAULT_WIDGET_COLOR, DEFAULT_LANGUAGE

logger = logging.getLogger(__name__)


class ThemeManager:
    """مدیریت تم با قفل خواندن/نوشتن برای جلوگیری از race condition"""

    def __init__(self):
        self.config_file = CONFIG_FILE
        self._lock = threading.RLock()
        self._button_color = DEFAULT_WIDGET_COLOR
        self._background_color: Optional[str] = None
        self._language = DEFAULT_LANGUAGE
        self._text_color = '#FFFFFF'
        self._load_config()

    def _load_config(self) -> None:
        """بارگذاری تنظیمات از فایل config.json"""
        with self._lock:
            try:
                if os.path.exists(self.config_file):
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        self._button_color = config.get('button_color', DEFAULT_WIDGET_COLOR)
                        self._background_color = config.get('background_color')
                        self._language = config.get('language', DEFAULT_LANGUAGE)
            except (OSError, json.JSONDecodeError) as e:
                logger.warning(f"Could not load config, using defaults: {e}")

    def _save_config(self) -> None:
        with self._lock:
            try:
                config = {
                    'button_color': self._button_color,
                    'background_color': self._background_color,
                    'language': self._language
                }
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, ensure_ascii=False, indent=2)
            except OSError as e:
                logger.error(f"Could not save config: {e}")

    def set_button_color(self, color: str) -> None:
        with self._lock:
            self._button_color = color
            self._save_config()

    def get_button_color(self) -> str:
        with self._lock:
            return self._button_color

    def set_background_color(self, color: str) -> None:
        with self._lock:
            self._background_color = color
            self._save_config()

    def get_background_color(self) -> Optional[str]:
        with self._lock:
            return self._background_color

    def set_language(self, lang: str) -> None:
        with self._lock:
            self._language = lang
            self._save_config()

    def get_language(self) -> str:
        with self._lock:
            return self._language

    def set_text_color(self, color: str) -> None:
        with self._lock:
            self._text_color = color

    def get_text_color(self) -> str:
        with self._lock:
            return self._text_color

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return (0, 0, 0)
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    @staticmethod
    def _get_luminance(hex_color: str) -> float:
        rgb = ThemeManager._hex_to_rgb(hex_color)
        return (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255

    def get_text_color_for_background(self, bg_color: str) -> str:
        luminance = self._get_luminance(bg_color)
        return '#000000' if luminance > 0.5 else '#FFFFFF'

    def get_button_style(self, color: Optional[str] = None) -> str:
        c = color or self._button_color
        text_color = self.get_text_color_for_background(c)
        return f"""
            QPushButton {{
                background-color: {c};
                color: {text_color};
                border: 2px solid #C0C0C0;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'B Titr';
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(c, 20)};
                border-color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: {self._darken_color(c, 40)};
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
                border-color: #666666;
            }}
            QPushButton:checked {{
                background-color: {self._darken_color(c, 30)};
                border-color: #FFD700;
            }}
        """

    @staticmethod
    def _darken_color(hex_color: str, amount: int) -> str:
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return hex_color
        r = max(0, int(hex_color[0:2], 16) - amount)
        g = max(0, int(hex_color[2:4], 16) - amount)
        b = max(0, int(hex_color[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"