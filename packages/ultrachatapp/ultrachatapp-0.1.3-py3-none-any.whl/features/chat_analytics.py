# chat_analytics.py
class ChatAnalytics:
    def __init__(self):
        self.message_count = 0
        self.user_message_count = {}

    def log_message(self, user_id):
        self.message_count += 1
        self.user_message_count[user_id] = self.user_message_count.get(user_id, 0) + 1

    def get_total_messages(self):
        return self.message_count

    def get_user_message_count(self, user_id):
        return self.user_message_count.get(user_id, 0)
