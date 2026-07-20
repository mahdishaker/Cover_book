# frames/date_dialog.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QWidget, QGridLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from jdatetime import date as jdate

from variables.languages import get_text, get_months
from core.theme_manager import ThemeManager


class PersianCalendarWidget(QWidget):
    """ویجت تقویم شمسی برای انتخاب تاریخ"""

    date_selected = pyqtSignal(jdate)

    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = parent.theme_manager if parent and hasattr(parent, 'theme_manager') else ThemeManager()

        # دریافت رنگ‌ها از ThemeManager
        self.bg_color = self.theme_manager.get_background_color() or "#00006d"
        self.button_color = self.theme_manager.get_button_color()
        self.text_color = self.theme_manager.get_text_color_for_background(self.bg_color)

        if initial_date is None:
            self.current_date = jdate.today()
        else:
            self.current_date = initial_date

        self.selected_date = self.current_date
        self.current_month = self.current_date.month
        self.current_year = self.current_date.year

        self.setFixedSize(500, 400)

        self.setup_ui()
        self.apply_theme()
        self.render_calendar()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(6)

        # هدر (ماه و سال)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)

        self.btn_prev_year = QPushButton("◀◀")
        self.btn_prev_year.setFixedSize(50, 32)
        self.btn_prev_year.setFont(QFont("B Titr", 10))
        self.btn_prev_year.setCursor(Qt.PointingHandCursor)
        self.btn_prev_year.clicked.connect(self.prev_year)
        header_layout.addWidget(self.btn_prev_year)

        self.btn_prev_month = QPushButton("◀")
        self.btn_prev_month.setFixedSize(50, 32)
        self.btn_prev_month.setFont(QFont("B Titr", 13))
        self.btn_prev_month.setCursor(Qt.PointingHandCursor)
        self.btn_prev_month.clicked.connect(self.prev_month)
        header_layout.addWidget(self.btn_prev_month)

        self.lbl_month_year = QLabel()
        self.lbl_month_year.setFont(QFont("B Titr", 16))
        self.lbl_month_year.setAlignment(Qt.AlignCenter)
        self.lbl_month_year.setMinimumWidth(160)
        header_layout.addWidget(self.lbl_month_year)

        self.btn_next_month = QPushButton("▶")
        self.btn_next_month.setFixedSize(50, 32)
        self.btn_next_month.setFont(QFont("B Titr", 13))
        self.btn_next_month.setCursor(Qt.PointingHandCursor)
        self.btn_next_month.clicked.connect(self.next_month)
        header_layout.addWidget(self.btn_next_month)

        self.btn_next_year = QPushButton("▶▶")
        self.btn_next_year.setFixedSize(50, 32)
        self.btn_next_year.setFont(QFont("B Titr", 10))
        self.btn_next_year.setCursor(Qt.PointingHandCursor)
        self.btn_next_year.clicked.connect(self.next_year)
        header_layout.addWidget(self.btn_next_year)

        layout.addLayout(header_layout)

        # روزهای هفته
        week_layout = QHBoxLayout()
        week_layout.setSpacing(3)
        days_of_week = get_text('Weekdays')
        self.week_labels = []
        for day in days_of_week:
            label = QLabel(day)
            label.setFont(QFont("B Titr", 10))
            label.setAlignment(Qt.AlignCenter)
            label.setFixedHeight(25)
            week_layout.addWidget(label)
            self.week_labels.append(label)

        layout.addLayout(week_layout)

        # شبکه روزها
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(3)
        self.grid_layout.setHorizontalSpacing(3)
        self.grid_layout.setVerticalSpacing(3)
        layout.addLayout(self.grid_layout)

    def go_to_today(self):
        today = jdate.today()
        self.current_year = today.year
        self.current_month = today.month
        self.current_date = today
        self.selected_date = today
        self.render_calendar()
        self.date_selected.emit(today)

    def prev_month(self):
        try:
            if self.current_month == 1:
                self.current_month = 12
                self.current_year -= 1
            else:
                self.current_month -= 1
            self.current_date = jdate(self.current_year, self.current_month, 1)
            self.render_calendar()
        except Exception as e:
            print(f"Error in prev_month: {e}")

    def next_month(self):
        try:
            if self.current_month == 12:
                self.current_month = 1
                self.current_year += 1
            else:
                self.current_month += 1
            self.current_date = jdate(self.current_year, self.current_month, 1)
            self.render_calendar()
        except Exception as e:
            print(f"Error in next_month: {e}")

    def prev_year(self):
        try:
            self.current_year -= 1
            self.current_date = jdate(self.current_year, self.current_month, 1)
            self.render_calendar()
        except Exception as e:
            print(f"Error in prev_year: {e}")

    def next_year(self):
        try:
            self.current_year += 1
            self.current_date = jdate(self.current_year, self.current_month, 1)
            self.render_calendar()
        except Exception as e:
            print(f"Error in next_year: {e}")

    def render_calendar(self):
        try:
            self._clear_grid()

            month_name = get_months()[self.current_month - 1]
            year_str = self._to_persian_digits(str(self.current_year))
            self.lbl_month_year.setText(f"{month_name} {year_str}")

            first_day = jdate(self.current_year, self.current_month, 1)
            start_day = first_day.weekday()
            days_in_month = self._get_days_in_month(self.current_year, self.current_month)

            row = 0
            col = 0

            # روزهای ماه قبل
            if start_day > 0:
                prev_month = self.current_month - 1
                prev_year = self.current_year
                if prev_month == 0:
                    prev_month = 12
                    prev_year -= 1
                prev_days = self._get_days_in_month(prev_year, prev_month)
                for i in range(start_day):
                    day_num = prev_days - start_day + i + 1
                    btn = self._create_day_button(day_num, False, prev_month, prev_year)
                    self.grid_layout.addWidget(btn, row, col)
                    col += 1

            # روزهای ماه جاری
            for day in range(1, days_in_month + 1):
                if col >= 7:
                    col = 0
                    row += 1

                is_selected = (day == self.selected_date.day and
                               self.current_month == self.selected_date.month and
                               self.current_year == self.selected_date.year)
                is_today = (day == jdate.today().day and
                            self.current_month == jdate.today().month and
                            self.current_year == jdate.today().year)

                btn = self._create_day_button(day, True, self.current_month, self.current_year, is_selected, is_today)
                self.grid_layout.addWidget(btn, row, col)
                col += 1

            # روزهای ماه بعد
            if col < 7:
                next_month = self.current_month + 1
                next_year = self.current_year
                if next_month == 13:
                    next_month = 1
                    next_year += 1
                day_num = 1
                remaining_days = 7 - col
                for _ in range(remaining_days):
                    btn = self._create_day_button(day_num, False, next_month, next_year)
                    self.grid_layout.addWidget(btn, row, col)
                    col += 1
                    day_num += 1

        except Exception as e:
            print(f"Error rendering calendar: {e}")

    def _clear_grid(self):
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                self.grid_layout.takeAt(i)

    def _get_days_in_month(self, year, month):
        if month <= 6:
            return 31
        elif month <= 11:
            return 30
        else:
            return 30 if jdate(year, 12, 1).isleap() else 29

    def _create_day_button(self, day, is_current_month, month, year, is_selected=False, is_today=False):
        btn = QPushButton(self._to_persian_digits(str(day)))
        btn.setFont(QFont("B Titr", 11))
        btn.setFixedSize(48, 34)
        btn.setCursor(Qt.PointingHandCursor)

        btn.day = day
        btn.month = month
        btn.year = year
        btn.is_current_month = is_current_month

        # دریافت رنگ‌ها
        button_color = self.theme_manager.get_button_color()
        bg_color = self.theme_manager.get_background_color() or "#00006d"
        text_color = self.theme_manager.get_text_color_for_background(bg_color)

        # محاسبه رنگ‌های تیره‌تر و روشن‌تر
        darker_button = self._darken_color(button_color, 30)
        hover_bg = self._adjust_color(bg_color, 30)  # کمی روشن‌تر برای هاور

        if is_selected:
            style = f"""
                QPushButton {{
                    background-color: {button_color};
                    color: {text_color};
                    border: 2px solid #FFFFFF;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {darker_button};
                }}
            """
        elif is_today:
            # امروز با رنگ طلایی
            style = f"""
                QPushButton {{
                    background-color: #FFD700;
                    color: #1a1a2e;
                    border: 2px solid #FFD700;
                    border-radius: 8px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #FFE44D;
                }}
            """
        elif not is_current_month:
            # روزهای ماه‌های دیگر (با رنگ ملایم‌تر)
            muted_color = self._adjust_color(text_color, -80)  # تیره‌تر کردن متن
            style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {muted_color};
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: rgba(255,255,255,0.08);
                    color: {text_color};
                }}
            """
        else:
            # روزهای معمولی ماه جاری
            style = f"""
                QPushButton {{
                    background-color: transparent;
                    color: {text_color};
                    border: none;
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    background-color: rgba(0,180,219,0.2);
                    border: 1px solid {button_color};
                    color: {text_color};
                }}
            """

        btn.setStyleSheet(style)
        btn.clicked.connect(lambda checked, b=btn: self._select_date(b))
        return btn

    def _select_date(self, btn):
        try:
            self.selected_date = jdate(btn.year, btn.month, btn.day)
            self.current_date = self.selected_date
            self.current_month = self.selected_date.month
            self.current_year = self.selected_date.year
            self.date_selected.emit(self.selected_date)
            self.render_calendar()
        except Exception as e:
            print(f"Error in _select_date: {e}")

    def _to_persian_digits(self, text):
        from variables.languages import get_current_language

        current_lang = get_current_language()
        if current_lang == 'persian' or current_lang == 'Arabic' :
            _digits = {
                '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
                '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
            }
        else:
            _digits = {
                '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
            }
        return ''.join(_digits.get(c, c) for c in text)

    def _darken_color(self, hex_color, amount):
        """تاریک‌تر کردن رنگ"""
        if not hex_color or not hex_color.startswith('#'):
            return hex_color
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return f"#{hex_color}"
        try:
            r = max(0, int(hex_color[0:2], 16) - amount)
            g = max(0, int(hex_color[2:4], 16) - amount)
            b = max(0, int(hex_color[4:6], 16) - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return f"#{hex_color}"

    def _adjust_color(self, hex_color, amount):
        """روشن‌تر یا تیره‌تر کردن رنگ (مقدار مثبت = روشن‌تر، منفی = تیره‌تر)"""
        if not hex_color or not hex_color.startswith('#'):
            return hex_color
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return f"#{hex_color}"
        try:
            r = max(0, min(255, int(hex_color[0:2], 16) + amount))
            g = max(0, min(255, int(hex_color[2:4], 16) + amount))
            b = max(0, min(255, int(hex_color[4:6], 16) + amount))
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return f"#{hex_color}"

    def apply_theme(self):
        """اعمال تم به کل ویجت تقویم"""
        bg_color = self.theme_manager.get_background_color() or "#00006d"
        text_color = self.theme_manager.get_text_color_for_background(bg_color)
        button_color = self.theme_manager.get_button_color()

        # استایل کلی ویجت
        style = f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 10px;
            }}
            QLabel {{
                color: {text_color};
                font-family: 'B Titr';
            }}
            QPushButton {{
                background-color: {button_color};
                color: {text_color};
                border: 1px solid #C0C0C0;
                border-radius: 6px;
                font-family: 'B Titr';
                padding: 4px;
            }}
            QPushButton:hover {{
                background-color: {self._darken_color(button_color, 25)};
                border-color: #FFFFFF;
            }}
        """
        self.setStyleSheet(style)

        # تنظیم استایل لیبل‌های روزهای هفته (همرنگ با متن)
        for label in self.week_labels:
            label.setStyleSheet(f"""
                QLabel {{
                    color: {text_color};
                    font-weight: bold;
                    background-color: transparent;
                }}
            """)


