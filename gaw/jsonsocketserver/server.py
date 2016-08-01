from __future__ import print_function
from gaw.jsonsocketserver.datatype import *
from gaw.postoffice import PostofficeServer
from gaw.serializable.serializable import Serializable
import traceback

class JsonSocketServer:

    def __init__(self, ip, port, secret=None, is_encrypt=False, verbose=False):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.verbose = verbose
        self.after_start_cb = None

        self._handle_by_route = dict()

    def register_route(self, path, handle):
        self._handle_by_route[path] = handle

    def start(self, after_start_cb=None):
        self.after_start_cb = after_start_cb
        if self.after_start_cb is not None:
            assert hasattr(self.after_start_cb, '__call__'), 'after start cb should be a function'

        PostofficeServer(self.ip, self.port, self._router,
                         secret=self.secret, is_encrypt=self.is_encrypt,
                         verbose=self.verbose, after_start_cb=after_start_cb)

    # private

    def _router(self, message):
        if self.verbose:
            print('jsonsocketserver: router got message:', str(message)[:100], '...')

        request = Serializable.parse(message)

        try:
            path = request.path
            fn = self._handle_by_route[path]
        except KeyError as e:
            print('jsonsocketserver: path not found', request.path)
            name = type(e).__name__
            trace = traceback.format_exc()
            response = ResponseDataType(
                resp_to=request.id,
                success=False,
                payload=dict(
                    name=name,
                    message='path: {} not found'.format(request.path),
                    trace=trace
                )
            )
            return Serializable.serialize(response)

        try:
            assert isinstance(request.payload, dict), 'request payload must be a dict of the function arguments'
            params = request.payload
            if len(params) > 0:
                result = fn(path=path, **params)
            else:
                # empty request payload
                result = fn(path=path)
        except Exception as e:
            # catch all error, and propagate it to the requester
            name = type(e).__name__
            message = str(e)
            trace = traceback.format_exc()

            print('jsonsocketserver: error encounter .. sending back')
            print('jsonsocketserver: \ntrace:', trace)

            response = ResponseDataType(
                resp_to=request.id,
                success=False,
                payload=dict(
                    name=name,
                    message=message,
                    trace=trace,
                )
            )
            return Serializable.serialize(response)

        # send response back to the requester
        response = ResponseDataType(resp_to=request.id,
                                    success=True,
                                    payload=result)
        raw_response = Serializable.serialize(response)
        return raw_response