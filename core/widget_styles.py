# core/widget_styles.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QFrame, QScrollArea, \
    QCheckBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from path_manager import get_font_path
from variables.constants import DEFAULT_WIDGET_COLOR


class WidgetStyles:
    """کلاس مدیریت استایل‌های ویجت‌ها"""

    @staticmethod
    def apply_button_style(button, color=DEFAULT_WIDGET_COLOR):
        """اعمال استایل دکمه"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: 2px solid #C0C0C0;
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #d4a860;
                border-color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #b89450;
            }}
            QPushButton:disabled {{
                background-color: #555555;
                color: #888888;
            }}
        """)
        return button

    @staticmethod
    def apply_entry_style(entry, color=DEFAULT_WIDGET_COLOR):
        """اعمال استایل ورودی"""
        entry.setStyleSheet(f"""
            QLineEdit {{
                background-color: #2a2a2a;
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 8px 12px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: #FFFFFF;
            }}
        """)
        return entry

    @staticmethod
    def apply_label_style(label, is_heading=False, is_subheading=False):
        """اعمال استایل لیبل"""
        font_size = 24 if is_heading else (18 if is_subheading else 14)
        weight = 'bold' if is_heading or is_subheading else 'normal'

        label.setStyleSheet(f"""
            QLabel {{
                color: white;
                font-family: 'B Titr';
                font-size: {font_size}px;
                font-weight: {weight};
            }}
        """)
        return label

    @staticmethod
    def apply_combobox_style(combobox, color=DEFAULT_WIDGET_COLOR):
        """اعمال استایل کامبوباکس"""
        combobox.setStyleSheet(f"""
            QComboBox {{
                background-color: #2a2a2a;
                color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 6px 12px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
                margin-right: 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: #2a2a2a;
                color: white;
                selection-background-color: {color};
                selection-color: white;
                border: 2px solid {color};
                border-radius: 8px;
            }}
        """)
        return combobox

    @staticmethod
    def apply_checkbox_style(checkbox, color=DEFAULT_WIDGET_COLOR):
        """اعمال استایل چک‌باکس"""
        checkbox.setStyleSheet(f"""
            QCheckBox {{
                color: white;
                font-family: 'B Titr';
                font-size: 14px;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {color};
                border-radius: 4px;
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {color};
                border-color: {color};
            }}
            QCheckBox::indicator:hover {{
                border-color: #FFFFFF;
            }}
        """)
        return checkbox

    @staticmethod
    def apply_frame_style(frame, background='transparent', border_color=None):
        """اعمال استایل فریم"""
        style = f"""
            QFrame {{
                background-color: {background};
                border: none;
                border-radius: 12px;
            }}
        """
        if border_color:
            style += f"""
                QFrame {{
                    border: 2px solid {border_color};
                    border-radius: 12px;
                }}
            """
        frame.setStyleSheet(style)
        return frame

    @staticmethod
    def apply_scrollarea_style(scrollarea, color=DEFAULT_WIDGET_COLOR):
        """اعمال استایل ناحیه پیمایش"""
        scrollarea.setStyleSheet(f"""
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {color};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: #d4a860;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """)
        return scrollarea