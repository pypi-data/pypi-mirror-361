  # Last seen, online status  
class Presence:
    def __init__(self, user_id):
      self.user_id = user_id
      self.status = "offline"
      self.last_seen = None

    def set_online(self):
      self.status = "online"
      self.last_seen = None

    def set_offline(self, last_seen_time):
      self.status = "offline"
      self.last_seen = last_seen_time

    def get_status(self):
      return {
        "user_id": self.user_id,
        "status": self.status,
        "last_seen": self.last_seen
      }