# frames/login_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QFrame, QMessageBox, QCheckBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from variables.languages import get_text
from core.theme_manager import ThemeManager
from core.auth_manager import AuthManager
from func.toast_notification import NotificationManager


class LoginFrame(QWidget):
    """فریم ورود به برنامه"""

    login_successful = pyqtSignal()

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
        main_scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #00b4db;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #00ffcc;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        main_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # ========== ویجت محتوای اصلی ==========
        content_widget = QWidget()
        content_widget.setStyleSheet("background: transparent;")
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignCenter)

        # ========== هدر ==========
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel("📚")
        icon_label.setFont(QFont("B Titr", 50))
        icon_label.setStyleSheet("color: #00b4db;")
        header_layout.addWidget(icon_label)

        title_label = QLabel(get_text('app_title'))
        title_label.setFont(QFont("B Titr", 28))
        title_label.setObjectName("loginTitle")
        title_label.setStyleSheet("color: #ffffff; font-weight: bold;")
        header_layout.addWidget(title_label)

        subtitle_label = QLabel(get_text('developer_team'))
        subtitle_label.setFont(QFont("B Titr", 14))
        subtitle_label.setStyleSheet("color: #888888;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        main_layout.addLayout(header_layout)

        # ========== فرم ورود ==========
        form_frame = QFrame()
        form_frame.setObjectName("loginForm")
        form_frame.setFixedWidth(400)
        form_frame.setMinimumHeight(420)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(30, 30, 30, 30)

        # ===== نام کاربری =====
        self.lbl_username = QLabel("👤 " + get_text('username'))
        self.lbl_username.setFont(QFont("B Titr", 14))
        self.lbl_username.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_username)

        self.ent_username = QLineEdit()
        self.ent_username.setFont(QFont("B Titr", 14))
        self.ent_username.setPlaceholderText(get_text('username_placeholder'))
        self.ent_username.setMinimumHeight(40)
        self.ent_username.setObjectName("usernameEntry")
        form_layout.addWidget(self.ent_username)

        # ===== رمز عبور =====
        self.lbl_password = QLabel("🔒 " + get_text('password'))
        self.lbl_password.setFont(QFont("B Titr", 14))
        self.lbl_password.setObjectName("formLabel")
        form_layout.addWidget(self.lbl_password)

        self.ent_password = QLineEdit()
        self.ent_password.setFont(QFont("B Titr", 14))
        self.ent_password.setPlaceholderText(get_text('password_placeholder'))
        self.ent_password.setEchoMode(QLineEdit.Password)
        self.ent_password.setMinimumHeight(40)
        self.ent_password.setObjectName("passwordEntry")
        self.ent_password.returnPressed.connect(self.login)
        form_layout.addWidget(self.ent_password)

        # ===== چک‌باکس Remember Me =====
        self.chk_remember = QCheckBox("🔐 " + get_text('remember_me'))
        self.chk_remember.setFont(QFont("B Titr", 12))
        self.chk_remember.setChecked(True)
        self.chk_remember.setObjectName("rememberCheck")
        form_layout.addWidget(self.chk_remember)

        # ===== دکمه‌ها =====
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)

        self.btn_login = self._create_button(get_text('login'))
        self.btn_login.setFixedSize(150, 45)
        self.btn_login.setObjectName("loginBtn")
        self.btn_login.clicked.connect(self.login)
        button_layout.addWidget(self.btn_login)

        self.btn_guest = self._create_button(get_text('guest_login'))
        self.btn_guest.setFixedSize(150, 45)
        self.btn_guest.setObjectName("guestBtn")
        self.btn_guest.clicked.connect(self.guest_login)
        button_layout.addWidget(self.btn_guest)

        form_layout.addLayout(button_layout)

        # ===== لینک ثبت‌نام =====
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)

        self.lbl_register_hint = QLabel(get_text('no_account'))
        self.lbl_register_hint.setFont(QFont("B Titr", 12))
        self.lbl_register_hint.setObjectName("hintLabel")
        register_layout.addWidget(self.lbl_register_hint)

        self.btn_register = QPushButton(get_text('register'))
        self.btn_register.setFont(QFont("B Titr", 12))
        self.btn_register.setObjectName("linkButton")
        self.btn_register.setCursor(Qt.PointingHandCursor)
        self.btn_register.setStyleSheet("""
            QPushButton#linkButton {
                background: transparent;
                border: none;
                color: #00b4db;
                text-decoration: underline;
                font-size: 12px;
                font-family: 'B Titr';
            }
            QPushButton#linkButton:hover {
                color: #00ffcc;
            }
        """)
        self.btn_register.clicked.connect(lambda: self.parent_app.show_frame('register'))
        register_layout.addWidget(self.btn_register)

        form_layout.addLayout(register_layout)

        main_layout.addWidget(form_frame, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        # ========== تنظیم اسکرول ==========
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
            bg_color = "#00006d"

        # رنگ دکمه‌ها
        button_color = self.theme_manager.get_button_color()

        style = f"""
            QLabel#loginTitle {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 28px;
                font-weight: bold;
            }}
            QFrame#loginForm {{
                background: rgba(0,0,0,0.5);
                border: 2px solid #3a3a4e;
                border-radius: 15px;
            }}
            QLabel#formLabel {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 14px;
                font-weight: bold;
            }}
            QLabel#hintLabel {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 12px;
            }}
            QCheckBox#rememberCheck {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 12px;
                spacing: 8px;
            }}
            QCheckBox#rememberCheck::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {button_color};
                border-radius: 4px;
                background: transparent;
            }}
            QCheckBox#rememberCheck::indicator:checked {{
                background: {button_color};
                border-color: {button_color};
            }}
            QCheckBox#rememberCheck::indicator:hover {{
                border-color: #FFFFFF;
            }}
            QLineEdit#usernameEntry, QLineEdit#passwordEntry {{
                background: rgba(0,0,0,0.6);
                color: {text_color};
                border: 2px solid #3a3a4e;
                border-radius: 8px;
                padding: 10px 15px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QLineEdit#usernameEntry:focus, QLineEdit#passwordEntry:focus {{
                border-color: {button_color};
            }}
            QPushButton#loginBtn, QPushButton#guestBtn {{
                background-color: {button_color};
                color: {text_color};
                border: 2px solid #C0C0C0;
                border-radius: 10px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: bold;
                font-family: 'B Titr';
            }}
            QPushButton#loginBtn:hover, QPushButton#guestBtn:hover {{
                background-color: {self.theme_manager._darken_color(button_color, 20)};
                border-color: #FFFFFF;
            }}
            QPushButton#loginBtn:pressed, QPushButton#guestBtn:pressed {{
                background-color: {self.theme_manager._darken_color(button_color, 40)};
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
                background-color: {button_color};
                border-radius: 4px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme_manager._darken_color(button_color, 20)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها (با استایل جدید)"""
        # استایل از apply_styles استفاده می‌کند
        self.apply_styles()

    def login(self):
        """ورود کاربر"""
        username = self.ent_username.text().strip()
        password = self.ent_password.text().strip()
        remember_me = self.chk_remember.isChecked()

        # اعتبارسنجی
        if not username:
            NotificationManager.warning(self, get_text('enter_username'))
            self.ent_username.setFocus()
            return

        if not password:
            NotificationManager.warning(self, get_text('enter_password'))
            self.ent_password.setFocus()
            return

        # تلاش برای ورود
        success, result = self.auth_manager.login_user(username, password, remember_me)

        if success:
            NotificationManager.success(self, f"{get_text('welcome_back')} {username}!")
            self.login_successful.emit()
            if self.parent_app:
                self.parent_app.show_frame('main')
                self.parent_app.update_user_info()
        else:
            NotificationManager.error(self, result)
            self.ent_password.clear()
            self.ent_password.setFocus()

    def guest_login(self):
        """ورود به عنوان مهمان"""
        success, result = self.auth_manager.login_guest()

        if success:
            NotificationManager.success(self, get_text('guest_welcome'))
            self.login_successful.emit()
            if self.parent_app:
                self.parent_app.show_frame('main')
                self.parent_app.update_user_info()
        else:
            NotificationManager.error(self, get_text('guest_login_error'))

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.lbl_username.setText("👤 " + get_text('username'))
        self.ent_username.setPlaceholderText(get_text('username_placeholder'))
        self.lbl_password.setText("🔒 " + get_text('password'))
        self.ent_password.setPlaceholderText(get_text('password_placeholder'))
        self.chk_remember.setText("🔐 " + get_text('remember_me'))
        self.btn_login.setText(get_text('login'))
        self.btn_guest.setText(get_text('guest_login'))
        self.lbl_register_hint.setText(get_text('no_account'))
        self.btn_register.setText(get_text('register'))

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()

    def keyPressEvent(self, event):
        """رویداد فشردن کلید"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.login()
        elif event.key() == Qt.Key_Escape:
            if self.parent_app:
                self.parent_app.close()
        else:
            super().keyPressEvent(event)

    def showEvent(self, event):
        """رویداد نمایش فریم"""
        super().showEvent(event)
        # تمرکز روی فیلد نام کاربری
        self.ent_username.setFocus()