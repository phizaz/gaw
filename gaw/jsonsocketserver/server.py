from __future__ import print_function
from gaw.jsonsocketserver.datatype import RequestDataType, ResponseDataType
from gaw.postoffice import PostofficeServer
import traceback

class JsonSocketServer:

    def __init__(self, ip, port, secret=None, is_encrypt=False, verbose=False):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.verbose = verbose

        self._handle_by_route = dict()

    def register_route(self, path, handle):
        self._handle_by_route[path] = handle

    def start(self):
        PostofficeServer(self.ip, self.port, self._router,
                         secret=self.secret, is_encrypt=self.is_encrypt,
                         verbose=self.verbose)

    # private

    def _router(self, message):
        if self.verbose:
            print('jsonsocketserver: router got message:', str(message)[:100], '...')

        request = RequestDataType.parse(message)

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
            return response.dict()

        try:
            if isinstance(request.payload, dict):
                # params can only be a dictionary
                params = request.payload
                result = fn(path=path, **params)
            else:
                assert request.payload.strip() == ''
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
            return response.dict()

        # send response back to the requester
        response = ResponseDataType(resp_to=request.id,
                                    success=True,
                                    payload=result)
        return response.dict()