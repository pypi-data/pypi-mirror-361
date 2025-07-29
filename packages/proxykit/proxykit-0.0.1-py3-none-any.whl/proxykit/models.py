from dataclasses import asdict, dataclass, fields
from enum import Enum


class ProxyProtocol(Enum):
    HTTP = "http"
    HTTPS = "https"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"


class AnonymityLevel(Enum):
    ELITE = "elite"
    ANONYMOUS = "anonymous"
    TRANSPARENT = "transparent"
    UNKNOWN = "unknown"


class ProxyDataFormat(Enum):
    JSON = "json"
    CSV = "csv"
    IP = "ip"
    CUSTOM = "custom"


@dataclass(frozen=True, eq=True)
class ProxyServer:
    host: str
    port: int
    country: str | None = None
    latency: float | None = None
    username: str | None = None
    password: str | None = None
    protocol: ProxyProtocol = ProxyProtocol.HTTP
    # provider:str = "local"
    anonymity: AnonymityLevel = AnonymityLevel.UNKNOWN
    is_working: bool = True

    def set_working(self, value: bool):
        object.__setattr__(self, "is_working", value)

    def to_dict(self) -> dict:
        d = asdict(self)

        for k, v in d.items():
            if isinstance(v, Enum):
                d[k] = v.value
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "ProxyServer":
        init_args = {}
        for field in fields(cls):
            value = data.get(field.name)
            if (
                isinstance(field.type, type)
                and issubclass(field.type, Enum)
                and value is not None
            ):
                init_args[field.name] = field.type(value)  # Reconstruct enum
            else:
                init_args[field.name] = value
        return cls(**init_args)


if "__main__" == __name__:
    a = ProxyServer("34.324.3.43.3", 34)
    asdict(a)
