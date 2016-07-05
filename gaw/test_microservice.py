from __future__ import print_function, absolute_import
from gaw import GawServer, entrypoint
from gaw.test_serializable import MathResult

class MathService(object):
    name = 'math_service'

    def __init__(self, hello_message):
        self.hello = hello_message

    @entrypoint
    def plus(self, a, b):
        return MathResult(self.hello, a + b)

    @entrypoint
    def multiply(self, a, b):
        return MathResult(self.hello, a * b)


service = GawServer('127.0.0.1', 5555, verbose=True, secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True)
service.add(MathService, hello_message='Hello!')
service.run()

