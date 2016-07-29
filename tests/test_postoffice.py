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
        self.assertTrue(False)

    def test_server_client_with_encryption(self):
        self.assertTrue(False)