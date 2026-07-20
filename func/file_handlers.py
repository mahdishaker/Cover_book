# func/file_handlers.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import datetime
import os
import logging
from PyQt5.QtWidgets import QFileDialog, QMessageBox

from variables.languages import get_text

logger = logging.getLogger(__name__)


class FileHandler:
    """مدیریت فایل‌ها با اعتبارسنجی مسیر و مجوز"""

    @staticmethod
    def select_pdf_file(parent, initial_dir: str = None) -> str:
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            get_text('select_file'),
            initial_dir,
            "PDF Files (*.pdf)"
        )
        if file_path and not os.path.exists(file_path):
            logger.warning(f"Selected PDF file does not exist: {file_path}")
            return None
        return file_path if file_path else None

    @staticmethod
    def select_save_location(parent, initial_dir: str = None) -> str:
        """
        انتخاب مسیر ذخیره با اعتبارسنجی کامل
        در صورت انتخاب مسیر نامعتبر، به دسکتاپ هدایت می‌شود
        """
        if initial_dir is None:
            # مسیر پیش‌فرض: دسکتاپ
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            if not os.path.exists(desktop):
                desktop = os.path.expanduser("~")
            initial_dir = os.path.join(desktop, f'{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}_output.bmp')

        file_path, _ = QFileDialog.getSaveFileName(
            parent,
            get_text('save_location'),
            initial_dir,
            "Bitmap Files (*.bmp)"
        )
        if not file_path:
            return None

        # اطمینان از پسوند صحیح
        if not file_path.lower().endswith('.bmp'):
            file_path += '.bmp'

        # بررسی و ایجاد پوشه والد
        parent_dir = os.path.dirname(file_path)
        if parent_dir:
            if not os.path.exists(parent_dir):
                try:
                    os.makedirs(parent_dir, exist_ok=True)
                    logger.info(f"Created directory: {parent_dir}")
                except OSError as e:
                    logger.error(f"Could not create directory {parent_dir}: {e}")
                    QMessageBox.warning(parent, "خطا", f"امکان ایجاد پوشه وجود ندارد:\n{parent_dir}\nلطفاً مسیر دیگری انتخاب کنید.")
                    return None
            # بررسی مجوز نوشتن
            if not os.access(parent_dir, os.W_OK):
                logger.error(f"No write permission for directory: {parent_dir}")
                QMessageBox.warning(parent, "خطا", f"مجوز نوشتن در این مسیر وجود ندارد:\n{parent_dir}\nلطفاً مسیر دیگری انتخاب کنید.")
                return None

        return file_path

    @staticmethod
    def select_folder(parent, initial_dir: str = None) -> str:
        if initial_dir is None:
            initial_dir = os.path.expanduser("~")
        folder_path = QFileDialog.getExistingDirectory(
            parent,
            get_text('select_folder'),
            initial_dir
        )
        if folder_path and not os.path.exists(folder_path):
            logger.warning(f"Selected folder does not exist: {folder_path}")
            return None
        return folder_path if folder_path else None

    @staticmethod
    def ensure_directory_exists(path: str) -> bool:
        if not path:
            return False
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except OSError as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False