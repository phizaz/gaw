try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from gaw import GawServer, GawClient
from multiprocessing import Process, Event

class GawTest(unittest.TestCase):
    def test_run_service_entrypoint_style(self):
        server_start = Event()

        def service():
            from gaw import entrypoint
            class Service(object):
                name = 'ServiceEntrypointStyle'

                @entrypoint
                def plus(self, a, b):
                    return a + b

                @entrypoint
                def mul(self, a, b):
                    return a * b

            GawServer(ip='0.0.0.0', port=4000).add(Service).run(lambda: server_start.set())

        def client():
            service = GawClient(ip='localhost', port=4000).ServiceEntrypointStyle

            self.assertEqual(service.plus(1, 2), 3)
            self.assertEqual(service.mul(10, 20), 200)

        p = Process(target=service)
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

    def test_run_service_interface_style(self):
        from gaw import interface_class, service_class, client_class

        server_start = Event()

        @interface_class(service_name='ServiceInterfaceStyle')
        class Interface(object):
            def plus(self, a, b): pass

            def mul(self, a, b): pass

        def service():
            @service_class
            class Service(Interface):
                def plus(self, a, b):
                    return a + b

                def mul(self, a, b):
                    return a * b

            GawServer(ip='0.0.0.0', port=4000).add(Service).run(lambda: server_start.set())

        def client():
            @client_class(ip='localhost', port=4000)
            class Client(Interface): pass

            client = Client()
            self.assertEqual(client.plus(2, 3), 5)
            self.assertEqual(client.mul(10, 20), 200)

        p = Process(target=service)
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

    def test_port_properly_destroyed(self):
        server_start = Event()

        def service():
            from gaw import entrypoint
            class Service(object):
                name = 'TestPortProperlyDestroyedService'

                @entrypoint
                def plus(self, a, b):
                    return a + b

                @entrypoint
                def mul(self, a, b):
                    return a * b

            GawServer(ip='0.0.0.0', port=4000).add(Service).run(lambda: server_start.set())

        def client():
            GawClient(ip='localhost', port=4000).TestPortProperlyDestroyedService.plus(1, 2)

        def run_test():
            server_start.clear()
            p = Process(target=service)
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

        run_test()
        run_test()

    def test_multiple_service(self):
        from gaw import entrypoint

        server_start = Event()

        class A(object):
            name = 'A'

            @entrypoint
            def a(self):
                return 10

        class B(object):
            name = 'B'

            @entrypoint
            def b(self):
                return 20

        class Both(object):
            name = 'Both'

            @entrypoint
            def sum(self):
                client = GawClient(ip='localhost', port=4000)
                A = client.A
                B = client.B
                return A.a() + B.b()

        def server():
            GawServer(ip='0.0.0.0', port=4000).add(A).add(B).add(Both).run(lambda: server_start.set())

        def client():
            conn = GawClient(ip='localhost', port=4000)
            a = conn.A
            b = conn.B
            both = conn.Both

            self.assertEqual(a.a(), 10)
            self.assertEqual(b.b(), 20)
            self.assertEqual(both.sum(), 30)

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

    def test_with_serializable(self):
        from gaw import Serializable, client_class, interface_class, service_class

        server_start = Event()

        class Response(Serializable):
            def __init__(self, a, b):
                self.a = a
                self.b = b

        @interface_class('TestWithSerializable')
        class Interface(object):
            def get(self, a, b): pass

        def server():
            @service_class
            class Service(Interface):
                def get(self, a, b):
                    return Response(a, b)

            GawServer(ip='0.0.0.0', port=4000).add(Service).run(lambda: server_start.set())

        def client():
            @client_class(ip='localhost', port=4000)
            class Client(Interface): pass

            res = Client().get(10, 20)
            self.assertTrue(isinstance(res, Response))
            self.assertEqual(res.a, 10)
            self.assertEqual(res.b, 20)

        from multiprocessing import Process
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

    def test_with_encryption(self):
        secret = 'rixIMTHM1tlRP3McKqhopU/18S+dIh8M'

        from gaw import interface_class, service_class, client_class

        server_start = Event()

        @interface_class(service_name='ServiceInterfaceStyle')
        class Interface(object):
            def plus(self, a, b): pass

            def mul(self, a, b): pass

        def service():
            @service_class
            class Service(Interface):
                def plus(self, a, b):
                    return a + b

                def mul(self, a, b):
                    return a * b

            GawServer(ip='0.0.0.0', port=4000, secret=secret, is_encrypt=True).add(Service).run(lambda: server_start.set())

        def client():
            @client_class(ip='localhost', port=4000, secret=secret, is_encrypt=True)
            class Client(Interface): pass

            client = Client()
            self.assertEqual(client.plus(2, 3), 5)
            self.assertEqual(client.mul(10, 20), 200)

        def wrong_client_no_secret():
            @client_class(ip='localhost', port=4000)
            class Client(Interface): pass

            client = Client()
            self.assertEqual(client.plus(2, 3), 5)
            self.assertEqual(client.mul(10, 20), 200)

        def wrong_client_no_encryption():
            @client_class(ip='localhost', port=4000, secret=secret)
            class Client(Interface): pass

            client = Client()
            self.assertEqual(client.plus(2, 3), 5)
            self.assertEqual(client.mul(10, 20), 200)

        p = Process(target=service)
        try:
            p.start()

            server_start.wait()
            client()

            from gaw import PostofficeException

            self.assertRaises(PostofficeException, wrong_client_no_secret)
            self.assertRaises(PostofficeException, wrong_client_no_encryption)

            p.terminate()
            p.join()
        except Exception as e:
            # gracefully stop
            p.terminate()
            p.join()
            raise
