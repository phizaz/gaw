# -*- coding: UTF-8 -*-

try:
    import unittest2 as unittest
except ImportError:
    import unittest  # noqa

from gaw.postoffice.server import PostofficeServer
from gaw.postoffice.client import PostofficeClient

class PostofficeTest(unittest.TestCase):

    def test_pad(self):
        from gaw.postoffice.core import pad

        b = bytes('A')
        res = bytearray(pad(b, 10))

        self.assertEqual(res[0], ord('A'))
        for each in res[1:]:
            self.assertEqual(each, 9) # padding with 9

    def test_unpad(self):
        from gaw.postoffice.core import pad, unpad

        b = bytes('A')
        padded = pad(b, 10)
        bb = unpad(padded)

        self.assertEqual(b, bb)

    def test_gen_random_bytes(self):
        from gaw.postoffice.core import get_random_bytes

        b = get_random_bytes(10)
        self.assertIsInstance(b, bytes)
        self.assertEqual(len(b), 10)

        b = get_random_bytes(15)
        self.assertIsInstance(b, bytes)
        self.assertEqual(len(b), 15)

    def test_sign_verify(self):
        import base64

        secret = base64.b64decode('2PUHk3nHknfs8uF7XO6Cvzt88uGO1yvQ')
        secret2 = base64.b64decode('6T0/bXKIqQTyFKQiOwJjhcqt8lNJTRhS')

        b = bytes('A')
        from gaw.postoffice.core import attach_signature, verify_signature, PostofficeException
        signed = attach_signature(b, secret)
        bb = verify_signature(signed, secret)

        self.assertEqual(b, bb)

        def test():
            return verify_signature(signed, secret2)

        self.assertRaises(PostofficeException, test)

    def test_encrypt_decrypt_verify(self):
        import base64

        secret = base64.b64decode('2PUHk3nHknfs8uF7XO6Cvzt88uGO1yvQ')
        secret2 = base64.b64decode('6T0/bXKIqQTyFKQiOwJjhcqt8lNJTRhS')

        b = bytes('A')
        from gaw.postoffice.core import encrypt_and_sign, decrypt_and_verify, PostofficeException
        signed = encrypt_and_sign(b, secret)
        bb = decrypt_and_verify(signed, secret)

        self.assertEqual(b, bb)

        def test():
            return decrypt_and_verify(signed, secret2)

        self.assertRaises(PostofficeException, test)

    def test_server_client(self):
        import time

        send_msg = u'test ฟนำีฟนำีฟนำีฟนำี'

        def on_message(msg):
            self.assertEqual(msg, send_msg)
            return msg

        def server():
            PostofficeServer(ip='0.0.0.0', port=4000, on_message=on_message)

        def client():
            client = PostofficeClient(ip='localhost', port=4000)
            response = client.send(send_msg)
            self.assertEqual(response, send_msg)

        from multiprocessing import Process
        p = Process(target=server)
        p.start()

        time.sleep(0.1)
        client()

        p.terminate()
        p.join()

    def test_server_client_verbose(self):
        import time

        send_msg = u'test ฟนำีฟนำีฟนำีฟนำี'

        def on_message(msg):
            self.assertEqual(msg, send_msg)

        def server():
            PostofficeServer(ip='0.0.0.0', port=4000, on_message=on_message, verbose=True)

        def client():
            client = PostofficeClient(ip='localhost', port=4000, verbose=True)
            client.send(send_msg)

        from multiprocessing import Process
        p = Process(target=server)
        p.start()

        time.sleep(0.1)
        client()

        p.terminate()
        p.join()

    def test_server_client_with_encryption(self):
        import time

        secret = '6T0/bXKIqQTyFKQiOwJjhcqt8lNJTRhS'
        send_msg = u'test ฟนำีฟนำีฟนำีฟนำี'

        def on_message(msg):
            self.assertEqual(msg, send_msg)

        def server():
            PostofficeServer(ip='0.0.0.0', port=4000, on_message=on_message, secret=secret, is_encrypt=True)

        def client():
            client = PostofficeClient(ip='localhost', port=4000, secret=secret, is_encrypt=True)
            client.send(send_msg)

        def wrong_client_no_secret():
            client = PostofficeClient(ip='localhost', port=4000)
            client.send(send_msg)

        def wrong_client_no_encryption():
            client = PostofficeClient(ip='localhost', port=4000, secret=secret)
            client.send(send_msg)

        from multiprocessing import Process
        p = Process(target=server)
        p.start()

        time.sleep(0.1)
        client()

        from gaw import PostofficeException
        self.assertRaises(PostofficeException, wrong_client_no_secret)
        self.assertRaises(PostofficeException, wrong_client_no_encryption)

        p.terminate()
        p.join()

    def test_multiple_client(self):
        import time
        from multiprocessing.pool import ThreadPool

        send_msg = u'test ฟนำีฟนำีฟนำีฟนำี'

        def on_message(msg):
            self.assertEqual(msg, send_msg)

        def server():
            PostofficeServer(ip='0.0.0.0', port=4000, on_message=on_message)

        def client(ith):
            client = PostofficeClient(ip='localhost', port=4000)
            client.send(send_msg)

        from multiprocessing import Process
        p = Process(target=server)
        p.start()

        time.sleep(0.1)

        pool = ThreadPool(100)
        pool.map(client, [i for i in range(100)])

        p.terminate()
        p.join()

    def test_multiple_concurrent_request_on_same_client(self):
        import time
        from multiprocessing.pool import ThreadPool

        send_msg = u'test ฟนำีฟนำีฟนำีฟนำี'

        def on_message(msg):
            self.assertEqual(msg, send_msg)

        def server():
            PostofficeServer(ip='0.0.0.0', port=4000, on_message=on_message)

        from multiprocessing import Process
        p = Process(target=server)
        p.start()

        time.sleep(0.1)

        c = PostofficeClient(ip='localhost', port=4000)

        def client(ith):
            c.send(send_msg)

        pool = ThreadPool(100)
        pool.map(client, [i for i in range(100)])

        p.terminate()
        p.join()