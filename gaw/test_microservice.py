from __future__ import print_function, absolute_import
from gaw.microservice import Microservice
from gaw.entrypoint import entrypoint

class TestService(object):

    name = 'test_service'

    def __init__(self):
        print('init a service')
        pass

    @entrypoint
    def plus(self, a, b):
        return a + b

    @entrypoint
    def multiply(self, a, b):
        return a * b

service = Microservice('127.0.0.1', 4444, verbose=False)
service.add(TestService).run()