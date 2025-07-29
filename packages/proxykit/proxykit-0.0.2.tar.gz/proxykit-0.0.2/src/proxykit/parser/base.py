from collections.abc import Iterable
from typing import List

from proxykit.models import ProxyServer

# opt-1. host and port are required fields for the ProxyServer class.
# opt-2. json format
# opt-3. csv format
# opt-4. custom format (host, port)[required] {optional}


class BaseProxyParser:
    """
    Base class for parsing proxy data from various formats.
    Subclasses should implement the `parse` method.
    """

    def parse(self, data: str) -> List[ProxyServer]:
        """
        Parse the given data and return a list of ProxyServer objects.

        Args:
            data (str): The raw proxy data in a specific format (e.g., JSON, CSV, etc.).
        Returns:
            list: A list of ProxyServer objects.
        """
        raise NotImplementedError("Subclasses must implement this method.")