class DateDialog(QDialog):
    """دیالوگ انتخاب تاریخ با تقویم شمسی"""

    date_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = parent.theme_manager if parent and hasattr(parent, 'theme_manager') else ThemeManager()

        # دریافت رنگ‌ها
        self.bg_color = self.theme_manager.get_background_color() or "#00006d"
        self.button_color = self.theme_manager.get_button_color()
        self.text_color = self.theme_manager.get_text_color_for_background(self.bg_color)

        self.setWindowTitle(get_text('select_date'))
        self.setFixedSize(540, 530)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)


        self.setup_ui()
        self.apply_styles()
        self.apply_theme()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.addStretch()
        self.lbl_title = QLabel("📅 " + get_text('select_date'))
        self.lbl_title.setFont(QFont("B Titr", 18))
        self.lbl_title.setObjectName("dialogTitle")
        header_layout.addWidget(self.lbl_title)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet(f"background-color: {self.button_color}; max-height: 2px;")
        layout.addWidget(line)

        initial_date = jdate.today()
        self.calendar = PersianCalendarWidget(self, initial_date)
        layout.addWidget(self.calendar)

        self.lbl_selected = QLabel()
        self.lbl_selected.setObjectName("selectedDate")
        self.lbl_selected.setAlignment(Qt.AlignCenter)
        self.lbl_selected.setFont(QFont("B Titr", 15))
        self.lbl_selected.setFixedHeight(45)
        self._update_selected_label()
        layout.addWidget(self.lbl_selected)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        button_layout.setAlignment(Qt.AlignCenter)

        self.btn_cancel = QPushButton(get_text('cancel'))
        self.btn_cancel.setFixedSize(140, 40)
        self.btn_cancel.setFont(QFont("B Titr", 12))
        self.btn_cancel.setCursor(Qt.PointingHandCursor)
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)

        self.btn_apply = QPushButton(get_text('apply'))
        self.btn_apply.setFixedSize(140, 40)
        self.btn_apply.setFont(QFont("B Titr", 12))
        self.btn_apply.setCursor(Qt.PointingHandCursor)
        self.btn_apply.clicked.connect(self.accept)
        button_layout.addWidget(self.btn_apply)

        layout.addLayout(button_layout)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)
        for btn in [self.btn_cancel, self.btn_apply]:
            btn.setStyleSheet(style)

    def _update_selected_label(self):
        if hasattr(self, 'calendar') and self.calendar:
            selected = self.calendar.selected_date
            if selected:
                day_str = self._to_persian_digits(str(selected.day))
                month_name = get_months()[selected.month - 1]
                year_str = self._to_persian_digits(str(selected.year))
                self.lbl_selected.setText(f"📌 {month_name} {year_str}")

    def _to_persian_digits(self, text):
        from variables.languages import get_current_language

        current_lang = get_current_language()
        if current_lang == 'persian' or current_lang == 'Arabic' :
            _digits = {
                '0': '۰', '1': '۱', '2': '۲', '3': '۳', '4': '۴',
                '5': '۵', '6': '۶', '7': '۷', '8': '۸', '9': '۹'
            }
        else:
            _digits = {
                '0': '0', '1': '1', '2': '2', '3': '3', '4': '4',
                '5': '5', '6': '6', '7': '7', '8': '8', '9': '9'
            }
        return ''.join(_digits.get(c, c) for c in text)

    def apply_styles(self):
        """اعمال استایل دیالوگ با رنگ‌های هماهنگ با تم"""
        bg_color = self.theme_manager.get_background_color() or "#00006d"
        text_color = self.theme_manager.get_text_color_for_background(bg_color)
        button_color = self.theme_manager.get_button_color()

        # محاسبه رنگ تیره‌تر برای گرادیانت
        darker_bg = self._darken_color(bg_color, 30)

        style = f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {bg_color},
                    stop:1 {darker_bg});
                border-radius: 15px;
            }}
            QLabel#dialogTitle {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 18px;
                font-weight: bold;
            }}
            QLabel#selectedDate {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 15px;
                padding: 10px;
                background: rgba(0,0,0,0.2);
                border-radius: 10px;
                border: 1px solid {button_color};
            }}
        """
        self.setStyleSheet(style)

    def _darken_color(self, hex_color, amount):
        if not hex_color or not hex_color.startswith('#'):
            return hex_color
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return f"#{hex_color}"
        try:
            r = max(0, int(hex_color[0:2], 16) - amount)
            g = max(0, int(hex_color[2:4], 16) - amount)
            b = max(0, int(hex_color[4:6], 16) - amount)
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return f"#{hex_color}"

    def on_date_selected(self, date):
        self._update_selected_label()

    def get_selected_date(self):
        if hasattr(self, 'calendar') and self.calendar:
            selected = self.calendar.selected_date
            if selected:

                month_name = get_months()[selected.month - 1]
                year_str = self._to_persian_digits(str(selected.year))
                return f"{month_name} {year_str}"

        today = jdate.today()

        month_name = get_months()[today.month - 1]
        year_str = self._to_persian_digits(str(today.year))
        return f"{month_name} {year_str}"

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.accept()
        elif event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)