# frames/other_programs_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import threading
import webbrowser
import os

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QFrame, QMessageBox, QApplication
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont

from func.github_manager import GitHubManager
from func.toast_notification import NotificationManager
from path_manager import get_base_path
from variables.languages import get_text
from core.theme_manager import ThemeManager


class OtherProgramsFrame(QWidget):
    """فریم برنامه‌های دیگر"""

    # سیگنال برای به‌روزرسانی ایمن UI
    update_signal = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self.github_manager = GitHubManager()
        self.repos = []
        self.is_loading = False

        # اتصال سیگنال
        self.update_signal.connect(self._display_repos)

        self.setup_ui()
        self.apply_styles()
        self.apply_theme()

        # بارگذاری اولیه با تاخیر
        QTimer.singleShot(100, self.load_repos)

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

        self.lbl_title = QLabel(get_text('other_programs_title'))
        self.lbl_title.setFont(QFont("B Titr", 24))
        self.lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # ========== اسکرول برنامه‌ها ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")
        self.scroll_area.setStyleSheet("""
            QScrollArea#scrollArea {
                background: transparent;
                border: 2px solid #3a3a4e;
                border-radius: 12px;
            }
            QScrollBar:vertical {
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #00b4db;
                border-radius: 6px;
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

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        # ========== دکمه بروزرسانی ==========
        self.btn_refresh = self._create_button(get_text('refresh'))
        self.btn_refresh.setFixedSize(150, 40)
        self.btn_refresh.clicked.connect(lambda: self.load_repos(force_refresh=True))

        refresh_layout = QHBoxLayout()
        refresh_layout.setAlignment(Qt.AlignCenter)
        refresh_layout.addWidget(self.btn_refresh)
        layout.addLayout(refresh_layout)

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
            QLabel#loadingLabel {{
                color: #888888;
                font-family: 'B Titr';
                font-size: 16px;
            }}
            QLabel#errorLabel {{
                color: #FF4444;
                font-family: 'B Titr';
                font-size: 16px;
            }}
            QLabel#emptyLabel {{
                color: #888888;
                font-family: 'B Titr';
                font-size: 16px;
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        # اعمال به دکمه‌های اصلی فریم
        for btn in [self.btn_back, self.btn_refresh]:
            if btn:
                btn.setStyleSheet(style)

        # اعمال به دکمه‌های داخل آیتم‌های ریپو
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                for btn in widget.findChildren(QPushButton):
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

        # به‌روزرسانی آیتم‌های برنامه‌ها
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                for label in widget.findChildren(QLabel):
                    if label.objectName() == 'repoName':
                        label.setStyleSheet(f"""
                            QLabel#repoName {{
                                color: {text_color};
                                font-family: 'B Titr';
                                font-size: 16px;
                                font-weight: bold;
                            }}
                        """)
                    elif label.objectName() == 'repoDesc':
                        label.setStyleSheet(f"""
                            QLabel#repoDesc {{
                                color: #CCCCCC;
                                font-family: 'B Titr';
                                font-size: 13px;
                            }}
                        """)

    def load_repos(self, force_refresh=False):
        """بارگذاری برنامه‌ها

        Args:
            force_refresh: اگر True باشد، کش را نادیده می‌گیرد و از API می‌گیرد
        """
        if self.is_loading:
            return
        try:
            os.remove(os.path.join(get_base_path(), 'repos_cache.txt'))
        except:
            pass

        self.is_loading = True
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText(get_text('loading_repos'))

        # پاک کردن آیتم‌های قبلی
        self._clear_items()

        # نمایش پیام بارگذاری
        loading_label = QLabel(get_text('loading_repos'))
        loading_label.setObjectName("loadingLabel")
        loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(loading_label)

        # اجباری به‌روزرسانی UI
        QApplication.processEvents()

        def load():
            try:
                # اگر force_refresh=True، کش را پاک کن
                if force_refresh:
                    self.github_manager.clear_repos_cache()

                repos = self.github_manager.get_repos(force_refresh=force_refresh)

                # لاگ کردن نام ریپوها برای دیباگ
                if repos:
                    names = [repo.get('name', 'unknown') for repo in repos]

                # ارسال نتیجه به ترد اصلی
                self.update_signal.emit(repos if repos else [])
            except Exception as e:
                print(f"Error loading repos: {e}")
                self.update_signal.emit([])

        threading.Thread(target=load, daemon=True).start()

    def _clear_items(self):
        """پاک کردن آیتم‌ها"""
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

    def _display_repos(self, repos):
        """نمایش برنامه‌ها (از سیگنال صدا زده میشه)"""
        self.is_loading = False
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText(get_text('refresh'))

        self._clear_items()

        # اگر repos None یا لیست خالی باشه
        if repos is None or len(repos) == 0:
            print("No repos to display")
            empty_label = QLabel(get_text('no_other_programs'))
            empty_label.setObjectName("emptyLabel")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for repo in repos:
            item = self._create_repo_item(repo)
            self.scroll_layout.addWidget(item)

        # اجباری به‌روزرسانی UI
        QApplication.processEvents()

    def _create_repo_item(self, repo):
        """ایجاد آیتم برنامه"""
        bg_color = self.theme_manager.get_background_color()
        if bg_color:
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
        else:
            text_color = '#FFFFFF'

        frame = QFrame()
        frame.setObjectName("repoFrame")
        frame.setStyleSheet(f"""
            QFrame#repoFrame {{
                background: rgba(0,0,0,0.3);
                border: 1px solid #3a3a4e;
                border-radius: 10px;
                padding: 10px;
            }}
            QLabel#repoName {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 16px;
                font-weight: bold;
            }}
            QLabel#repoDesc {{
                color: #CCCCCC;
                font-family: 'B Titr';
                font-size: 13px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(5)

        # نام
        repo_name = repo.get('name', get_text('unknown'))
        name = QLabel(f"📁 {repo_name}")
        name.setObjectName("repoName")
        layout.addWidget(name)

        # توضیحات
        desc_text = repo.get('description', get_text('no_description'))
        desc = QLabel(desc_text)
        desc.setObjectName("repoDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # دکمه‌ها
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignRight)

        # دکمه مشاهده در گیت‌هاب
        btn_github = QPushButton(get_text('view_on_github'))
        btn_github.setFont(QFont("B Titr", 14))
        btn_github.setCursor(Qt.PointingHandCursor)
        btn_github.clicked.connect(lambda: webbrowser.open(repo.get('html_url', '')))
        btn_layout.addWidget(btn_github)

        # دکمه اطلاعات بیشتر
        btn_info = QPushButton(get_text('more_info'))
        btn_info.setFont(QFont("B Titr", 14))
        btn_info.setCursor(Qt.PointingHandCursor)
        btn_info.clicked.connect(lambda: self._show_repo_info(repo))
        btn_layout.addWidget(btn_info)

        layout.addLayout(btn_layout)

        # اعمال تم روی دکمه‌های جدید
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)
        btn_github.setStyleSheet(style)
        btn_info.setStyleSheet(style)

        return frame

    def _show_repo_info(self, repo):
        """نمایش اطلاعات برنامه"""
        info_text = f"""
{get_text('description')}: {repo.get('description', get_text('no_description'))}
{get_text('language')}: {repo.get('language', get_text('unknown'))}
{get_text('stars')}: {repo.get('stargazers_count', 0)}
{get_text('created_at')}: {repo.get('created_at', '')[:10]}
{get_text('updated_at')}: {repo.get('updated_at', '')[:10]}
{get_text('link')}: {repo.get('html_url', '')}
        """

        msg = QMessageBox(self)
        msg.setWindowTitle(f"{get_text('more_info')} {repo.get('name', '')}")
        msg.setText(info_text)
        msg.setFont(QFont("B Titr", 12))
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
            }}
            QMessageBox QLabel {{
                color: white;
                font-family: 'B Titr';
            }}
            QMessageBox QPushButton {{
                background-color: {self.theme_manager.get_button_color()};
                color: {self.theme_manager.get_text_color()};
                border: 2px solid #C0C0C0;
                border-radius: 8px;
                padding: 8px 20px;
                font-family: 'B Titr';
            }}
            QMessageBox QPushButton:hover {{
                background-color: {self.theme_manager._darken_color(self.theme_manager.get_button_color(), 20)};
            }}
        """)
        msg.exec_()

    def _show_error(self, error_msg):
        """نمایش خطا"""
        self.is_loading = False
        self.btn_refresh.setEnabled(True)
        self.btn_refresh.setText(get_text('refresh'))

        self._clear_items()

        error_label = QLabel(f"{get_text('github_error')}\n{error_msg}")
        error_label.setObjectName("errorLabel")
        error_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(error_label)

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.btn_back.setText(get_text('back'))
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.lbl_title.setText(get_text('other_programs_title'))
        self.btn_refresh.setText(get_text('refresh'))

        # به‌روزرسانی دکمه‌های داخل آیتم‌ها
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                for btn in widget.findChildren(QPushButton):
                    if btn.text() == get_text('view_on_github') or btn.text() == 'مشاهده در گیت‌هاب':
                        btn.setText(get_text('view_on_github'))
                    elif btn.text() == get_text('more_info') or btn.text() == 'اطلاعات بیشتر':
                        btn.setText(get_text('more_info'))

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()