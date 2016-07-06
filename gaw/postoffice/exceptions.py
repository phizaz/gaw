class ConnectionTerminated(Exception):
    def __init__(self): super(ConnectionTerminated, self).__init__('Connection Terminated')

class PostofficeException(Exception):

    def __init__(self, name, message, trace=None):
        self.name = name
        self.message = message
        self.trace = trace

    def __str__(self):
        return '\nname: {}\nmessage: {}\ntrace: {}'.format(self.name, self.message, self.trace)