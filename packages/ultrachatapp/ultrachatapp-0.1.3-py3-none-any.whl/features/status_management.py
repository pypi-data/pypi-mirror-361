class StatusManagement:
    def __init__(self):
        self.user_status = {}

    def set_status(self, user_id, status):
        """Set the status of a user."""
        self.user_status[user_id] = status

    def get_status(self, user_id):
        """Get the status of a user."""
        return self.user_status.get(user_id, "Offline")

    def remove_status(self, user_id):
        """Remove the status of a user."""
        if user_id in self.user_status:
            del self.user_status[user_id]
