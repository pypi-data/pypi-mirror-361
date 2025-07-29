 # Profile settings  
class UserProfiles:
    def __init__(self, username, email):
        self.username = username
        self.email = email

    def update_email(self, new_email):
        self.email = new_email

    def display_profile(self):
        return f"Username: {self.username}, Email: {self.email}"