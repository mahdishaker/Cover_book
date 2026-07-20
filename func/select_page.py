# func/select_page.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import traceback
import logging

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QScrollArea, QWidget, QMessageBox, QGridLayout,
    QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QMutex, QMutexLocker
from PyQt5.QtGui import QPixmap, QImage, QFont, QPainter, QColor

import pymupdf

from variables.languages import get_text
from func.toast_notification import NotificationManager
from core.theme_manager import ThemeManager

logger = logging.getLogger(__name__)


class PageLoader(QThread):
    """بارگذاری صفحات در ترد جداگانه با مدیریت خطا"""

    page_loaded = pyqtSignal(int, QPixmap)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, pdf_path, title, no_back_cover=False):
        super().__init__()
        self.pdf_path = pdf_path
        self.title = title
        self.no_back_cover = no_back_cover
        self._is_running = True
        self._mutex = QMutex()

    def run(self):
        doc = None
        try:
            if not os.path.exists(self.pdf_path):
                self.error.emit(get_text('page_selector_pdf_not_found'))
                return

            doc = pymupdf.open(self.pdf_path)
            page_count = doc.page_count
            if page_count == 0:
                self.error.emit(get_text('page_selector_pdf_empty'))
                return

            pages_to_show = []
            if self.title == get_text('title_on'):
                pages_to_show = list(range(min(10, page_count)))
            else:
                if self.no_back_cover:
                    self.error.emit(get_text('page_selector_no_back_cover_ok'))
                    return
                else:
                    start = max(0, page_count - 10)
                    pages_to_show = list(range(start, page_count))

            if not pages_to_show:
                self.error.emit(get_text('page_selector_no_pages'))
                return

            for i in pages_to_show:
                if not self._is_running:
                    break

                try:
                    page = doc[i]
                    zoom = 0.25
                    mat = pymupdf.Matrix(zoom, zoom)
                    pix = page.get_pixmap(matrix=mat)

                    pixmap = self._pix_to_qpixmap(pix)
                    if pixmap and not pixmap.isNull():
                        scaled = pixmap.scaled(200, 260, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.page_loaded.emit(i, scaled)
                    else:
                        placeholder = self._create_placeholder(i)
                        self.page_loaded.emit(i, placeholder)

                except Exception as e:
                    logger.warning(f"Error loading page {i}: {e}")
                    continue

            self.finished.emit()

        except Exception as e:
            error_msg = get_text('page_selector_pdf_error').format(str(e))
            logger.error(error_msg)
            traceback.print_exc()
            self.error.emit(error_msg)
        finally:
            if doc:
                try:
                    doc.close()
                except:
                    pass
            self._is_running = False

    def _pix_to_qpixmap(self, pix):
        try:
            img_bytes = pix.tobytes("png")
            if img_bytes:
                qimage = QImage.fromData(img_bytes)
                if qimage and not qimage.isNull():
                    return QPixmap.fromImage(qimage)
        except:
            pass
        try:
            img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            if img and not img.isNull():
                return QPixmap.fromImage(img)
        except:
            pass
        try:
            img_bytes = pix.tobytes("ppm")
            if img_bytes:
                qimage = QImage.fromData(img_bytes)
                if qimage and not qimage.isNull():
                    return QPixmap.fromImage(qimage)
        except:
            pass
        return None

    def _create_placeholder(self, page_num):
        pixmap = QPixmap(200, 260)
        pixmap.fill(QColor(40, 40, 60))
        painter = QPainter(pixmap)
        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("B Titr", 14))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, get_text('page_selector_placeholder').format(page_num + 1))
        painter.end()
        return pixmap

    def stop(self):
        """متوقف کردن ترد با اطمینان از پایان کار"""
        with QMutexLocker(self._mutex):
            self._is_running = False
        self.quit()
        self.wait(1000)


