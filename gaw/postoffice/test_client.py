from __future__ import absolute_import
from gaw.postoffice.client import PostofficeClient

client = PostofficeClient(ip='127.0.0.1', port=4444, verbose=True)
response = client.send(dict(a=10))

print('response:', response)