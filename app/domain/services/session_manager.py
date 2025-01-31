import logging
import redis
import json
from typing import List, Dict

class SessionManager:
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.redis = redis.Redis(host=host, port=port, db=db)

    @staticmethod
    def _get_key(user_id: str) -> str:
        return f"session:{user_id}"

    def create_session(self, user_id: str) -> None:
        """
        Create a new chat session for a user or do nothing if the session already exists.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            None
        """
        key = self._get_key(user_id)

        if not self.session_exists(key):
            logging.info(f"New session created for user_id: {user_id}")
        else:
            logging.info(f"Session already exists for user_id: {user_id}")

    def session_exists(self, user_id: str) -> bool:
        """
        Check if a chat session exists for a given user.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            bool: True if the session exists, False otherwise.
        """
        key = self._get_key(user_id)
        return self.redis.exists(key) == 1

    def add_message(self, user_id: str, role: str, content: str) -> None:
        """
        Add a message to the chat session history for a user.

        This method appends a message to the session history stored in Redis for the specified user.
        Each message is represented as a dictionary containing the role and content.

        Args:
            user_id (str): The unique identifier of the user.
            role (str): The role of the sender, e.g., 'user' or 'assistant'.
            content (str): The content of the message to be added.

        Returns:
            None
        """
        key = self._get_key(user_id)
        message = {"role": role, "content": content}
        self.redis.rpush(key, json.dumps(message))

    def get_history(self, user_id: str) -> List[Dict[str, str]]:
        """
        Retrieve the chat session history for a given user.

        This method retrieves the chat session history stored in Redis for the specified user.
        The history is represented as a list of dictionaries, each containing the role and content of a message.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            List[Dict[str, str]]: The chat session history for the user, or an empty list if the user has no history.
        """
        key = self._get_key(user_id)
        messages = self.redis.lrange(key, 0, -1)
        return [json.loads(message) for message in messages]

    def clear_history(self, user_id: str) -> None:
        """
        Clear the chat session history for a given user.

        This method removes the chat session history stored in Redis for the specified user.
        After calling this method, the user's history will be an empty list when retrieved.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            None
        """
        key = self._get_key(user_id)
        self.redis.delete(key)
        key = self._get_key(user_id)
        self.redis.delete(key)