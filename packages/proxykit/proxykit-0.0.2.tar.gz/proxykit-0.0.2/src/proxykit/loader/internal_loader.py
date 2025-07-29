from typing import Dict, List, Optional

import requests

from proxykit.exceptions import InvalidProxyError
from proxykit.models import ProxyDataFormat, ProxyServer
from proxykit.storage import CacheManager
from proxykit.utils import parse_data
from proxykit.validator import ProxyValidator


class _InternalProxyLoader:
    """
    This have implementation of loading proxy data from various formats, called from ProxyLoader class.
    """  # noqa: E501

    @staticmethod
    def load_local(
        path: str,
        format: ProxyDataFormat = ProxyDataFormat.IP,
        key_mapping: Dict[str, str] = {},
        entry: List[str] = [],
    ):
        try:
            with open(path, "r") as f:
                data = f.readlines()
            values = parse_data(
                data,
                format,
                key_mapping=key_mapping,
                entry=entry,
            )

            _InternalProxyLoader.validate_and_save_data(values)

        except Exception as e:
            raise InvalidProxyError(f"Failed to load from path with {e}") from e

    @staticmethod
    def load_remote(
        url: str,
        format: ProxyDataFormat = ProxyDataFormat.IP,
        key_mapping: Dict[str, str] = {},
        entry: List[str] = [],
        token: Optional[str] = None,
    ):
        try:
            # todo: yet to implement token handling

            # response = httpx.get(url)
            response = requests.get(url)
            response.raise_for_status()
            data = response.text

            values = parse_data(
                data,
                format,
                key_mapping=key_mapping,
                entry=entry,
            )

            _InternalProxyLoader.validate_and_save_data(values)

        except Exception as e:
            raise InvalidProxyError(f"Failed to load from URL with {e}") from e

    # @staticmethod
    # def validate_and_save_data(data: List[ProxyServer], threads=10):
    #     """
    #     Assuming data is already in the form of ProxyServer objects,
    #     data will be validated and then stored in the internal storage.
    #     """
    #     if not isinstance(data, list) or not all(
    #         isinstance(d, ProxyServer) for d in data
    #     ):
    #         raise InvalidProxyError(
    #             "Invalid proxy data format. Expected a list of ProxyServer objects."
    #         )

    #     # Here you would implement the logic to save the validated data
    #     # to your internal storage.
    #     # print("Data validated and ready to be saved:", data)

    #     valids = ProxyValidator.validate_list(data)
    #     # print("Valid proxies:", valids)
    #     print(len(valids))
    #     for p in valids:
    #         print(f"{p.host}:{p.port}")

    @staticmethod
    def validate_and_save_data(data: List[ProxyServer]):
        """
        Validates and saves proxy data using multithreading.
        """
        if not isinstance(data, list) or not all(
            isinstance(d, ProxyServer) for d in data
        ):
            raise InvalidProxyError(
                "Invalid proxy data format. Expected a list of ProxyServer objects."
            )

        valid_proxies = ProxyValidator.validate_list(data)

        store = CacheManager()
        store.append_proxies(valid_proxies)

        # print(len(valid_proxies))
        # for proxy in valid_proxies:
        #     print(f"{proxy.host}:{proxy.port}")
