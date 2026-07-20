# frames/register_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFrame, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from variables.languages import get_text
from core.theme_manager import ThemeManager
from core.auth_manager import AuthManager
from func.toast_notification import NotificationManager


class RegisterFrame(QWidget):
    """فریم ثبت‌نام کاربر جدید"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self.auth_manager = AuthManager()

        self.setup_ui()
        self.apply_styles()
        self.apply_theme()

    def _create_button(self, text):
        """ایجاد دکمه با رنگ فعلی"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 14))
        return btn

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        # ========== اسکرول اصلی ==========
        main_scroll = QScrollArea()
        main_scroll.setWidgetResizable(True)
        main_scroll.setFrameShape(QFrame.NoFrame)
        main_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ویجت محتوای اصلی
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(50, 20, 50, 20)
        main_layout.setSpacing(15)
        main_layout.setAlignment(Qt.AlignCenter)

        # ========== هدر ==========
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("📝")
        icon_label.setFont(QFont("B Titr", 40))
        header_layout.addWidget(icon_label)

        title_label = QLabel(get_text('register_title'))
        title_label.setFont(QFont("B Titr", 24))
        title_label.setObjectName("registerTitle")
        header_layout.addWidget(title_label)

        main_layout.addLayout(header_layout)

        # ========== فرم ثبت‌نام ==========
        form_frame = QFrame()
        form_frame.setObjectName("registerForm")
        form_frame.setFixedWidth(420)
        form_frame.setMinimumHeight(450)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(12)
        form_layout.setContentsMargins(30, 25, 30, 25)

        # نام کامل
        self.lbl_fullname = QLabel("👤 " + get_text('full_name'))
        self.lbl_fullname.setFont(QFont("B Titr", 13))
        self.lbl_fullname.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_fullname)

        self.ent_fullname = QLineEdit()
        self.ent_fullname.setFont(QFont("B Titr", 14))
        self.ent_fullname.setPlaceholderText(get_text('full_name_placeholder'))
        form_layout.addWidget(self.ent_fullname)

        # نام کاربری
        self.lbl_username = QLabel("👤 " + get_text('username'))
        self.lbl_username.setFont(QFont("B Titr", 13))
        self.lbl_username.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_username)

        self.ent_username = QLineEdit()
        self.ent_username.setFont(QFont("B Titr", 14))
        self.ent_username.setPlaceholderText(get_text('username_placeholder'))
        form_layout.addWidget(self.ent_username)



        # رمز عبور
        self.lbl_password = QLabel("🔒 " + get_text('password'))
        self.lbl_password.setFont(QFont("B Titr", 13))
        self.lbl_password.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_password)

        self.ent_password = QLineEdit()
        self.ent_password.setFont(QFont("B Titr", 14))
        self.ent_password.setPlaceholderText(get_text('password_placeholder'))
        self.ent_password.setEchoMode(QLineEdit.Password)
        form_layout.addWidget(self.ent_password)

        # تکرار رمز عبور
        self.lbl_confirm = QLabel("🔒 " + get_text('confirm_password'))
        self.lbl_confirm.setFont(QFont("B Titr", 13))
        self.lbl_confirm.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_confirm)

        self.ent_confirm = QLineEdit()
        self.ent_confirm.setFont(QFont("B Titr", 14))
        self.ent_confirm.setPlaceholderText(get_text('confirm_password_placeholder'))
        self.ent_confirm.setEchoMode(QLineEdit.Password)
        self.ent_confirm.returnPressed.connect(self.register)
        form_layout.addWidget(self.ent_confirm)

        # دکمه‌ها
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.btn_register = self._create_button(get_text('register'))
        self.btn_register.setFixedSize(150, 45)
        self.btn_register.clicked.connect(self.register)
        button_layout.addWidget(self.btn_register)

        self.btn_back = self._create_button(get_text('back'))
        self.btn_back.setFixedSize(150, 45)
        self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('login'))
        button_layout.addWidget(self.btn_back)

        form_layout.addLayout(button_layout)

        main_layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        # تنظیم اسکرول
        main_scroll.setWidget(content_widget)

        # ========== لایه‌بندی نهایی ==========
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0, 0, 0, 0)
        final_layout.addWidget(main_scroll)

    def apply_styles(self):
        """اعمال استایل"""
        bg_color = self.theme_manager.get_background_color()
        if bg_color:
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
        else:
            text_color = '#FFFFFF'

        style = f"""
            QLabel#registerTitle {{
                color: {text_color};
                font-family: 'B Titr';
            }}
            QFrame#registerForm {{
                background: rgba(0,0,0,0.4);
                border: 2px solid #3a3a4e;
                border-radius: 15px;
            }}
            QLabel#formLabel {{
                color: {text_color};
                font-family: 'B Titr';
            }}
            QLineEdit {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid #00b4db;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: #00ffcc;
            }}
            QScrollArea {{
                background: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #00b4db;
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #00ffcc;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in [self.btn_register, self.btn_back]:
            btn.setStyleSheet(style)

    def register(self):
        """ثبت‌نام کاربر"""
        username = self.ent_username.text().strip()
        password = self.ent_password.text().strip()
        confirm = self.ent_confirm.text().strip()
        full_name = self.ent_fullname.text().strip()

        # اعتبارسنجی
        if not username or len(username) < 3:
            NotificationManager.warning(self, get_text('username_min_length'))
            return

        if not password or len(password) < 4:
            NotificationManager.warning(self, get_text('password_min_length'))
            return

        if password != confirm:
            NotificationManager.warning(self, get_text('password_mismatch'))
            return

        # ثبت‌نام
        success, result = self.auth_manager.register_user(username, password, None, full_name)

        if success:
            NotificationManager.success(self, f"{get_text('register_success')} {username}!")
            self.parent_app.show_frame('login')
        else:
            NotificationManager.error(self, result)

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.lbl_fullname.setText("👤 " + get_text('full_name'))
        self.ent_fullname.setPlaceholderText(get_text('full_name_placeholder'))
        self.lbl_username.setText("👤 " + get_text('username'))
        self.ent_username.setPlaceholderText(get_text('username_placeholder'))
        self.lbl_password.setText("🔒 " + get_text('password'))
        self.ent_password.setPlaceholderText(get_text('password_placeholder'))
        self.lbl_confirm.setText("🔒 " + get_text('confirm_password'))
        self.ent_confirm.setPlaceholderText(get_text('confirm_password_placeholder'))
        self.btn_register.setText(get_text('register'))
        self.btn_back.setText(get_text('back'))

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()