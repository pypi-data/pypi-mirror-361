# Fetch external user details
class GetExternalUserURL:
    def __init__(self, base_url):
        self.base_url = base_url

    def build_url(self, user_id):
        if not user_id:
            raise ValueError("User ID cannot be empty")
        return f"{self.base_url}/external_user/{user_id}"

# Example usage
# url_builder = GetExternalUserURL("https://api.example.com")
# print(url_builder.build_url("12345"))