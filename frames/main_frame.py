# frames/main_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from variables.languages import get_text
from core.theme_manager import ThemeManager


class MainFrame(QWidget):
    """فریم اصلی برنامه"""

    frame_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self.setup_ui()

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # ========== دکمه‌های بالایی ==========
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_history = self._create_button(get_text('history_button'))
        self.btn_history.setFixedSize(80, 40)
        self.btn_history.setToolTip(get_text('history_tooltip'))
        self.btn_history.clicked.connect(lambda: self.parent_app.show_frame('history'))
        top_layout.addWidget(self.btn_history)

        top_layout.addStretch()

        self.btn_theme = self._create_button(get_text('theme_button'))
        self.btn_theme.setFixedSize(80, 40)
        self.btn_theme.setToolTip(get_text('theme_tooltip'))
        self.btn_theme.clicked.connect(lambda: self.parent_app.show_frame('theme'))
        top_layout.addWidget(self.btn_theme)

        layout.addLayout(top_layout)

        # ========== دکمه راهنما ==========
        help_layout = QHBoxLayout()
        help_layout.addStretch()

        self.btn_guide = self._create_button(get_text('guide_button'))
        self.btn_guide.setFixedSize(200, 40)
        self.btn_guide.setToolTip(get_text('guide_tooltip'))
        self.btn_guide.clicked.connect(self.show_shortcuts_help)
        help_layout.addWidget(self.btn_guide)

        help_layout.addStretch()
        layout.addLayout(help_layout)

        # ========== دکمه اصلی پایان‌نامه ==========
        main_btn_layout = QVBoxLayout()
        main_btn_layout.setAlignment(Qt.AlignCenter)

        self.btn_dissertation = self._create_button(get_text('dissertation_cover'))
        self.btn_dissertation.setFixedSize(220, 200)
        self.btn_dissertation.setToolTip(get_text('dissertation_tooltip'))
        self.btn_dissertation.clicked.connect(lambda: self.parent_app.show_frame('dissertation'))
        main_btn_layout.addWidget(self.btn_dissertation, alignment=Qt.AlignCenter)

        layout.addLayout(main_btn_layout)

        # ========== دکمه‌های غیرفعال ==========
        inactive_layout = QHBoxLayout()
        inactive_layout.setSpacing(15)
        inactive_layout.setAlignment(Qt.AlignCenter)

        inactive_buttons = [
            ('gilded_book_cover', 'inactive_frame'),
            ('notebook_cover', 'inactive_frame'),
            ('book_cover', 'inactive_frame')
        ]

        for text_key, tooltip_key in inactive_buttons:
            btn = self._create_button(get_text(text_key))
            btn.setFixedSize(150, 100)
            btn.setEnabled(False)
            btn.setToolTip(get_text(tooltip_key))
            inactive_layout.addWidget(btn)

        layout.addLayout(inactive_layout)

        # ========== دکمه‌های پایینی ==========
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        bottom_layout.setAlignment(Qt.AlignCenter)

        self.btn_other = self._create_button(get_text('other_programs'))
        self.btn_other.setFixedSize(160, 50)
        self.btn_other.setToolTip(get_text('other_tooltip'))
        self.btn_other.clicked.connect(lambda: self.parent_app.show_frame('other_programs'))
        bottom_layout.addWidget(self.btn_other)

        self.btn_about = self._create_button(get_text('about_button'))
        self.btn_about.setFixedSize(90, 50)
        self.btn_about.setToolTip(get_text('about_tooltip'))
        self.btn_about.clicked.connect(self.show_about)
        bottom_layout.addWidget(self.btn_about)

        self.btn_update = self._create_button(get_text('check_update'))
        self.btn_update.setFixedSize(160, 50)
        self.btn_update.setToolTip(get_text('update_tooltip'))
        self.btn_update.clicked.connect(lambda: self.parent_app.show_frame('update'))
        bottom_layout.addWidget(self.btn_update)

        layout.addLayout(bottom_layout)

        # اعمال رنگ
        self.apply_theme()

    def _create_button(self, text):
        """ایجاد دکمه با رنگ فعلی"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 12))
        # برای دکمه‌هایی که چند خطی هستند، از \n در متن استفاده می‌کنیم
        # و اندازه دکمه را تنظیم می‌کنیم
        return btn

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in self.findChildren(QPushButton):
            if btn is not self.parent_app.findChild(QPushButton, "menuBtn") and \
                    btn is not self.parent_app.findChild(QPushButton, "minBtn") and \
                    btn is not self.parent_app.findChild(QPushButton, "closeBtn") and \
                    btn is not self.parent_app.findChild(QPushButton, "logoutBtn"):
                btn.setStyleSheet(style)

    def show_about(self):
        """نمایش درباره ما"""
        from frames.about_frame import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()

    def show_shortcuts_help(self):
        """نمایش راهنمای میانبرها"""
        from PyQt5.QtWidgets import QMessageBox
        from variables.shortcuts import get_shortcuts_text

        msg = QMessageBox(self)
        msg.setWindowTitle(get_text('keyboard_shortcuts'))
        msg.setText(get_shortcuts_text())
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
            }
            QMessageBox QLabel {
                color: white;
                font-family: 'B titr';
                font-size: 12px;
            }
            QMessageBox QPushButton {
                background: #00b4db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 20px;
            }
        """)
        msg.exec_()

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.btn_history.setText(get_text('history_button'))
        self.btn_history.setToolTip(get_text('history_tooltip'))
        self.btn_theme.setText(get_text('theme_button'))
        self.btn_theme.setToolTip(get_text('theme_tooltip'))
        self.btn_guide.setText(get_text('guide_button'))
        self.btn_guide.setToolTip(get_text('guide_tooltip'))
        self.btn_dissertation.setText(get_text('dissertation_cover'))
        self.btn_dissertation.setToolTip(get_text('dissertation_tooltip'))
        self.btn_other.setText(get_text('other_programs'))
        self.btn_other.setToolTip(get_text('other_tooltip'))
        self.btn_update.setText(get_text('check_update'))
        self.btn_update.setToolTip(get_text('update_tooltip'))
        self.btn_about.setText(get_text('about_button'))
        self.btn_about.setToolTip(get_text('about_tooltip'))

        # به‌روزرسانی دکمه‌های غیرفعال
        inactive_texts = ['gilded_book_cover', 'notebook_cover', 'book_cover']
        idx = 0
        for btn in self.findChildren(QPushButton):
            if not btn.isEnabled() and btn not in [self.parent_app.findChild(QPushButton, "menuBtn"),
                                                   self.parent_app.findChild(QPushButton, "minBtn"),
                                                   self.parent_app.findChild(QPushButton, "closeBtn"),
                                                   self.parent_app.findChild(QPushButton, "logoutBtn")]:
                if idx < len(inactive_texts):
                    btn.setText(get_text(inactive_texts[idx]))
                    btn.setToolTip(get_text('inactive_frame'))
                    idx += 1

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()