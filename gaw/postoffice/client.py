from __future__ import print_function, absolute_import
from eventlet.green import socket
from gaw.postoffice.core import send, recieve
from gaw.postoffice.exceptions import PostofficeException
import base64
from queue import Queue

class PostofficeClient(object):

    def __init__(self, ip, port, secret=None, is_encrypt=False, verbose=False):
        self.ip = ip
        self.port = int(port)
        self.secret = base64.b64decode(secret) if secret else None
        self.is_encrypt = is_encrypt
        self.verbose = verbose

        self.socket = socket.socket()
        self.socket.connect((ip, port))

        self.run_token = Queue()
        self.run_token.put(True)

    def send(self, data):
        token = self.run_token.get()
        result = self._process_job(data)
        self.run_token.put(token)
        return result

    def _process_job(self, data):
        if self.verbose:
            print('postofficeclient: sending data', data)

        send(self.socket, data, self.secret, is_encrypt=self.is_encrypt)

        if self.verbose:
            print('postofficeclient: sending done')

        response = recieve(self.socket, self.secret, is_encrypt=self.is_encrypt)

        if not response['succ']:
            raise PostofficeException(name=response['name'],
                                      message=response['message'],
                                      trace=response['trace'])

        if self.verbose:
            print('postofficeclient: receciving done')

        return response['data']