from __future__ import absolute_import
from gaw.jsonsocketserver.client import JsonSocketClient
import time

ip = '127.0.0.1'
port = 4444

client = JsonSocketClient()

print(client.request(ip, port, 'plus', dict(a=10.5,
                                            b=20)))

times = 10000
start_time = time.time()
for i in range(times):
    client.request(ip, port, 'home', '')
end_time = time.time()


print('taken:', (end_time - start_time) * 1000 / times)