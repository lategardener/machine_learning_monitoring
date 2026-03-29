
import time

class RateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 2):
        self.max_requests = max_requests
        self.window = window_seconds
        self.clients = {}

    def is_allowed(self, client_id: str) -> bool:
        now = time.time()

        # On initialise l'historique pour un nouveau client
        if client_id not in self.clients:
            self.clients[client_id] = []

        # Nettoie les anciennes requêtes qui sont en dehors de la fenêtre de temps
        self.clients[client_id] = [req for req in self.clients[client_id] if now - req < self.window]

        # On autorise la requête s'il reste de la place
        if len(self.clients[client_id]) < self.max_requests:
            self.clients[client_id].append(now)
            return True

        return False