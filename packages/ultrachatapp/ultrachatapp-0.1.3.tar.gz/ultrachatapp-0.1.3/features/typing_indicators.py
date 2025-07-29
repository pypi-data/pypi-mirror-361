# Show typing status 
class TypingIndicators:
    def __init__(self):
        self.users_typing = set()

    def user_started_typing(self, user_id):
        """Mark a user as typing."""
        self.users_typing.add(user_id)

    def user_stopped_typing(self, user_id):
        """Remove a user from typing status."""
        self.users_typing.discard(user_id)

    def get_typing_users(self):
        """Get a list of users currently typing."""
        return list(self.users_typing)