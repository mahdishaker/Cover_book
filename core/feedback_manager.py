# core/feedback_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import json
import os
import requests
from datetime import datetime
from core.database_manager import DatabaseManager


class FeedbackManager:
    """مدیریت بازخوردهای کاربران"""

    def __init__(self):
        self.db = DatabaseManager()
        self.github_owner = 'shaker-cpu'
        self.github_repo = 'cover_version'
        self.github_path = 'CB_data/feedbacks/feedbacks.json'

    def save_feedback(self, user_id, rating, comment='', suggestions='', cover_type=''):
        """ذخیره بازخورد"""
        return self.db.add_feedback(user_id, rating, comment, suggestions, cover_type)

    def get_feedbacks(self, user_id=None):
        """دریافت بازخوردها"""
        return self.db.get_feedbacks(user_id)

    def send_feedback_to_github(self, feedback_id=None):
        """ارسال بازخورد به GitHub (برای آینده)"""
        # این تابع برای ارسال بازخورد به GitHub آماده شده است
        # اما فعلاً فقط در دیتابیس محلی ذخیره می‌شود
        pass

    def get_average_rating(self, user_id=None):
        """محاسبه میانگین امتیاز"""
        feedbacks = self.get_feedbacks(user_id)
        if not feedbacks:
            return 0

        total = sum(f[2] for f in feedbacks)  # ستون rating
        return total / len(feedbacks)

    def get_feedback_stats(self, user_id=None):
        """دریافت آمار بازخوردها"""
        feedbacks = self.get_feedbacks(user_id)
        if not feedbacks:
            return {'total': 0, 'average': 0, 'distribution': {}}

        distribution = {}
        for f in feedbacks:
            rating = f[2]
            distribution[rating] = distribution.get(rating, 0) + 1

        return {
            'total': len(feedbacks),
            'average': sum(f[2] for f in feedbacks) / len(feedbacks),
            'distribution': distribution
        }