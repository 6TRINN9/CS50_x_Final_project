import redis
from flask import current_app

class RedisClient:

    def __init__(self, app=None):
        self.redis = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.redis = redis.from_url(app.config['REDIS_URL'], decode_respinses=True)

    @staticmethod
    def _key(session_id: int, seat_id :int) -> str:
        return f"reservation:{session_id}:{seat_id}"

    def reserve(self, session_id: int, seat_id: int, user_id: int, ttl: int) -> bool:
        """
        Reserves space atomically.
        SET key value NX EX ttl — returns True if the key didn't exist.
        This is race condition protection: only one client will receive True.
        """

        key = self._key(session_id, seat_id)
        result = self.redis.set(key, str(user_id), nx=True, ex=ttl)
        return result is not None

    def release(self, session_id: int, seat_id: int, user_id: int) -> bool:
        """Frees the seat (only if it is owned by the same user)."""
        key = self._key(session_id, seat_id)
        # Lua script for atomic owner check and deletion
        lua = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
        return redis.call('DEL', KEYS[1])
        else
        return 0
        end
        """
        script = self.redis.register_script(lua)
        return bool(script(keys=[key], args=[str(user_id)]))

    def get_owner(self, session_id: int, seat_id: int):
        """Returned ID owner reserve or None"""
        key = self._key(session_id, seat_id)
        val = self.redis.get(key)
        return int(val) if val else None

    def get_ttl(self, session_id: int, seat_id: int) -> int:
        """Remaining reserve time in seconds."""
        key = self._key(session_id, seat_id)
        return self.redis.ttl(key)

    def extend(self, session_id: int, seat_id: int, user_id: int, ttl: int) -> bool:
        """Extend the reserve (if the owner is the same)."""
        key = self._key(session_id, seat_id)
        lua = """
        if redis.call('GET', KEYS[1]) == ARGV[1] then
            return redis.call('EXPIRE', KEYS[1], ARGV[2])
        else
            return 0
        end
        """

        script = self.redis.register_script(lua)
        return bool(script(keys=[key], args=[str(user_id), str(ttl)]))
