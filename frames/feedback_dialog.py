# frames/feedback_dialog.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import logging
import traceback
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QTextEdit, QFrame, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QPolygonF
import math

from variables.languages import get_text
from core.theme_manager import ThemeManager
from core.feedback_manager import FeedbackManager

logger = logging.getLogger(__name__)


class StarRatingWidget(QWidget):
    """ویجت امتیازدهی ستاره‌ای"""

    rating_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("StarRatingWidget.__init__ started")
        try:
            self.rating = 0
            self.hover_rating = 0
            self.setFixedSize(280, 55)
            self.setMinimumHeight(55)
            self.setCursor(Qt.PointingHandCursor)
            self._star_size = 42
            self._spacing = 12

            if parent and hasattr(parent, 'theme_manager'):
                self._theme_manager = parent.theme_manager
            else:
                self._theme_manager = ThemeManager()
        except Exception as e:
            logger.exception(f"Error in StarRatingWidget.__init__: {e}")

    def _get_star_polygon(self, index: int) -> QPolygonF:
        try:
            star_size = self._star_size
            spacing = self._spacing
            total_width = 5 * (star_size + spacing) - spacing
            start_x = (self.width() - total_width) // 2
            x = start_x + index * (star_size + spacing)
            y = (self.height() - star_size) // 2

            center_x = x + star_size // 2
            center_y = y + star_size // 2
            outer_radius = star_size // 2
            inner_radius = outer_radius * 0.4

            points = []
            for i in range(10):
                angle = -math.pi / 2 + i * 2 * math.pi / 10
                radius = outer_radius if i % 2 == 0 else inner_radius
                px = center_x + radius * math.cos(angle)
                py = center_y + radius * math.sin(angle)
                points.append(QPointF(px, py))

            return QPolygonF(points)
        except Exception as e:
            logger.exception(f"Error in _get_star_polygon: {e}")
            return QPolygonF()

    def paintEvent(self, event):
        try:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            current_rating = self.hover_rating if self.hover_rating > 0 else self.rating

            for i in range(5):
                polygon = self._get_star_polygon(i)
                if i < current_rating:
                    painter.setPen(QPen(QColor(255, 215, 0), 2))
                    painter.setBrush(QColor(255, 215, 0))
                else:
                    painter.setPen(QPen(QColor(255, 215, 0), 2))
                    painter.setBrush(Qt.transparent)
                painter.drawPolygon(polygon)
        except Exception as e:
            logger.exception(f"Error in paintEvent: {e}")

    def mousePressEvent(self, event):
        try:
            star_size = self._star_size
            spacing = self._spacing
            total_width = 5 * (star_size + spacing) - spacing
            start_x = (self.width() - total_width) // 2

            for i in range(5):
                x = start_x + i * (star_size + spacing)
                if x <= event.x() <= x + star_size:
                    self.rating = i + 1
                    self.hover_rating = 0
                    self.rating_changed.emit(self.rating)
                    self.update()
                    break
        except Exception as e:
            logger.exception(f"Error in mousePressEvent: {e}")

    def mouseMoveEvent(self, event):
        try:
            star_size = self._star_size
            spacing = self._spacing
            total_width = 5 * (star_size + spacing) - spacing
            start_x = (self.width() - total_width) // 2

            hover = 0
            for i in range(5):
                x = start_x + i * (star_size + spacing)
                if x <= event.x() <= x + star_size:
                    hover = i + 1
                    break

            if hover != self.hover_rating:
                self.hover_rating = hover
                self.update()
        except Exception as e:
            logger.exception(f"Error in mouseMoveEvent: {e}")

    def leaveEvent(self, event):
        try:
            self.hover_rating = 0
            self.update()
        except Exception as e:
            logger.exception(f"Error in leaveEvent: {e}")

    def set_rating(self, rating: int) -> None:
        try:
            self.rating = min(5, max(0, rating))
            self.update()
        except Exception as e:
            logger.exception(f"Error in set_rating: {e}")

    def get_rating(self) -> int:
        return self.rating


