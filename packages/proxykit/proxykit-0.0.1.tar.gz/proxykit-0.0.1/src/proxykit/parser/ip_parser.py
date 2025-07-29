from collections.abc import Iterable

from proxykit.exceptions import InvalidProxyError
from proxykit.models import ProxyServer

from .base import BaseProxyParser


class IpProxyParser:
    """
    Parses proxy data in IP format.
    """

    @staticmethod
    def parse(data: str) -> list[ProxyServer]:
        """
        Parse the given IP data and return a list of ProxyServer objects.

        Args:
            data (str): The raw proxy data in IP format.

        Returns:
            list: A list of ProxyServer objects.
        """
        if not isinstance(data, str) or not data.strip():
            raise InvalidProxyError(
                "Invalid IP data format. Expected a non-empty string."
            )

        proxies: list[ProxyServer] = []
        for value in data.splitlines():
            try:
                ip, port = value.strip().split(":")
                server = ProxyServer(host=ip, port=int(port))
                proxies.append(server)
            except Exception as e:
                # raise InvalidProxyError(f"Invalid proxy format: {e}")
                print(
                    f"\033[91mInvalid proxy format: {e} Input data: `{value.strip()}`\033[0m"  # noqa: E501
                )
        return proxies
