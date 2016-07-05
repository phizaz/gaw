from gaw import Serializable

class MathResult(Serializable):

    def __init__(self, header, result):
        self.header = header
        self.result = result

    def get_result(self):
        return self.result

    def get_header(self):
        return self.header
