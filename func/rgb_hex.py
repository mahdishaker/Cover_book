# func/rgb_hex.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import colorsys


class RGBHelper:
    """کمک‌کننده برای کار با رنگ‌ها"""

    @staticmethod
    def hex_to_rgb(hex_color):
        """تبدیل هگز به RGB"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            return None
        return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))

    @staticmethod
    def rgb_to_hex(rgb):
        """تبدیل RGB به هگز"""
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    @staticmethod
    def get_contrast_color(rgb):
        """دریافت رنگ متضاد (سفید یا سیاه)"""
        if rgb is None:
            return 'white'

        # محاسبه روشنایی
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255

        if luminance > 0.5:
            return 'black'
        else:
            return 'white'

    @staticmethod
    def is_dark_color(rgb):
        """بررسی تیره بودن رنگ"""
        luminance = (0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]) / 255
        return luminance < 0.5

    @staticmethod
    def darken_color(hex_color, amount=20):
        """تاریک‌تر کردن رنگ"""
        rgb = RGBHelper.hex_to_rgb(hex_color)
        if rgb is None:
            return hex_color

        r = max(0, rgb[0] - amount)
        g = max(0, rgb[1] - amount)
        b = max(0, rgb[2] - amount)

        return RGBHelper.rgb_to_hex((r, g, b))

    @staticmethod
    def lighten_color(hex_color, amount=20):
        """روشن‌تر کردن رنگ"""
        rgb = RGBHelper.hex_to_rgb(hex_color)
        if rgb is None:
            return hex_color

        r = min(255, rgb[0] + amount)
        g = min(255, rgb[1] + amount)
        b = min(255, rgb[2] + amount)

        return RGBHelper.rgb_to_hex((r, g, b))

    @staticmethod
    def get_adjusted_background(hex_color):
        """تنظیم رنگ پس‌زمینه برای ویجت‌های ورودی"""
        rgb = RGBHelper.hex_to_rgb(hex_color)
        if rgb is None:
            return '#2a2a2a'

        if RGBHelper.is_dark_color(rgb):
            # تیره: روشن‌تر کن
            return RGBHelper.lighten_color(hex_color, 30)
        else:
            # روشن: تیره‌تر کن
            return RGBHelper.darken_color(hex_color, 30)