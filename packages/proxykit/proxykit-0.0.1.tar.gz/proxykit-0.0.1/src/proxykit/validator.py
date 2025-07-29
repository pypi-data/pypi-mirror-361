import random
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from requests.exceptions import (
    ConnectionError,
    ConnectTimeout,
    ProxyError,
    ReadTimeout,
    SSLError,
)
from tqdm import tqdm

from proxykit.constants import TEST_SITES, THREADS
from proxykit.models import ProxyServer
from proxykit.utils import format_proxy_protocol


class ProxyValidator:
    """
    ProxyValidator is a class that provides methods to validate proxy data.
    """

    @staticmethod
    def validate(proxy: ProxyServer) -> bool:
        """
        Validate the given proxy server object.

        Args:
            proxy (ProxyServer): The proxy server object to validate.

        Returns:
            bool: True if the proxy is valid, False otherwise.
        """
        if not proxy.host or not proxy.port:
            return False
        if proxy.port < 1 or proxy.port > 65535:
            return False

        try:
            protocol = format_proxy_protocol(proxy.protocol)
            if proxy.username is None or proxy.password is None:
                proxy_url = f"{protocol}://{proxy.host}:{proxy.port}"
            else:
                proxy_url = f"{protocol}://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}"

            # url = "https://api.myip.com"
            url = random.choice(TEST_SITES)
            proxies = {"http": proxy_url, "https": proxy_url}

            # Set short timeout to avoid hanging on dead proxies
            res = requests.get(url, proxies=proxies, timeout=15)

            # todo: add this in log file
            print(proxy_url)
            # print(f"Response from {url}:")
            # print(res.status_code)
            # print(res.content)
            # print()

            return res.status_code < 300

        except (
            ProxyError,
            ConnectTimeout,
            ReadTimeout,
            SSLError,
            ConnectionError,
        ):
            # todo: add this to log file
            # print(f"Proxy failed: {proxy.host}:{proxy.port} => {e}")
            return False

    @staticmethod
    def validate_list(proxies: list[ProxyServer]) -> list[ProxyServer]:
        """
        Validate a list of proxy server objects.

        Args:
            proxies (list[ProxyServer]): The list of proxy server objects to validate.

        Returns:
            list[ProxyServer]: A list of valid proxy server objects.
        """

        # return [proxy for proxy in proxies if ProxyValidator.validate(proxy)]
        def validate(proxy: ProxyServer) -> ProxyServer | None:
            return proxy if ProxyValidator.validate(proxy) else None

        valid_proxies = []

        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            future_to_proxy = {
                executor.submit(validate, proxy): proxy for proxy in proxies
            }

            for future in tqdm(
                as_completed(future_to_proxy),
                total=len(proxies),
                desc="Validating proxies",
            ):
                result = future.result()
                if result:
                    valid_proxies.append(result)
        print("Total valid proxies count: ", len(valid_proxies))
        return valid_proxies
