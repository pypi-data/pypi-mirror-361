import time
from typing import Any, Dict

class Cache:
    def __init__(self, ttl: int):
        self.ttl = ttl  # Cache expiration time in seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def _is_expired(self, timestamp: float) -> bool:
        """ Checking whether data has expired or not """
        return (time.time() - timestamp) > self.ttl

    def get(self, key: str) -> Any:
        """ Getting data from cache """
        cache_item = self.cache.get(key)
        
        if cache_item and not self._is_expired(cache_item["timestamp"]):
            return cache_item["data"]
        
        return None

    def set(self, key: str, data: Any):
        """ Store data in cache """
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()  # Data storage time
        }

    def clear(self, key: str):
        """ Delete data from cache """
        if key in self.cache:
            del self.cache[key]

    def clear_all(self):
        """" Delete all data from cache """
        self.cache.clear()