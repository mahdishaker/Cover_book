# variables/constants.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import json
from path_manager import get_base_path, get_font_path, ensure_directories

# ایجاد پوشه‌های مورد نیاز
ensure_directories()

# مسیر پایه
HERE = get_base_path()
SCRIPT_PATH = HERE

# ========== بارگذاری تنظیمات از فایل config.json ==========
CONFIG_FILE = os.path.join(HERE, 'CB_data/config.json')

# رنگ‌های پیش‌فرض
DEFAULT_WIDGET_COLOR = "#FDCB6E"
DEFAULT_BACKGROUND_COLOR = "#00006d"
DEFAULT_LANGUAGE = 'persian'

# متغیرهای تنظیمات
current_color = DEFAULT_WIDGET_COLOR
background_color = None
current_language = DEFAULT_LANGUAGE

# بارگذاری فایل کانفیگ
try:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            current_color = config.get('button_color', DEFAULT_WIDGET_COLOR)
            background_color = config.get('background_color', None)
            current_language = config.get('language', DEFAULT_LANGUAGE)
except:
    current_color = DEFAULT_WIDGET_COLOR
    background_color = None
    current_language = DEFAULT_LANGUAGE

# رنگ‌های پیش‌فرض با بارگذاری از config
DEFAULT_WIDGET_COLOR = current_color if current_color else DEFAULT_WIDGET_COLOR
DEFAULT_BACKGROUND_COLOR = DEFAULT_BACKGROUND_COLOR
DEFAULT_LANGUAGE = current_language if current_language else DEFAULT_LANGUAGE

# ========== ادامه ثابت‌ها ==========

# مسیرهای تاریخچه
HISTORY_PATH = os.path.join(HERE, 'CB_data/history_cover')
HISTORY_FILE = os.path.join(HISTORY_PATH, 'history.db')

# فایل‌های مستثنی
EXCLUDED_FILES = [
    '.gitignore', 'README.md', 'README', '.git', '.github',
    '.vscode', '.idea', '__pycache__', '*.pyc', '*.pyo',
    '*.pyd', '.DS_Store', 'Thumbs.db', '*.log', '*.tmp',
    '*.temp', 'venv', 'env', '.env', 'dist', 'build', '*.egg-info'
]

# اطلاعات گیت‌هاب - به‌روزرسانی شده با اطلاعات جدید
GITHUB_USERNAME = 'mahdishaker'
REPO_NAME = 'Cover_book'
RAW_CONTENT_URL = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main'

# دسکتاپ
DESKTOP_PATH = os.path.join(os.path.expanduser("~"), "Desktop")

# لیست رنگ‌های دکمه‌های پیش‌فرض (Hex)
COLORS = [
    '#001F3F', '#0074D9', '#6CA0D6', '#7FDBFF',
    '#FFB300', '#FFD700', '#FFF176', DEFAULT_WIDGET_COLOR,
    '#C71585', '#FF1493', '#FF69B4', '#FFB6C1',
    '#2E8B57', '#32CD32', '#7CFC00', '#ADFF2F'
]

# مسیر فونت - استفاده از path_manager
fonts_dict = get_font_path('TitrB.ttf')

# لیست ماه‌ها (به فارسی)
months = ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
          'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند']

# متغیرهای سراسری برای ویجت‌ها (برای سازگاری با کد قبلی)
all_buttons = []
all_entry = []
all_label = []
all_combo_box = []
all_check_box = []
all_textbox = []
all_Scrollable_Frame = []
all_tab_view = []
all_option_menu = []
name_txt_lbl = []

# مرجع پنجره اصلی
main_window_ref = None


def set_main_window_ref(window):
    """تنظیم مرجع پنجره اصلی"""
    global main_window_ref
    main_window_ref = window


def get_main_window_ref():
    """دریافت مرجع پنجره اصلی"""
    return main_window_ref


def get_config_value(key, default=None):
    """دریافت یک مقدار از فایل کانفیگ"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config.get(key, default)
    except:
        pass
    return default


def save_config_value(key, value):
    """ذخیره یک مقدار در فایل کانفیگ"""
    try:
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)

        config[key] = value

        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except:
        return False