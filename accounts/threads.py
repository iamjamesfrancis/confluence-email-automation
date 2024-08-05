import threading


class EmailThread(threading.Thread):
    """
    This class is used to send emails in a separate thread.
    """

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()
