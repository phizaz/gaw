from __future__ import absolute_import
from gaw import GawClient
from gaw.test_serializable import MathResult # must import

client = GawClient('127.0.0.1', 5555, secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True, verbose=True)
rpc = client.math_service

# test serializable
print(rpc.plus(a=10, b=20).__dict__)
print(rpc.multiply(10, 20).__dict__)