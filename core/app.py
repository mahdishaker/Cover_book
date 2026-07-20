# core/app.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (
    QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QHBoxLayout, QPushButton, QLabel, QFrame, QApplication,
    QMenu, QAction, QMessageBox
)

from core.auth_manager import AuthManager
from core.database_manager import DatabaseManager
from core.theme_manager import ThemeManager
from path_manager import get_icon_path
from variables.languages import get_text, set_language
from variables.shortcuts import ShortcutManager


class CoverApp(QMainWindow):
    """پنجره اصلی برنامه"""

    language_changed = pyqtSignal(str)  # اطلاع‌رسانی تغییر زبان به تمام فریم‌ها (ارسال کد زبان)
    theme_changed = pyqtSignal(str)  # اطلاع‌رسانی تغییر رنگ تم به تمام ویجت‌ها (ارسال کد رنگ Hex)

    def __init__(self):
        super().__init__()

        # مدیریت تم
        self.theme_manager = ThemeManager()

        # مدیریت احراز هویت و دیتابیس
        self.auth_manager = AuthManager()
        self.db_manager = DatabaseManager()

        # تنظیم زبان از فایل کانفیگ
        saved_lang = self.theme_manager.get_language()
        set_language(saved_lang)

        # تنظیمات اولیه پنجره
        self.setWindowTitle(get_text('app_title'))
        self.setMinimumSize(700, 700)
        self.setWindowIcon(QIcon(get_icon_path()))
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # مرکز کردن پنجره
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(
            (screen.width() - 750) // 2,
            (screen.height() - 800) // 2,
            750, 800
        )

        # ذخیره‌سازی موقعیت ماوس برای کشیدن پنجره بدون حاشیه (Frameless)
        self.drag_position = None

        # زمان سنج جلسه (بروزرسانی هر دقیقه)
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self._update_session_time)
        self.session_timer.start(60000)

        # ساخت رابط کاربری
        self._setup_ui()

        # ثبت میانبرهای صفحه کلید
        self.shortcut_manager = ShortcutManager(self)

        QTimer.singleShot(100, self._apply_enter_animation)

        # بررسی وضعیت احراز هویت
        QTimer.singleShot(500, self._check_auth)

    def _check_auth(self):
        """بررسی خودکار احراز هویت و نمایش فریم مناسب"""
        if self.auth_manager.is_authenticated():
            self.show_frame('main')
            self.update_user_info()
            self._update_session_time()
        else:
            self.show_frame('login')

    def _update_session_time(self):
        """بروزرسانی نمایش زمان باقیمانده جلسه"""
        if self.auth_manager.is_authenticated():
            remaining = self.auth_manager.get_remaining_time()
            if remaining:
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                time_str = f"{hours:02d}:{minutes:02d}"

                title_bar = self.findChild(QFrame, "titleBar")
                if title_bar:
                    for child in title_bar.findChildren(QLabel):
                        if child.objectName() == "sessionLabel":
                            child.setText(f"⏱ {time_str}")
                            break
            else:
                self.auth_manager.logout_user(clear_remember=False)
                self.show_frame('login')
                QMessageBox.warning(
                    self,
                    get_text('session_expired'),
                    get_text('session_expired_message')
                )

    def _apply_enter_animation(self):
        """اجرای انیمیشن محو شدن هنگام نمایش پنجره"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def _setup_ui(self):
        """راه‌اندازی رابط کاربری اصلی"""
        self.central_widget = QWidget()
        self.central_widget.setObjectName("centralWidget")
        self.setCentralWidget(self.central_widget)

        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # نوار عنوان
        title_bar = self._create_title_bar()
        main_layout.addWidget(title_bar)

        # ویجت پشت فریم ها برای تعویض فریم‌ها
        self.stack = QStackedWidget()
        self.stack.setObjectName("stackWidget")
        main_layout.addWidget(self.stack)

        # ایجاد فریم‌ها
        self.frames = {}
        self._create_frames()

        # اعمال تم با تاخیر
        QTimer.singleShot(50, self.apply_theme)

    def _create_frames(self):
        """ایجاد تمام فریم‌های برنامه"""
        from frames.main_frame import MainFrame
        from frames.dissertation_frame import DissertationFrame
        from frames.history_frame import HistoryFrame
        from frames.theme_frame import ThemeFrame
        from frames.guide_frame import GuideFrame
        from frames.update_frame import UpdateFrame
        from frames.other_programs_frame import OtherProgramsFrame
        from frames.login_frame import LoginFrame
        from frames.register_frame import RegisterFrame

        self.frames['login'] = LoginFrame(self)
        self.stack.addWidget(self.frames['login'])

        self.frames['register'] = RegisterFrame(self)
        self.stack.addWidget(self.frames['register'])

        self.frames['main'] = MainFrame(self)
        self.stack.addWidget(self.frames['main'])

        self.frames['dissertation'] = DissertationFrame(self)
        self.stack.addWidget(self.frames['dissertation'])

        self.frames['history'] = HistoryFrame(self)
        self.stack.addWidget(self.frames['history'])

        self.frames['theme'] = ThemeFrame(self)
        self.stack.addWidget(self.frames['theme'])

        self.frames['guide'] = GuideFrame(self)
        self.stack.addWidget(self.frames['guide'])

        self.frames['update'] = UpdateFrame(self)
        self.stack.addWidget(self.frames['update'])

        self.frames['other_programs'] = OtherProgramsFrame(self)
        self.stack.addWidget(self.frames['other_programs'])

    def show_frame(self, frame_name):
        """نمایش فریم مشخص شده"""
        if frame_name in self.frames:
            self.stack.setCurrentWidget(self.frames[frame_name])
            if frame_name == 'main':
                self.update_user_info()

    def get_current_frame(self):
        """دریافت نام فریم جاری"""
        current_widget = self.stack.currentWidget()
        for name, widget in self.frames.items():
            if widget == current_widget:
                return name
        return None

    def update_user_info(self):
        """بروزرسانی اطلاعات کاربر در نوار عنوان"""
        user = self.auth_manager.get_current_user()
        if user:
            title_bar = self.findChild(QFrame, "titleBar")
            if title_bar:
                for child in title_bar.findChildren(QLabel):
                    if child.objectName() == "titleLabel":
                        child.setText(f"{get_text('app_title')}")

    def _create_title_bar(self):
        """ساخت نوار عنوان سفارشی"""
        title_bar = QFrame()
        title_bar.setFixedHeight(55)
        title_bar.setObjectName("titleBar")

        layout = QHBoxLayout(title_bar)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(8)

        # دکمه منو
        menu_btn = QPushButton("☰")
        menu_btn.setFixedSize(40, 40)
        menu_btn.setObjectName("menuBtn")
        menu_btn.setFont(QFont("B Titr", 14))
        menu_btn.setToolTip(get_text('main_menu'))
        menu_btn.clicked.connect(self.show_main_menu)
        layout.addWidget(menu_btn)

        # عنوان برنامه
        title_label = QLabel(get_text('app_title'))
        title_label.setFont(QFont("B Titr", 16))
        title_label.setObjectName("titleLabel")
        layout.addWidget(title_label)

        # تیم توسعه‌دهنده
        dev_label = QLabel("• " + get_text('developer_team'))
        dev_label.setFont(QFont("B Titr", 11))
        dev_label.setObjectName("devLabel")
        dev_label.setStyleSheet("color: #888;")
        layout.addWidget(dev_label)

        layout.addStretch()

        # برچسب زمان جلسه
        self.session_label = QLabel("⏱ 12:00")
        self.session_label.setFont(QFont("B Titr", 12))
        self.session_label.setObjectName("sessionLabel")
        self.session_label.setStyleSheet("color: #00ffcc;")
        layout.addWidget(self.session_label)

        # برچسب ساعت
        self.time_label = QLabel()
        self.time_label.setFont(QFont("B Titr", 12))
        self.time_label.setObjectName("timeLabel")
        self.time_label.setStyleSheet("color: #aaa;")
        self._update_time()
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self._update_time)
        self.time_timer.start(1000)
        layout.addWidget(self.time_label)

        # دکمه خروج از حساب
        logout_btn = QPushButton("🚪")
        logout_btn.setFixedSize(40, 40)
        logout_btn.setFont(QFont("B Titr", 14))
        logout_btn.setObjectName("logoutBtn")
        logout_btn.setToolTip(get_text('logout'))
        logout_btn.clicked.connect(self.logout_user)
        layout.addWidget(logout_btn)

        # دکمه کوچک‌سازی
        min_btn = QPushButton("─")
        min_btn.setFixedSize(40, 40)
        min_btn.setFont(QFont("B Titr", 16))
        min_btn.setObjectName("minBtn")
        min_btn.setToolTip(get_text('minimize'))
        min_btn.clicked.connect(self.showMinimized)
        layout.addWidget(min_btn)

        # دکمه بستن
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(40, 40)
        close_btn.setFont(QFont("B Titr", 16))
        close_btn.setObjectName("closeBtn")
        close_btn.setToolTip(get_text('close'))
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        return title_bar

    def _update_time(self):
        """بروزرسانی ساعت جاری"""
        from datetime import datetime
        now = datetime.now()
        self.time_label.setText(now.strftime("%H:%M:%S"))

    def show_main_menu(self):
        """نمایش منوی اصلی برنامه"""
        menu = QMenu(self)
        menu.setFont(QFont("B Titr", 12))
        menu.setStyleSheet("""
            QMenu {
                background: #1a1a2e;
                color: white;
                border: 1px solid #3a3a4e;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background: #00b4db;
            }
            QMenu::separator {
                height: 1px;
                background: #3a3a4e;
                margin: 5px 10px;
            }
        """)

        user = self.auth_manager.get_current_user() # دریافت اطلاعات کاربر فعلی از سیستم احراز هویت
        if user:
            username = user.get('username', get_text('guest'))
            user_action = QAction(f"👤 {username}", self)
            user_action.setEnabled(False)
            menu.addAction(user_action)

            remaining = self.auth_manager.get_remaining_time()  # دریافت زمان باقیمانده از جلسه کاربر (پایان جلسه پس از ۱۲ ساعت)
            if remaining:
                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60
                time_action = QAction(f"⏱ {hours:02d}:{minutes:02d} {get_text('remaining')}", self)
                time_action.setEnabled(False)
                menu.addAction(time_action)

            menu.addSeparator()

        # ایجاد دکمه درباره ما در نوار منو بالای برنامه
        about_action = QAction("ℹ️ " + get_text('about_button'), self)
        about_action.triggered.connect(self.show_about)
        menu.addAction(about_action)

        menu.addSeparator()

        theme_action = QAction("🎨 " + get_text('theme_button'), self)
        theme_action.triggered.connect(lambda: self.show_frame('theme'))
        menu.addAction(theme_action)

        menu.addSeparator()

        logout_action = QAction("🚪 " + get_text('logout'), self)
        logout_action.triggered.connect(self.logout_user)
        menu.addAction(logout_action)

        menu.addSeparator()

        exit_action = QAction("🚪 " + get_text('exit'), self)
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)

        menu.exec_(self.mapToGlobal(QPoint(60, 60)))

    def logout_user(self):
        """خروج از حساب کاربری"""
        reply = QMessageBox.question(
            self,
            get_text('logout'),
            get_text('logout_confirm'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.auth_manager.logout_user(clear_remember=True)
            self.show_frame('login')

    def show_about(self):
        """نمایش دیالوگ درباره برنامه"""
        from frames.about_frame import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec_()

    def change_button_color(self, color_code):
        """تغییر رنگ دکمه‌ها و اعمال تم"""
        self.theme_manager.set_button_color(color_code)
        self.apply_theme()
        self.theme_changed.emit(color_code)

    def change_background_color(self, color_code):
        """تغییر رنگ پس‌زمینه"""
        self.theme_manager.set_background_color(color_code)
        self.apply_theme()

    def apply_theme(self):
        """اعمال تم بر روی تمام ویجت‌ها"""

        # دریافت رنگ پس‌زمینه از فایل تنیمات (config.json)
        bg_color = self.theme_manager.get_background_color()

        if bg_color:
            # محاسبه خودکار رنگ متن (سیاه یا سفید) بر اساس روشنایی پس‌زمینه برای خوانایی بهتر
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
        else:
            text_color = '#FFFFFF'
            bg_color = "#00006d"

        # اعمال رنگ مناسب برای دکمه ها
        self.theme_manager.set_text_color(text_color)

        self.central_widget.setStyleSheet(f"""
            QWidget#centralWidget {{
                background-color: {bg_color};
                border-radius: 15px;
            }}
        """)

        title_bar = self.findChild(QFrame, "titleBar")
        if title_bar:
            title_bar.setStyleSheet(f"""
                QFrame#titleBar {{
                    background: rgba(0,0,0,0.5);
                    border-radius: 10px;
                }}
                QLabel#titleLabel {{
                    color: {text_color};
                    font-size: 16px;
                    font-weight: bold;
                    font-family: 'B Titr';
                }}
                QLabel#devLabel {{
                    color: #888;
                    font-size: 11px;
                    font-family: 'B Titr';
                }}
                QLabel#timeLabel {{
                    color: {text_color};
                    font-size: 12px;
                    font-family: 'B Titr';
                }}
                QLabel#sessionLabel {{
                    color: #00ffcc;
                    font-size: 12px;
                    font-family: 'B Titr';
                }}
                QPushButton#menuBtn {{
                    background: rgba(0,180,219,0.8);
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    font-family: 'B Titr';
                }}
                QPushButton#menuBtn:hover {{
                    background: rgba(0,180,219,1);
                }}
                QPushButton#logoutBtn {{
                    background: rgba(255,50,50,0.7);
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    font-family: 'B Titr';
                }}
                QPushButton#logoutBtn:hover {{
                    background: rgba(255,0,0,1);
                }}
                QPushButton#minBtn {{
                    background: rgba(50,50,50,0.8);
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    font-family: 'B Titr';
                }}
                QPushButton#minBtn:hover {{
                    background: rgba(100,100,100,1);
                }}
                QPushButton#closeBtn {{
                    background: rgba(255,50,50,0.8);
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                    font-family: 'B Titr';
                }}
                QPushButton#closeBtn:hover {{
                    background: rgba(255,0,0,1);
                }}
            """)

        for frame in self.frames.values():
            if hasattr(frame, 'apply_theme'):
                frame.apply_theme()
            if hasattr(frame, 'update_text_colors'):
                frame.update_text_colors(text_color)
            if hasattr(frame, 'apply_styles'):
                frame.apply_styles()

    def change_language(self, lang_code):
        """تغییر زبان و بروزرسانی تمام فریم‌ها"""
        if set_language(lang_code):
            self.theme_manager.set_language(lang_code)
            self.language_changed.emit(lang_code)
            self.setWindowTitle(get_text('app_title'))

            for frame in self.frames.values():
                if hasattr(frame, 'update_texts'):
                    frame.update_texts()
                if hasattr(frame, 'update_text_colors'):
                    frame.update_text_colors(self.theme_manager.get_text_color())
                if hasattr(frame, 'apply_styles'):
                    frame.apply_styles()

            title_bar = self.findChild(QFrame, "titleBar")
            if title_bar:
                for child in title_bar.findChildren(QLabel):
                    if child.objectName() == "titleLabel":
                        user = self.auth_manager.get_current_user()
                        if user and user.get('is_guest', False):
                            child.setText(f"{get_text('app_title')} - {get_text('guest')}")
                        elif user:
                            child.setText(f"{get_text('app_title')} - {user.get('username', '')}")
                        else:
                            child.setText(get_text('app_title'))
                    elif child.objectName() == "devLabel":
                        child.setText("• " + get_text('developer_team'))

                for btn in title_bar.findChildren(QPushButton):
                    if btn.objectName() == "menuBtn":
                        btn.setToolTip(get_text('main_menu'))
                    elif btn.objectName() == "logoutBtn":
                        btn.setToolTip(get_text('logout'))
                    elif btn.objectName() == "minBtn":
                        btn.setToolTip(get_text('minimize'))
                    elif btn.objectName() == "closeBtn":
                        btn.setToolTip(get_text('close'))

    # رویدادهای مربوط به کشیدن پنجره
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position:
            self.move(self.pos() + event.globalPos() - self.drag_position)
            self.drag_position = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.drag_position = None

    def closeEvent(self, event):
        self.time_timer.stop()
        self.session_timer.stop()
        event.accept()
