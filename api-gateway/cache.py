import time

class CacheItem:
    def __init__(self, value, ttl: int):
        self.value = value
        self.expire_at = time.time() + ttl

    def is_expired(self):
        return time.time() > self.expire_at

class SimpleCache:
    def __init__(self, ttl: int = 600):
        self.ttl = ttl
        self.store = {}

    def get(self, key):
        item = self.store.get(key)
        if item and not item.is_expired():
            return item.value
        if key in self.store:
            del self.store[key]
        return None

    def set(self, key, value):
        self.store[key] = CacheItem(value, self.ttl)