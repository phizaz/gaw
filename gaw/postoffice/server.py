from __future__ import print_function, absolute_import
import eventlet
from gaw.postoffice.core import recieve, send, ConnectionTerminated, DecodeError
import base64

class PostofficeServer:

    def __init__(self, ip, port, on_message, secret=None, is_encrypt=False, verbose=False):
        print('postoffice: listening on ip:', ip, 'port:', port)

        self.secret = base64.b64decode(secret) if secret else None
        self.is_encrypt = is_encrypt
        self.verbose = verbose
        self.on_message = on_message

        server = eventlet.listen((ip, port))
        pool = eventlet.GreenPool()
        while True:
            try:
                socket, address = server.accept()
                pool.spawn_n(self._on_connection, socket, address)
            except (SystemExit, KeyboardInterrupt):
                break

    def _on_connection(self, socket, address):
        if self.verbose:
            print('postoffice: get a connection from', address)

        # loop until connection terminated
        while True:

            try:
                data = recieve(socket, self.secret, is_encrypt=self.is_encrypt)
                if self.verbose: print('postoffice: get a message ', str(data)[:150], '...')
            except ConnectionTerminated:
                if self.verbose: print('postoffice: connection ended')
                return
            except DecodeError:
                if self.verbose: print('postoffice: signature verfication failed')
                continue

            response = self.on_message(data)
            send(socket, response, self.secret, is_encrypt=self.is_encrypt)