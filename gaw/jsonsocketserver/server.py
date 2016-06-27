from __future__ import print_function
from gaw.jsonsocketserver.datatype import RequestDataType, ResponseDataType
from gaw.postoffice import PostofficeServer
import traceback

class JsonSocketServer:

    def __init__(self, ip, port, verbose=False):
        self.ip = ip
        self.port = port
        self.verbose = verbose

        self._all_routes = dict()

    def register_route(self, path, handle):
        self._all_routes[path] = handle

    def start(self):
        PostofficeServer(self.ip, self.port, self._router, verbose=self.verbose)

    # private

    def _router(self, message):
        if self.verbose:
            print('jsonsocketserver: router got message:', str(message)[:100], '...')

        request = RequestDataType.parse(message)

        try:
            path = request.path
            fn = self._all_routes[path]
        except KeyError as e:
            print('jsonsocketserver: path not found', request.path)
            name = type(e).__name__
            trace = traceback.format_exc()
            response = ResponseDataType(
                resp_to=request.id,
                success=False,
                payload=dict(
                    type='path not found',
                    name=name,
                    message='path: {} not found'.format(request.path),
                    trace=trace
                )
            )
            return response.dict()

        try:
            if not isinstance(request.payload, dict):
                assert request.payload.strip() == ''
                result = fn(path=path)
            else:
                params = request.payload
                result = fn(path=path, **params)
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
                    type='exception',
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