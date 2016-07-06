from __future__ import print_function, absolute_import
import eventlet
from gaw.postoffice.core import recieve, send
from gaw.postoffice.exceptions import ConnectionTerminated, PostofficeException
import base64
import traceback

class PostofficeServer:

    def __init__(self, ip, port, on_message, secret=None, is_encrypt=False, verbose=False):
        print('postoffice: listening on ip:', ip, 'port:', port, 'secret:', secret, 'is_encrypt:', is_encrypt)

        self.ip = ip
        self.port = int(port)
        self.on_message = on_message
        self.secret = base64.b64decode(secret) if secret else None
        self.is_encrypt = is_encrypt
        self.verbose = verbose

        server = eventlet.listen((self.ip, self.port))
        pool = eventlet.GreenPool()
        while True:
            try:
                socket, address = server.accept()
                pool.spawn_n(self._on_connection, socket, address)
            except (SystemExit, KeyboardInterrupt):
                break

    def _success(self, payload):
        return dict(succ=True, data=payload)

    def _fail(self, name, message, trace=None):
        return dict(succ=False, data=dict(name=name,
                                          message=message,
                                          trace=trace))

    def _on_connection(self, socket, address):
        if self.verbose:
            print('postoffice: get a connection from', address)

        # loop until connection terminated
        while True:

            try:
                request = recieve(socket, self.secret, is_encrypt=self.is_encrypt)
                if self.verbose: print('postoffice: get a message ', str(request)[:150], '...')
            except ConnectionTerminated:
                if self.verbose: print('postoffice: connection ended')
                return
            except PostofficeException as e:
                if self.verbose: print('postoffice: ', e)
                wrapped_response = self._fail(name=e.name,
                                              message=e.message,
                                              trace=e.trace)
            except Exception as e:
                if self.verbose: print('postoffice: exception: ', e)
                name = type(e).__name__
                trace = traceback.format_exc()
                wrapped_response = self._fail(name=name,
                                              message=e.__str__(),
                                              trace=trace)
            else:
                response = self.on_message(request)
                wrapped_response = self._success(response)

            send(socket, wrapped_response, self.secret, is_encrypt=self.is_encrypt)