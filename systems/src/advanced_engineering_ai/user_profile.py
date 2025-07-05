"""
User Profile and Feedback Mechanism
"""
class UserProfile:
    def __init__(self, username):
        self.username = username
        self.preferences = {}
        self.history = []

    def update_preferences(self, new_preferences):
        self.preferences.update(new_preferences)

    def add_history(self, interaction):
        self.history.append(interaction)
