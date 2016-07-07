from __future__ import absolute_import
from gaw.postoffice.client import PostofficeClient

client = PostofficeClient(ip='127.0.0.1',
                          port=4444,
                          secret='anfJdufzm2FSbQca0dD8RgN01SO4Pgn0',
                          is_encrypt=True,
                          verbose=False)

response = client.send(dict(a='aoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuaoeuoa'))
print('response:', response)

import time

rounds = 1000
start_time = time.time()
for i in range(rounds):
    response = client.send(dict(a=u'aoeu'))
end_time = time.time()

print('each:', (end_time - start_time) / float(rounds) * 1000, 'ms')