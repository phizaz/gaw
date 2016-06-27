from __future__ import absolute_import
from gaw.postoffice.server import PostofficeServer

def handle(message):
    print(message)
    return 'success'

PostofficeServer(ip='0.0.0.0',
                 port=4444,
                 on_message=handle,
                 verbose=True)