# func/select_footer.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import re
import pymupdf
from PIL import Image, ImageOps


class FooterCrop:
    """برش خودکار پاورقی صفحات PDF"""

    def __init__(self, pdf_img_pil, page_doc_pymupdf):
        self.page_doc = page_doc_pymupdf
        self.final_page = None
        self._process_page(pdf_img_pil)

    def _process_page(self, pdf_img_pil):
        """پردازش صفحه و برش پاورقی"""
        try:
            # استخراج متن صفحه
            page_dict = self.page_doc.get_text("dict", flags=pymupdf.TEXTFLAGS_TEXT)
            blocks = page_dict.get('blocks', [])

            page_height = self.page_doc.rect.height
            footer_search_area_y0 = page_height * 0.85

            # الگوی شماره صفحه
            number_pattern = re.compile(
                r'^([0-9\u06f0-\u06f9]{1,3}|[\u0600-\u06FF\u0750-\u077F\u0790-\u07BF\u07C0-\u07FF\u0870-\u089F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]|الف)$'
            )

            found_page_number = None

            # جستجوی شماره صفحه در پاورقی
            for block in blocks:
                if block['type'] == 0:  # متن
                    for line in block['lines']:
                        line_text = ""
                        line_bbox = None

                        for span in line['spans']:
                            line_text += span['text']
                            if line_bbox is None:
                                line_bbox = span['bbox']

                        cleaned_text = line_text.strip().replace('\n', '').replace('\t', '')

                        if line_bbox and line_bbox[3] >= footer_search_area_y0:
                            if cleaned_text and number_pattern.fullmatch(cleaned_text):
                                found_page_number = {
                                    'text': cleaned_text,
                                    'bbox': line_bbox
                                }
                                break
                    if found_page_number:
                        break

            # برش صفحه
            if found_page_number:
                page_num_bbox = found_page_number['bbox']
                crop_rect = pymupdf.Rect(
                    0, 0,
                    self.page_doc.rect.width,
                    page_num_bbox[1]
                )

                pix = self.page_doc.get_pixmap()
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                # ✅ اصلاح: استفاده از crop_rect به صورت تاپل (x0, y0, x1, y1)
                cropped = img.crop((crop_rect.x0, crop_rect.y0, crop_rect.x1, crop_rect.y1))

                # حذف حاشیه‌های خالی
                inverted = ImageOps.invert(cropped)
                bbox = inverted.getbbox()
                self.final_page = cropped.crop(bbox) if bbox else cropped
            else:
                self.final_page = pdf_img_pil

        except Exception as e:
            print(f"Error processing footer: {e}")
            self.final_page = pdf_img_pil