# frames/dissertation_frame.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

"""
ماژول فریم ساخت جلد پایان‌نامه
این ماژول شامل کلاس‌های اصلی برای ساخت جلد پایان‌نامه از فایل PDF است
"""

import os
import logging
import traceback
from math import ceil
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QCheckBox, QFrame, QProgressBar,
    QDialog, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, QElapsedTimer
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent, QFont

import pymupdf

from variables.languages import get_text
from core.theme_manager import ThemeManager
from core.auth_manager import AuthManager
from core.feedback_manager import FeedbackManager
from func.file_handlers import FileHandler
from func.covers_func import CoverCreator
from func.select_page import PageSelector
from func.history_manager import HistoryManager
from func.toast_notification import NotificationManager

logger = logging.getLogger(__name__)


class DropFrame(QFrame):
    """
    فریم دریافت فایل PDF با قابلیت Drag & Drop و کلیک برای انتخاب فریم
    """

    file_dropped = pyqtSignal(str)  # ارسال سیگنال دریافت فایل PDF
    clicked = pyqtSignal()  # ارسال سیگنال کلیک بر روی صفحه Drag & Drop

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        logger.debug(f"DropFrame.__init__ called")
        try:
            self.setAcceptDrops(True)
            self.setMinimumHeight(80)
            self.setCursor(Qt.PointingHandCursor)

            font = QFont("B Titr", 12)

            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #00b4db;
                    border-radius: 12px;
                    background: rgba(0,180,219,0.1);
                }
                QFrame:hover {
                    border-color: #00ffcc;
                    background: rgba(0,255,204,0.1);
                }
            """)

            layout = QVBoxLayout(self)
            layout.setAlignment(Qt.AlignCenter)

            self.label = QLabel("📂 " + get_text('drag_drop_hint'))
            self.label.setFont(font)
            self.label.setStyleSheet("color: #888888;")
            layout.addWidget(self.label)

            logger.debug("DropFrame initialized successfully")
        except Exception as e:
            logger.exception(f"Error initializing DropFrame: {e}")

    def mousePressEvent(self, event: QMouseEvent) -> None:
        try:
            if event.button() == Qt.LeftButton:
                self.clicked.emit()
        except Exception as e:
            logger.exception(f"Error in mousePressEvent: {e}")

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        try:
            if event.mimeData().hasUrls():
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QFrame {
                        border: 2px solid #00ffcc;
                        border-radius: 12px;
                        background: rgba(0,255,204,0.2);
                    }
                """)
        except Exception as e:
            logger.exception(f"Error in dragEnterEvent: {e}")

    def dragLeaveEvent(self, event) -> None:
        try:
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #00b4db;
                    border-radius: 12px;
                    background: rgba(0,180,219,0.1);
                }
            """)
        except Exception as e:
            logger.exception(f"Error in dragLeaveEvent: {e}")

    def dropEvent(self, event) -> None:
        try:
            self.setStyleSheet("""
                QFrame {
                    border: 2px dashed #00b4db;
                    border-radius: 12px;
                    background: rgba(0,180,219,0.1);
                }
            """)
            files = [u.toLocalFile() for u in event.mimeData().urls()]
            if files:
                logger.info(f"File dropped: {files[0]}")
                self.file_dropped.emit(files[0])
        except Exception as e:
            logger.exception(f"Error in dropEvent: {e}")

    def update_text_colors(self, text_color: str) -> None:
        try:
            self.label.setStyleSheet(f"color: {text_color};")
        except Exception as e:
            logger.exception(f"Error in update_text_colors: {e}")


class CoverWorker(QThread):
    """ترد جداگانه برای ساخت جلد"""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool)
    error = pyqtSignal(str)

    def __init__(self, metadata: Dict[str, Any], pdf_path: str, save_path: str,
                 front_page: Optional[int] = None, back_page: Optional[int] = None) -> None:
        super().__init__()
        logger.info(f"CoverWorker.__init__ called")
        logger.debug(f"  - pdf_path: {pdf_path}")
        logger.debug(f"  - save_path: {save_path}")
        logger.debug(f"  - front_page: {front_page}")
        logger.debug(f"  - back_page: {back_page}")

        self.metadata = metadata
        self.pdf_path = pdf_path
        self.save_path = save_path
        self.front_page = front_page
        self.back_page = back_page
        self.elapsed_timer: Optional[QElapsedTimer] = None

    def run(self) -> None:
        logger.info("=" * 60)
        logger.info("CoverWorker.run STARTED")
        try:
            self.elapsed_timer = QElapsedTimer()
            self.elapsed_timer.start()
            logger.debug("Timer started")

            creator = CoverCreator(
                self.metadata,
                self.pdf_path,
                self.save_path,
                None,
                self.front_page,
                self.back_page
            )
            logger.debug("CoverCreator created successfully")

            creator.progress_callback = lambda v, s: self.progress.emit(v, s)
            logger.debug("Progress callback connected")

            logger.info("Starting cover creation...")
            success = creator.create_cover()
            logger.info(f"Cover creation completed, success: {success}")

            elapsed = self.elapsed_timer.elapsed() if self.elapsed_timer else 0
            logger.info(f"Cover creation took {elapsed}ms")

            self.finished.emit(success)

        except Exception as e:
            logger.exception(f"Error in CoverWorker.run: {e}")
            traceback.print_exc()
            self.error.emit(str(e))
        finally:
            logger.info("CoverWorker.run ENDED")
            logger.info("=" * 60)


class DissertationFrame(QWidget):
    """فریم اصلی ساخت جلد پایان‌نامه"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        logger.info("=" * 60)
        logger.info("DissertationFrame.__init__ STARTED")
        try:
            super().__init__(parent)
            self.parent_app = parent

            self.theme_manager = parent.theme_manager if parent else ThemeManager()
            self.auth_manager = AuthManager()
            self.feedback_manager = FeedbackManager()
            logger.debug("Managers initialized")

            self.selected_pdf: Optional[str] = None
            self.save_folder: Optional[str] = None
            self.metadata: Dict[str, Any] = {}
            self.cover_worker: Optional[CoverWorker] = None
            self._is_processing: bool = False

            self.setup_ui()
            self.apply_styles()
            self.apply_theme()

            logger.info("DissertationFrame.__init__ COMPLETED SUCCESSFULLY")
        except Exception as e:
            logger.exception(f"CRITICAL ERROR in DissertationFrame.__init__: {e}")
            traceback.print_exc()
            raise

    def _create_button(self, text: str) -> QPushButton:
        try:
            btn = QPushButton(text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFont(QFont("B Titr", 14))
            return btn
        except Exception as e:
            logger.exception(f"Error in _create_button: {e}")
            return QPushButton(text)

    def setup_ui(self) -> None:
        logger.info("DissertationFrame.setup_ui STARTED")
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(15, 15, 15, 15)
            main_layout.setSpacing(10)

            header_layout = self._create_header()
            main_layout.addLayout(header_layout)

            content_layout = self._create_content()
            main_layout.addLayout(content_layout)

            action_layout = self._create_action_buttons()
            main_layout.addLayout(action_layout)

            progress_layout = self._create_progress_bar()
            main_layout.addLayout(progress_layout)

            logger.info("DissertationFrame.setup_ui COMPLETED")
        except Exception as e:
            logger.exception(f"Error in setup_ui: {e}")
            traceback.print_exc()
            raise

    def _create_header(self) -> QHBoxLayout:
        try:
            header_layout = QHBoxLayout()

            self.btn_back = self._create_button(get_text('back'))
            self.btn_back.setFixedSize(80, 40)
            self.btn_back.setToolTip(get_text('back_tooltip'))
            self.btn_back.clicked.connect(lambda: self.parent_app.show_frame('main'))
            header_layout.addWidget(self.btn_back)

            header_layout.addStretch()

            self.lbl_title = QLabel(get_text('dissertation_cover').replace('\n', ''))
            self.lbl_title.setFont(QFont("B Titr", 24))
            self.lbl_title.setObjectName("pageTitle")
            header_layout.addWidget(self.lbl_title)

            header_layout.addStretch()

            self.btn_guide = self._create_button(get_text('guide_button'))
            self.btn_guide.setFixedSize(80, 40)
            self.btn_guide.setToolTip(get_text('guide_tooltip'))
            self.btn_guide.clicked.connect(lambda: self.parent_app.show_frame('guide'))
            header_layout.addWidget(self.btn_guide)

            return header_layout
        except Exception as e:
            logger.exception(f"Error in _create_header: {e}")
            return QHBoxLayout()

    def _create_content(self) -> QHBoxLayout:
        try:
            content_layout = QHBoxLayout()
            content_layout.setSpacing(15)

            file_frame = self._create_file_section()
            content_layout.addWidget(file_frame)

            input_frame = self._create_input_section()
            content_layout.addWidget(input_frame)

            return content_layout
        except Exception as e:
            logger.exception(f"Error in _create_content: {e}")
            return QHBoxLayout()

    def _create_file_section(self) -> QFrame:
        try:
            file_frame = QFrame()
            file_frame.setObjectName("sectionFrame")
            file_frame.setFixedWidth(280)
            file_layout = QVBoxLayout(file_frame)
            file_layout.setSpacing(10)

            self.lbl_file_section = QLabel(get_text('file_section'))
            self.lbl_file_section.setFont(QFont("B Titr", 18))
            self.lbl_file_section.setObjectName("sectionTitle")
            file_layout.addWidget(self.lbl_file_section, alignment=Qt.AlignCenter)

            self.drop_frame = DropFrame()
            self.drop_frame.file_dropped.connect(self.on_file_dropped)
            self.drop_frame.clicked.connect(self.select_pdf_file)
            file_layout.addWidget(self.drop_frame)

            self.lbl_pdf_status = QLabel(get_text('no_file_selected'))
            self.lbl_pdf_status.setFont(QFont("B Titr", 12))
            self.lbl_pdf_status.setObjectName("statusLabel")
            file_layout.addWidget(self.lbl_pdf_status)

            self.btn_select_pdf = self._create_button(get_text('select_file'))
            self.btn_select_pdf.setToolTip(get_text('select_file_tooltip'))
            self.btn_select_pdf.clicked.connect(self.select_pdf_file)
            file_layout.addWidget(self.btn_select_pdf)

            self.lbl_save_status = QLabel(get_text('no_folder_selected'))
            self.lbl_save_status.setFont(QFont("B Titr", 12))
            self.lbl_save_status.setObjectName("statusLabel")
            file_layout.addWidget(self.lbl_save_status)

            self.btn_select_folder = self._create_button(get_text('save_location'))
            self.btn_select_folder.setToolTip(get_text('save_location_tooltip'))
            self.btn_select_folder.clicked.connect(self.select_save_folder)
            file_layout.addWidget(self.btn_select_folder)

            file_layout.addStretch()
            return file_frame
        except Exception as e:
            logger.exception(f"Error in _create_file_section: {e}")
            return QFrame()

    def _create_input_section(self) -> QFrame:
        try:
            input_frame = QFrame()
            input_frame.setObjectName("sectionFrame")
            input_frame.setFixedWidth(320)
            input_layout = QVBoxLayout(input_frame)
            input_layout.setSpacing(10)

            self.lbl_info_title = QLabel(get_text('info_title'))
            self.lbl_info_title.setFont(QFont("B Titr", 18))
            self.lbl_info_title.setObjectName("sectionTitle")
            input_layout.addWidget(self.lbl_info_title, alignment=Qt.AlignCenter)

            self.ent_title = QLineEdit()
            self.ent_title.setFont(QFont("B Titr", 14))
            self.ent_title.setPlaceholderText(get_text('title_placeholder'))
            self.ent_title.setToolTip(get_text('title_tooltip'))
            input_layout.addWidget(self.ent_title)

            self.ent_author = QLineEdit()
            self.ent_author.setFont(QFont("B Titr", 14))
            self.ent_author.setPlaceholderText(get_text('author_placeholder'))
            self.ent_author.setToolTip(get_text('author_tooltip'))
            input_layout.addWidget(self.ent_author)

            date_layout = QHBoxLayout()
            self.btn_calendar = self._create_button('📅')
            self.btn_calendar.setFixedSize(45, 45)
            self.btn_calendar.setToolTip(get_text('calendar_tooltip'))
            self.btn_calendar.clicked.connect(self.show_calendar)
            date_layout.addWidget(self.btn_calendar)

            self.ent_date = QLineEdit()
            self.ent_date.setFont(QFont("B Titr", 14))
            self.ent_date.setPlaceholderText(get_text('date_placeholder'))
            self.ent_date.setToolTip(get_text('date_tooltip'))
            date_layout.addWidget(self.ent_date)
            input_layout.addLayout(date_layout)

            level_layout = QHBoxLayout()
            self.lbl_level = QLabel(get_text('level'))
            self.lbl_level.setFont(QFont("B Titr", 14))
            self.lbl_level.setObjectName("formLabel")
            level_layout.addWidget(self.lbl_level)

            self.cmb_level = QComboBox()
            self.cmb_level.addItems([get_text('no_level'), '1', '2', '3', '4'])
            self.cmb_level.setFont(QFont("B Titr", 14))
            self.cmb_level.setToolTip(get_text('level_tooltip'))
            level_layout.addWidget(self.cmb_level)
            input_layout.addLayout(level_layout)

            self.chk_no_back_cover = QCheckBox(get_text('no_back_cover'))
            self.chk_no_back_cover.setFont(QFont("B Titr", 14))
            self.chk_no_back_cover.setToolTip(get_text('no_back_cover_tooltip'))
            input_layout.addWidget(self.chk_no_back_cover)

            self.chk_both_sides = QCheckBox(get_text('both_sides_printed'))
            self.chk_both_sides.setFont(QFont("B Titr", 14))
            self.chk_both_sides.setChecked(True)
            self.chk_both_sides.setToolTip(get_text('both_sides_tooltip'))
            input_layout.addWidget(self.chk_both_sides)

            self.ent_spine = QLineEdit()
            self.ent_spine.setFont(QFont("B Titr", 14))
            self.ent_spine.setPlaceholderText(get_text('spine_placeholder'))
            self.ent_spine.setToolTip(get_text('spine_tooltip'))
            input_layout.addWidget(self.ent_spine)

            self.btn_calc_spine = self._create_button(get_text('spine_calculation'))
            self.btn_calc_spine.setToolTip(get_text('spine_calc_tooltip'))
            self.btn_calc_spine.clicked.connect(self.calculate_spine)
            input_layout.addWidget(self.btn_calc_spine)

            return input_frame
        except Exception as e:
            logger.exception(f"Error in _create_input_section: {e}")
            return QFrame()

    def _create_action_buttons(self) -> QHBoxLayout:
        try:
            action_layout = QHBoxLayout()
            action_layout.setSpacing(20)
            action_layout.setAlignment(Qt.AlignCenter)

            self.btn_start = self._create_button(get_text('start_making'))
            self.btn_start.setFixedSize(180, 60)
            self.btn_start.setToolTip(get_text('start_tooltip'))
            self.btn_start.clicked.connect(self.start_making)
            action_layout.addWidget(self.btn_start)

            self.btn_refresh = self._create_button(get_text('refresh_page'))
            self.btn_refresh.setFixedSize(140, 60)
            self.btn_refresh.setToolTip(get_text('refresh_tooltip'))
            self.btn_refresh.clicked.connect(self.refresh_form)
            action_layout.addWidget(self.btn_refresh)

            return action_layout
        except Exception as e:
            logger.exception(f"Error in _create_action_buttons: {e}")
            return QHBoxLayout()

    def _create_progress_bar(self) -> QVBoxLayout:
        try:
            progress_layout = QVBoxLayout()
            progress_layout.setSpacing(5)

            self.progress_bar = QProgressBar()
            self.progress_bar.setVisible(False)
            self.progress_bar.setFont(QFont("B Titr", 10))
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    background-color: #2a2a2a;
                    border: 2px solid #3a3a4e;
                    border-radius: 8px;
                    text-align: center;
                    color: white;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00b4db, stop:1 #00ffcc);
                    border-radius: 6px;
                }
            """)
            progress_layout.addWidget(self.progress_bar)

            self.lbl_progress_status = QLabel('')
            self.lbl_progress_status.setVisible(False)
            self.lbl_progress_status.setFont(QFont("B Titr", 12))
            self.lbl_progress_status.setStyleSheet("color: #00ffcc;")
            progress_layout.addWidget(self.lbl_progress_status, alignment=Qt.AlignCenter)

            return progress_layout
        except Exception as e:
            logger.exception(f"Error in _create_progress_bar: {e}")
            return QVBoxLayout()

    def apply_styles(self) -> None:
        try:
            bg_color = self.theme_manager.get_background_color()
            text_color = self.theme_manager.get_text_color_for_background(bg_color) if bg_color else '#FFFFFF'

            style = f"""
                QFrame#sectionFrame {{
                    background: rgba(0,0,0,0.3);
                    border: 2px solid #3a3a4e;
                    border-radius: 12px;
                    padding: 15px;
                }}
                QLabel#sectionTitle {{
                    color: {text_color};
                    font-family: 'B Titr';
                }}
                QLabel#pageTitle {{
                    color: {text_color};
                    font-family: 'B Titr';
                }}
                QLabel#statusLabel {{
                    color: #888888;
                    font-family: 'B Titr';
                }}
                QLabel#formLabel {{
                    color: {text_color};
                    font-family: 'B Titr';
                }}
                QLineEdit {{
                    background: rgba(0,0,0,0.5);
                    color: {text_color};
                    border: 2px solid #00b4db;
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'B Titr';
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border-color: #00ffcc;
                }}
                QCheckBox {{
                    color: {text_color};
                    font-family: 'B Titr';
                    font-size: 14px;
                    spacing: 8px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid #00b4db;
                    border-radius: 4px;
                    background: transparent;
                }}
                QCheckBox::indicator:checked {{
                    background: #00b4db;
                }}
                QComboBox {{
                    background: rgba(0,0,0,0.5);
                    color: {text_color};
                    border: 2px solid #00b4db;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-family: 'B Titr';
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
            """
            self.setStyleSheet(style)
        except Exception as e:
            logger.exception(f"Error in apply_styles: {e}")

    def apply_theme(self) -> None:
        try:
            color = self.theme_manager.get_button_color()
            style = self.theme_manager.get_button_style(color)
            for btn in self.findChildren(QPushButton):
                btn.setStyleSheet(style)
        except Exception as e:
            logger.exception(f"Error in apply_theme: {e}")

    def update_text_colors(self, text_color: str) -> None:
        try:
            color = self.theme_manager.get_button_color()

            self.lbl_title.setStyleSheet(f"""
                QLabel#pageTitle {{
                    color: {text_color};
                    font-family: 'B Titr';
                    font-size: 24px;
                }}
            """)

            for label in [self.lbl_file_section, self.lbl_info_title]:
                if label:
                    label.setStyleSheet(f"""
                        QLabel#sectionTitle {{
                            color: {text_color};
                            font-family: 'B Titr';
                            font-size: 18px;
                        }}
                    """)

            for label in [self.lbl_pdf_status, self.lbl_save_status]:
                if label:
                    label.setStyleSheet(f"""
                        QLabel#statusLabel {{
                            color: #888888;
                            font-family: 'B Titr';
                            font-size: 12px;
                        }}
                    """)

            for entry in self.findChildren(QLineEdit):
                entry.setStyleSheet(f"""
                    QLineEdit {{
                        background: rgba(0,0,0,0.5);
                        color: {text_color};
                        border: 2px solid {color};
                        border-radius: 8px;
                        padding: 8px 12px;
                        font-family: 'B Titr';
                        font-size: 14px;
                    }}
                    QLineEdit:focus {{
                        border-color: #00ffcc;
                    }}
                """)

            for checkbox in self.findChildren(QCheckBox):
                checkbox.setStyleSheet(f"""
                    QCheckBox {{
                        color: {text_color};
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

            self.cmb_level.setStyleSheet(f"""
                QComboBox {{
                    background: rgba(0,0,0,0.5);
                    color: {text_color};
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-family: 'B Titr';
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

            if hasattr(self, 'drop_frame'):
                self.drop_frame.setStyleSheet(f"""
                    QFrame {{
                        border: 2px dashed {color};
                        border-radius: 12px;
                        background: rgba(0,180,219,0.1);
                    }}
                    QFrame:hover {{
                        border-color: #00ffcc;
                        background: rgba(0,255,204,0.1);
                    }}
                """)
                self.drop_frame.update_text_colors(text_color)

        except Exception as e:
            logger.exception(f"Error in update_text_colors: {e}")

    def on_file_dropped(self, file_path: str) -> None:
        logger.info(f"File dropped: {file_path}")
        try:
            if file_path.lower().endswith('.pdf'):
                if os.path.exists(file_path):
                    self.selected_pdf = file_path
                    self.lbl_pdf_status.setText(os.path.basename(file_path))
                    self.lbl_pdf_status.setStyleSheet("color: #00ffcc;")
                    self._show_safe_notification('success', get_text('file_selected'))
                else:
                    self._show_safe_notification('error', "فایل وجود ندارد")
            else:
                self._show_safe_notification('warning', get_text('pdf_only'))
        except Exception as e:
            logger.exception(f"Error in on_file_dropped: {e}")
            self._show_safe_notification('error', f"خطا: {str(e)}")

    def select_pdf_file(self) -> None:
        logger.info("select_pdf_file called")
        try:
            file_path = FileHandler.select_pdf_file(self)
            if file_path and os.path.exists(file_path):
                self.selected_pdf = file_path
                self.lbl_pdf_status.setText(os.path.basename(file_path))
                self.lbl_pdf_status.setStyleSheet("color: #00ffcc;")
                logger.info(f"PDF file selected via dialog: {file_path}")
        except Exception as e:
            logger.exception(f"Error in select_pdf_file: {e}")
            self._show_safe_notification('error', f"خطا در انتخاب فایل: {str(e)}")

    def select_save_folder(self) -> None:
        logger.info("select_save_folder called")
        try:
            file_path = FileHandler.select_save_location(self)
            if file_path:
                self.save_folder = file_path
                self.lbl_save_status.setText(os.path.basename(file_path))
                self.lbl_save_status.setStyleSheet("color: #00ffcc;")
                logger.info(f"Save folder selected: {file_path}")
        except Exception as e:
            logger.exception(f"Error in select_save_folder: {e}")
            self._show_safe_notification('error', f"خطا در انتخاب مسیر: {str(e)}")

    def show_calendar(self) -> None:
        logger.info("show_calendar called")
        try:
            from frames.date_dialog import DateDialog
            dialog = DateDialog(self)
            if dialog.exec_():
                date_str = dialog.get_selected_date()
                if date_str:
                    self.ent_date.setText(date_str)
                    logger.info(f"Date selected: {date_str}")
        except ImportError as e:
            logger.exception(f"Could not import DateDialog: {e}")
            self._show_safe_notification('error', "ماژول تقویم یافت نشد")
        except Exception as e:
            logger.exception(f"Error in show_calendar: {e}")
            self._show_safe_notification('error', f"خطا در نمایش تقویم: {str(e)}")

    def calculate_spine(self) -> None:
        logger.info("calculate_spine called")
        try:
            if not self.selected_pdf or not os.path.exists(self.selected_pdf):
                logger.warning("No PDF selected, showing input dialog")
                self._show_spine_input_dialog()
                return

            doc = pymupdf.open(self.selected_pdf)
            page_count = doc.page_count
            doc.close()

            both_sides = self.chk_both_sides.isChecked()
            effective_pages = page_count if both_sides else page_count * 2
            spine = int(ceil(((effective_pages) * 0.8) / 20)) + 5
            self.ent_spine.setText(str(spine))
            logger.info(f"Spine calculated: {spine}mm")
        except Exception as e:
            logger.exception(f"Error in calculate_spine: {e}")
            self._show_safe_notification('error', f"{get_text('error')}: {str(e)}")

    def _show_spine_input_dialog(self) -> None:
        logger.info("_show_spine_input_dialog called")
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(get_text('spine_calculation'))
            dialog.setFixedSize(380, 250)
            dialog.setModal(True)
            dialog.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)

            bg_color = self.theme_manager.get_background_color() or "#00006d"
            button_color = self.theme_manager.get_button_color()
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
            darker_bg = self.theme_manager._darken_color(bg_color, 30)

            dialog.setStyleSheet(f"""
                QDialog {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 {bg_color},
                        stop:1 {darker_bg});
                    border-radius: 15px;
                }}
                QLabel {{
                    color: {text_color};
                    font-family: 'B Titr';
                }}
                QLineEdit {{
                    background: rgba(0,0,0,0.3);
                    color: {text_color};
                    border: 2px solid {button_color};
                    border-radius: 8px;
                    padding: 8px 12px;
                    font-family: 'B Titr';
                    font-size: 14px;
                }}
                QLineEdit:focus {{
                    border-color: #00ffcc;
                }}
            """)

            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)

            label = QLabel(get_text('dissertation_number'))
            label.setFont(QFont("B Titr", 16))
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            entry = QLineEdit()
            entry.setFont(QFont("B Titr", 14))
            entry.setPlaceholderText(get_text('enter_page_count'))
            entry.setAlignment(Qt.AlignCenter)
            layout.addWidget(entry)

            both_sides = self.chk_both_sides.isChecked()
            status_text = get_text('both_sides_printed') + ": " + (get_text('yes') if both_sides else get_text('no'))
            if not both_sides:
                status_text += " (" + get_text('pages_doubled') + ")"
            status_label = QLabel(status_text)
            status_label.setFont(QFont("B Titr", 12))
            status_label.setStyleSheet(f"color: #FFD700;")
            status_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(status_label)

            button_layout = QHBoxLayout()
            button_layout.setSpacing(20)
            button_layout.setAlignment(Qt.AlignCenter)

            def on_ok() -> None:
                try:
                    page_count = int(entry.text())
                    if page_count <= 0:
                        self._show_safe_notification('warning', get_text('enter_valid_number'))
                        return
                    both_sides = self.chk_both_sides.isChecked()
                    effective_pages = page_count if both_sides else page_count * 2
                    spine = int(ceil(((effective_pages) * 0.8) / 20)) + 5
                    self.ent_spine.setText(str(spine))
                    logger.info(f"Manual spine calculated: {spine}mm")
                    dialog.accept()
                except ValueError:
                    self._show_safe_notification('warning', get_text('enter_valid_number'))

            btn_cancel = QPushButton(get_text('cancel'))
            btn_cancel.setFont(QFont("B Titr", 14))
            btn_cancel.setFixedSize(120, 40)
            btn_cancel.clicked.connect(dialog.reject)
            btn_cancel.setStyleSheet(self.theme_manager.get_button_style(button_color))

            btn_ok = QPushButton(get_text('apply'))
            btn_ok.setFont(QFont("B Titr", 14))
            btn_ok.setFixedSize(120, 40)
            btn_ok.clicked.connect(on_ok)
            btn_ok.setStyleSheet(self.theme_manager.get_button_style(button_color))

            button_layout.addWidget(btn_cancel)
            button_layout.addWidget(btn_ok)

            layout.addLayout(button_layout)
            entry.returnPressed.connect(on_ok)
            dialog.exec_()
        except Exception as e:
            logger.exception(f"Error in _show_spine_input_dialog: {e}")
            self._show_safe_notification('error', f"خطا: {str(e)}")

    def _show_safe_notification(self, msg_type: str, message: str) -> None:
        try:
            if msg_type == 'success':
                QMessageBox.information(self, get_text('success'), message)
            elif msg_type == 'error':
                QMessageBox.critical(self, get_text('error'), message)
            elif msg_type == 'warning':
                QMessageBox.warning(self, get_text('warning'), message)
            else:
                QMessageBox.information(self, get_text('info'), message)
        except Exception as e:
            logger.exception(f"Error in _show_safe_notification: {e}")

    def start_making(self) -> None:
        """شروع فرآیند ساخت جلد با اعتبارسنجی کامل"""
        logger.info("=" * 60)
        logger.info("start_making STARTED")
        try:
            if self._is_processing:
                logger.warning("Already processing, ignoring duplicate request")
                self._show_safe_notification('warning', "در حال حاضر ساخت جلد در حال اجراست")
                return

            # ========== اعتبارسنجی فیلدها ==========
            empty_fields = []
            logger.debug("Validating fields...")

            if not self.ent_title.text().strip():
                empty_fields.append(get_text('title'))
                logger.debug("Title is empty")

            if not self.ent_author.text().strip():
                empty_fields.append(get_text('author'))
                logger.debug("Author is empty")

            if not self.ent_date.text().strip():
                empty_fields.append(get_text('date'))
                logger.debug("Date is empty")

            spine = self.ent_spine.text().strip()
            if not spine:
                empty_fields.append(get_text('spine'))
                logger.debug("Spine is empty")
            elif not spine.isdigit():
                logger.warning(f"Spine is not a number: {spine}")
                self._show_safe_notification('error', get_text('spine_number_error'))
                return

            if not self.selected_pdf:
                empty_fields.append(get_text('pdf_file'))
                logger.debug("No PDF selected")
            elif not os.path.exists(self.selected_pdf):
                logger.warning(f"PDF file not found: {self.selected_pdf}")
                self._show_safe_notification('error', "فایل PDF انتخاب‌شده وجود ندارد")
                return

            if not self.save_folder:
                empty_fields.append(get_text('save_location'))
                logger.debug("No save location selected")
            else:
                parent_dir = os.path.dirname(self.save_folder)
                if parent_dir and not os.path.exists(parent_dir):
                    try:
                        os.makedirs(parent_dir, exist_ok=True)
                        logger.info(f"Created directory: {parent_dir}")
                    except OSError as e:
                        logger.error(f"Failed to create directory: {e}")
                        self._show_safe_notification('error', f"خطا در ایجاد پوشه: {e}")
                        return
                if parent_dir and not os.access(parent_dir, os.W_OK):
                    logger.error(f"No write permission: {parent_dir}")
                    self._show_safe_notification('error', f"مجوز نوشتن در مسیر {parent_dir} وجود ندارد.")
                    return

            if empty_fields:
                fields_text = " - ".join(empty_fields)
                logger.warning(f"Empty fields: {fields_text}")
                self._show_safe_notification('error', get_text('empty_fields_error').format(fields_text))
                return

            logger.info("All fields validated successfully")

            # ========== آماده‌سازی متادیتا ==========
            level = self.cmb_level.currentText()
            if level == get_text('no_level'):
                level = ''

            self.metadata = {
                'title': self.ent_title.text().strip(),
                'author': self.ent_author.text().strip(),
                'date': self.ent_date.text().strip(),
                'spine': int(spine),
                'both_sides_printed': self.chk_both_sides.isChecked(),
                'output_path': self.save_folder,
                'level': level,
                'no_back_cover': self.chk_no_back_cover.isChecked(),
            }
            logger.debug(f"Metadata prepared: {self.metadata}")

            # ========== انتخاب صفحات ==========
            logger.info("Selecting front page...")
            try:
                selector_front = PageSelector(self, self.selected_pdf, get_text('title_on'), False)
                if not selector_front.exec_():
                    logger.info("Front page selection cancelled")
                    return
                front_page = selector_front.selected_page
                logger.info(f"Front page selected: {front_page}")
            except Exception as e:
                logger.exception(f"Error in front page selector: {e}")
                self._show_safe_notification('error', f"خطا در انتخاب صفحه روی جلد: {str(e)}")
                return

            back_page = None
            if not self.chk_no_back_cover.isChecked():
                logger.info("Selecting back page...")
                try:
                    selector_back = PageSelector(self, self.selected_pdf, get_text('title_back'),
                                                 self.chk_no_back_cover.isChecked())
                    if not selector_back.exec_():
                        logger.info("Back page selection cancelled")
                        return
                    back_page = selector_back.selected_page
                    logger.info(f"Back page selected: {back_page}")
                except Exception as e:
                    logger.exception(f"Error in back page selector: {e}")
                    self._show_safe_notification('error', f"خطا در انتخاب صفحه پشت جلد: {str(e)}")
                    return

            # ========== شروع ساخت ==========
            self._is_processing = True
            self.progress_bar.setVisible(True)
            self.lbl_progress_status.setVisible(True)
            self.progress_bar.setValue(0)
            self.btn_start.setEnabled(False)
            logger.info("Starting cover creation worker...")

            try:
                self.cover_worker = CoverWorker(
                    self.metadata,
                    self.selected_pdf,
                    self.save_folder,
                    front_page,
                    back_page
                )
                logger.debug("CoverWorker created")

                # اتصال سیگنال‌ها با لاگ
                self.cover_worker.progress.connect(self._update_progress)
                logger.debug("Progress signal connected")

                # اتصال finished با لامبدا برای اطمینان از اجرا
                self.cover_worker.finished.connect(lambda s: self._on_cover_finished(s))
                logger.debug("Finished signal connected with lambda")

                self.cover_worker.error.connect(self._on_cover_error)
                logger.debug("Error signal connected")

                self.cover_worker.finished.connect(self.cover_worker.deleteLater)
                self.cover_worker.error.connect(self.cover_worker.deleteLater)
                logger.debug("DeleteLater connections done")

                self.cover_worker.start()
                logger.info("Cover worker started successfully")

            except Exception as e:
                logger.exception(f"Error starting cover worker: {e}")
                self._is_processing = False
                self.btn_start.setEnabled(True)
                self._show_safe_notification('error', f"خطا در شروع ساخت: {str(e)}")

        except Exception as e:
            logger.exception(f"CRITICAL Error in start_making: {e}")
            traceback.print_exc()
            self._is_processing = False
            self.btn_start.setEnabled(True)
            self._show_safe_notification('error', f"خطا: {str(e)}")
        finally:
            logger.info("start_making ENDED")
            logger.info("=" * 60)

    def _update_progress(self, value: int, status: str) -> None:
        try:
            self.progress_bar.setValue(value)
            self.lbl_progress_status.setText(status)
        except Exception as e:
            logger.exception(f"Error in _update_progress: {e}")

    def _on_cover_finished(self, success: bool) -> None:
        """پردازش پایان ساخت جلد با مدیریت کامل خطا"""
        logger.info("=" * 60)
        logger.info(f"_on_cover_finished STARTED, success: {success}")
        try:
            self.progress_bar.setValue(100)
            self.lbl_progress_status.setText(get_text('progress_complete'))
            self.btn_start.setEnabled(True)
            self._is_processing = False

            if success:
                logger.info("Cover creation SUCCESSFUL")

                # نمایش پیام موفقیت
                try:
                    QMessageBox.information(self, get_text('success'), get_text('cover_created_success'))
                    logger.debug("Success message shown")
                except Exception as e:
                    logger.error(f"Error showing success message: {e}")

                # افزودن به تاریخچه
                try:
                    history_manager = HistoryManager()
                    history_manager.add_to_history({
                        'file_name': os.path.basename(self.save_folder),
                        'save_path': self.save_folder,
                        'metadata': self.metadata,
                        'pdf_path': self.selected_pdf
                    })
                    logger.debug("History added successfully")
                except Exception as e:
                    logger.error(f"Error adding to history: {e}")

                # نمایش دیالوگ بازخورد با تاخیر
                try:
                    logger.info("Showing feedback dialog with delay...")
                    QTimer.singleShot(500, self._show_feedback_dialog_safe)
                    logger.info("Feedback dialog scheduled")
                except Exception as e:
                    logger.error(f"Error scheduling feedback dialog: {e}")

            else:
                logger.warning("Cover creation FAILED")
                try:
                    QMessageBox.warning(self, get_text('error'), get_text('progress_error'))
                except Exception as e:
                    logger.error(f"Error showing warning: {e}")

            # ریست نوار پیشرفت
            try:
                QTimer.singleShot(2000, self.reset_progress)
            except Exception as e:
                logger.error(f"Error in timer: {e}")
                self.reset_progress()

        except Exception as e:
            logger.exception(f"CRITICAL Error in _on_cover_finished: {e}")
            traceback.print_exc()
            self.btn_start.setEnabled(True)
            self._is_processing = False
            try:
                QMessageBox.critical(self, get_text('error'), f"خطا در پایان ساخت جلد:\n{str(e)}")
            except:
                pass
        finally:
            logger.info("_on_cover_finished ENDED")
            logger.info("=" * 60)

    def _show_feedback_dialog_safe(self) -> None:
        """نمایش دیالوگ بازخورد با مدیریت کامل خطا"""
        logger.info("=" * 50)
        logger.info("_show_feedback_dialog_safe STARTED")
        try:
            # اگر دیالوگ بازخورد مشکل دارد، فقط یک پیام ساده نشان بده
            try:
                from frames.feedback_dialog import FeedbackDialog
                logger.debug("FeedbackDialog imported successfully")

                user_id = self.auth_manager.current_user if self.auth_manager.is_authenticated() else None
                logger.debug(f"user_id: {user_id}")

                logger.info("Creating FeedbackDialog...")
                dialog = FeedbackDialog(self, user_id=user_id, cover_type='dissertation')
                logger.info("FeedbackDialog created successfully")

                logger.info("Executing FeedbackDialog...")
                dialog.exec_()
                logger.info("FeedbackDialog exec completed")

            except ImportError as e:
                logger.exception(f"Could not import FeedbackDialog: {e}")
                QMessageBox.information(self, get_text('thanks'), get_text('feedback_thanks'))
            except Exception as e:
                logger.exception(f"Error in FeedbackDialog: {e}")
                # در صورت هر گونه خطا، یک پیام ساده نشان بده
                QMessageBox.information(self, get_text('thanks'), get_text('feedback_thanks'))

        except Exception as e:
            logger.exception(f"CRITICAL Error in _show_feedback_dialog_safe: {e}")
            try:
                QMessageBox.information(self, get_text('thanks'), get_text('feedback_thanks'))
            except:
                pass
        finally:
            logger.info("_show_feedback_dialog_safe ENDED")
            logger.info("=" * 50)

    def _on_cover_error(self, error_msg: str) -> None:
        logger.error(f"_on_cover_error called: {error_msg}")
        try:
            self.btn_start.setEnabled(True)
            self._is_processing = False
            QMessageBox.critical(self, get_text('error'), f"{get_text('error')}: {error_msg}")
        except Exception as e:
            logger.exception(f"Error in _on_cover_error: {e}")
        finally:
            try:
                QTimer.singleShot(2000, self.reset_progress)
            except Exception:
                self.reset_progress()

    def reset_progress(self) -> None:
        try:
            self.progress_bar.setVisible(False)
            self.lbl_progress_status.setVisible(False)
            self.progress_bar.setValue(0)
            self.btn_start.setEnabled(True)
            self._is_processing = False
        except Exception as e:
            logger.exception(f"Error in reset_progress: {e}")

    def refresh_form(self) -> None:
        logger.info("refresh_form called")
        try:
            self.ent_title.clear()
            self.ent_author.clear()
            self.ent_date.clear()
            self.ent_spine.clear()
            self.chk_both_sides.setChecked(True)
            self.chk_no_back_cover.setChecked(False)
            self.cmb_level.setCurrentIndex(0)
            self.lbl_pdf_status.setText(get_text('no_file_selected'))
            self.lbl_pdf_status.setStyleSheet("color: #888888;")
            self.lbl_save_status.setText(get_text('no_folder_selected'))
            self.lbl_save_status.setStyleSheet("color: #888888;")
            self.selected_pdf = None
            self.save_folder = None
            self._show_safe_notification('success', get_text('form_cleared'))
        except Exception as e:
            logger.exception(f"Error in refresh_form: {e}")

    def update_texts(self) -> None:
        try:
            self.btn_back.setText(get_text('back'))
            self.btn_back.setToolTip(get_text('back_tooltip'))
            self.lbl_title.setText(get_text('dissertation_cover').replace('\n', ''))
            self.btn_guide.setText(get_text('guide_button'))
            self.btn_guide.setToolTip(get_text('guide_tooltip'))
            self.lbl_file_section.setText(get_text('file_section'))
            self.lbl_pdf_status.setText(get_text('no_file_selected'))
            self.btn_select_pdf.setText(get_text('select_file'))
            self.btn_select_pdf.setToolTip(get_text('select_file_tooltip'))
            self.lbl_save_status.setText(get_text('no_folder_selected'))
            self.btn_select_folder.setText(get_text('save_location'))
            self.btn_select_folder.setToolTip(get_text('save_location_tooltip'))
            self.lbl_info_title.setText(get_text('info_title'))
            self.ent_title.setPlaceholderText(get_text('title_placeholder'))
            self.ent_title.setToolTip(get_text('title_tooltip'))
            self.ent_author.setPlaceholderText(get_text('author_placeholder'))
            self.ent_author.setToolTip(get_text('author_tooltip'))
            self.ent_date.setPlaceholderText(get_text('date_placeholder'))
            self.ent_date.setToolTip(get_text('date_tooltip'))
            self.lbl_level.setText(get_text('level'))
            self.cmb_level.setToolTip(get_text('level_tooltip'))
            self.chk_no_back_cover.setText(get_text('no_back_cover'))
            self.chk_no_back_cover.setToolTip(get_text('no_back_cover_tooltip'))
            self.chk_both_sides.setText(get_text('both_sides_printed'))
            self.chk_both_sides.setToolTip(get_text('both_sides_tooltip'))
            self.ent_spine.setPlaceholderText(get_text('spine_placeholder'))
            self.ent_spine.setToolTip(get_text('spine_tooltip'))
            self.btn_calc_spine.setText(get_text('spine_calculation'))
            self.btn_calc_spine.setToolTip(get_text('spine_calc_tooltip'))
            self.btn_start.setText(get_text('start_making'))
            self.btn_start.setToolTip(get_text('start_tooltip'))
            self.btn_refresh.setText(get_text('refresh_page'))
            self.btn_refresh.setToolTip(get_text('refresh_tooltip'))
            self.drop_frame.label.setText("📂 " + get_text('drag_drop_hint'))
            self.cmb_level.clear()
            self.cmb_level.addItems([get_text('no_level'), '1', '2', '3', '4'])
        except Exception as e:
            logger.exception(f"Error in update_texts: {e}")

    def update_theme(self) -> None:
        try:
            self.apply_theme()
        except Exception as e:
            logger.exception(f"Error in update_theme: {e}")