class PageSelector(QDialog):
    """دیالوگ انتخاب صفحه از PDF"""

    page_selected = pyqtSignal(int)
    canceled = pyqtSignal()

    def __init__(self, parent, pdf_path, title, no_back_cover=False):
        super().__init__(parent)
        self.parent = parent
        self.pdf_path = pdf_path
        self.title = title
        self.no_back_cover = no_back_cover
        self.selected_page = None
        self.loader = None
        self.page_buttons = {}
        self.selected_button = None
        self.is_loading = True

        if parent and hasattr(parent, 'theme_manager'):
            self.theme_manager = parent.theme_manager
        else:
            self.theme_manager = ThemeManager()

        self.setWindowTitle(title)
        self.setFixedSize(720, 650)
        self.setModal(True)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()
        self.apply_styles()
        self.apply_theme()

        QTimer.singleShot(50, self.load_pages)

    def _create_button(self, text):
        btn = QPushButton(text)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("B Titr", 14))
        return btn

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header_layout = QHBoxLayout()
        if self.title == get_text('title_on'):
            info_text = get_text('page_selector_title_front')
        else:
            if self.no_back_cover:
                info_text = get_text('page_selector_no_back_cover')
            else:
                info_text = get_text('page_selector_title_back')

        self.lbl_info = QLabel(info_text)
        self.lbl_info.setFont(QFont("B Titr", 16))
        self.lbl_info.setObjectName("infoLabel")
        self.lbl_info.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.lbl_info)
        layout.addLayout(header_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scrollArea")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.scroll_layout = QGridLayout(self.scroll_content)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.loading_label = QLabel(get_text('page_selector_loading'))
        self.loading_label.setObjectName("loadingLabel")
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(self.loading_label, 0, 0, 1, 3)

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        bottom_layout.setAlignment(Qt.AlignCenter)

        self.lbl_selected_info = QLabel(get_text('page_selector_no_page_selected'))
        self.lbl_selected_info.setObjectName("selectedInfo")
        bottom_layout.addWidget(self.lbl_selected_info)

        bottom_layout.addStretch()

        self.btn_ok = self._create_button(get_text('apply'))
        self.btn_ok.setFixedSize(160, 45)
        self.btn_ok.clicked.connect(self.confirm_selection)
        self.btn_ok.setEnabled(False)
        bottom_layout.addWidget(self.btn_ok)

        self.btn_cancel = self._create_button(get_text('cancel'))
        self.btn_cancel.setFixedSize(160, 45)
        self.btn_cancel.clicked.connect(self.cancel_selection)
        bottom_layout.addWidget(self.btn_cancel)

        layout.addLayout(bottom_layout)

    def apply_styles(self):
        bg_color = self.theme_manager.get_background_color()
        if bg_color:
            text_color = self.theme_manager.get_text_color_for_background(bg_color)
        else:
            text_color = '#FFFFFF'

        style = f"""
            QDialog {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {bg_color or '#0f0c29'},
                    stop:0.5 {self._adjust_color(bg_color, 30) if bg_color else '#302b63'},
                    stop:1 {self._adjust_color(bg_color, 60) if bg_color else '#24243e'});
                border-radius: 15px;
            }}
            QLabel#infoLabel {{
                color: {text_color};
                font-family: 'B Titr';
                font-size: 16px;
            }}
            QLabel#loadingLabel {{
                color: #888888;
                font-family: 'B Titr';
                font-size: 16px;
                padding: 40px;
            }}
            QLabel#selectedInfo {{
                color: #00ffcc;
                font-family: 'B Titr';
                font-size: 14px;
                padding: 8px 16px;
                background: rgba(0,0,0,0.3);
                border-radius: 8px;
            }}
            QScrollArea#scrollArea {{
                background-color: transparent;
                border: 2px solid {self.theme_manager.get_button_color()};
                border-radius: 12px;
            }}
            QWidget#scrollContent {{
                background: transparent;
            }}
            QScrollBar:vertical {{
                background-color: #2a2a2a;
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.theme_manager.get_button_color()};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.theme_manager._darken_color(self.theme_manager.get_button_color(), 20)};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
        self.setStyleSheet(style)

    def _adjust_color(self, hex_color, amount):
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
        color = self.theme_manager.get_button_color()
        style = self.theme_manager.get_button_style(color)
        for btn in self.findChildren(QPushButton):
            if btn.objectName() not in ['menuBtn', 'minBtn', 'closeBtn']:
                btn.setStyleSheet(style)

    def load_pages(self):
        if not os.path.exists(self.pdf_path):
            NotificationManager.error(self, get_text('page_selector_pdf_not_found'))
            self.reject()
            return

        self.loader = PageLoader(self.pdf_path, self.title, self.no_back_cover)
        self.loader.page_loaded.connect(self.add_page_button)
        self.loader.finished.connect(self.on_load_finished)
        self.loader.error.connect(self.on_load_error)
        self.loader.start()

        QTimer.singleShot(15000, self._check_timeout)

    def _check_timeout(self):
        if self.is_loading and self.loader and self.loader.isRunning():
            self.on_load_error(get_text('page_selector_timeout'))

    def add_page_button(self, page_index, pixmap):
        if self.loading_label and self.loading_label.parent():
            self.loading_label.deleteLater()
            self.loading_label = None

        bg_color = self.theme_manager.get_background_color() or "#00006d"
        text_color = self.theme_manager.get_text_color_for_background(bg_color)

        card = QFrame()
        card.setObjectName("pageCard")
        card.setFixedSize(200, 280)
        card.setProperty("selected", False)
        card.setStyleSheet(f"""
            QFrame#pageCard {{
                background: rgba(0,0,0,0.3);
                border: 2px solid {self.theme_manager.get_button_color()};
                border-radius: 12px;
                padding: 8px;
            }}
            QFrame#pageCard:hover {{
                border-color: #00b4db;
                background: rgba(0,180,219,0.1);
            }}
            QFrame#pageCard[selected="true"] {{
                border-color: #00ffcc;
                background: rgba(0,255,204,0.15);
                border-width: 3px;
            }}
        """)

        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(5)
        card_layout.setAlignment(Qt.AlignCenter)

        img_label = QLabel()
        if pixmap and not pixmap.isNull():
            img_label.setPixmap(pixmap)
        else:
            img_label.setText(get_text('page_selector_placeholder').format(page_index + 1))
            img_label.setStyleSheet("color: #888; font-size: 16px;")
        img_label.setAlignment(Qt.AlignCenter)
        img_label.setStyleSheet("border-radius: 8px; background: transparent;")
        card_layout.addWidget(img_label)

        page_num = QLabel(f"📄 {get_text('page_selector_page')} {page_index + 1}")
        page_num.setFont(QFont("B Titr", 12))
        page_num.setStyleSheet(f"color: {text_color}; background: transparent;")
        page_num.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(page_num)

        self.page_buttons[page_index] = card

        def make_click_handler(idx):
            return lambda e: self.select_page(idx)

        card.mousePressEvent = make_click_handler(page_index)

        row = len(self.page_buttons) // 3
        col = len(self.page_buttons) % 3
        self.scroll_layout.addWidget(card, row, col)

    def on_load_finished(self):
        self.is_loading = False
        if self.loader:
            self.loader = None

        if not self.page_buttons:
            if self.no_back_cover and self.title != get_text('title_on'):
                error_label = QLabel(get_text('page_selector_no_back_cover_ok'))
                error_label.setStyleSheet("color: #00ffcc; font-size: 18px; padding: 40px;")
                error_label.setAlignment(Qt.AlignCenter)
                self.scroll_layout.addWidget(error_label, 0, 0, 1, 3)
                self.btn_ok.setEnabled(False)
            else:
                error_label = QLabel(get_text('page_selector_no_pages'))
                error_label.setStyleSheet("color: #FF4444; font-size: 16px; padding: 40px;")
                error_label.setAlignment(Qt.AlignCenter)
                self.scroll_layout.addWidget(error_label, 0, 0, 1, 3)

    def on_load_error(self, error_msg):
        self.is_loading = False
        if self.loader:
            self.loader.stop()
            self.loader = None

        if error_msg == get_text('page_selector_no_back_cover_ok'):
            self.no_back_cover = True
            error_label = QLabel(get_text('page_selector_no_back_cover_ok'))
            error_label.setStyleSheet("color: #00ffcc; font-size: 18px; padding: 40px;")
            error_label.setAlignment(Qt.AlignCenter)
            self._clear_layout(self.scroll_layout)
            self.scroll_layout.addWidget(error_label, 0, 0, 1, 3)
            self.btn_ok.setEnabled(False)
            self.lbl_info.setText(get_text('page_selector_no_back_cover'))
            return

        error_label = QLabel(f"❌ {error_msg}")
        error_label.setStyleSheet("color: #FF4444; font-size: 16px; padding: 40px;")
        error_label.setAlignment(Qt.AlignCenter)

        self._clear_layout(self.scroll_layout)
        self.scroll_layout.addWidget(error_label, 0, 0, 1, 3)
        self.btn_ok.setEnabled(False)

    def _clear_layout(self, layout):
        if layout is None:
            return
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def select_page(self, page_index):
        if self.selected_button:
            self.selected_button.setProperty("selected", False)
            self.selected_button.setStyleSheet(self.selected_button.styleSheet())

        if page_index in self.page_buttons:
            self.selected_button = self.page_buttons[page_index]
            self.selected_button.setProperty("selected", True)
            self.selected_button.setStyleSheet(self.selected_button.styleSheet())

            self.selected_page = page_index
            self.lbl_selected_info.setText(get_text('page_selector_page_selected').format(page_index + 1))
            self.btn_ok.setEnabled(True)

    def confirm_selection(self):
        if self.selected_page is not None:
            self.page_selected.emit(self.selected_page)
            self.accept()
        else:
            NotificationManager.warning(self, get_text('page_selector_select_page'))

    def cancel_selection(self):
        reply = QMessageBox.question(
            self,
            get_text('warning'),
            get_text('cancel_create'),
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.canceled.emit()
            self.reject()

    def closeEvent(self, event):
        if self.loader and self.loader.isRunning():
            self.loader.stop()
            self.loader = None
        event.accept()