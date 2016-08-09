from __future__ import print_function, absolute_import
from gaw.jsonsocketserver.datatype import *
from gaw.postoffice import PostofficeClient
from threading import Thread
from gaw.jsonsocketserver.exceptions import JsonSocketException
from gaw.postoffice.exceptions import PostofficeException, ConnectionTerminated
from gaw.serializable.serializable import Serializable
import uuid
import datetime
import time
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

    def request(self, ip, port, path, payload, secret=None, is_encrypt=False, retries=-1):
        # may retry many times
        from builtins import range
        if retries == -1:
            from itertools import count
            retries_range = count()
        else:
            retries_range = range(retries + 1)

        for retry_no in retries_range:
            if self.verbose: print('jsonsocketclient: retry no:', retry_no, 'of', retries)

            client = self._get_client(ip, port, secret, is_encrypt, retries)
            assert isinstance(client, PostofficeClient)

            if self.verbose:
                print('jsonsocketclient: requesting ip', ip, 'port', port, 'path', path, 'payload', payload)

            request = RequestDataType(id=uuid.uuid1().int,
                                      path=path,
                                      payload=payload)
            raw_request = Serializable.serialize(request)

            try:
                raw_response = client.send(raw_request)
            except PostofficeException as e:
                raise
            except ConnectionTerminated as e:
                print('jsonsocketclient: connection reset by peer ... path: ', path, 'ip:', ip, 'port:', port)
                # delete the old client
                self._delete(self._key(ip, port, secret, is_encrypt))

                if retry_no == retries:
                    raise

                time.sleep(1)
                # retry
                continue
            except IOError as e:
                if e.errno == errno.EPIPE:
                    print('jsonsocketclient: connection error ... path:', path, 'ip:', ip, 'port:', port)
                    # delete the old client
                    self._delete(self._key(ip, port, secret, is_encrypt))
                    if retry_no == retries:
                        raise
                    time.sleep(1)
                    # retry
                    continue
                if e.errno == errno.ECONNRESET:
                    print('jsonsocketclient: connection reset by peer (ECONNRESET) ... path:', path, 'ip:', ip, 'port:',
                          port)
                    self._delete(self._key(ip, port, secret, is_encrypt))
                    if retry_no == retries:
                        raise
                    time.sleep(1)
                    continue
                else:
                    # unexpected error
                    raise

            if self.verbose:
                print('jsonsocketclient: raw response ', raw_response)

            response = Serializable.parse(raw_response)

            if self.verbose:
                print('jsonsocketclien: response', type(response), response.__dict__)

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

    def _init_client(self, ip, port, secret, is_encrypt, retries):
        from builtins import range
        # may retry connection many times
        if retries == -1:
            from itertools import count
            retry_range = count()
        else:
            retry_range = range(retries + 1)


        for retry_no in retry_range:
            if self.verbose: print('jsonsocketclient: init retry no:', retry_no, 'of', retries)
            try:
                if self.verbose:
                    print('jsonsocketclient: init client ip: {} port: {} secret: {} is_encrypt: {}'.format(ip, port,
                                                                                                           secret,
                                                                                                           is_encrypt))
                return PostofficeClient(ip, port, verbose=self.verbose,
                                        secret=secret,
                                        is_encrypt=is_encrypt)
            except Exception:
                print('jsonsocketclient: host is down retrying ... ip: {} port: {}'.format(ip, port))
                if retry_no == retries:
                    raise
                time.sleep(5)

    def _get_client(self, ip, port, secret, is_encrypt, retries):
        key = self._key(ip, port, secret, is_encrypt)

        if key not in self._client_pool:
            self._client_pool[key] = self._init_client(ip, port, secret, is_encrypt, retries)

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
            time.sleep(10)  # cleaning interval
            now = datetime.datetime.now()

            for key in list(self._client_pool.keys()):
                if self._is_busy[key]:
                    continue

                last_act = self._last_act_at[key]

                if now - last_act > datetime.timedelta(seconds=self.client_lifetime):
                    self._delete(key)
