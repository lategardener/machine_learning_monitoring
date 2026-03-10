
import time

class RateLimiter:
    def __init__(self, interval_seconds: int = 20):
        self.interval = interval_seconds
        self.clients = {} 

    def is_allowed(self, client_id: str):
        now = time.time()
        last = self.clients.get(client_id, 0)
        if now - last < self.interval:
            return False
        self.clients[client_id] = now
        return True