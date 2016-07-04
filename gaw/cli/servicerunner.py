from __future__ import absolute_import, print_function
import importlib
import inspect
from gaw import GawServer
from gaw.entrypoint import Entrypoint
from argparse import ArgumentParser
import itertools
import sys
import signal
import os

def on_sigint(signal, frame):
    print('Exiting...')
    sys.exit(0)

def servicerunner_cli():
    signal.signal(signal.SIGINT, on_sigint)

    # add the executor path to the pythonpath
    sys.path.insert(0, os.getcwd())

    parser = ArgumentParser(description='Gaw Service Runner - CLI')
    parser.add_argument('module_name', type=str)
    parser.add_argument('--service', type=str)
    parser.add_argument('--port', type=int, default=5555)
    parser.add_argument('--ip', type=str, default='127.0.0.1')
    parser.add_argument('--secret', type=str)
    parser.add_argument('--is_encrypt', action='store_true')
    parser.add_argument('--kwargs', type=str)
    args = parser.parse_args()

    print('Gaw Service Runner - CLI')

    # load the designated module
    module_name = args.module_name
    module = importlib.import_module(module_name)

    # get a list of all gaw services in the module
    def is_gaw_service(cls):
        entry_points = Entrypoint.get_entrypoints_from_class(cls)
        return len(entry_points) > 0

    gaw_services = []
    for name, obj in inspect.getmembers(module):
        if not inspect.isclass(obj):
            continue

        if is_gaw_service(obj):
            service_name = getattr(obj, 'name')
            gaw_services.append((service_name, obj))

    # filter down according to the --service argument
    def filter_service(service):
        name, cls = service
        if args.service:
            return name == args.service
        else:
            return True

    selected_services = list(filter(filter_service, gaw_services))

    if len(selected_services) == 0:
        print('gawrunner: no service to be run, exiting...')
        return

    # run the service (try many ports in sequential fashion)
    for port_shifting in itertools.count():
        port = args.port + port_shifting
        try:
            # start the server
            server = GawServer(args.ip, port, secret=args.secret, is_encrypt=args.is_encrypt)
            for name, service_class in selected_services:
                if args.kwargs:
                    kwargs = eval('dict({})'.format(args.kwargs))
                    print('gawrunner: run {} service with parameters {}'.format(name, kwargs))
                    server.add(service_class, **kwargs)
                else:
                    server.add(service_class)
            server.run()
            # this is important!
            # forget to 'break' here, you cannot stop the programm from keeping running
            break
        except OSError as err:
            if err.errno == 48:
                print('gawrunner: [err 48] port {} taken ... trynig another'.format(port))
                continue
            else:
                raise err

if __name__ == '__main__':
    servicerunner_cli()