from __future__ import print_function, absolute_import
from gaw.entrypoint import Entrypoint
from gaw.jsonsocketserver import JsonSocketServer
from gaw.serializable.serializable import Serializable

def pluck(d, *args):
    assert isinstance(d, dict)
    return (d[arg] for arg in args)

class GawServer:

    def __init__(self, ip, port, secret=None, is_encrypt=False, verbose=False):
        self.ip = ip
        self.port = port
        self.secret = secret
        self.is_encrypt = is_encrypt
        self.verbose = verbose
        self.socketserver = JsonSocketServer(ip, port, secret=secret, is_encrypt=is_encrypt, verbose=verbose)

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

    def run(self):
        self.socketserver.start()

    def router(self, path, **payload):
        if self.verbose:
            print('gawserver: router path:', path)

        cls, method_name, args, kwargs = pluck(self.path[path], 'service_class', 'method_name', 'args', 'kwargs')

        # init a new instance of the class
        cls_instance = cls(*args, **kwargs)

        # call the designated method
        args = payload['args']
        kwargs = payload['kwargs']
        result = getattr(cls_instance, method_name)(*args, **kwargs)

        if self.verbose:
            print('gawserver: result ', result)

        # serialize result using Serializable
        serialized_result = Serializable.serialize(result)
        return serialized_result