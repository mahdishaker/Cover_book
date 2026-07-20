# main.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from path_manager import ensure_directories
from core.app import CoverApp
from frames.splash_screen import SplashScreen

# تنظیمات لاگ‌گیری
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cover_app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """نقطه ورود اصلی برنامه"""
    
    try:
        ensure_directories() # اطمینان از وجود مسیر ها
    except Exception as e:
        logger.critical(f"Failed to create directories: {e}")
        sys.exit(1)

    # فعال‌سازی مقیاس‌پذیری خودکار برای نمایشگرهای با وضوح بالا (4K، Retina)
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    font = QFont("Segoe UI", 10)
    app.setFont(font)


    splash = SplashScreen()
    splash.show()

    def show_main():
        try:
            window = CoverApp()
            window.show()
            splash.close()
        except Exception as e:
            logger.exception(f"Failed to start main window (error is :{e})")
            splash.close()
            raise

    QTimer.singleShot(4000, show_main)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()