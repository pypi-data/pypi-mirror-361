class ReadReceipts:
    def __init__(self):
        self.receipts = {}

    def mark_as_read(self, message_id, user_id):
        if message_id not in self.receipts:
            self.receipts[message_id] = set()
        self.receipts[message_id].add(user_id)

    def has_been_read_by(self, message_id, user_id):
        return message_id in self.receipts and user_id in self.receipts[message_id]

    def get_read_by_users(self, message_id):
        return self.receipts.get(message_id, set())