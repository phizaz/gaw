from __future__ import absolute_import
from gaw.jsonsocketserver.client import JsonSocketClient
from gaw.jsonsocketserver.exceptions import JsonSocketException
import time

ip = '127.0.0.1'
port = 4444

client = JsonSocketClient(verbose=True)

# test client side error handling
try:
    print(client.request(ip, port, 'home', dict(), secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True))
except JsonSocketException as e:
    print(e.name)
    print(e.trace)

print(client.request(ip, port, 'plus', dict(a=10, b=20), secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True))

# times = 10000
# start_time = time.time()
# for i in range(times):
#     client.request(ip, port, 'home', '')
# end_time = time.time()
#
#
# print('taken:', (end_time - start_time) * 1000 / times)