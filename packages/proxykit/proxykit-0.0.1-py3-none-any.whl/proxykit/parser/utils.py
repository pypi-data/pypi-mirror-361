def extract_keys(key_mapping: dict[str, str] = {}) -> dict[str, str]:
    """
    Normalize key mapping with default fallbacks.
    """
    if key_mapping is None:
        key_mapping = {}

    return {
        "ip": key_mapping.get("ip", "ip"),
        "port": key_mapping.get("port", "port"),
        "protocol": key_mapping.get("protocol", "protocol"),
        "anonymity": key_mapping.get("anonymity", "anonymity"),
        "username": key_mapping.get("username", "username"),
        "password": key_mapping.get("password", "password"),
        "country": key_mapping.get("country", "country"),
        "latency": key_mapping.get("latency", "latency"),
        "is_working": key_mapping.get("is_working", "is_working"),
    }
