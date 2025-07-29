from enum import Enum

from proxykit.models import ProxyDataFormat, ProxyServer

from .internal_loader import _InternalProxyLoader


class ProxyLoader:
    """
    ProxyLoader is a class that provides methods to load proxy data from various formats
    It supports JSON, CSV, IP formats and custom formats.
    """

    @staticmethod
    def load(
        source: str,
        format: ProxyDataFormat = ProxyDataFormat.JSON,
        key_mapping: dict[str, str] = {},
        entry: list[str] = [],
        token: str | None = None,
    ):
        """
        Load proxy data from the specified source in the given format.

        Args:
            source (str): The source of the proxy data (URL for remote access or local file path).
             URLs must start with http or https.
            format (ProxyDataFormat): The format of the proxy data.
                <br>**Try to avoid csv format, or be more cautious about your data and key_mapping**
            key_mapping (dict[str, str]): Optional mapping of keys for parsing.
                Available keys to map: "ip", "port", "protocol", "anonymity",
                "username", "password", "country", "latency", "is_working".
                <br>`Keys (we expecting): values (your data should have these keys)`<br>
                Example: {"ip": "your-host", "port": "your-port"}
                <br>Ignore matching keys
            entry (list[str]): [Only for JSON] Optional entry point for nested data structures.
                entry should be a list of keys to navigate through the JSON structure.
                <br> json: {'a': {'b': {'c': 'value'}}} -> entry=['a', 'b', 'c'] to get 'value'.
            token (str | None): Optional token for authentication or access control. [only for remote sources]

        Returns:
            list: A list of parsed proxy server objects.
        """  # noqa: E501

        if source.startswith("http://") or source.startswith("https://"):
            _InternalProxyLoader.load_remote(
                url=source,
                format=format,
                key_mapping=key_mapping,
                entry=entry,
                token=token,
            )
        else:
            _InternalProxyLoader.load_local(
                path=source,
                format=format,
                key_mapping=key_mapping,
                entry=entry,
            )

    @staticmethod
    def custom_load(data: list[ProxyServer]):
        """
        Assuming data is already in the form of ProxyServer objects,
        data will be validated and then stored in the internal storage.
        """
        _InternalProxyLoader.validate_and_save_data(data)
