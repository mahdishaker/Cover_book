# frames/splash_screen.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from PyQt5.QtWidgets import (
    QSplashScreen, QLabel, QProgressBar, QVBoxLayout, QWidget, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont

from path_manager import get_icon_path
from variables.languages import get_text, set_language
from variables.constants import DEFAULT_WIDGET_COLOR, DEFAULT_LANGUAGE
from core.theme_manager import ThemeManager


class SplashScreen(QSplashScreen):
    """Splash screen with language support"""

    def __init__(self):
        super().__init__()

        # Load language from config
        self.theme_manager = ThemeManager()
        saved_lang = self.theme_manager.get_language()
        set_language(saved_lang)

        # Create splash widget
        self.splash_widget = QWidget()
        self.splash_widget.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #0a0a0a, stop:0.5 #1a1a2e, stop:1 #0a0a0a);
                border: 2px solid {DEFAULT_WIDGET_COLOR};
                border-radius: 15px;
            }}
            QLabel {{
                color: white;
                font-family: 'B Titr';
            }}
            QProgressBar {{
                background-color: #2a2a3e;
                border: 2px solid #3a3a4e;
                border-radius: 8px;
                text-align: center;
                color: white;
                height: 20px;
                font-family: 'B Titr';
                font-size: 11px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #00b4db, stop:1 #00ffcc);
                border-radius: 6px;
            }}
        """)

        self.splash_layout = QVBoxLayout(self.splash_widget)
        self.splash_layout.setContentsMargins(40, 40, 40, 40)
        self.splash_layout.setSpacing(15)

        # Icon with emoji
        self.lbl_icon = QLabel('📚')
        self.lbl_icon.setFont(QFont("B Titr", 80))
        self.lbl_icon.setStyleSheet(f"color: {DEFAULT_WIDGET_COLOR};")
        self.splash_layout.addWidget(self.lbl_icon, alignment=Qt.AlignCenter)

        # Title
        self.lbl_title = QLabel(get_text('app_title'))
        self.lbl_title.setFont(QFont("B Titr", 32))
        self.lbl_title.setStyleSheet(f"color: {DEFAULT_WIDGET_COLOR};")
        self.splash_layout.addWidget(self.lbl_title, alignment=Qt.AlignCenter)

        # Developer team
        self.lbl_team = QLabel(get_text('developer_team'))
        self.lbl_team.setFont(QFont("B Titr", 16))
        self.lbl_team.setStyleSheet("color: #C0C0C0;")
        self.splash_layout.addWidget(self.lbl_team, alignment=Qt.AlignCenter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setFont(QFont("B Titr", 10))
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        self.splash_layout.addWidget(self.progress_bar)

        # Status text
        self.lbl_status = QLabel(get_text('loading'))
        self.lbl_status.setFont(QFont("B Titr", 13))
        self.lbl_status.setStyleSheet("color: #888888;")
        self.splash_layout.addWidget(self.lbl_status, alignment=Qt.AlignCenter)

        # Footer
        self.lbl_footer = QLabel(f"1404-1405 {get_text('Kharazmi')}")
        self.lbl_footer.setFont(QFont("B Titr", 11))
        self.lbl_footer.setStyleSheet("color: #666666;")
        self.splash_layout.addWidget(self.lbl_footer, alignment=Qt.AlignBottom)

        # Set size
        self.splash_widget.setFixedSize(550, 450)

        # Update splash
        self._update_splash()

        # Center on screen
        screen = self.screen().geometry()
        x = (screen.width() - 550) // 2
        y = (screen.height() - 450) // 2
        self.setGeometry(x, y, 550, 450)

        # Animation steps
        self.current_step = 0
        self.steps = [
            (get_text('loading_modules'), 10),
            (get_text('loading_database'), 25),
            (get_text('loading_fonts'), 40),
            (get_text('loading_theme'), 55),
            (get_text('checking_updates'), 70),
            (get_text('preparing_widgets'), 85),
            (get_text('starting_app'), 100)
        ]

        # Start timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._next_step)
        self._timer.start(600)

    def _update_splash(self):
        """Update splash image"""
        pixmap = self.splash_widget.grab()
        self.setPixmap(pixmap)
        self.repaint()
        QApplication.processEvents()

    def _next_step(self):
        """Next animation step"""
        if self.current_step < len(self.steps):
            text, value = self.steps[self.current_step]
            self.progress_bar.setValue(value)
            self.lbl_status.setText(text)
            self.current_step += 1
            self._update_splash()
        else:
            self._timer.stop()
            self.progress_bar.setValue(100)
            self.lbl_status.setText(get_text('starting_app'))
            self._update_splash()