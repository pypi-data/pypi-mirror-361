class ProxyKitError(Exception):
    """Base exception for all ProxyKit-related errors."""
    pass

class InvalidProxyError(ProxyKitError):
    """Raised when a proxy has invalid or missing fields."""
    pass

class NoAvailableConfigError(ProxyKitError):
    """Raised when no valid proxies, user agents, or headers are available."""
    pass

# this will be used by context manager to handle proxy failures
class ProxyNotWorkingError(ProxyKitError):
    """Raised when a proxy is not working or has failed."""
    def __init__(self, message: str, proxy: str):
        super().__init__(message)
        self.proxy = proxy