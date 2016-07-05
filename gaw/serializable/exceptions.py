class SerializeError(Exception):

    def __init__(self, val):
        self.val = val

    def __str__(self):
        return self.val