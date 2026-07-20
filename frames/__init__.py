# frames/__init__.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

from frames.main_frame import MainFrame
from frames.dissertation_frame import DissertationFrame
from frames.history_frame import HistoryFrame
from frames.theme_frame import ThemeFrame
from frames.guide_frame import GuideFrame
from frames.update_frame import UpdateFrame
from frames.other_programs_frame import OtherProgramsFrame
from frames.about_frame import AboutDialog
from frames.splash_screen import SplashScreen
from frames.login_frame import LoginFrame
from frames.register_frame import RegisterFrame
from frames.feedback_dialog import FeedbackDialog

__all__ = [
    'MainFrame',
    'DissertationFrame',
    'HistoryFrame',
    'ThemeFrame',
    'GuideFrame',
    'UpdateFrame',
    'OtherProgramsFrame',
    'AboutDialog',
    'SplashScreen',
    'LoginFrame',
    'RegisterFrame',
    'FeedbackDialog',
]