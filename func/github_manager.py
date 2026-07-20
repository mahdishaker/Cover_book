# func/github_manager.py
# Developer Team: MUSHAK
# Kharazmi 1404-1405

import os
import requests
import zipfile
import shutil
import tempfile
import json
import re
import base64
from datetime import datetime

from variables.constants import GITHUB_USERNAME, REPO_NAME, EXCLUDED_FILES, HERE
from variables.languages import get_text
from path_manager import get_ver_path


class GitHubManager:
    """مدیریت ارتباط با گیت‌هاب"""

    def __init__(self):
        self.username = GITHUB_USERNAME
        self.repo_name = REPO_NAME
        self.api_url = f'https://api.github.com/repos/{self.username}/{self.repo_name}'
        self.raw_url = f'https://raw.githubusercontent.com/{self.username}/{self.repo_name}/main'
        self.github_url = f'https://github.com/{self.username}/{self.repo_name}'

    def get_current_version(self):
        """دریافت نسخه فعلی"""
        try:
            ver_path = get_ver_path()
            if os.path.exists(ver_path):
                with open(ver_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            return None
        except:
            return None

    def clear_repos_cache(self):
        """پاک کردن کش لیست مخازن"""
        cache_file = os.path.join(os.path.dirname(get_ver_path()), 'repos_cache.txt')
        try:
            if os.path.exists(cache_file):
                os.remove(cache_file)

                return True
            return False
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

    def get_latest_version_method1(self):
        """روش 1: استفاده از API گیت‌هاب"""
        try:
            url = f'{self.api_url}/contents/CB_data/assets/ver.txt'
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'CoverApp/1.0'
            }

            response = requests.get(url, headers=headers, timeout=3)

            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data['content']).decode('utf-8')
                return content.strip()
            return None
        except Exception as e:
            print(f"Method 1 failed: {e}")
            return None

    def get_latest_version_method2(self):
        """روش 2: استفاده از raw.githubusercontent.com"""
        try:
            url = f'{self.raw_url}/CB_data/assets/ver.txt'
            headers = {'User-Agent': 'CoverApp/1.0'}

            response = requests.get(url, headers=headers, timeout=3)

            if response.status_code == 200:
                return response.text.strip()
            return None
        except Exception as e:
            print(f"Method 2 failed: {e}")
            return None

    def get_latest_version_method3(self):
        """روش 3: استخراج نسخه از صفحه وب گیت‌هاب"""
        try:
            url = f'{self.github_url}/blob/main/CB_data/assets/ver.txt'
            headers = {'User-Agent': 'CoverApp/1.0'}

            response = requests.get(url, headers=headers, timeout=5)

            if response.status_code == 200:
                patterns = [
                    r'(\d+\.\d+\.\d+)',
                    r'ver\.txt.*?(\d+\.\d+\.\d+)',
                    r'blob/main/CB_data/assets/ver\.txt.*?(\d+\.\d+\.\d+)'
                ]

                for pattern in patterns:
                    match = re.search(pattern, response.text)
                    if match:
                        return match.group(1)
            return None
        except Exception as e:
            print(f"Method 3 failed: {e}")
            return None

    def get_latest_version_method4(self):
        """روش 4: استفاده از API releases"""
        try:
            url = f'{self.api_url}/releases/latest'
            headers = {'User-Agent': 'CoverApp/1.0'}

            response = requests.get(url, headers=headers, timeout=3)

            if response.status_code == 200:
                data = response.json()
                return data.get('tag_name', '').lstrip('v')
            return None
        except Exception as e:
            print(f"Method 4 failed: {e}")
            return None

    def get_latest_version(self):
        """دریافت آخرین نسخه با استفاده از چندین روش"""
        methods = [
            self.get_latest_version_method1,
            self.get_latest_version_method2,
            self.get_latest_version_method3,
            self.get_latest_version_method4,
        ]

        for method in methods:
            try:
                version = method()
                if version:
                    return version
            except Exception as e:
                print(f"Method {method.__name__} failed: {e}")
                continue

        return None

    def get_repos(self, force_refresh=False):
        """دریافت لیست مخازن گیت‌هاب (به جز مخزن اصلی)

        Args:
            force_refresh: اگر True باشد، کش را نادیده می‌گیرد و از API می‌گیرد
        """
        cache_file = os.path.join(os.path.dirname(get_ver_path()), 'repos_cache.txt')

        # اگر force_refresh=True، کش را پاک کن
        if force_refresh:
            self.clear_repos_cache()

        # تلاش برای استفاده از کش
        cached_repos = self._get_cached_repos(cache_file)
        if cached_repos is not None:
            cached_names = [repo.get('name') for repo in cached_repos]
            return cached_repos

        try:
            url = f'https://api.github.com/users/{self.username}/repos'
            headers = {
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'CoverApp/1.0'
            }

            response = requests.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            all_repos = response.json()

            all_names = [repo.get('name') for repo in all_repos]

            # فیلتر کردن مخزن اصلی (Cover_book)
            filtered_repos = [repo for repo in all_repos if repo.get('name') != self.repo_name]

            # ذخیره در کش
            self._save_repos_cache(cache_file, filtered_repos)

            return filtered_repos

        except requests.exceptions.Timeout:
            print("Timeout getting repos, using cache if available (ignoring expiry)")
            return self._get_cached_repos(cache_file, ignore_expiry=True)
        except Exception as e:
            print(f"Error getting repos: {e}")
            return self._get_cached_repos(cache_file, ignore_expiry=True)

    def _get_cached_repos(self, cache_file, ignore_expiry=False):
        """دریافت مخازن از کش"""
        try:
            if os.path.exists(cache_file):
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    if ignore_expiry:
                        return data.get('repos', [])

                    # اگر کش کمتر از 1 ساعت پیش ذخیره شده، از آن استفاده کن
                    timestamp = data.get('timestamp', 0)
                    if datetime.now().timestamp() - timestamp < 3600:
                        return data.get('repos', [])
            return None
        except:
            return None

    def _save_repos_cache(self, cache_file, repos):
        """ذخیره مخازن در کش"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'repos': repos,
                    'timestamp': datetime.now().timestamp()
                }, f)
        except:
            pass

    def check_update(self):
        """بررسی وجود بروزرسانی"""
        current = self.get_current_version()
        latest = self.get_latest_version()

        if current is None or latest is None:
            return {
                'current': current or 'نامشخص',
                'latest': latest or 'نامشخص',
                'is_up_to_date': False,
                'error': current is None or latest is None
            }

        def parse_version(v):
            try:
                return [int(x) for x in v.split('.')]
            except:
                return [0, 0, 0]

        try:
            current_parts = parse_version(current)
            latest_parts = parse_version(latest)

            while len(current_parts) < len(latest_parts):
                current_parts.append(0)
            while len(latest_parts) < len(current_parts):
                latest_parts.append(0)

            is_up_to_date = True
            for c, l in zip(current_parts, latest_parts):
                if c < l:
                    is_up_to_date = False
                    break
                elif c > l:
                    is_up_to_date = True
                    break

            return {
                'current': current,
                'latest': latest,
                'is_up_to_date': is_up_to_date,
                'error': False
            }
        except:
            return {
                'current': current,
                'latest': latest,
                'is_up_to_date': False,
                'error': True
            }

    def download_and_update(self, progress_callback=None):
        """دانلود و نصب بروزرسانی"""
        try:
            api_url = f'{self.api_url}/zipball/main'
            headers = {'User-Agent': 'CoverApp/1.0'}

            response = requests.get(api_url, stream=True, headers=headers, timeout=30)
            response.raise_for_status()

            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = os.path.join(temp_dir, 'update.zip')

                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0

                with open(zip_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback and total_size:
                                progress = int((downloaded / total_size) * 100)
                                progress_callback(progress)

                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)

                extracted_dirs = [
                    d for d in os.listdir(temp_dir)
                    if os.path.isdir(os.path.join(temp_dir, d))
                ]

                source_dir = None
                for d in extracted_dirs:
                    if d.startswith(f'{self.username}-{self.repo_name}') or d.startswith(self.repo_name):
                        source_dir = os.path.join(temp_dir, d)
                        break

                if not source_dir:
                    return False

                for root, dirs, files in os.walk(source_dir):
                    rel_path = os.path.relpath(root, source_dir)
                    dest_dir = os.path.join(HERE, rel_path) if rel_path != '.' else HERE

                    if rel_path != '.' and not os.path.exists(dest_dir):
                        os.makedirs(dest_dir, exist_ok=True)

                    for file in files:
                        if file in EXCLUDED_FILES:
                            continue

                        should_exclude = False
                        for pattern in EXCLUDED_FILES:
                            if pattern.startswith('*') and file.endswith(pattern[1:]):
                                should_exclude = True
                                break

                        if should_exclude:
                            continue

                        src_file = os.path.join(root, file)
                        dest_file = os.path.join(dest_dir, file)

                        try:
                            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                            shutil.copy2(src_file, dest_file)
                        except Exception as e:
                            print(f"Error copying {file}: {e}")

                latest_version = self.get_latest_version()
                if latest_version:
                    ver_path = get_ver_path()
                    with open(ver_path, 'w', encoding='utf-8') as f:
                        f.write(latest_version)

                return True

        except Exception as e:
            print(f"Update error: {e}")
            return False