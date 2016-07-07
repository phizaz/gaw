from __future__ import absolute_import
from gaw.postoffice.client import PostofficeClient


client = PostofficeClient(ip='0.0.0.0',
                         port=4444,
                         secret='anfJdufzm2FSbQca0dD8RgN01SO4Pgn0',
                         is_encrypt=True,
                         verbose=True)

from multiprocessing.pool import ThreadPool

p = ThreadPool(100)
p.map(client.send, [i for i in range(100)])