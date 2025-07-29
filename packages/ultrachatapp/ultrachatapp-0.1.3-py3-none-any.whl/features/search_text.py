# Search messages/users 
from typing import List
from rapidfuzz import process, fuzz
class Search:
    def __init__(self, data):
        """
        Initialize the Search class with data.
        :param data: List of messages or users to search from.
        """
        self.data = data

    def search_by_keyword(self, keyword):
        return [
            item for item in self.data
            if keyword.lower() in item.get("message", "").lower()
        ]

# def search_by_user(self, username):
#     """
#     Search for messages by a specific user.
#     :param username: The username to search for.
#     :return: List of messages by the user.
#     """
#     return [item for item in self.data if item.get('user', '').lower() == username.lower()]


# Utility function for fuzzy search
def fuzzy_search(keyword: str, data: List[str], limit: int = 5, threshold: int = 60):
    matches = process.extract(keyword, data, scorer=fuzz.WRatio, limit=limit)
    return [match[0] for match in matches if match[1] >= threshold]