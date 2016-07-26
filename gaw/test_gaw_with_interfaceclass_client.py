from gawclient import client_class
from test_gaw_with_interfaceclass import Interface

@client_class(ip='127.0.0.1', port=3500)
class Service(Interface): pass

service = Service()
print(service.plus(10, 20))

import time

start_time = time.time()
for i in range(1000):
    service.plus(10, 20)
end_time = time.time()
print('elapsed:', (end_time - start_time), 'ms')