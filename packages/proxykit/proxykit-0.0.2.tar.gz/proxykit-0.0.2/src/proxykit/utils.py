# utils/key_mapping.py

from typing import Dict, List, Union

from proxykit.exceptions import InvalidProxyError
from proxykit.models import ProxyDataFormat, ProxyProtocol, ProxyServer
from proxykit.parser.csv_parser import CsvProxyParser
from proxykit.parser.ip_parser import IpProxyParser
from proxykit.parser.json_parser import JsonProxyParser


def parse_data(
    data: Union[List[str], str],
    format: ProxyDataFormat,
    key_mapping: Dict[str, str] = {},
    entry: List[str] = [],
) -> List[ProxyServer]:
    if isinstance(data, list):
        data = "".join(data)
    if format == ProxyDataFormat.IP:
        return IpProxyParser.parse(data)
    if format == ProxyDataFormat.JSON:
        return JsonProxyParser.parse(data, key_mapping, entry)
    if format == ProxyDataFormat.CSV:
        return CsvProxyParser.parse(data, key_mapping)
    raise InvalidProxyError("Invalid use of Custom ProxyDataFormat")


def format_proxy_protocol(protocol: ProxyProtocol):
    if protocol == ProxyProtocol.HTTP:
        return "http"
    if protocol == ProxyProtocol.HTTPS:
        return "https"
    if protocol == ProxyProtocol.SOCKS4:
        return "socks4"
    return "socks5"


def verbose_print(verbose: bool, *args, **kargs):
    if verbose:
        print(*args, **kargs)
