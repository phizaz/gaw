from __future__ import print_function, absolute_import
from gaw.entrypoint import Entrypoint, entrypoint
from gaw.jsonsocketserver import JsonSocketServer
from functools import wraps
import inspect
from abc import abstractmethod

INTERFACE_CLASS_ATTR = '__gaw_interface_class__'
INTERFACE_CLASS_METHOD_ATTR = '__gaw_interface_class_method__'


def pluck(d, *args):
    assert isinstance(d, dict)
    return (d[arg] for arg in args)


class GawServer(object):
    def __init__(self, ip, port, secret=None, is_encrypt=False, verbose=False):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.verbose = verbose
        self.socketserver = JsonSocketServer(ip, port, secret=secret, is_encrypt=is_encrypt, verbose=verbose)
        self.after_start_cb = None

        self.path = dict()

    def add(self, service_class, *args, **kwargs):
        service_name = service_class.name

        print('gawserver: running service', service_name)

        entry_methods = Entrypoint.get_entrypoints_from_class(service_class)

        for method_name in entry_methods:
            path = '{}/{}'.format(service_name, method_name)

            if self.verbose: print('gawserver: add path {}'.format(path))

            # add path
            self.socketserver.register_route(path, self.router)

            # save misc
            self.path[path] = dict(service_name=service_name,
                                   service_class=service_class,
                                   method_name=method_name,
                                   args=args,
                                   kwargs=kwargs)

        return self

    def run(self, after_start_cb=None):
        self.after_start_cb = after_start_cb
        if self.after_start_cb is not None:
            assert hasattr(self.after_start_cb, '__call__'), 'after_start_cb should be a function'

        self.socketserver.start(after_start_cb=after_start_cb)

    def router(self, path, **payload):
        if self.verbose:
            print('gawserver: router path:', path)

        cls, method_name, args, kwargs = pluck(self.path[path], 'service_class', 'method_name', 'args', 'kwargs')

        # init a new instance of the class
        cls_instance = cls(*args, **kwargs)

        # note: parsing and serializing the response is now the job of json socket server
        # call the designated method
        args = payload['args']
        kwargs = payload['kwargs']
        result = getattr(cls_instance, method_name)(*args, **kwargs)

        if self.verbose:
            print('gawserver: result ', result)

        return result


def interface_class(service_name):
    assert isinstance(service_name, str), 'service_name must be a string'

    def set_interface_class(cls):
        '''
        wrap a class in which all methods are "entrypoints" by adding a flag to it, and is a template for service client
        '''
        setattr(cls, 'name', service_name)  # automatically assign the service name

        assert hasattr(cls, 'name'), 'intf_cls should have a name defined'
        setattr(cls, INTERFACE_CLASS_ATTR, True)

        for name, obj in inspect.getmembers(cls, predicate=lambda x: inspect.isfunction(x) or inspect.ismethod(
                x)):  # for python 2 and 3 support
            @wraps(obj)
            def wrapper(*args, **kwargs):
                return obj(*args, **kwargs)

            setattr(wrapper, INTERFACE_CLASS_METHOD_ATTR, True)

            setattr(cls, name, wrapper)

        return cls

    return set_interface_class


def service_class(cls):
    '''
    wrap a class in which methods according to intf_cls are entrypoints
    '''

    base = [
        c
        for c in inspect.getmro(cls)
        if c is not cls and hasattr(c, INTERFACE_CLASS_ATTR)
        ]

    assert len(base) == 1, 'should have only one interface_class decorated class'

    intf_cls = base.pop()

    assert hasattr(intf_cls, INTERFACE_CLASS_ATTR), 'intf_cls should be decorated by interface_class'
    assert hasattr(intf_cls, 'name'), 'intf_cls should have a name defined'

    intf_methods = [
        name
        for name, obj in inspect.getmembers(intf_cls)
        if hasattr(obj, INTERFACE_CLASS_METHOD_ATTR)
        ]

    def method_by(cls, name):
        method = getattr(cls, name)

        @entrypoint
        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs)

        return wrapper

    for name in intf_methods:
        setattr(cls, name, method_by(cls, name))

    return cls
