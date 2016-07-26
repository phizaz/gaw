from gaw.gawserver import GawServer, interface_class, service_class

@interface_class
class Interface(object):
    name = 'Service'

    def plus(self, a, b): pass

@service_class
class Service(Interface):

    def plus(self, a, b):
        return a + b

if __name__ == '__main__':
    GawServer(ip='0.0.0.0', port=3500).add(Service).run()