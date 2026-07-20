# func/toast_notification.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QApplication
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QBrush, QPainterPath, QLinearGradient


class ToastNotification(QWidget):
    """اعلان مدرن با انیمیشن و طراحی جذاب"""

    closed = pyqtSignal()

    def __init__(self, parent=None, message="", duration=3000, message_type="info"):
        super().__init__(parent)
        self.parent = parent
        self.message = message
        self.duration = duration
        self.message_type = message_type
        self.opacity = 1.0
        self.is_closing = False

        # تنظیمات پنجره
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.Tool |
            Qt.WindowStaysOnTopHint |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)

        # رنگ‌ها بر اساس نوع پیام
        self.colors = {
            "success": {
                "bg": "#00a86b",
                "border": "#00d68f",
                "icon": "✅",
                "shadow": "rgba(0, 168, 107, 0.4)"
            },
            "info": {
                "bg": "#007bff",
                "border": "#4da3ff",
                "icon": "ℹ️",
                "shadow": "rgba(0, 123, 255, 0.4)"
            },
            "warning": {
                "bg": "#ff8c00",
                "border": "#ffa940",
                "icon": "⚠️",
                "shadow": "rgba(255, 140, 0, 0.4)"
            },
            "error": {
                "bg": "#dc3545",
                "border": "#ff6b7a",
                "icon": "❌",
                "shadow": "rgba(220, 53, 69, 0.4)"
            }
        }

        self.setup_ui()
        self.position_toast()

        # انیمیشن ورود
        self.show_animation()

        # تایمر برای بسته شدن خودکار
        if duration > 0:
            QTimer.singleShot(duration, self.close_animation)

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # فریم اصلی با سایه
        self.main_frame = QFrame()
        self.main_frame.setObjectName("toastFrame")
        layout.addWidget(self.main_frame)

        # استایل فریم
        colors = self.colors.get(self.message_type, self.colors["info"])

        # ایجاد گرادیان برای پس‌زمینه
        gradient = QLinearGradient(0, 0, 1, 1)
        gradient.setCoordinateMode(QLinearGradient.ObjectMode)
        gradient.setColorAt(0, QColor(colors["bg"]))
        gradient.setColorAt(1, QColor(self._darken_color(colors["bg"], 20)))

        self.main_frame.setStyleSheet(f"""
            QFrame#toastFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {colors["bg"]}, 
                    stop:1 {self._darken_color(colors["bg"], 30)});
                border: 2px solid {colors["border"]};
                border-radius: 12px;
            }}
            QFrame#toastFrame:hover {{
                border-color: white;
            }}
        """)

        # محتوای داخلی
        inner_layout = QHBoxLayout(self.main_frame)
        inner_layout.setContentsMargins(12, 8, 12, 8)
        inner_layout.setSpacing(8)

        # آیکون
        self.icon_label = QLabel(colors["icon"])
        self.icon_label.setFont(QFont("Segoe UI Emoji", 20))
        self.icon_label.setStyleSheet("background: transparent;")
        inner_layout.addWidget(self.icon_label)

        # متن
        self.message_label = QLabel(self.message)
        self.message_label.setFont(QFont("B Titr", 11))
        self.message_label.setStyleSheet("""
            color: white;
            background: transparent;
            font-family: 'B Titr';
        """)
        self.message_label.setWordWrap(True)
        self.message_label.setMaximumWidth(350)
        inner_layout.addWidget(self.message_label)

        # دکمه بستن
        self.close_btn = QLabel("✕")
        self.close_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.close_btn.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            background: transparent;
            padding: 2px 4px;
            border-radius: 3px;
        """)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.mousePressEvent = lambda e: self.close_animation()
        self.close_btn.enterEvent = lambda e: self.close_btn.setStyleSheet("""
            color: white;
            background: rgba(255,255,255,0.2);
            padding: 2px 4px;
            border-radius: 3px;
        """)
        self.close_btn.leaveEvent = lambda e: self.close_btn.setStyleSheet("""
            color: rgba(255,255,255,0.7);
            background: transparent;
            padding: 2px 4px;
            border-radius: 3px;
        """)
        inner_layout.addWidget(self.close_btn)

        # تنظیم اندازه بر اساس متن
        self.message_label.adjustSize()
        width = min(self.message_label.width() + 90, 450)
        height = max(self.message_label.height() + 20, 40)
        self.setFixedSize(max(width, 220), min(height, 80))

    def _darken_color(self, hex_color, amount):
        """تاریک‌تر کردن رنگ"""
        hex_color = hex_color.lstrip('#')
        r = max(0, int(hex_color[0:2], 16) - amount)
        g = max(0, int(hex_color[2:4], 16) - amount)
        b = max(0, int(hex_color[4:6], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def position_toast(self):
        """قرارگیری در گوشه پایین سمت راست"""
        if self.parent:
            # موقعیت پنجره والد
            parent_geo = self.parent.geometry()
            parent_x = parent_geo.x()
            parent_y = parent_geo.y()
            parent_w = parent_geo.width()
            parent_h = parent_geo.height()

            # محاسبه موقعیت (گوشه پایین سمت راست)
            x = parent_x + parent_w - self.width() - 15
            y = parent_y + parent_h - self.height() - 15

            # محاسبه موقعیت با توجه به اعلان‌های موجود
            for widget in QApplication.topLevelWidgets():
                if isinstance(widget, ToastNotification) and widget is not self:
                    if widget.x() == x:
                        y = widget.y() - self.height() - 5

            self.move(x, max(y, parent_y + 10))

    def show_animation(self):
        """انیمیشن ورود"""
        self.setWindowOpacity(0)

        # انیمیشن fade in
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.start()

        # انیمیشن حرکت از پایین
        target_y = self.y()
        self.move(self.x(), target_y + 20)

        self.move_anim = QPropertyAnimation(self, b"pos")
        self.move_anim.setDuration(300)
        self.move_anim.setStartValue(QPoint(self.x(), target_y + 20))
        self.move_anim.setEndValue(QPoint(self.x(), target_y))
        self.move_anim.setEasingCurve(QEasingCurve.OutBack)
        self.move_anim.start()

        self.show()

    def close_animation(self):
        """انیمیشن خروج"""
        if self.is_closing:
            return
        self.is_closing = True

        # انیمیشن fade out
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(250)
        self.anim.setStartValue(1)
        self.anim.setEndValue(0)
        self.anim.setEasingCurve(QEasingCurve.InCubic)
        self.anim.finished.connect(self.close)
        self.anim.start()

        # انیمیشن حرکت به پایین
        target_y = self.y() + 20
        self.move_anim = QPropertyAnimation(self, b"pos")
        self.move_anim.setDuration(250)
        self.move_anim.setStartValue(QPoint(self.x(), self.y()))
        self.move_anim.setEndValue(QPoint(self.x(), target_y))
        self.move_anim.setEasingCurve(QEasingCurve.InCubic)
        self.move_anim.start()

    def closeEvent(self, event):
        """رویداد بستن"""
        self.closed.emit()
        self.raise_()
        super().closeEvent(event)

    def paintEvent(self, event):
        """رسم سایه"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # سایه نرم
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(4, 4, self.width() - 4, self.height() - 4, 12, 12)

        colors = self.colors.get(self.message_type, self.colors["info"])
        shadow_color = QColor(colors["shadow"])
        painter.fillPath(shadow_path, shadow_color)

        super().paintEvent(event)


