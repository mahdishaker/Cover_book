# frames/history_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QScrollArea, QFrame, QMessageBox,
    QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont

from func.history_manager import HistoryManager
from func.toast_notification import NotificationManager
from variables.languages import get_text, get_date_range_options
from core.theme_manager import ThemeManager


class HistoryItem(QFrame):
    """آیتم تاریخچه"""

    def __init__(self, item_data, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.parent_widget = parent
        self.theme_manager = parent.theme_manager if parent and hasattr(parent, 'theme_manager') else ThemeManager()
        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # نام فایل
        self.lbl_name = QLabel(self.item_data.get('original_name', get_text('unknown')))
        self.lbl_name.setMinimumWidth(200)
        layout.addWidget(self.lbl_name)

        # تاریخ
        self.lbl_date = QLabel(f"📅 {self.item_data.get('date_added', '')}")
        self.lbl_date.setMinimumWidth(150)
        layout.addWidget(self.lbl_date)

        # عنوان و نویسنده
        metadata = self.item_data.get('metadata', {})
        title = metadata.get('title', get_text('unknown'))[:20]
        author = metadata.get('author', get_text('unknown'))[:15]
        self.lbl_info = QLabel(f"📖 {title} | ✍️ {author}")
        self.lbl_info.setMinimumWidth(200)
        layout.addWidget(self.lbl_info)

        layout.addStretch()

        # دکمه‌ها
        self.btn_open = QPushButton('🎭')
        self.btn_open.setFixedSize(35, 35)
        self.btn_open.setToolTip(get_text('open_file'))
        self.btn_open.clicked.connect(self.open_file)
        layout.addWidget(self.btn_open)

        self.btn_location = QPushButton('📂')
        self.btn_location.setFixedSize(35, 35)
        self.btn_location.setToolTip(get_text('open_location'))
        self.btn_location.clicked.connect(self.open_location)
        layout.addWidget(self.btn_location)

        self.btn_save = QPushButton('💾')
        self.btn_save.setFixedSize(35, 35)
        self.btn_save.setToolTip(get_text('save_file'))
        self.btn_save.clicked.connect(self.save_file)
        layout.addWidget(self.btn_save)

        self.btn_delete = QPushButton('🗑️')
        self.btn_delete.setFixedSize(35, 35)
        self.btn_delete.setToolTip(get_text('delete'))
        self.btn_delete.clicked.connect(self.delete_item)
        layout.addWidget(self.btn_delete)

        # اعمال استایل پایه
        self.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border: 2px solid #f5c277;
                border-radius: 8px;
            }
            QLabel {
                color: white;
                font-family: 'B titr';
                font-size: 13px;
            }
        """)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in [self.btn_open, self.btn_location, self.btn_save, self.btn_delete]:
            btn.setStyleSheet(style)

        # به‌روزرسانی حاشیه فریم
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {color};
                border-radius: 8px;
            }}
            QLabel {{
                color: white;
                font-family: 'B titr';
                font-size: 13px;
            }}
        """)

    def update_text_colors(self, text_color):
        """به‌روزرسانی رنگ متون آیتم تاریخچه"""
        color = self.theme_manager.get_button_color()

        self.lbl_name.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 13px;
            }}
        """)

        self.lbl_date.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 13px;
            }}
        """)

        self.lbl_info.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 13px;
            }}
        """)

        self.setStyleSheet(f"""
            QFrame {{
                background-color: #2a2a2a;
                border: 2px solid {color};
                border-radius: 8px;
            }}
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 13px;
            }}
        """)

    def open_file(self):
        """باز کردن فایل"""
        history_manager = HistoryManager()
        history_manager.open_file(self.item_data)

    def open_location(self):
        """باز کردن مسیر فایل"""
        history_manager = HistoryManager()
        history_manager.open_file_location(self.item_data)

    def save_file(self):
        """ذخیره فایل"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            get_text('save_file'),
            self.item_data.get('original_name', 'cover.bmp'),
            "Bitmap Files (*.bmp)"
        )
        if file_path:
            history_path = self.item_data.get('history_path')
            if history_path and os.path.exists(history_path):
                import shutil
                shutil.copy2(history_path, file_path)
                NotificationManager.success(self, get_text('file_saved_to'))

    def delete_item(self):
        """حذف آیتم"""
        reply = QMessageBox.question(
            self,
            get_text('guide_button'),
            get_text('delete_confirm').format(self.item_data.get('original_name', '')),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            history_manager = HistoryManager()
            history_manager.remove_from_history(self.item_data['id'])
            if self.parent_widget:
                self.parent_widget.load_history()


class HistoryFrame(QWidget):
    """فریم تاریخچه"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.theme_manager = parent.theme_manager if parent else ThemeManager()
        self.history_manager = HistoryManager()
        self.history_data = []
        self.current_filter = 'all_time'
        self.search_term = ''

        self.setup_ui()
        self.apply_theme()
        self.load_history()

    def _create_button(self, text):
        """ایجاد دکمه با رنگ فعلی"""
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # ========== هدر ==========
        header_layout = QHBoxLayout()

        self.btn_back = self._create_button(get_text('back'))
        self.btn_back.setFixedSize(80, 40)
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('main'))
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        self.lbl_title = QLabel(get_text('history_button'))
        self.lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # ========== فیلترها ==========
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)

        self.lbl_filter = QLabel(f"{get_text('filter_date_range')}:")
        filter_layout.addWidget(self.lbl_filter)

        self.cmb_date_range = QComboBox()
        self.cmb_date_range.addItems(get_date_range_options())
        self.cmb_date_range.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.cmb_date_range)

        filter_layout.addStretch()

        # جستجو
        self.ent_search = QLineEdit()
        self.ent_search.setPlaceholderText(get_text('search_placeholder'))
        self.ent_search.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.ent_search)

        self.btn_clear_search = self._create_button('✕')
        self.btn_clear_search.setFixedSize(35, 35)
        self.btn_clear_search.setToolTip(get_text('clear_search'))
        self.btn_clear_search.clicked.connect(self.clear_search)
        filter_layout.addWidget(self.btn_clear_search)

        main_layout.addLayout(filter_layout)

        # ========== لیست آیتم‌ها ==========
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        # ========== دکمه‌های پایین ==========
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.setAlignment(Qt.AlignCenter)

        self.btn_clear_all = self._create_button(get_text('clear_all'))
        self.btn_clear_all.setFixedSize(200, 50)
        self.btn_clear_all.setToolTip(get_text('clear_all_tooltip'))
        self.btn_clear_all.clicked.connect(self.clear_all_history)
        bottom_layout.addWidget(self.btn_clear_all)

        self.btn_refresh = self._create_button(get_text('refresh'))
        self.btn_refresh.setFixedSize(200, 50)
        self.btn_refresh.setToolTip(get_text('refresh_tooltip'))
        self.btn_refresh.clicked.connect(self.load_history)
        bottom_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(bottom_layout)

        # اعمال استایل
        self.apply_styles()

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
                font-size: 26px;
                font-weight: bold;
            }}
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
            }}
            QLineEdit {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid #00b4db;
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: #00ffcc;
            }}
            QComboBox {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid #00b4db;
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                color: {text_color};
                selection-background-color: #00b4db;
            }}
            QScrollArea#scrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: #00b4db;
                border-radius: 6px;
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

        for btn in self.findChildren(QPushButton):
            btn.setStyleSheet(style)

        # به‌روزرسانی کامبوباکس
        self.cmb_date_range.setStyleSheet(f"""
            QComboBox {{
                background: rgba(0,0,0,0.5);
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                color: white;
                selection-background-color: {color};
            }}
        """)

        # به‌روزرسانی خط جستجو
        self.ent_search.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.5);
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: #00ffcc;
            }}
        """)

    def update_text_colors(self, text_color):
        """به‌روزرسانی رنگ متون بر اساس پس‌زمینه"""
        color = self.theme_manager.get_button_color()

        # به‌روزرسانی عنوان صفحه
        self.lbl_title.setStyleSheet(f"""
            QLabel#pageTitle {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 26px;
                font-weight: bold;
            }}
        """)

        # به‌روزرسانی برچسب فیلتر
        self.lbl_filter.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-family: 'B titr';
                font-size: 14px;
            }}
        """)

        # به‌روزرسانی جستجو
        self.ent_search.setStyleSheet(f"""
            QLineEdit {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: #00ffcc;
            }}
        """)

        # به‌روزرسانی کامبوباکس
        self.cmb_date_range.setStyleSheet(f"""
            QComboBox {{
                background: rgba(0,0,0,0.5);
                color: {text_color};
                border: 2px solid {color};
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B titr';
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox QAbstractItemView {{
                background: #1a1a2e;
                color: {text_color};
                selection-background-color: {color};
            }}
        """)

        # به‌روزرسانی آیتم‌های تاریخچه
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'update_text_colors'):
                widget.update_text_colors(text_color)

    def load_history(self):
        """بارگذاری تاریخچه"""
        self.history_data = self.history_manager.load_history()
        self.apply_filters()

    def apply_filters(self):
        """اعمال فیلترها"""
        filtered_data = self.history_data

        # فیلتر بازه زمانی
        if self.current_filter != 'all_time':
            range_map = {
                'today': 1,
                'this_week': 7,
                'this_month': 30,
                'this_year': 365,
                'last_3_months': 90,
                'last_6_months': 180,
                'last_year': 365
            }

            days = range_map.get(self.current_filter, 0)
            if days > 0:
                cutoff = datetime.now() - timedelta(days=days)
                cutoff_str = cutoff.strftime("%Y-%m-%d")
                filtered_data = [
                    item for item in filtered_data
                    if item.get('date_added', '').startswith(cutoff_str) or
                       item.get('date_added', '') > cutoff_str
                ]

        # فیلتر جستجو
        if self.search_term:
            search_lower = self.search_term.lower()
            filtered_data = [
                item for item in filtered_data
                if search_lower in item.get('original_name', '').lower() or
                   search_lower in item.get('metadata', {}).get('title', '').lower() or
                   search_lower in item.get('metadata', {}).get('author', '').lower() or
                   search_lower in item.get('date_added', '').lower()
            ]

        self.display_items(filtered_data)

    def display_items(self, items):
        """نمایش آیتم‌ها"""
        # پاک کردن آیتم‌های قبلی
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        if not items:
            empty_label = QLabel(get_text('empty_history'))
            empty_label.setStyleSheet("color: #888888; font-family: 'B titr'; font-size: 16px;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.scroll_layout.addWidget(empty_label)
            return

        for item in items:
            item_widget = HistoryItem(item, self)
            item_widget.apply_theme()
            self.scroll_layout.addWidget(item_widget)

    def on_filter_changed(self, index):
        """تغییر فیلتر بازه زمانی"""
        range_map = {
            0: 'all_time',
            1: 'today',
            2: 'this_week',
            3: 'this_month',
            4: 'this_year',
            5: 'last_3_months',
            6: 'last_6_months',
            7: 'last_year'
        }
        self.current_filter = range_map.get(index, 'all_time')
        self.apply_filters()

    def on_search_changed(self, text):
        """تغییر جستجو"""
        self.search_term = text
        # تاخیر در اجرای جستجو
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.apply_filters)
        self._search_timer.start(300)

    def clear_search(self):
        """پاک کردن جستجو"""
        self.ent_search.clear()
        self.apply_filters()

    def clear_all_history(self):
        """پاک کردن کل تاریخچه"""
        if not self.history_data:
            NotificationManager.warning(self, get_text('empty_history'))
            return

        reply = QMessageBox.question(
            self,
            get_text('guide_button'),
            get_text('clear_all_confirm'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.history_manager.clear_all_history()
            NotificationManager.success(self, get_text('clear_all_success'))
            self.load_history()

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.btn_back.setText(get_text('back'))
        self.btn_back.setToolTip(get_text('back_tooltip'))
        self.lbl_title.setText(get_text('history_button'))
        self.lbl_filter.setText(f"{get_text('filter_date_range')}:")
        self.ent_search.setPlaceholderText(get_text('search_placeholder'))
        self.btn_clear_all.setText(get_text('clear_all'))
        self.btn_clear_all.setToolTip(get_text('clear_all_tooltip'))
        self.btn_refresh.setText(get_text('refresh'))
        self.btn_refresh.setToolTip(get_text('refresh_tooltip'))

        # به‌روزرسانی کامبوباکس
        self.cmb_date_range.clear()
        self.cmb_date_range.addItems(get_date_range_options())

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()
        # به‌روزرسانی آیتم‌های تاریخچه
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget and hasattr(widget, 'apply_theme'):
                widget.apply_theme()