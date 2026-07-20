# frames/guide_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTabWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from variables.languages import get_text
from core.theme_manager import ThemeManager


class GuideFrame(QWidget):
    """فریم راهنما"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent

        if parent and hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
        else:
            self.theme_manager = ThemeManager()

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ========== هدر ==========
        header_layout = QHBoxLayout()

        self.btn_back = self._create_button(get_text('back'))
        self.btn_back.setFixedSize(80, 40)
        self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('dissertation'))
        header_layout.addWidget(self.btn_back)

        header_layout.addStretch()

        self.lbl_title = QLabel(get_text('guide'))
        self.lbl_title.setObjectName("pageTitle")
        header_layout.addWidget(self.lbl_title)

        header_layout.addStretch()
        layout.addLayout(header_layout)

        # ========== تب‌ها ==========
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("guideTabs")

        # تب ۱: مرحله ۱
        self.tab1 = self._create_step1_tab()
        self.tab_widget.addTab(self.tab1, get_text('step1'))

        # تب ۲: مرحله ۲
        self.tab2 = self._create_step2_tab()
        self.tab_widget.addTab(self.tab2, get_text('step2'))

        # تب ۳: مرحله ۳
        self.tab3 = self._create_step3_tab()
        self.tab_widget.addTab(self.tab3, get_text('step3'))

        layout.addWidget(self.tab_widget)

    def _create_step1_tab(self):
        """ایجاد تب مرحله ۱"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        icon = QLabel("📝")
        icon.setObjectName("tabIcon")
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        title = QLabel(get_text('guide_step1_title'))
        title.setObjectName("stepTitle")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("QFrame { background-color: #FFFFFF; max-height: 2px; }")
        layout.addWidget(sep)

        desc = QLabel(get_text('guide_step1_desc'))
        desc.setObjectName("stepDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        formula_frame = QFrame()
        formula_frame.setObjectName("formulaFrame")
        formula_layout = QVBoxLayout(formula_frame)

        formula = QLabel(get_text('spine_formula'))
        formula.setObjectName("formulaText")
        formula.setWordWrap(True)
        formula_layout.addWidget(formula)

        layout.addWidget(formula_frame)
        layout.addStretch()

        return tab

    def _create_step2_tab(self):
        """ایجاد تب مرحله ۲"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        icon = QLabel("📂")
        icon.setObjectName("tabIcon")
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        title = QLabel(get_text('guide_step2_title'))
        title.setObjectName("stepTitle")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("QFrame { background-color: #FFFFFF; max-height: 2px; }")
        layout.addWidget(sep)

        desc = QLabel(get_text('guide_step2_desc'))
        desc.setObjectName("stepDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        icons_frame = QHBoxLayout()
        icons_frame.setAlignment(Qt.AlignCenter)

        file_icon = QLabel("📄 PDF")
        file_icon.setObjectName("fileIcon")
        icons_frame.addWidget(file_icon)

        arrow = QLabel("→")
        arrow.setObjectName("arrowIcon")
        icons_frame.addWidget(arrow)

        folder_icon = QLabel(f"💾 {get_text('save_location')}")
        folder_icon.setObjectName("fileIcon")
        icons_frame.addWidget(folder_icon)

        layout.addLayout(icons_frame)
        layout.addStretch()

        return tab

    def _create_step3_tab(self):
        """ایجاد تب مرحله ۳"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignTop)

        icon = QLabel("🎨")
        icon.setObjectName("tabIcon")
        layout.addWidget(icon, alignment=Qt.AlignCenter)

        title = QLabel(get_text('guide_step3_title'))
        title.setObjectName("stepTitle")
        layout.addWidget(title, alignment=Qt.AlignCenter)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("QFrame { background-color: #FFFFFF; max-height: 2px; }")
        layout.addWidget(sep)

        desc = QLabel(get_text('guide_step3_desc'))
        desc.setObjectName("stepDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        process_frame = QFrame()
        process_frame.setObjectName("processFrame")
        process_layout = QVBoxLayout(process_frame)

        steps = [
            f"✅ 1. {get_text('title_on')}",
            f"✅ 2. {get_text('title_back')}",
            f"✅ 3. {get_text('start_making')}",
            f"✅ 4. {get_text('save_file')}"
        ]

        for step in steps:
            label = QLabel(step)
            label.setObjectName("processStep")
            process_layout.addWidget(label)

        layout.addWidget(process_frame)

        result_frame = QFrame()
        result_frame.setObjectName("resultFrame")
        result_layout = QVBoxLayout(result_frame)

        result = QLabel(get_text('guide_result'))
        result.setObjectName("resultText")
        result.setWordWrap(True)
        result_layout.addWidget(result)

        layout.addWidget(result_frame)
        layout.addStretch()

        return tab

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
                font-size: 26px;
                font-weight: bold;
            }}
            QLabel#tabIcon {{
                font-size: 32px;
                color: {text_color};
            }}
            QLabel#stepTitle {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 20px;
                font-weight: bold;
            }}
            QLabel#stepDesc {{
                color: #CCCCCC;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QLabel#fileIcon {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 16px;
                padding: 10px;
            }}
            QLabel#arrowIcon {{
                color: #C0C0C0;
                font-family: 'B Titr';
                font-size: 20px;
                padding: 10px;
            }}
            QLabel#processStep {{
                color: #90EE90;
                font-family: 'B Titr';
                font-size: 14px;
                padding: 5px 10px;
            }}
            QLabel#resultText {{
                color: #FFB6C1;
                font-family: 'B Titr';
                font-size: 14px;
                padding: 10px;
            }}
            QFrame#formulaFrame {{
                background-color: #2a2a3a;
                border: 1px solid #FFFFFF;
                border-radius: 12px;
                padding: 15px;
                margin: 10px 0px;
            }}
            QLabel#formulaText {{
                color: #FFD700;
                font-family: 'B Titr';
                font-size: 13px;
            }}
            QFrame#processFrame {{
                background-color: #2a2a3a;
                border: 1px solid #FFFFFF;
                border-radius: 12px;
                padding: 15px;
                margin: 10px 0px;
            }}
            QFrame#resultFrame {{
                background-color: #2a2a3a;
                border: 1px solid #FFFFFF;
                border-radius: 12px;
                padding: 15px;
                margin: 10px 0px;
            }}
            QTabWidget::pane {{
                background-color: transparent;
                border: 2px solid #3a3a4e;
                border-radius: 12px;
            }}
            QTabBar::tab {{
                background-color: {self.theme_manager.get_button_color()};
                color: {text_color};
                padding: 8px 16px;
                margin: 2px;
                border-radius: 8px;
                font-family: 'B Titr';
                font-size: 14px;
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme_manager._darken_color(self.theme_manager.get_button_color(), 30)};
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme_manager._darken_color(self.theme_manager.get_button_color(), 20)};
            }}
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        """اعمال تم به دکمه‌ها"""
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)

        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ['menuBtn', 'minBtn', 'closeBtn']:
                btn.setStyleSheet(style)

    def update_text_colors(self, text_color):
        """به‌روزرسانی رنگ متون بر اساس پس‌زمینه"""
        for label in self.findChildren(QLabel):
            obj_name = label.objectName()
            if obj_name == 'pageTitle':
                label.setStyleSheet(f"""
                    QLabel#pageTitle {{
                        color: {text_color};
                        font-family: 'B Titr';
                        font-size: 26px;
                        font-weight: bold;
                    }}
                """)
            elif obj_name == 'tabIcon':
                label.setStyleSheet(f"""
                    QLabel#tabIcon {{
                        font-size: 32px;
                        color: {text_color};
                    }}
                """)
            elif obj_name == 'stepTitle':
                label.setStyleSheet(f"""
                    QLabel#stepTitle {{
                        color: {text_color};
                        font-family: 'B Titr';
                        font-size: 20px;
                        font-weight: bold;
                    }}
                """)
            elif obj_name == 'stepDesc':
                label.setStyleSheet(f"""
                    QLabel#stepDesc {{
                        color: #CCCCCC;
                        font-family: 'B Titr';
                        font-size: 14px;
                    }}
                """)
            elif obj_name == 'fileIcon':
                label.setStyleSheet(f"""
                    QLabel#fileIcon {{
                        color: {text_color};
                        font-family: 'B Titr';
                        font-size: 16px;
                        padding: 10px;
                    }}
                """)
            elif obj_name == 'arrowIcon':
                label.setStyleSheet(f"""
                    QLabel#arrowIcon {{
                        color: #C0C0C0;
                        font-family: 'B Titr';
                        font-size: 20px;
                        padding: 10px;
                    }}
                """)
            elif obj_name == 'processStep':
                label.setStyleSheet(f"""
                    QLabel#processStep {{
                        color: #90EE90;
                        font-family: 'B Titr';
                        font-size: 14px;
                        padding: 5px 10px;
                    }}
                """)
            elif obj_name == 'resultText':
                label.setStyleSheet(f"""
                    QLabel#resultText {{
                        color: #FFB6C1;
                        font-family: 'B Titr';
                        font-size: 14px;
                        padding: 10px;
                    }}
                """)
            elif obj_name == 'formulaText':
                label.setStyleSheet(f"""
                    QLabel#formulaText {{
                        color: #FFD700;
                        font-family: 'B Titr';
                        font-size: 13px;
                    }}
                """)

    def update_texts(self):
        """به‌روزرسانی متن‌ها"""
        self.btn_back.setText(get_text('back'))
        self.lbl_title.setText(get_text('guide'))
        self.tab_widget.setTabText(0, get_text('step1'))
        self.tab_widget.setTabText(1, get_text('step2'))
        self.tab_widget.setTabText(2, get_text('step3'))

        # بازسازی تب‌ها با متن‌های جدید
        self._refresh_tabs()

    def _refresh_tabs(self):
        """بازسازی تب‌ها با متن‌های جدید"""
        self.tab_widget.clear()

        self.tab1 = self._create_step1_tab()
        self.tab_widget.addTab(self.tab1, get_text('step1'))

        self.tab2 = self._create_step2_tab()
        self.tab_widget.addTab(self.tab2, get_text('step2'))

        self.tab3 = self._create_step3_tab()
        self.tab_widget.addTab(self.tab3, get_text('step3'))

    def update_theme(self):
        """به‌روزرسانی تم"""
        self.apply_theme()