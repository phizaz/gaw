from __future__ import print_function, absolute_import
from gaw.postoffice.core import recieve, send
from gaw.postoffice.exceptions import ConnectionTerminated, PostofficeException
import SocketServer
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

        POSTOFFICE = self # shared with the classes inside

        class TCPHandler(SocketServer.BaseRequestHandler):
            '''
            declaring a class inside a class is not a good practice but it is neccessary in this case
            because we want to be able to share the 'self' from PostofficeServer
            '''

            def _success(self, payload):
                return dict(succ=True, data=payload)

            def _fail(self, name, message, trace=None):
                return dict(succ=False, data=dict(name=name,
                                                  message=message,
                                                  trace=trace))

            def handle(self):
                socket = self.request
                address = self.client_address

                if POSTOFFICE.verbose:
                    print('postoffice: get a connection from', address)

                # loop until connection terminated
                while True:

                    try:
                        request = recieve(socket, POSTOFFICE.secret, is_encrypt=POSTOFFICE.is_encrypt)
                        if POSTOFFICE.verbose: print('postoffice: get a message ', str(request)[:150], '...')
                    except ConnectionTerminated:
                        if POSTOFFICE.verbose: print('postoffice: connection ended')
                        return
                    except PostofficeException as e:
                        if POSTOFFICE.verbose: print('postoffice: ', e)
                        wrapped_response = self._fail(name=e.name,
                                                      message=e.message,
                                                      trace=e.trace)
                    except Exception as e:
                        if POSTOFFICE.verbose: print('postoffice: exception: ', e)
                        name = type(e).__name__
                        trace = traceback.format_exc()
                        wrapped_response = self._fail(name=name,
                                                      message=e.__str__(),
                                                      trace=trace)
                    else:
                        response = POSTOFFICE.on_message(request)
                        wrapped_response = self._success(response)

                    send(socket, wrapped_response, POSTOFFICE.secret, is_encrypt=POSTOFFICE.is_encrypt)

        class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
            pass

        self.server = ThreadedTCPServer((self.ip, self.port), TCPHandler)
        self.server.serve_forever()
