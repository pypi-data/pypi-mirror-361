from typing import Optional
from proxykit.models import ProxyServer
from proxykit.storage.cache_manager import CacheManager
from proxykit.utils import verbose_print


class ProxyKit:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.__cache_manager = CacheManager(verbose)

    def __enter__(self):
        verbose_print(self.verbose, "ProxyKit Initialized")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Clean up or save cache on exit
        self.__cache_manager.save_proxies()
        if self.verbose:
            print("ProxyKit closed")

    def get_random_proxy(self) -> Optional[ProxyServer]:
        """
        Randomly selects one valid working proxy
        """
        return self.__cache_manager.get_random_proxy()

    def clear_cache(self):
        """
        Will clear all the proxies data
        """
        self.__cache_manager.clear_cache()

    def get_proxy_count(self) -> int:
        """
        Returns total count of valid proxies
        """
        return self.__cache_manager.get_proxies_count()

    @staticmethod
    def clear_all_data():
        """
        Clears all cache data can call (static method)
        """
        CacheManager.clear_all_data()
