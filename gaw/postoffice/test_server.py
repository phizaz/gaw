from __future__ import absolute_import
from gaw.postoffice.server import PostofficeServer

def handle(message):
    return 'success: {}'.format(message)

PostofficeServer(ip='0.0.0.0',
                 port=4444,
                 on_message=handle,
                 secret='anfJdufzm2FSbQca0dD8RgN01SO4Pgn0',
                 is_encrypt=True,
                 verbose=False)