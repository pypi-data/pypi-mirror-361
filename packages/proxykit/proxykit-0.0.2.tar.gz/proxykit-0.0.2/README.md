# ProxyKit

A lightweight Python package for managing and rotating proxy servers with built-in validation and caching.

## Features

- 🔄 **Multiple Data Formats**: JSON, CSV, and IP list support
- ✅ **Proxy Validation**: Multi-threaded validation with configurable test sites
- 💾 **Smart Caching**: Persistent storage with TTL-based expiration
- 🎯 **Context Manager**: Easy integration with HTTP requests
- 🔀 **Random Selection**: Built-in proxy rotation

## Installation

```bash
pip install proxykit
```

## Quick Start

```python
from proxykit import ProxyKit, ProxyLoader
from proxykit.models import ProxyDataFormat

# clear all previous Proxies
ProxyKit.clear_all_data() # Optional only if you want to have fresh start

# Load proxies from various sources
ProxyLoader.load("proxies.json", format=ProxyDataFormat.JSON)
ProxyLoader.load("https://api.example.com/proxies", format=ProxyDataFormat.JSON)

# Use with context manager
with ProxyKit() as pk:
    proxy = pk.get_random_proxy()
    print(f"Using proxy: {proxy.host}:{proxy.port}")
```

## Supported Formats

- _`ip` and `port` are required rest all are optional_
- _`ip` can also be proper ip address with port separated by `:`, e.g: `127.0.0.1:8080` in this case `port` is ignored_

### JSON Format

```python
ProxyLoader.load(
    "proxies.json",
    format=ProxyDataFormat.JSON,
    entry=["data"],  # Navigate nested JSON
    key_mapping={
        "ip": "host",
        "anonymity": "anonymityLevel"
    }
)
```

### CSV Format

```python
ProxyLoader.load(
    "proxies.csv",
    format=ProxyDataFormat.CSV,
    key_mapping={
        "ip": "proxy_host",
        "port": "proxy_port"
    }
)
```

### IP List Format

```python
# Simple text file with IP:PORT format
ProxyLoader.load("proxies.txt", format=ProxyDataFormat.IP)
```

## API Reference

### ProxyLoader

| Method                                            | Description                                                     |
| ------------------------------------------------- | --------------------------------------------------------------- |
| `load(source, format, key_mapping, entry, token)` | Load proxies from file or URL                                   |
| `custom_load(data)`                               | Load pre-parsed [`ProxyServer`](src/proxykit/models.py) objects |

### ProxyKit

| Method               | Description                     |
| -------------------- | ------------------------------- |
| `get_random_proxy()` | Get a random validated proxy    |
| `clear_cache()`      | Clear cached proxy data         |
| `clear_all_data()`   | Static method to clear all data |

## Key Mapping

Map your data fields to ProxyKit's expected format:
<br> _key-mapping required for only unmatched keys_

```python
key_mapping = {
    "ip": "your_host_field",
    "port": "your_port_field",
    "protocol": "your_protocol_field",
    "anonymity": "your_anonymity_field",
    "username": "your_username_field",
    "password": "your_password_field",
    "country": "your_country_field",
    "latency": "your_latency_field",
    "is_working": "your_status_field"
}
```

## Models

### ProxyServer

```python
@dataclass
class ProxyServer:
    host: str
    port: int
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    anonymity: AnonymityLevel = AnonymityLevel.UNKNOWN
    country: str | None = None
    latency: float | None = None
    username: str | None = None
    password: str | None = None
    is_working: bool = True
```

### Enums

- **ProxyProtocol**: `HTTP`, `HTTPS`, `SOCKS4`, `SOCKS5`
- **AnonymityLevel**: `ELITE`, `ANONYMOUS`, `TRANSPARENT`, `UNKNOWN`
- **ProxyDataFormat**: `JSON`, `CSV`, `IP`, `CUSTOM`

## Configuration

Customize validation settings in [`constants.py`](src/proxykit/constants.py):

```python
TEST_SITES = [
    "https://httpbin.org/ip",
    "https://icanhazip.com",
    "https://example.com"
]
THREADS = 25  # Validation concurrency
```

## Requirements

- Python ≥ 3.8
- Dependencies: [`appdirs`](https://pypi.org/project/appdirs/), [`requests`](https://pypi.org/project/requests/), [`tqdm`](https://pypi.org/project/tqdm/)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Author

**Suraj Airi** - [surajairi.ml@gmail.com](mailto:surajairi.ml@gmail.com)
