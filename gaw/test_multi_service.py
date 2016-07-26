from gaw import GawServer, entrypoint, GawClient

class A(object):

    name = 'A'

    @entrypoint
    def home(self):
        return 'A home'

class B(object):

    name = 'B'

    @entrypoint
    def home(self):
        return 'B home'

class Both(object):

    name = 'Both'

    @entrypoint
    def home(self):
        client = GawClient(ip='localhost', port=12345)
        A = client.A
        B = client.B
        return A.home() + B.home()

GawServer(ip='0.0.0.0', port=12345).add(A).add(B).add(Both).run()