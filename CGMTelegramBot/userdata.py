import time


class NonPersistentUserData:

    __slots__ = "mute_until"

    def __init__(self):
        self.mute_until = 0


class UserDataManager:

    def __init__(self):
        self.user_data: {str: NonPersistentUserData} = {}

    def init_username(self, username):
        if username not in self.user_data:
            self.user_data[username] = NonPersistentUserData()

    def is_username_silenced(self, username):
        if not self.contains_username(username):
            return False

        return self.user_data[username].mute_until > time.time()

    def silence_username_for_seconds(self, username, time_in_seconds):
        if not self.contains_username(username):
            return

        self.user_data[username].mute_until = time.time() + time_in_seconds

    def silence_username_for_minutes(self, username, time_in_minutes):
        if not self.contains_username(username):
            return

        self.silence_username_for_seconds(username, time_in_minutes * 60)

    def unmute_username(self, username):
        if not self.contains_username(username):
            return

        self.user_data[username].mute_until = 0

    def contains_username(self, username):
        if username is None or len(username) < 1:
            return False

        return username in self.user_data
