import json

from proxykit.exceptions import InvalidProxyError
from proxykit.models import AnonymityLevel, ProxyProtocol, ProxyServer

from .utils import extract_keys


class JsonProxyParser:
    """
    Parses proxy data in JSON format.
    """

    # todo: flexibly handle little change in key names in json data
    @staticmethod
    def parse(
        data: str, key_mapping: dict[str, str] = {}, entry: list[str] = []
    ) -> list[ProxyServer]:
        """
        Parse the given JSON data and return a list of ProxyServer objects.

        Args:
            data (str): The raw proxy data in JSON format, where each item is a dictionary containing proxy details.

        Returns:
            list: A list of ProxyServer objects.

        """  # noqa: E501
        val: dict = json.loads(data) if isinstance(data, str) else data
        proxy_servers: list[ProxyServer] = []

        for key in entry:
            if key not in val:
                raise InvalidProxyError(f"Invalid entry point in JSON: {key}")
            val = val[key]

        keys = extract_keys(key_mapping)

        for proxy in val:
            try:
                ip_value = proxy.get(keys["ip"])
                port_value = proxy.get(keys["port"])

                if ip_value and ":" in ip_value:
                    host, port = ip_value.split(":", 1)
                    port = int(port)
                elif ip_value and port_value:
                    host = ip_value
                    port = int(port_value)
                else:
                    raise InvalidProxyError("Missing IP or Port in proxy data")

                server = ProxyServer(
                    host=host,
                    port=port,
                    country=proxy.get(keys["country"]),
                    latency=proxy.get(keys["latency"]),
                    username=proxy.get(keys["username"]),
                    password=proxy.get(keys["password"]),
                    protocol=ProxyProtocol(proxy.get(keys["protocol"], "http")),
                    anonymity=AnonymityLevel(proxy.get(keys["anonymity"], "unknown")),
                    is_working=proxy.get(keys["is_working"], True),
                )
                proxy_servers.append(server)
            except KeyError as e:
                # raise InvalidProxyError(f"Invalid proxy entry: {proxy}") from e
                print(f"\033[91mInvalid proxy entry: {e} Input data: `{proxy}`\033[0m")

        return proxy_servers
