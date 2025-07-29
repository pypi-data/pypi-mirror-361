import json
import os
import time
from typing import Union

from appdirs import user_cache_dir


class AppDirsManager:
    CACHE_TTL = 86400  # 24 hours

    @staticmethod
    def get_cache_path(filename: str):
        path = os.path.join(user_cache_dir("proxykit"), filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path

    @staticmethod
    def save_data(data: Union[list, dict], filename: str):
        cache_data = {"updated_at": time.time(), "data": data}
        with open(AppDirsManager.get_cache_path(filename), "w") as f:
            json.dump(cache_data, f)

    @staticmethod
    def remove_cached_data(filename: str):
        """
        Remove cached data file if it exists.
        Args:
            filename (str): The name of the cache file to remove.
        """
        path = AppDirsManager.get_cache_path(filename)
        if os.path.exists(path):
            os.remove(path)

    @staticmethod
    def load_cached_data(filename: str):
        """
        Load cached data from a file if it exists and is not expired.
        Args:
            filename (str): The name of the cache file.

        Returns:
            dict: The cached data if available and not expired, otherwise an empty dict.
            <br>`actual data is in dict['data']`
        """
        path = AppDirsManager.get_cache_path(filename)
        if not os.path.exists(path):
            return {}
        with open(path) as f:
            data = json.load(f)
            if time.time() - data.get("updated_at", 0) < AppDirsManager.CACHE_TTL:
                return data
        return {}  # Cache expired
