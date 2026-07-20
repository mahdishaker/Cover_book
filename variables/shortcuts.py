# variables/shortcuts.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import QShortcut, QMessageBox
from PyQt5.QtGui import QKeySequence
from variables.languages import get_text


class ShortcutManager:
    """مدیریت میانبرهای صفحه کلید"""

    def __init__(self, parent):
        self.parent = parent

        # ثبت میانبرها
        self._register_shortcuts()

    def _register_shortcuts(self):
        """ثبت تمام میانبرها"""
        shortcuts = [
            ('Ctrl+H', lambda: self.parent.show_frame('history')),
            ('Ctrl+T', lambda: self.parent.show_frame('theme')),
            ('Ctrl+U', lambda: self.parent.show_frame('update')),
            ('Ctrl+?', self.show_help),
            ('F1', self.show_help),
            ('Escape', lambda: self.parent.show_frame('main')),
            ('Ctrl+N', self.new_project),
            ('Ctrl+S', self.start_making),
            ('Ctrl+O', self.open_pdf),
            ('Ctrl+R', self.refresh_form),
            ('Ctrl+Shift+C', self.calc_spine),
        ]

        for key, callback in shortcuts:
            shortcut = QShortcut(QKeySequence(key), self.parent)
            shortcut.activated.connect(callback)

    def _get_theme_manager(self):
        """دریافت ThemeManager از برنامه اصلی"""
        if hasattr(self.parent, 'theme_manager'):
            return self.parent.theme_manager
        return None

    def _get_button_color(self):
        """دریافت رنگ دکمه فعلی"""
        tm = self._get_theme_manager()
        if tm:
            return tm.get_button_color()
        return '#f5c277'  # رنگ پیش‌فرض

    def _get_text_color(self):
        """دریافت رنگ متن فعلی"""
        tm = self._get_theme_manager()
        if tm:
            return tm.get_text_color()
        return '#FFFFFF'

    def show_help(self):
        """نمایش راهنما با هماهنگی با تم برنامه"""
        button_color = self._get_button_color()
        text_color = self._get_text_color()

        # اگر text_color هنوز تنظیم نشده، از روشنایی رنگ دکمه استفاده کن
        if text_color == '#FFFFFF' and button_color:
            from core.theme_manager import ThemeManager
            tm = ThemeManager()
            text_color = tm.get_text_color_for_background(button_color)

        msg = QMessageBox(self.parent)
        msg.setWindowTitle(get_text('keyboard_shortcuts'))
        msg.setText(get_shortcuts_text())

        # استایل هماهنگ با تم برنامه
        msg.setStyleSheet(f"""
            QMessageBox {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
                border-radius: 12px;
            }}
            QMessageBox QLabel {{
                color: white;
                font-family: 'B Titr';
                font-size: 13px;
                padding: 10px;
            }}
            QMessageBox QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 2px solid #C0C0C0;
                border-radius: 8px;
                padding: 10px 30px;
                font-family: 'B Titr';
                font-size: 14px;
                min-width: 80px;
            }}
            QMessageBox QPushButton:hover {{
                background-color: {self._darken_color(button_color, 20)};
                border-color: #FFFFFF;
            }}
            QMessageBox QPushButton:pressed {{
                background-color: {self._darken_color(button_color, 40)};
            }}
        """)
        msg.exec_()

    def _darken_color(self, hex_color, amount):
        """تاریک‌تر کردن رنگ"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return hex_color
        r = max(0, int(hex_color[0:2], 16) - amount)
        g = max(0, int(hex_color[2:4], 16) - amount)
        b = max(0, int(hex_color[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def new_project(self):
        """پروژه جدید (پاک کردن فرم)"""
        from func.toast_notification import NotificationManager
        current_frame = self.parent.get_current_frame()
        if current_frame == 'dissertation':
            frame = self.parent.frames.get('dissertation')
            if frame and hasattr(frame, 'refresh_form'):
                frame.refresh_form()
                NotificationManager.success(self.parent, get_text('form_cleared'))
        else:
            NotificationManager.info(self.parent, get_text('shortcut_refresh_form'))

    def start_making(self):
        """شروع ساخت"""
        from func.toast_notification import NotificationManager
        current_frame = self.parent.get_current_frame()
        if current_frame == 'dissertation':
            frame = self.parent.frames.get('dissertation')
            if frame and hasattr(frame, 'start_making'):
                frame.start_making()
        else:
            NotificationManager.info(self.parent, get_text('shortcut_start_making'))

    def open_pdf(self):
        """باز کردن PDF"""
        from func.toast_notification import NotificationManager
        current_frame = self.parent.get_current_frame()
        if current_frame == 'dissertation':
            frame = self.parent.frames.get('dissertation')
            if frame and hasattr(frame, 'select_pdf_file'):
                frame.select_pdf_file()
        else:
            NotificationManager.info(self.parent, get_text('shortcut_open_pdf'))

    def refresh_form(self):
        """پاکسازی فرم"""
        from func.toast_notification import NotificationManager
        current_frame = self.parent.get_current_frame()
        if current_frame == 'dissertation':
            frame = self.parent.frames.get('dissertation')
            if frame and hasattr(frame, 'refresh_form'):
                frame.refresh_form()
                NotificationManager.success(self.parent, get_text('form_cleared'))
        else:
            NotificationManager.info(self.parent, get_text('shortcut_refresh_form'))

    def calc_spine(self):
        """محاسبه عطف"""
        from func.toast_notification import NotificationManager
        current_frame = self.parent.get_current_frame()
        if current_frame == 'dissertation':
            frame = self.parent.frames.get('dissertation')
            if frame and hasattr(frame, 'calculate_spine'):
                frame.calculate_spine()
        else:
            NotificationManager.info(self.parent, get_text('shortcut_calc_spine'))


def get_shortcuts_text():
    """دریافت متن راهنمای میانبرها"""
    text = "⌨️ " + get_text('keyboard_shortcuts') + ":\n\n"

    text += "【 " + get_text('general') + " 】\n"
    text += "  Ctrl+H: " + get_text('shortcut_show_history') + "\n"
    text += "  Ctrl+T: " + get_text('shortcut_show_theme') + "\n"
    text += "  Ctrl+U: " + get_text('shortcut_check_update') + "\n"
    text += "  Ctrl+?: " + get_text('shortcut_show_help') + "\n"
    text += "  F1: " + get_text('shortcut_quick_help') + "\n"
    text += "  Escape: " + get_text('shortcut_back_to_main') + "\n"

    text += "\n【 " + get_text('dissertation_cover').replace('\n', ' ') + " 】\n"
    text += "  Ctrl+N: " + get_text('shortcut_new_project') + "\n"
    text += "  Ctrl+S: " + get_text('shortcut_start_making') + "\n"
    text += "  Ctrl+O: " + get_text('shortcut_open_pdf') + "\n"
    text += "  Ctrl+R: " + get_text('shortcut_refresh_form') + "\n"
    text += "  Ctrl+Shift+C: " + get_text('shortcut_calc_spine') + "\n"

    text += "\n💡 " + get_text('shortcuts_note')

    return text