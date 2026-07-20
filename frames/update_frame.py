# frames/update_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import threading
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from func.github_manager import GitHubManager
from func.toast_notification import NotificationManager
from variables.languages import get_text
from core.theme_manager import ThemeManager


class UpdateFrame(QWidget):
    """فریم بروزرسانی"""

    # سیگنال برای به‌روزرسانی ایمن UI از تردهای دیگه
    update_signal = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self.github_manager = GitHubManager()

        # اتصال سیگنال به تابع به‌روزرسانی UI
        self.update_signal.connect(self._safe_update_ui)

        self.setup_ui()
        self.apply_styles()
        self.apply_theme()
        self.load_initial_info()

    def _create_button(self, text):
        """ایجاد دکمه با رنگ فعلی"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 14))
        return btn

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ========== هدر ==========
        header_layout = QHBoxLayout()

        self.btn_back = self._create_button(get_text('back'))
        self.btn_back.setFixedSize(80, 40)
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('main'))
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        self.lbl_title = QLabel(get_text('update_title'))
        self.lbl_title.setFont(QFont("B Titr", 24))
        self.lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # ========== اطلاعات نسخه ==========
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)
        info_layout.setAlignment(Qt.AlignCenter)

        self.lbl_current_version = QLabel(get_text('current_version_checking'))
        self.lbl_current_version.setFont(QFont("B Titr", 16))
        self.lbl_current_version.setObjectName("versionLabel")
        info_layout.addWidget(self.lbl_current_version)

        self.lbl_latest_version = QLabel(get_text('latest_version_checking'))
        self.lbl_latest_version.setFont(QFont("B Titr", 16))
        self.lbl_latest_version.setObjectName("versionLabel")
        info_layout.addWidget(self.lbl_latest_version)

        self.lbl_status = QLabel('')
        self.lbl_status.setFont(QFont("B Titr", 14))
        self.lbl_status.setObjectName("statusLabel")
        info_layout.addWidget(self.lbl_status)

        layout.addLayout(info_layout)

        # ========== نوار پیشرفت ==========
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setFont(QFont("B Titr", 10))
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #2a2a2a;
                border: 2px solid #3a3a4e;
                border-radius: 8px;
                text-align: center;
                color: white;
                height: 20px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4db, stop:1 #00ffcc);
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)

        # ========== دکمه‌ها ==========
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.setAlignment(Qt.AlignCenter)

        self.btn_check = self._create_button(get_text('check_update'))
        self.btn_check.setFixedSize(200, 50)
        self.btn_check.clicked.connect(self.check_update)
        button_layout.addWidget(self.btn_check)

        self.btn_update = self._create_button(get_text('start_update'))
        self.btn_update.setFixedSize(200, 50)
        self.btn_update.setVisible(False)
        self.btn_update.clicked.connect(self.start_update)
        button_layout.addWidget(self.btn_update)

        layout.addLayout(button_layout)
        layout.addStretch()

        # اعمال تم اولیه
        self.apply_theme()

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
                font-family: 'B Titr';
                font-size: 24px;
            }}
            QLabel#versionLabel {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 16px;
            }}
            QLabel#statusLabel {{
                color: #FFD700;
                font-family: 'B Titr';
                font-size: 14px;
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in [self.btn_back, self.btn_check, self.btn_update]:
            if btn:
                btn.setStyleSheet(style)

    def update_text_colors(self, text_color):
        """به‌روزرسانی رنگ متون بر اساس پس‌زمینه"""
        self.lbl_title.setStyleSheet(f"""
            QLabel#pageTitle {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 24px;
            }}
        """)

        for label in [self.lbl_current_version, self.lbl_latest_version]:
            label.setStyleSheet(f"""
                QLabel#versionLabel {{
                    color: {text_color};
                    font-family: 'B Titr';
                    font-size: 16px;
                }}
            """)

        self.lbl_status.setStyleSheet(f"""
            QLabel#statusLabel {{
                color: #FFD700;
                font-family: 'B Titr';
                font-size: 14px;
            }}
        """)

    def load_initial_info(self):
        """بارگذاری اطلاعات اولیه"""
        current_version = self.github_manager.get_current_version()
        if current_version:
            self.lbl_current_version.setText(f"{get_text('current_version')}: {current_version}")
        else:
            self.lbl_current_version.setText(get_text('current_version_unknown'))

    def check_update(self):
        """بررسی بروزرسانی"""
        # غیرفعال کردن دکمه
        self.btn_check.setEnabled(False)
        self.btn_check.setText(get_text('checking'))

        # تنظیم وضعیت اولیه
        self.lbl_status.setText(get_text('connecting_github'))
        self.lbl_status.setStyleSheet("color: #FFD700; font-family: 'B Titr'; font-size: 14px;")
        self.lbl_latest_version.setText(get_text('latest_version_checking'))

        # اجباری به‌روزرسانی UI
        QApplication.processEvents()

        def check():
            try:
                result = self.github_manager.check_update()

                # ارسال نتیجه به ترد اصلی از طریق سیگنال
                self.update_signal.emit(result)

            except Exception as e:
                print(f"Error in check thread: {e}")
                # ارسال خطا به ترد اصلی
                self.update_signal.emit({'error': True, 'message': str(e)})

        # اجرا در ترد جداگانه
        threading.Thread(target=check, daemon=True).start()

    def _safe_update_ui(self, result):
        """به‌روزرسانی ایمن UI از ترد اصلی (با سیگنال)"""

        # فعال کردن دکمه
        self.btn_check.setEnabled(True)
        self.btn_check.setText(get_text('check_again'))

        # دریافت نسخه‌ها
        current = result.get('current', 'نامشخص')
        latest = result.get('latest', 'نامشخص')

        # به‌روزرسانی لیبل‌ها
        self.lbl_current_version.setText(f"{get_text('current_version')}: {current}")
        self.lbl_latest_version.setText(f"{get_text('latest_version')}: {latest}")

        # مدیریت خطا
        if result.get('error', False):
            error_msg = result.get('message', get_text('github_connection_error'))
            self.lbl_status.setText(error_msg)
            self.lbl_status.setStyleSheet("color: #FF4444; font-family: 'B Titr'; font-size: 14px;")
            self.btn_update.setVisible(False)
            return

        # بررسی بروز بودن
        if result.get('is_up_to_date', False):
            self.lbl_status.setText(get_text('app_up_to_date'))
            self.lbl_status.setStyleSheet("color: #44FF44; font-family: 'B Titr'; font-size: 14px;")
            self.btn_update.setVisible(False)
        else:
            self.lbl_status.setText(get_text('new_version_available').format(latest))
            self.lbl_status.setStyleSheet("color: #FFD700; font-family: 'B Titr'; font-size: 14px;")
            self.btn_update.setVisible(True)

        # اعمال مجدد تم روی دکمه‌ها
        self.apply_theme()

        # اجباری به‌روزرسانی UI
        QApplication.processEvents()

    def show_error(self, error_msg):
        """نمایش خطا"""
        self.btn_check.setEnabled(True)
        self.btn_check.setText(get_text('check_again'))
        self.lbl_status.setText(f"{get_text('error')}: {error_msg}")
        self.lbl_status.setStyleSheet("color: #FF4444; font-family: 'B Titr'; font-size: 14px;")
        self.lbl_latest_version.setText(get_text('latest_version_checking'))
        self.btn_update.setVisible(False)
        QApplication.processEvents()

    def start_update(self):
        """شروع بروزرسانی"""
        reply = QMessageBox.question(
            self,
            get_text('update'),
            f"{get_text('update_question')}\n\n{get_text('update_note')}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.btn_check.setEnabled(False)
        self.btn_update.setEnabled(False)
        self.btn_update.setText(get_text('updating'))
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.lbl_status.setText(get_text('downloading_updating'))
        self.lbl_status.setStyleSheet("color: #FFD700; font-family: 'B Titr'; font-size: 14px;")
        QApplication.processEvents()

        def update():
            def progress_callback(value):
                self.progress_bar.setValue(value)

            success = self.github_manager.download_and_update(progress_callback)
            QTimer.singleShot(0, lambda: self.show_update_final(success))

        threading.Thread(target=update, daemon=True).start()

    def show_update_final(self, success):
        """نمایش نتیجه نهایی بروزرسانی"""
        self.progress_bar.setVisible(False)
        self.btn_check.setEnabled(True)
        self.btn_update.setEnabled(True)

        if success:
            self.lbl_status.setText(get_text('update_successful'))
            self.lbl_status.setStyleSheet("color: #44FF44; font-family: 'B Titr'; font-size: 14px;")
            self.btn_update.setVisible(False)

            reply = QMessageBox.question(
                self,
                get_text('update_successful_title'),
                f"{get_text('update_successful_message')}\n\n{get_text('restart_question')}",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.restart_application()
        else:
            self.lbl_status.setText(get_text('update_error'))
            self.lbl_status.setStyleSheet("color: #FF4444; font-family: 'B Titr'; font-size: 14px;")
            self.btn_update.setText(get_text('start_update'))

        # اعمال مجدد تم
        self.apply_theme()
        QApplication.processEvents()

    def restart_application(self):
        """راه‌اندازی مجدد برنامه"""
        import sys
        import subprocess

        try:
            python = sys.executable
            script = os.path.join(os.path.dirname(sys.argv[0]), 'main.py')
            subprocess.Popen([python, script])
            sys.exit(0)
        except Exception as e:
            NotificationManager.error(self, f"{get_text('restart_error')}: {str(e)}")

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.btn_back.setText(get_text('back'))
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.lbl_title.setText(get_text('update_title'))
        self.lbl_current_version.setText(get_text('current_version_checking'))
        self.lbl_latest_version.setText(get_text('latest_version_checking'))
        self.btn_check.setText(get_text('check_update'))
        self.btn_update.setText(get_text('start_update'))

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()