# frames/theme_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QFrame, QColorDialog, QGridLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from variables.languages import get_text, get_current_language
from core.theme_manager import ThemeManager
from func.toast_notification import NotificationManager


class ThemeFrame(QWidget):
    """فریم تنظیمات تم و زبان"""

    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self._updating_language = False
        self._first_show = True

        self.setup_ui()
        self.apply_styles()
        self.apply_theme()

    def _create_button(self, text):
        """ایجاد دکمه با رنگ فعلی"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 14))
        return btn

    def _create_fixed_color_button(self, color):
        """ایجاد دکمه رنگ ثابت"""
        btn = QPushButton()
        btn.setFixedSize(80, 50)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setProperty("colorButton", True)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 3px solid #C0C0C0;
                border-radius: 12px;
            }}
            QPushButton:hover {{
                border-color: #FFFFFF;
                border-width: 3px;
            }}
            QPushButton:pressed {{
                border-color: #FFD700;
                border-width: 4px;
            }}
        """)
        btn.setToolTip(f"{color}")
        return btn

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        # ========== هدر ==========
        header_layout = QHBoxLayout()

        self.btn_back = self._create_button(get_text('back'))
        self.btn_back.setFixedSize(80, 40)
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('main'))
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        self.lbl_title = QLabel(get_text('theme_button'))
        self.lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()

        self.btn_guide = self._create_button(get_text('guide_button'))
        self.btn_guide.setFixedSize(80, 40)
        self.btn_guide.setToolTip(get_text('guide_tooltip'))
        self.btn_guide.clicked.connect(self.show_guide)
        header_layout.addWidget(self.btn_guide)

        layout.addLayout(header_layout)

        # ========== کومبو باکس زبان ==========
        lang_layout = QHBoxLayout()
        lang_layout.setAlignment(Qt.AlignCenter)

        self.lbl_language = QLabel(get_text('language') + ":")
        self.lbl_language.setObjectName("langLabel")
        lang_layout.addWidget(self.lbl_language)

        self.cmb_language = QComboBox()
        self.cmb_language.setFixedWidth(160)
        self.cmb_language.setToolTip(get_text('language_tooltip'))

        # پر کردن آیتم‌ها با نام‌های ثابت
        self.cmb_language.addItems(['فارسی', 'English', 'العربية'])

        current_lang = get_current_language()
        lang_map = {'persian': 0, 'english': 1, 'arabic': 2}
        self.cmb_language.setCurrentIndex(lang_map.get(current_lang, 0))

        self.cmb_language.currentIndexChanged.connect(self.on_language_changed)
        lang_layout.addWidget(self.cmb_language)

        layout.addLayout(lang_layout)

        # ========== ۹ دکمه رنگ ثابت ==========
        gradient_colors = [
            '#FF6B6B', '#FF9F43', '#FECA57',
            '#00B894', '#00CEC9', '#0984E3',
            '#6C5CE7', '#FD79A8', '#FDCB6E',
        ]

        colors_layout = QGridLayout()
        colors_layout.setSpacing(12)
        colors_layout.setAlignment(Qt.AlignCenter)

        for i, color in enumerate(gradient_colors):
            btn = self._create_fixed_color_button(color)
            btn.clicked.connect(lambda checked, c=color: self.select_button_color(c))
            row = i // 3
            col = i % 3
            colors_layout.addWidget(btn, row, col)

        layout.addLayout(colors_layout)

        # ========== دکمه رنگ‌های دیگر ==========
        other_color_layout = QHBoxLayout()
        other_color_layout.setAlignment(Qt.AlignCenter)

        self.btn_other_color = self._create_button(get_text('other_colors'))
        self.btn_other_color.setFixedSize(200, 45)
        self.btn_other_color.setToolTip(get_text('other_colors_tooltip'))
        self.btn_other_color.clicked.connect(self.select_other_color)
        other_color_layout.addWidget(self.btn_other_color)

        layout.addLayout(other_color_layout)

        # ========== دکمه رنگ پس‌زمینه ==========
        bg_layout = QHBoxLayout()
        bg_layout.setAlignment(Qt.AlignCenter)

        self.btn_background = self._create_button(get_text('background_color'))
        self.btn_background.setFixedSize(200, 45)
        self.btn_background.setToolTip(get_text('background_tooltip'))
        self.btn_background.clicked.connect(self.select_background_color)
        bg_layout.addWidget(self.btn_background)

        layout.addLayout(bg_layout)

        layout.addStretch()

    def apply_styles(self):
        """اعمال استایل"""
        bg_color = self.theme_manager.get_background_color()
        if bg_color:
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
        else:
            text_color = '#FFFFFF'

        style = f"""
            QLabel#pageTitle {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 24px;
                font-weight: bold;
            }}
            QLabel#langLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 14px;
                font-weight: bold;
            }}
            QComboBox {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid #00b4db;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B titr';
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                color: {text_color};
                selection-background-color: #00b4db;
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in self.findChildren(QPushButton):
            if not btn.property("colorButton"):
                btn.setStyleSheet(style)

    def update_text_colors(self, text_color):
        """به‌روزرسانی رنگ متون بر اساس پس‌زمینه"""
        self.lbl_title.setStyleSheet(f"""
            QLabel#pageTitle {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 24px;
                font-weight: bold;
            }}
        """)

        self.lbl_language.setStyleSheet(f"""
            QLabel#langLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 14px;
                font-weight: bold;
            }}
        """)

        color = self.theme_manager.get_button_color()
        self.cmb_language.setStyleSheet(f"""
            QComboBox {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B titr';
                font-size: 13px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                color: {text_color};
                selection-background-color: {color};
            }}
        """)

    def select_button_color(self, color):
        """انتخاب رنگ برای دکمه‌ها"""
        self.parent_app.change_button_color(color)
        self.apply_theme()
        NotificationManager.success(self, f"{get_text('theme_button')} {get_text('changed')}")

    def select_other_color(self):
        """انتخاب رنگ سفارشی"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent_app.change_button_color(color.name())
            self.apply_theme()
            NotificationManager.success(self, f"{get_text('theme_button')} {get_text('changed')}")

    def select_background_color(self):
        """انتخاب رنگ پس‌زمینه"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.parent_app.change_background_color(color.name())
            NotificationManager.success(self, f"{get_text('background_color')} {get_text('changed')}")

    def on_language_changed(self, index):
        """تغییر زبان"""
        if self._updating_language:
            return

        self._updating_language = True

        try:
            lang_map = {0: 'persian', 1: 'english', 2: 'arabic'}
            lang_code = lang_map.get(index, 'persian')
            self.parent_app.change_language(lang_code)
            self.parent_app.show_frame('main')
            NotificationManager.success(self, f"{get_text('language')} {get_text('changed')}")
        except Exception as e:
            print(f"Error changing language: {e}")
        finally:
            self._updating_language = False

    def show_guide(self):
        """نمایش راهنما"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self,
            get_text('theme_guide_title'),
            get_text('theme_guide_message'),
            QMessageBox.Ok
        )

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        if self._updating_language:
            return

        # به‌روزرسانی متن دکمه‌ها و لیبل‌ها
        self.btn_back.setText(get_text('back'))
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.lbl_title.setText(get_text('theme_button'))
        self.btn_other_color.setText(get_text('other_colors'))
        self.btn_other_color.setToolTip(get_text('other_colors_tooltip'))
        self.btn_background.setText(get_text('background_color'))
        self.btn_background.setToolTip(get_text('background_tooltip'))
        self.btn_guide.setText(get_text('guide_button'))
        self.btn_guide.setToolTip(get_text('guide_tooltip'))
        self.lbl_language.setText(get_text('language') + ":")

        # به‌روزرسانی ایندکس کامبوباکس بدون ایجاد سیگنال
        current_lang = get_current_language()
        lang_map = {'persian': 0, 'english': 1, 'arabic': 2}
        target_index = lang_map.get(current_lang, 0)

        if self.cmb_language.currentIndex() != target_index:
            self.cmb_language.blockSignals(True)
            self.cmb_language.setCurrentIndex(target_index)
            self.cmb_language.blockSignals(False)

        # به‌روزرسانی استایل
        self.apply_styles()
        self.apply_theme()

    def showEvent(self, event):
        """هنگام نمایش فریم - متن‌ها را به‌روز می‌کند"""
        super().showEvent(event)
        # با تاخیر کوچک برای اطمینان از آماده بودن ویجت‌ها
        QTimer.singleShot(50, self.update_texts)

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()