class FeedbackDialog(QDialog):
    """دیالوگ بازخورد کاربر"""

    feedback_submitted = pyqtSignal(dict)
    _rating_texts = {1: 'very_bad', 2: 'bad', 3: 'average', 4: 'good', 5: 'excellent'}

    def __init__(self, parent=None, user_id=None, cover_type=''):
        logger.info("=" * 50)
        logger.info("FeedbackDialog.__init__ STARTED")
        try:
            super().__init__(parent)
            self.parent_app = parent
            self.user_id = user_id
            self.cover_type = cover_type

            if parent and hasattr(parent, 'theme_manager'):
                self.theme_manager = parent.theme_manager
            else:
                self.theme_manager = ThemeManager()

            self.feedback_manager = FeedbackManager()

            self._setup_window()
            self._setup_ui()
            self._apply_styles()
            self._apply_theme()

            logger.info("FeedbackDialog.__init__ COMPLETED")
        except Exception as e:
            logger.exception(f"CRITICAL Error in FeedbackDialog.__init__: {e}")
            traceback.print_exc()
            try:
                QMessageBox.information(parent, get_text('feedback_title'), get_text('feedback_thanks'))
            except:
                pass
            self.reject()

    def _setup_window(self) -> None:
        try:
            self.setWindowTitle(get_text('feedback_title'))
            self.setFixedSize(540, 640)
            self.setModal(True)
            self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint | Qt.WindowTitleHint)
        except Exception as e:
            logger.exception(f"Error in _setup_window: {e}")
            raise

    def _setup_ui(self) -> None:
        try:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(30, 25, 30, 25)
            main_layout.setSpacing(15)

            header = self._create_header()
            main_layout.addLayout(header)

            rating_frame = self._create_rating_section()
            main_layout.addWidget(rating_frame)
            main_layout.addSpacing(5)

            comment_section = self._create_text_section('comment', 'comment_placeholder', 110)
            main_layout.addLayout(comment_section)
            main_layout.addSpacing(5)

            suggestion_section = self._create_text_section('suggestions', 'suggestions_placeholder', 80)
            main_layout.addLayout(suggestion_section)
            main_layout.addSpacing(10)

            button_layout = self._create_buttons()
            main_layout.addLayout(button_layout)

            self._connect_signals()
        except Exception as e:
            logger.exception(f"Error in _setup_ui: {e}")
            raise

    def _create_header(self) -> QHBoxLayout:
        try:
            header = QHBoxLayout()
            header.setSpacing(10)

            icon = QLabel("💬")
            icon.setFont(QFont("B Titr", 30))
            header.addWidget(icon)

            title = QLabel(get_text('feedback_title'))
            title.setFont(QFont("B Titr", 22, QFont.Bold))
            title.setObjectName("feedbackTitle")
            header.addWidget(title)

            header.addStretch()

            close_btn = QPushButton("✕")
            close_btn.setFixedSize(32, 32)
            close_btn.setFont(QFont("B Titr", 14))
            close_btn.setObjectName("closeBtn")
            close_btn.clicked.connect(self.reject)
            header.addWidget(close_btn)

            return header
        except Exception as e:
            logger.exception(f"Error in _create_header: {e}")
            return QHBoxLayout()

    def _create_rating_section(self) -> QFrame:
        try:
            frame = QFrame()
            frame.setObjectName("ratingFrame")
            frame.setFixedHeight(140)

            layout = QVBoxLayout(frame)
            layout.setSpacing(10)
            layout.setContentsMargins(20, 15, 20, 15)
            layout.setAlignment(Qt.AlignCenter)

            label = QLabel(get_text('rate_experience'))
            label.setFont(QFont("B Titr", 15))
            label.setObjectName("ratingLabel")
            label.setAlignment(Qt.AlignCenter)
            layout.addWidget(label)

            self.star_rating = StarRatingWidget(self)
            layout.addWidget(self.star_rating, alignment=Qt.AlignCenter)

            self.lbl_rating_text = QLabel(get_text('select_rating'))
            self.lbl_rating_text.setFont(QFont("B Titr", 13))
            self.lbl_rating_text.setObjectName("ratingText")
            self.lbl_rating_text.setAlignment(Qt.AlignCenter)
            self.lbl_rating_text.setMinimumHeight(30)
            layout.addWidget(self.lbl_rating_text)

            return frame
        except Exception as e:
            logger.exception(f"Error in _create_rating_section: {e}")
            return QFrame()

    def _create_text_section(self, label_key: str, placeholder_key: str, height: int) -> QVBoxLayout:
        try:
            layout = QVBoxLayout()
            layout.setSpacing(5)

            label = QLabel(get_text(label_key))
            label.setFont(QFont("B Titr", 14))
            label.setObjectName("formLabel")
            layout.addWidget(label)

            text_edit = QTextEdit()
            text_edit.setFont(QFont("B Titr", 13))
            text_edit.setPlaceholderText(get_text(placeholder_key))
            text_edit.setMaximumHeight(height)
            text_edit.setMinimumHeight(height - 10)
            text_edit.setObjectName(f"text{label_key.title()}")

            if label_key == 'comment':
                self.txt_comment = text_edit
            else:
                self.txt_suggestions = text_edit

            layout.addWidget(text_edit)
            return layout
        except Exception as e:
            logger.exception(f"Error in _create_text_section: {e}")
            return QVBoxLayout()

    def _create_buttons(self) -> QHBoxLayout:
        try:
            layout = QHBoxLayout()
            layout.setSpacing(25)
            layout.setAlignment(Qt.AlignCenter)

            self.btn_submit = QPushButton(get_text('submit_feedback'))
            self.btn_submit.setFixedSize(190, 50)
            self.btn_submit.setCursor(Qt.PointingHandCursor)
            self.btn_submit.setFont(QFont("B Titr", 14, QFont.Bold))
            self.btn_submit.clicked.connect(self.submit_feedback)
            layout.addWidget(self.btn_submit)

            self.btn_cancel = QPushButton(get_text('skip'))
            self.btn_cancel.setFixedSize(130, 50)
            self.btn_cancel.setCursor(Qt.PointingHandCursor)
            self.btn_cancel.setFont(QFont("B Titr", 14, QFont.Bold))
            self.btn_cancel.clicked.connect(self.reject)
            layout.addWidget(self.btn_cancel)

            return layout
        except Exception as e:
            logger.exception(f"Error in _create_buttons: {e}")
            return QHBoxLayout()

    def _connect_signals(self) -> None:
        try:
            self.star_rating.rating_changed.connect(self._update_rating_text)
        except Exception as e:
            logger.exception(f"Error in _connect_signals: {e}")

    def _apply_styles(self) -> None:
        try:
            bg_color = self.theme_manager.get_background_color()
            text_color = self.theme_manager.get_text_color_for_background(bg_color) if bg_color else '#FFFFFF'

            style = f"""
                QDialog {{
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #0f0c29, stop:0.5 #302b63, stop:1 #24243e);
                    border-radius: 16px;
                }}
                QLabel#feedbackTitle {{
                    color: {text_color};
                    font-family: 'B Titr';
                }}
                QLabel#ratingLabel {{
                    color: {text_color};
                    font-family: 'B Titr';
                    font-weight: bold;
                }}
                QLabel#ratingText {{
                    color: #FFD700;
                    font-family: 'B Titr';
                    font-weight: bold;
                    font-size: 14px;
                }}
                QLabel#formLabel {{
                    color: {text_color};
                    font-family: 'B Titr';
                    font-weight: bold;
                    font-size: 14px;
                }}
                QFrame#ratingFrame {{
                    background: rgba(0,0,0,0.25);
                    border: 2px solid rgba(58,58,78,0.6);
                    border-radius: 14px;
                    padding: 10px;
                }}
                QTextEdit {{
                    background: rgba(0,0,0,0.35);
                    color: {text_color};
                    border: 2px solid rgba(58,58,78,0.6);
                    border-radius: 10px;
                    padding: 12px;
                    font-family: 'B Titr';
                    font-size: 13px;
                }}
                QTextEdit:focus {{
                    border-color: #00b4db;
                    background: rgba(0,0,0,0.45);
                }}
                QTextEdit:hover {{
                    border-color: #00b4db;
                }}
                QPushButton#closeBtn {{
                    background: rgba(255,50,50,0.85);
                    border-radius: 16px;
                    font-size: 14px;
                    font-weight: bold;
                    color: white;
                    font-family: 'B Titr';
                }}
                QPushButton#closeBtn:hover {{
                    background: rgba(255,0,0,1);
                }}
                QPushButton {{
                    font-family: 'B Titr';
                }}
            """
            self.setStyleSheet(style)
        except Exception as e:
            logger.exception(f"Error in _apply_styles: {e}")

    def _apply_theme(self) -> None:
        try:
            color = self.theme_manager.get_button_color()
            style = self.theme_manager.get_button_style(color)
            for btn in [self.btn_submit, self.btn_cancel]:
                if btn:
                    btn.setStyleSheet(style)
        except Exception as e:
            logger.exception(f"Error in _apply_theme: {e}")

    def _update_rating_text(self, rating: int) -> None:
        try:
            text_key = self._rating_texts.get(rating, 'select_rating')
            self.lbl_rating_text.setText(get_text(text_key))
        except Exception as e:
            logger.exception(f"Error in _update_rating_text: {e}")

    def submit_feedback(self) -> None:
        logger.info("submit_feedback STARTED")
        try:
            rating = self.star_rating.get_rating()
            comment = self.txt_comment.toPlainText().strip()
            suggestions = self.txt_suggestions.toPlainText().strip()

            if rating == 0:
                QMessageBox.warning(self, get_text('warning'), get_text('select_rating_warning'))
                return

            feedback_data = {
                'user_id': self.user_id,
                'rating': rating,
                'comment': comment,
                'suggestions': suggestions,
                'cover_type': self.cover_type
            }

            success = self.feedback_manager.save_feedback(**feedback_data)

            if success:
                QMessageBox.information(self, get_text('thanks'), get_text('feedback_thanks'))
                self.feedback_submitted.emit(feedback_data)
                self.accept()
            else:
                QMessageBox.critical(self, get_text('error'), get_text('feedback_error'))
        except Exception as e:
            logger.exception(f"Error in submit_feedback: {e}")
            try:
                QMessageBox.critical(self, get_text('error'), f"خطا در ارسال بازخورد: {str(e)}")
            except:
                pass
            self.accept()
        logger.info("submit_feedback ENDED")

    def showEvent(self, event):
        try:
            super().showEvent(event)
            if hasattr(self, 'star_rating'):
                self.star_rating.setFocus()
        except Exception as e:
            logger.exception(f"Error in showEvent: {e}")

    def keyPressEvent(self, event):
        try:
            if event.key() == Qt.Key_Escape:
                self.reject()
            elif event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.submit_feedback()
            else:
                super().keyPressEvent(event)
        except Exception as e:
            logger.exception(f"Error in keyPressEvent: {e}")
            self.reject()

    def closeEvent(self, event):
        logger.info("FeedbackDialog.closeEvent called")
        try:
            event.accept()
        except Exception as e:
            logger.exception(f"Error in closeEvent: {e}")
            event.accept()