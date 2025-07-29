# Message filtering  
class Moderation:
    def __init__(self, banned_words=None):
        if banned_words is None:
            banned_words = []
        self.banned_words = set(banned_words)

    def add_banned_word(self, word):
        self.banned_words.add(word)

    def remove_banned_word(self, word):
        self.banned_words.discard(word)

    def is_message_allowed(self, message):
        for word in self.banned_words:
            if word in message:
                return False
        return True