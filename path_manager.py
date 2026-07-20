# path_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import sys
import base64


def get_base_path():
    """
    دریافت مسیر پایه برنامه
    - در حالت توسعه: مسیر فایل اصلی
    - در حالت exe: مسیر فایل اجرایی
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


def get_asset_path(relative_path):
    """
    دریافت مسیر کامل یک فایل در پوشه assets
    """
    base_path = get_base_path()

    search_paths = [
        os.path.join(base_path, 'CB_data/assets', relative_path),
        os.path.join(base_path, 'variables', 'CB_data/assets', relative_path),
        os.path.join(base_path, '_internal', 'CB_data/assets', relative_path)
    ]

    for path in search_paths:
        if os.path.exists(path):
            return path

    return os.path.join(base_path, 'CB_data/assets', relative_path)


def get_font_path(font_name='TitrB.ttf'):
    """دریافت مسیر فایل فونت"""
    from variables.assets_b import font
    font_path = get_asset_path(font_name)

    if not os.path.exists(font_path):
        font_bytes = base64.b64decode(font)
        with open(font_path, "wb") as f:
            f.write(font_bytes)

    return font_path


def get_icon_path():
    """دریافت مسیر فایل آیکون"""
    from variables.assets_b import icon
    icon_path = get_asset_path('icon.ico')

    if not os.path.exists(icon_path):
        icon_bytes = base64.b64decode(icon)
        with open(icon_path, "wb") as f:
            f.write(icon_bytes)

    return icon_path


def get_ver_path():
    """دریافت مسیر فایل نسخه"""
    from variables.assets_b import ver
    ver_path = get_asset_path('ver.txt')

    if not os.path.exists(ver_path):
        ver_bytes = base64.b64decode(ver)
        with open(ver_path, "wb") as f:
            f.write(ver_bytes)

    return ver_path


def ensure_directories():
    """ایجاد پوشه‌های مورد نیاز"""
    base_path = get_base_path()

    directories = [
        os.path.join(base_path, 'CB_data'),
        os.path.join(base_path, 'CB_data/history_cover'),
        os.path.join(base_path, 'CB_data/assets')
    ]

    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except:
                pass

