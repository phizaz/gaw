from __future__ import print_function, absolute_import
from gaw.jsonsocketserver.datatype import RequestDataType, ResponseDataType
from gaw.postoffice import PostofficeClient
from threading import Thread
from gaw.jsonsocketserver.exceptions import JsonSocketException
from gaw.postoffice.exceptions import PostofficeException
import uuid
import datetime
import time
import eventlet
import traceback
import errno

class JsonSocketClient:

    def __init__(self, client_lifetime=30, verbose=False):
        self.client_lifetime = client_lifetime
        self.verbose = verbose

        self._client_pool = dict()
        self._is_busy = dict()
        self._last_act_at = dict()

        self._cleaner = Thread(target=self._cleaner)
        self._cleaner.daemon = True
        self._cleaner.start()

    def request(self, ip, port, path, payload, secret=None, is_encrypt=False):
        # may retry many times
        while True:
            client = self._get_client(ip, port, secret, is_encrypt)
            assert isinstance(client, PostofficeClient)

            if self.verbose:
                print('jsonsocketclient: requesting ip', ip, 'port', port, 'path', path, 'payload', payload)

            request = RequestDataType(id=uuid.uuid1().int,
                                      path=path,
                                      payload=payload)

            try:
                raw_response = client.send(request.dict())
            except PostofficeException as e:
                raise e
            except IOError as e:
                if e.errno == errno.EPIPE:
                    print('jsonsocketclient: connection error retrying ...')
                    # delete the old client
                    self._delete(self._key(ip, port, secret, is_encrypt))
                    eventlet.sleep(1)
                    # retry
                    continue
                else:
                    # unexpected error
                    raise e

            if self.verbose:
                print('jsonsocketclient: response ', raw_response)

            response = ResponseDataType.parse(raw_response)

            if response.resp_to != request.id:
                raise ValueError('request error: wrong response id')

            if not response.success:
                exception = response.payload
                name = exception['name']
                message = exception['message']
                trace = exception['trace']
                raise JsonSocketException(name=name, message=message, trace=trace)

            return response.payload

    # private
    def _key(self, ip, port, secret, is_encrypt):
        return '{}:{}:{}:{}'.format(ip, port, secret, is_encrypt)

    def _init_client(self, ip, port, secret, is_encrypt):
        # may retry connection many times
        while True:
            try:
                if self.verbose:
                    print('jsonsocketclient: init client ip: {} port: {} secret: {} is_encrypt: {}'.format(ip, port, secret, is_encrypt))
                return PostofficeClient(ip, port, verbose=self.verbose,
                                        secret=secret,
                                        is_encrypt=is_encrypt)
            except Exception:
                print('jsonsocketclient: host is down retrying ...')
                eventlet.sleep(5)

    def _get_client(self, ip, port, secret, is_encrypt):
        key = self._key(ip, port, secret, is_encrypt)

        if key not in self._client_pool:
            self._client_pool[key] = self._init_client(ip, port, secret, is_encrypt)

        self._last_act_at[key] = datetime.datetime.now()
        self._is_busy[key] = True

        return self._client_pool[key]

    def _delete(self, key):
        del self._client_pool[key]
        del self._last_act_at[key]
        del self._is_busy[key]

        if self.verbose:
            print('jsonsocketclient: cleared', key)

    def _cleaner(self):
        while True:
            time.sleep(10) # cleaning interval
            now = datetime.datetime.now()

            for key in list(self._client_pool.keys()):
                if self._is_busy[key]:
                    continue

                last_act = self._last_act_at[key]

                if now - last_act > datetime.timedelta(seconds=self.client_lifetime):
                    self._delete(key)