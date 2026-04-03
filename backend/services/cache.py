"""In-memory LRU cache with TTL for fast response reuse."""

import hashlib
import time
from collections import OrderedDict
from config import get_settings


class ResponseCache:
    """Thread-safe in-memory LRU cache with TTL expiration."""

    def __init__(self):
        settings = get_settings()
        self.max_size = settings.cache_max_size
        self.ttl = settings.cache_ttl_seconds
        self._cache: OrderedDict[str, dict] = OrderedDict()

    def _make_key(self, message: str, conversation_context: str = "") -> str:
        """Create a cache key from the message + context hash."""
        raw = f"{message.strip().lower()}|{conversation_context[-500:]}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def get(self, message: str, conversation_context: str = "") -> str | None:
        """Get cached response if exists and not expired."""
        key = self._make_key(message, conversation_context)
        if key not in self._cache:
            return None

        entry = self._cache[key]
        if time.time() - entry["timestamp"] > self.ttl:
            del self._cache[key]
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        return entry["response"]

    def set(self, message: str, response: str, conversation_context: str = ""):
        """Cache a response."""
        key = self._make_key(message, conversation_context)

        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = {"response": response, "timestamp": time.time()}
            return

        if len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)  # Remove oldest

        self._cache[key] = {"response": response, "timestamp": time.time()}

    def clear(self):
        """Clear all cached responses."""
        self._cache.clear()

    @property
    def size(self) -> int:
        return len(self._cache)


# Singleton instance
cache = ResponseCache()
