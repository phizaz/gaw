from __future__ import print_function, absolute_import
import eventlet
from gaw.postoffice.core import recieve, send, ConnectionTerminated

class PostofficeServer:

    def __init__(self, ip, port, on_message, verbose=False):
        print('postoffice: listening on ip:', ip, 'port:', port)

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
                data = recieve(socket)
                print('postoffice: get a message ', str(data)[:150], '...')
            except ConnectionTerminated:
                if self.verbose:
                    print('postoffice: connection ended')
                return

            response = self.on_message(data)
            send(socket, response)