class ToastManager:
    """مدیریت اعلان‌ها با صف و جلوگیری از همپوشانی"""

    _toasts = []
    _queue = []
    _is_processing = False
    _max_toasts = 5

    @classmethod
    def show(cls, parent, message, duration=3000, message_type="info"):
        """نمایش اعلان"""
        # حذف اعلان‌های بسته شده
        cls._toasts = [t for t in cls._toasts if t.isVisible()]

        # اگر تعداد اعلان‌ها از حداکثر بیشتر شد، قدیمی‌ترین را حذف کن
        if len(cls._toasts) >= cls._max_toasts:
            old_toast = cls._toasts[0]
            old_toast.close()
            cls._toasts.pop(0)

        # ایجاد اعلان جدید
        toast = ToastNotification(parent, message, duration, message_type)
        toast.closed.connect(lambda: cls._remove_toast(toast))
        cls._toasts.append(toast)

        return toast

    @classmethod
    def _remove_toast(cls, toast):
        """حذف اعلان از لیست"""
        if toast in cls._toasts:
            cls._toasts.remove(toast)

    @classmethod
    def clear_all(cls):
        """بستن همه اعلان‌ها"""
        for toast in cls._toasts[:]:
            toast.close_animation()
        cls._toasts.clear()


class NotificationManager:
    """رابط کاربری ساده برای استفاده"""

    @staticmethod
    def success(parent, message, duration=2500):
        """اعلان موفقیت"""
        return ToastManager.show(parent, message, duration, "success")

    @staticmethod
    def info(parent, message, duration=2500):
        """اعلان اطلاعات"""
        return ToastManager.show(parent, message, duration, "info")

    @staticmethod
    def warning(parent, message, duration=3000):
        """اعلان هشدار"""
        return ToastManager.show(parent, message, duration, "warning")

    @staticmethod
    def error(parent, message, duration=3500):
        """اعلان خطا"""
        return ToastManager.show(parent, message, duration, "error")

    @staticmethod
    def show(parent, message, duration=3000, message_type="info"):
        """نمایش اعلان سفارشی"""
        return ToastManager.show(parent, message, duration, message_type)

    @staticmethod
    def clear_all():
        """بستن همه اعلان‌ها"""
        ToastManager.clear_all()