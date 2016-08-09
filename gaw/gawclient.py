from __future__ import print_function, absolute_import
from gaw.jsonsocketserver import JsonSocketClient
from gaw.gawserver import INTERFACE_CLASS_ATTR, INTERFACE_CLASS_METHOD_ATTR
import inspect
from functools import wraps


class GawClient(object):
    def __init__(self, ip, port, secret=None, is_encrypt=False,
                 connection_lifetime=30, verbose=False, retries=-1,
                 _request_maker=None,
                 _state=0, _service_name=None, _method_name=None):

        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.connection_lifetime = connection_lifetime
        self.verbose = verbose
        self.retries = retries

        if _request_maker is None:
            self._request_maker = JsonSocketClient(client_lifetime=connection_lifetime, verbose=verbose)
        else:
            self._request_maker = _request_maker

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
                retries=self.retries,
                _request_maker=self._request_maker,
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
                retries=self.retries,
                request_maker=self._request_maker,
                verbose=self.verbose
            )
        else:
            raise ValueError('state not recognized')

    def get_procedure_caller(self, service_name, method_name,
                             ip, port, secret, is_encrypt, retries,
                             request_maker, verbose):
        assert isinstance(request_maker, JsonSocketClient), 'request maker should be a jsonsocketclient'
        path = '{}/{}'.format(service_name, method_name)

        def rpc(*args, **kwargs):
            if verbose:
                print('gawclient: procedure call path', path, 'args:', args, 'kwargs:', kwargs)

            # note: parsing and serializing the response is now the job of json socket server
            response = request_maker.request(ip=ip, port=port, path=path,
                                             secret=secret, is_encrypt=is_encrypt,
                                             retries=retries,
                                             payload=dict(
                                                 args=args,
                                                 kwargs=kwargs
                                             ))

            return response

        return rpc


def client_class(ip, port, secret=None, is_encrypt=False, connection_lifetime=30, verbose=False, retries=-1):
    '''
    GawClient class decorator, the class must inherit from a class of Interface, decorated using interface_class
    this client will directly point to that service
    '''
    client = GawClient(ip=ip, port=port, secret=secret, is_encrypt=is_encrypt, connection_lifetime=connection_lifetime,
                       verbose=verbose, retries=retries)

    def decorator(cls):
        base = [
            c
            for c in inspect.getmro(cls)
            if c is not cls and hasattr(c, INTERFACE_CLASS_ATTR)
            ]

        assert len(base) == 1, 'should have only one interface_class decorated class'

        intf_cls = base.pop()

        assert hasattr(intf_cls, INTERFACE_CLASS_ATTR), 'intf_cls should be decorated by interface_class'
        service_name = intf_cls.name
        service_client = getattr(client, service_name)

        def method_by(name):
            method = getattr(service_client, name)

            @wraps(obj)
            def wrapper(self, *args, **kwargs):
                return method(*args, **kwargs)

            return wrapper

        for name, obj in inspect.getmembers(cls):
            if hasattr(obj, INTERFACE_CLASS_METHOD_ATTR):
                setattr(cls, name, method_by(name))

        return cls

    return decorator
