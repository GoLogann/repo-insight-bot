import redis
import json
from typing import List, Dict

class SessionManager:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    @staticmethod
    def _get_key(user_id: str) -> str:
        return f"session:{user_id}"

    def add_message(self, user_id: str, role: str, content: str) -> None:
        key = self._get_key(user_id)
        message = {"role": role, "content": content}
        self.redis.rpush(key, json.dumps(message))

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        key = self._get_key(user_id)
        messages = self.redis.lrange(key, 0, -1)
        return [json.loads(message) for message in messages]

    def clear_history(self, user_id: str) -> None:
        key = self._get_key(user_id)
        self.redis.delete(key)