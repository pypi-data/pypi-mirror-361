import random

from proxykit.models import ProxyServer
from proxykit.utils import verbose_print

from .appdirs_manager import AppDirsManager


class CacheManager:
    _instance = None

    def __new__(cls, verbose=False):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
            cls._instance._init_once(verbose)
        else:
            cls._instance.verbose = verbose
        return cls._instance

    def _init_once(self, verbose=False):
        self.cache = {}
        self.is_initiated = False
        self.verbose = verbose
        self.load_proxies()

    # def __init__(self):
    #     self.cache = {}
    #     self.is_initiated = False

    def get_proxies(self) -> list[ProxyServer]:
        """
        Get the cached proxies.
        Returns:
            dict: The cached proxies.
        """
        return self.cache.get("proxies", [])

    def get_proxies_count(self) -> int:
        """
        Returns total count of valid proxies
        """
        return len(self.cache.get("proxies", []))

    def get_random_proxy(self) -> ProxyServer | None:
        """
        Get a random proxy from the cache.
        Returns:
            ProxyServer | None: A random proxy if available, otherwise None.
        """
        if not self.cache.get("proxies"):
            return None
        return random.choice(self.cache["proxies"])

    def append_proxies(self, proxies: list[ProxyServer]):
        """
        Append proxies to the cache.
        Args:
            proxies (list[ProxyServer]): The list of proxies to append.
        """
        # don't append duplicates
        existing = self.cache.get("proxies", {})
        self.cache["proxies"] = self.cache.get("proxies", []) + [
            p for p in proxies if p not in existing
        ]
        verbose_print(self.verbose, "new proxies added successfully")
        self.save_proxies()

    def save_proxies(self):
        """
        Save the cached proxies to the appdirs cache.
        """
        data = [i.to_dict() for i in self.cache.get("proxies", [])]
        AppDirsManager.save_data(data, "proxies.json")
        verbose_print(self.verbose, "proxies file updated successfully")

    def load_proxies(self):
        """
        Load the cached proxies from the appdirs cache.
        """
        data = AppDirsManager.load_cached_data("proxies.json")
        if data is None or "data" not in data:
            if self.verbose:
                print("No valid data found")
            return
        self.cache["proxies"] = [
            ProxyServer.from_dict(item) for item in data.get("data", [])
        ]
        verbose_print(self.verbose, "Proxies loaded successfully")

    def clear_cache(self):
        """
        Clear the cache.
        """
        self.cache = {}
        AppDirsManager.remove_cached_data("proxies.json")

        verbose_print(self.verbose, "All proxies data is cleared")

    def delete_proxy(self, proxy: ProxyServer):
        """
        Delete a specific proxy from the cache.
        Args:
            proxy (ProxyServer): The proxy to delete.
        """
        self.cache["proxies"] = [p for p in self.cache.get("proxies", []) if p != proxy]
        verbose_print(self.verbose, "Proxy deleted successfully", proxy)
        self.save_proxies()

    @staticmethod
    def clear_all_data():
        AppDirsManager.remove_cached_data("proxies.json")


# # Sample ProxyServer instances for testing
# def create_sample_proxies() -> list[ProxyServer]:
#     """
#     Create sample ProxyServer instances for testing purposes.
#     Returns:
#         list[ProxyServer]: A list of sample proxy servers.
#     """
#     return [
#         ProxyServer(host="192.168.1.100", port=8080),
#         ProxyServer(host="10.0.0.50", port=3128),
#     ]
