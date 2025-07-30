from cachetools import LRUCache

class Cache:
    def __init__(self, max_size: int = 100000):
        self.cache = LRUCache(maxsize=max_size)

    def get(self, key: str):
        return self.cache.get(key)

    def set(self, key: str, value):
        self.cache[key] = value

    def has(self, key: str) -> bool:
        return key in self.cache

    def delete(self, key: str) -> bool:
        return self.cache.pop(key, None) is not None

    def clear(self):
        self.cache.clear()

global_cache = Cache()