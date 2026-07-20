# frames/about_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QFrame, QScrollArea, QApplication, QWidget
)
from PyQt5.QtCore import Qt, QPropertyAnimation
from PyQt5.QtGui import QFont

from path_manager import get_icon_path, get_ver_path
from variables.languages import get_text
from core.theme_manager import ThemeManager
from func.github_manager import GitHubManager
from func.toast_notification import NotificationManager


class AboutDialog(QDialog):
    """دیالوگ درباره ما با رنگ بندی مدرن (آبی-بنفش ملایم)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent

        if parent and hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
        else:
            self.theme_manager = ThemeManager()

        self.setWindowTitle(get_text('about_title'))
        self.setFixedSize(600, 700)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)


        self.setup_ui()
        self.apply_styles()
        self.apply_theme()
        self._apply_enter_animation()

    def _apply_enter_animation(self):
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(400)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def _create_button(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 14))
        return btn

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # هدر
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(35, 35)
        close_btn.setFont(QFont("B Titr", 14))
        close_btn.setObjectName("closeBtn")
        close_btn.setToolTip(get_text('close'))
        close_btn.clicked.connect(self.accept)
        header_layout.addWidget(close_btn)
        layout.addLayout(header_layout)

        # محتوای اسکرول‌دار
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scrollArea")
        scroll.setStyleSheet("""
            QScrollArea#scrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background-color: rgba(255,255,255,0.08);
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #00b4db;
                border-radius: 5px;
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

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignTop)

        # عنوان
        title_label = QLabel(get_text('app_title'))
        title_label.setFont(QFont("B Titr", 28))
        title_label.setObjectName("appTitle")
        title_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(title_label)

        # نسخه
        version = GitHubManager().get_current_version() or '1.0.0'
        version_label = QLabel(f"{get_text('current_version')}: {version}")
        version_label.setFont(QFont("B Titr", 14))
        version_label.setObjectName("versionLabel")
        version_label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(version_label)

        # خط جداکننده
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setObjectName("separator")
        sep.setStyleSheet(f"""
            QFrame#separator {{
                background-color: {self.theme_manager.get_button_color()};
                max-height: 2px;
            }}
        """)
        content_layout.addWidget(sep)

        # متن درباره
        about_text = get_text('about_message').format(version)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("B Titr", 13))
        text_edit.setHtml(self._format_text(about_text))
        text_edit.setObjectName("aboutText")
        text_edit.setStyleSheet("""
            QTextEdit#aboutText {
                background: rgba(0,0,0,0.15);
                color: #F0F0F0;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 15px;
            }
            QTextEdit#aboutText p {
                color: #F0F0F0;
            }
        """)
        content_layout.addWidget(text_edit)

        # خط جداکننده دوم
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setObjectName("separator")
        sep2.setStyleSheet(f"""
            QFrame#separator {{
                background-color: {self.theme_manager.get_button_color()};
                max-height: 2px;
            }}
        """)
        content_layout.addWidget(sep2)

        # اطلاعات تماس
        contact_layout = QVBoxLayout()
        contact_layout.setAlignment(Qt.AlignCenter)
        contact_label = QLabel(get_text('id').format('@Moghiseh1390', '@M_M_SH_n'))
        contact_label.setFont(QFont("B Titr", 13))
        contact_label.setObjectName("contactLabel")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setWordWrap(True)
        contact_label.setCursor(Qt.PointingHandCursor)
        contact_label.mousePressEvent = lambda e: self.copy_to_clipboard("@Moghiseh1390\n@M_M_SH_n")
        contact_label.enterEvent = lambda e: contact_label.setStyleSheet("color: #00ffcc; font-family: 'B Titr';")
        contact_label.leaveEvent = lambda e: contact_label.setStyleSheet("color: #CCCCCC; font-family: 'B Titr';")
        contact_layout.addWidget(contact_label)
        content_layout.addLayout(contact_layout)

        # دکمه بستن
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignCenter)
        close_btn2 = self._create_button(get_text('close'))
        close_btn2.setFixedSize(120, 40)
        close_btn2.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn2)
        content_layout.addLayout(btn_layout)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _format_text(self, text):
        lines = text.strip().split('\n')
        html_lines = []
        for line in lines:
            if line.strip():
                html_lines.append(
                    f"<p style='margin: 8px 0; color: #F0F0F0; font-family: \"B Titr\";'>{line.strip()}</p>")
            else:
                html_lines.append("<br>")
        return f"""
            <div style='font-family: "B Titr", Tahoma; font-size: 14px; line-height: 1.8;'>
                {''.join(html_lines)}
            </div>
        """

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        NotificationManager.success(self, get_text('copyed'))

    def apply_styles(self):
        """
        گرادیانت مدرن با رنگ‌های آبی روشن تا بنفش ملایم
        نه خیلی تیره، نه صورتی
        """
        style = """
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2);
                border-radius: 15px;
            }
            QLabel#appTitle {
                color: white;
                font-family: 'B Titr';
                font-size: 28px;
                font-weight: bold;
                text-shadow: 0 2px 12px rgba(0,0,0,0.3);
            }
            QLabel#versionLabel {
                color: #FFD700;
                font-family: 'B Titr';
                font-size: 14px;
                font-weight: bold;
                text-shadow: 0 1px 6px rgba(0,0,0,0.3);
            }
            QLabel#contactLabel {
                color: #EEEEEE;
                font-family: 'B Titr';
                padding: 8px 16px;
                border-radius: 8px;
                background: rgba(255,255,255,0.05);
            }
            QLabel#contactLabel:hover {
                background: rgba(255,255,255,0.15);
                color: #00ffcc;
            }
            QPushButton#closeBtn {
                background: rgba(255,50,50,0.8);
                border-radius: 17px;
                font-size: 16px;
                font-weight: bold;
                color: white;
                font-family: 'B Titr';
            }
            QPushButton#closeBtn:hover {
                background: rgba(255,0,0,1);
            }
        """
        self.setStyleSheet(style)

    def apply_theme(self):
        color = self.theme_manager.get_button_color()
        btn_style = self.theme_manager.get_button_style(color)
        for btn in self.findChildren(QPushButton):
            if btn.objectName() != "closeBtn":
                btn.setStyleSheet(btn_style)