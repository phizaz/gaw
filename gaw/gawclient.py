from __future__ import print_function, absolute_import
from gaw.jsonsocketserver import JsonSocketClient
from gaw.serializable.serializable import Serializable

class GawClient:

    def __init__(self, ip, port, secret=None, is_encrypt=False,
                 connection_lifetime = 30, verbose=False,
                 request_maker=None,
                 _state=0, _service_name=None, _method_name=None):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.connection_lifetime = connection_lifetime
        self.verbose = verbose

        if request_maker is None:
            self.request_maker = JsonSocketClient(client_lifetime=connection_lifetime, verbose=verbose)
        else:
            self.request_maker = request_maker

        self._state = _state
        self._service_name = _service_name
        self._method_name = _method_name

    def __getattr__(self, item):
        # dynamic method calling handler
        if self._state == 0:
            state = 1
            service_name = item

            return GawClient(
                ip=self.ip, port=self.port,
                secret=self.secret, is_encrypt=self.is_encrypt,
                connection_lifetime=self.connection_lifetime,
                verbose=self.verbose,
                request_maker=self.request_maker,
                _state=state,
                _service_name=service_name,
                _method_name=self._method_name
            )
        elif self._state == 1:
            method_name = item

            return self.get_procedure_caller(
                service_name=self._service_name,
                method_name=method_name,
                ip=self.ip,
                port=self.port,
                secret=self.secret,
                is_encrypt=self.is_encrypt,
                request_maker=self.request_maker,
                verbose=self.verbose
            )
        else:
            raise ValueError('state not recognized')

    def get_procedure_caller(self, service_name, method_name,
                             ip, port, secret, is_encrypt,
                             request_maker, verbose):
        assert isinstance(request_maker, JsonSocketClient), 'request maker should be a jsonsocketclient'
        path = '{}/{}'.format(service_name, method_name)

        def rpc(*args, **kwargs):
            if verbose:
                print('gawclient: procedure call path', path, 'args:', args, 'kwargs:', kwargs)

            response = request_maker.request(ip=ip, port=port, path=path,
                                             secret=secret, is_encrypt=is_encrypt,
                                             payload=dict(
                                                 # support serialize as the arguments
                                                 args=Serializable.serialize(args),
                                                 kwargs=Serializable.serialize(kwargs)
                                             ))

            # parse the response using Serializable
            parsed_response = Serializable.parse(response)
            return parsed_response

        return rpc
