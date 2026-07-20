# func/covers_func.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import logging
from datetime import datetime
from typing import Optional, Callable, Dict, Any

import pymupdf
from PIL import Image, ImageFont, ImageDraw
import arabic_reshaper
from bidi.algorithm import get_display
from PyQt5.QtWidgets import QApplication

from variables.languages import get_text
from variables.constants import HISTORY_PATH, fonts_dict
from func.select_page import PageSelector
from func.select_footer import FooterCrop

try:
    from peasy_image import compress
    HAS_PEASY = True
except ImportError:
    HAS_PEASY = False
    compress = None

logger = logging.getLogger(__name__)


class CoverCreator:
    """ساخت جلد پایان‌نامه با مدیریت خطا و پاک‌سازی منابع"""

    def __init__(self, metadata: Dict[str, Any], pdf_path: str, output_path: str,
                 parent=None, front_page: Optional[int] = None,
                 back_page: Optional[int] = None):
        self.metadata = metadata
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.parent = parent
        self.progress_callback: Optional[Callable[[int, str], None]] = None
        self._doc = None
        self._canvas = None
        self.front_page_index = front_page
        self.back_page_index = back_page
        self.no_back_cover = metadata.get('no_back_cover', False)

    def create_cover(self) -> bool:
        try:
            self._update_progress(5, get_text('progress_init'))
            QApplication.processEvents()

            spine_mm = int(self.metadata.get('spine', 10))
            atf = spine_mm / 10

            if self.no_back_cover:
                canvas_w = round(self._cm_to_px(20 + atf))
            else:
                canvas_w = round(self._cm_to_px(42 + atf))
            canvas_h = round(self._cm_to_px(30))

            self._canvas = Image.new('RGB', (canvas_w, canvas_h), 'white')
            self._update_progress(10, "Canvas created")

            self._doc = pymupdf.open(self.pdf_path)
            page_count = self._doc.page_count
            self._update_progress(20, f"PDF loaded, pages={page_count}")

            # انتخاب صفحه روی جلد
            if self.front_page_index is None:
                if self.parent:
                    selector = PageSelector(self.parent, self.pdf_path, get_text('title_on'), False)
                    if selector.exec_():
                        self.front_page_index = selector.selected_page
                    else:
                        return False
                else:
                    raise ValueError("Parent not provided for page selection")

            page_top = self._doc.load_page(self.front_page_index)
            pdf_img_top = self._get_page_image(page_top)
            pdf_img_top_clipped = FooterCrop(pdf_img_top, page_top).final_page
            self._place_front_image(pdf_img_top_clipped)
            self._update_progress(50, "Front cover placed")

            # متن عطف
            self._draw_spine_text()
            self._update_progress(60, "Spine text drawn")

            # صفحه پشت جلد
            if not self.no_back_cover:
                if self.back_page_index is None:
                    if self.parent:
                        selector_back = PageSelector(
                            self.parent, self.pdf_path, get_text('title_back'), self.no_back_cover
                        )
                        if selector_back.exec_():
                            self.back_page_index = selector_back.selected_page
                        else:
                            return False
                    else:
                        raise ValueError("Parent not provided for back page selection")

                page_back = self._doc.load_page(self.back_page_index)
                pdf_img_back = self._get_page_image(page_back)
                pdf_img_back_clipped = FooterCrop(pdf_img_back, page_back).final_page
                self._place_back_image(pdf_img_back_clipped)
                self._update_progress(80, "Back cover placed")

            # چرخش نهایی
            self._canvas = self._canvas.rotate(90, expand=True)
            self._update_progress(90, "Saving...")

            if not self._save_cover():
                raise RuntimeError(f"Failed to save cover to {self.output_path}")

            self._update_progress(100, get_text('progress_complete'))
            self._play_success_sound()
            return True

        except Exception as e:
            logger.exception("Error creating cover")
            if self.progress_callback:
                self.progress_callback(0, get_text('progress_error'))
            return False
        finally:
            # ===== آزادسازی حافظه =====
            if self._doc:
                try:
                    self._doc.close()
                except:
                    pass
                self._doc = None
            if self._canvas:
                try:
                    del self._canvas
                except:
                    pass
                self._canvas = None
            import gc
            gc.collect()

    def _get_page_image(self, page):
        zoom = 200 / 72
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        return Image.frombytes('RGB', (pix.width, pix.height), pix.samples)

    def _place_front_image(self, img: Image.Image) -> None:
        canvas_w, canvas_h = self._canvas.size
        pw, ph = img.size
        top_margin = self._cm_to_px(3)
        bottom_margin = self._cm_to_px(5)
        max_h = canvas_h - (top_margin + bottom_margin)
        spine_mm = int(self.metadata.get('spine', 10))
        atf = spine_mm / 10

        if self.no_back_cover:
            front_width = canvas_w - self._cm_to_px(atf)
        else:
            front_width = self._cm_to_px(20)

        scale = min(front_width / pw, max_h / ph)
        pw = round(pw * scale)
        ph = round(ph * scale)
        y = round(top_margin + (max_h - ph) / 2)
        x = 0 if self.no_back_cover else round((self._cm_to_px(20) - pw) / 2 - self._cm_to_px(1.75))
        x = max(0, x)
        y = max(0, y)
        img_resized = img.resize((pw, ph), Image.LANCZOS)
        self._canvas.paste(img_resized, (x, y))

    def _place_back_image(self, img: Image.Image) -> None:
        canvas_w, canvas_h = self._canvas.size
        spine_mm = int(self.metadata.get('spine', 10))
        atf = spine_mm / 10
        top_margin = self._cm_to_px(3)
        bottom_margin = self._cm_to_px(5)
        max_h = canvas_h - (top_margin + bottom_margin)
        pw, ph = img.size
        scale = min(self._cm_to_px(20 - 1.75) / pw, max_h / ph)
        pw = round(pw * scale)
        ph = round(ph * scale)
        y = round(top_margin + (max_h - ph) / 2)
        x = round(self._cm_to_px(22 + atf + 1.75) + (self._cm_to_px(20) - pw) / 2)
        x = max(self._cm_to_px(20 + atf + 1.75), x)
        y = max(self._cm_to_px(3), y)
        img_resized = img.resize((pw, ph), Image.LANCZOS)
        self._canvas.paste(img_resized, (x, y))

    def _draw_spine_text(self) -> None:
        title = self.metadata.get('title', '')
        author = self.metadata.get('author', '')
        date = self.metadata.get('date', '')
        level = self.metadata.get('level', '')
        parts = [title, author, date]
        if level:
            parts.append(f"سطح {level}")
        text = "  " + "  ".join(parts) + "  "

        spine_mm = int(self.metadata.get('spine', 10))
        atf = spine_mm / 10

        draw = ImageDraw.Draw(self._canvas)
        font_size = 120
        font = ImageFont.truetype(fonts_dict, font_size)
        reshaped = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped)

        while font_size > 10:
            bbox = draw.textbbox((0, 0), bidi_text, font=font)
            w = int(bbox[2] - bbox[0])
            h = int(bbox[3] - bbox[1])
            if self._px_to_cm(h) <= atf and self._px_to_cm(w) <= 22:
                break
            font_size -= 1
            font = ImageFont.truetype(fonts_dict, font_size)

        temp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        temp_draw = ImageDraw.Draw(temp)
        temp_draw.text((-bbox[0], -bbox[1]), bidi_text, fill='black', font=font)
        temp_rotate = temp.rotate(90, expand=True)
        rot_w, rot_h = temp_rotate.size
        canvas_w, canvas_h = self._canvas.size
        max_h = canvas_h - self._cm_to_px(3) - self._cm_to_px(5)
        max_h2 = (max_h - rot_h) / 2

        if self.no_back_cover:
            front_width = canvas_w - self._cm_to_px(atf)
            x = round(front_width + (self._cm_to_px(atf) - rot_w) / 2)
        else:
            x = canvas_w // 2 - rot_w // 2
        y = round(max_h2 + self._cm_to_px(3))
        x = max(0, min(x, canvas_w - rot_w))
        self._canvas.paste(temp_rotate, (x, y), temp_rotate)

    def _save_cover(self) -> bool:
        try:
            logger.info(f"Saving cover to: {self.output_path}")
            if not self.compress_image_bmp(self.output_path, self._canvas):
                logger.error(f"Primary save failed for {self.output_path}")
                return False

            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = os.path.basename(self.output_path)
            history_file = f"{timestamp}_{file_name}"
            history_path = os.path.join(HISTORY_PATH, history_file)
            history_canvas = self._canvas.copy()
            if not self.compress_image_bmp(history_path, history_canvas):
                logger.warning(f"History copy failed for {history_path}")

            return True
        except Exception as e:
            logger.exception("Error in _save_cover")
            return False

    def compress_image_bmp(self, output_path: str, image: Image.Image, dpi: int = 200) -> bool:
        try:
            img = image.convert('L').convert('1', dither=Image.FLOYDSTEINBERG)
            max_dim = 3000
            if img.width > max_dim or img.height > max_dim:
                ratio = img.width / img.height
                img.thumbnail((max_dim, max_dim * ratio), Image.LANCZOS)

            direct_path = output_path + ".direct.bmp"
            try:
                img.save(direct_path, format='BMP', dpi=(dpi, dpi))
                logger.debug(f"Direct save successful: {direct_path}")
            except Exception as e:
                logger.error(f"Direct save failed: {e}")
                return False

            if HAS_PEASY:
                try:
                    compressed = compress(direct_path, quality=60, fmt="BMP")
                    if os.path.exists(compressed) and os.path.getsize(compressed) > 0:
                        if os.path.exists(output_path):
                            os.remove(output_path)
                        os.rename(compressed, output_path)
                        logger.info(f"Peasy compression successful: {output_path}")
                        if os.path.exists(direct_path) and direct_path != output_path:
                            os.remove(direct_path)
                        return True
                except Exception as e:
                    logger.warning(f"Peasy compression failed: {e}")

            if os.path.exists(direct_path) and os.path.getsize(direct_path) > 0:
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(direct_path, output_path)
                logger.info(f"Used direct save (no compression): {output_path}")
                return True

            return False

        except Exception as e:
            logger.exception(f"Compression error for {output_path}")
            return False

    def _update_progress(self, value: int, status: str) -> None:
        if self.progress_callback:
            self.progress_callback(value, status)

    @staticmethod
    def _cm_to_px(cm: float) -> int:
        return round((cm / 2.54) * 200)

    @staticmethod
    def _px_to_cm(px: int) -> float:
        return (px / 200) * 2.54

    @staticmethod
    def _play_success_sound() -> None:
        try:
            import winsound
            for freq, dur in [(523, 250), (659, 250), (784, 500), (1047, 500)]:
                winsound.Beep(freq, dur)
        except Exception:
            pass