class Session:
    def __init__(self, user_id, session_id, start_time):
        """
        Initialize a new session.

        :param user_id: ID of the user associated with the session
        :param session_id: Unique identifier for the session
        :param start_time: Timestamp when the session started
        """
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = start_time
        self.is_active = True

    def end_session(self, end_time):
        """
        End the session.

        :param end_time: Timestamp when the session ended
        """
        self.end_time = end_time
        self.is_active = False

    def get_session_duration(self):
        """
        Calculate the duration of the session.

        :return: Duration of the session in seconds, or None if the session is still active
        """
        if self.is_active:
            return None
        return (self.end_time - self.start_time).total_seconds()

    def __repr__(self):
        return f"Session(user_id={self.user_id}, session_id={self.session_id}, is_active={self.is_active})"