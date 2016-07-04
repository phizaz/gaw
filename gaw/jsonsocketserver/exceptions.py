class JsonSocketException(Exception):

    def __init__(self, name, message, trace):
        self.name = name
        self.message = message
        self.trace = trace

    def __str__(self):
        return '\nname: {}\nmessage: {}\ntrace: {}'.format(self.name, self.message, self.trace)