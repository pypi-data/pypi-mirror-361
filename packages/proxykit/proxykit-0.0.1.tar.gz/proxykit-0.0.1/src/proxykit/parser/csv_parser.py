import csv
from io import StringIO

from proxykit.exceptions import InvalidProxyError
from proxykit.models import AnonymityLevel, ProxyProtocol, ProxyServer

from .utils import extract_keys  # Use same util as JsonParser


class CsvProxyParser:
    """
    Parses proxy data in CSV format using key mapping.
    Only 'ip' and 'port' are required (can be separate or combined as 'ip:port').
    """

    @staticmethod
    def parse(data: str, key_mapping: dict[str, str] = {}) -> list[ProxyServer]:
        proxy_servers: list[ProxyServer] = []
        reader = csv.DictReader(StringIO(data))
        keys = extract_keys(key_mapping)

        for row in reader:
            try:
                ip_value = row.get(keys["ip"], "").strip()
                port_value = row.get(keys["port"], "").strip()

                if ":" in ip_value:
                    host, port = ip_value.split(":", 1)
                    port = int(port)
                elif ip_value and port_value:
                    host = ip_value
                    port = int(port_value)
                else:
                    raise InvalidProxyError("Missing IP or Port in CSV row")

                server = ProxyServer(
                    host=host,
                    port=port,
                    protocol=ProxyProtocol(row.get(keys["protocol"], "http")),
                    latency=float(row[keys["latency"]])
                    if row.get(keys["latency"])
                    else None,
                    country=row.get(keys["country"]),
                    username=row.get(keys["username"]),
                    password=row.get(keys["password"]),
                    anonymity=AnonymityLevel(row.get(keys["anonymity"], "unknown")),
                    is_working=row.get(keys["is_working"], "true").strip().lower()
                    == "true",
                )
                proxy_servers.append(server)

            except KeyError as e:
                # raise InvalidProxyError(f"Missing required field: {e}") from e
                print(f"\033[91mMissing required field: {e} Input data: `{row}`\033[0m")
            except ValueError as ve:
                # raise InvalidProxyError(f"Invalid value in CSV row: {row}") from ve
                print(
                    f"\033[91mInvalid value in CSV row: {ve} Input data: `{row}`\033[0m"
                )

        return proxy_servers
