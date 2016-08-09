# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from gaw.jsonsocketserver.client import JsonSocketClient
from gaw.jsonsocketserver.server import JsonSocketServer
from gaw import JsonSocketException


class JsonSocketServerTest(unittest.TestCase):
    def test_server_client(self):
        from multiprocessing import Process, Event

        server_start = Event()

        def a(path):
            return path

        def b(path, a, b):
            return a + b

        def c(path, a, b):
            return a * b

        def server():
            server = JsonSocketServer(ip='0.0.0.0', port=4000)
            server.register_route(u'a ฟนำี', a)  # unicode path
            server.register_route('b', b)
            server.register_route('c', c)
            server.start(lambda: server_start.set())

        def client():
            client = JsonSocketClient()
            aa = client.request(ip='localhost', port=4000, path=u'a ฟนำี', payload=dict())
            self.assertEqual(aa, u'a ฟนำี')  # return the path unicode
            bb = client.request(ip='localhost', port=4000, path='b', payload=dict(a=1, b=2))
            self.assertEqual(bb, 3)
            cc = client.request(ip='localhost', port=4000, path='c', payload=dict(a=10, b=20))
            self.assertEqual(cc, 200)

        def wrong_client_path_not_found():
            client = JsonSocketClient()
            client.request(ip='localhost', port=4000, path='d', payload=dict())

        p = Process(target=server)
        try:
            p.start()
            server_start.wait()
            client()
            self.assertRaises(JsonSocketException, wrong_client_path_not_found)
            p.terminate()
            p.join()
        except Exception as e:
            # gracefully stop
            p.terminate()
            p.join()
            raise

    def test_server_client_verbose(self):
        from multiprocessing import Process, Event

        server_start = Event()

        def a(path):
            return path

        def b(path, a, b):
            return a + b

        def c(path, a, b):
            return a * b

        def server():
            server = JsonSocketServer(ip='0.0.0.0', port=4000, verbose=True)
            server.register_route(u'a ฟนำี', a)
            server.register_route('b', b)
            server.register_route('c', c)
            server.start(lambda: server_start.set())

        def client():
            client = JsonSocketClient(verbose=True)
            aa = client.request(ip='localhost', port=4000, path=u'a ฟนำี', payload=dict())
            self.assertEqual(aa, u'a ฟนำี')  # return the path test with unicode path
            bb = client.request(ip='localhost', port=4000, path='b', payload=dict(a=1, b=2))
            self.assertEqual(bb, 3)
            cc = client.request(ip='localhost', port=4000, path='c', payload=dict(a=10, b=20))
            self.assertEqual(cc, 200)

        p = Process(target=server)
        try:
            p.start()
            server_start.wait()
            client()
            p.terminate()
            p.join()
        except Exception as e:
            # gracefully stop
            p.terminate()
            p.join()
            raise


class JsonSocketServerFailTest(unittest.TestCase):

    def test_host_is_down(self):
        from multiprocessing import Event, Process

        server_start = Event()

        def a(path):
            return path

        def b(path, a, b):
            return a + b

        def c(path, a, b):
            return a * b

        def server():
            server = JsonSocketServer(ip='0.0.0.0', port=4000, verbose=True)
            server.register_route(u'a ฟนำี', a)
            server.register_route('b', b)
            server.register_route('c', c)
            server.start(lambda: server_start.set())

        def client():
            client = JsonSocketClient(verbose=True)
            self.assertRaises(Exception, client.request, ip='localhost', port=4000, path=u'a ฟนำี', payload=dict(), retries=0)

        p = Process(target=server)
        p.start()

        server_start.wait()

        p.terminate()
        p.join()

        client()

