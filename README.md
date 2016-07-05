# Gaw
 
*"gaw" means "glue" in Thai*

**Gaw** is a small library that helps you developing microservices over simple TCP socket with ease.

This is how it works!

**On the server side** (say, `services.py`)

```
from gaw import entrypoint

class MathService(object):
    name = 'math_service'
    
    def __init__(self, hello_msg):
    	self.msg = hello_msg

    @entrypoint # expose this method to the rest of the world
    def plus(self, a, b):
		return '{}:{}'.format(self.msg, a + b)

    @entrypoint
    def multiply(self, a, b):
		return '{}:{}'.format(self.msg, a * b)
```

You can start the server using `GawServer` like:

```
from services import MathService
from gaw import GawServer

GawServer('127.0.0.1', 5555).add(MathService, 'hello!').run() # runs forever
```

Alternatively, using a command-line interface

```
$ gaw services --kwargs="hello_msg='hello!'" # runs all services in the module 'services'
# or
$ gaw services --service=math_service --kwargs="hello_msg='hello!'"
```

Anyways, usually, we don't really need the use of parameters like the above.

**On the client side**

```
from gaw import GawClient

client = GawClient('127.0.0.1', 5555)
rpc = client.math_service
print(rpc.plus(10, 20)) # Hello!: 30
print(rpc.multiply(10, 20)) # Hello!: 200
```

In some scenarios, you might need this

```
from gaw import GawServer, entrypoint
from somewhere import MathEngine

class MathService(object):
    name = 'math_service'
    math_engine = MathEngine()

    def __init__(self, hello_message):
        self.hello = hello_message

    @entrypoint # expose this method to the rest of the world
    def plus(self, a, b):
        return '{}: {}'.format(self.hello, self.math_engine.plus(a, b))

    @entrypoint
    def multiply(self, a, b):
        return '{}: {}'.format(self.hello, self.math_engine.multiply(a, b)))


service = GawServer('127.0.0.1', 5555)
service.add(MathService, hello_message='Hello!')
service.run() # runs forever
```

In the example above, you can guarantee that there should be only one MathEngine initiated.

**Gaw** is heavily influenced by **Nameko**, another python microservice framework.

*Note: it supports python 3.4, and tested with python 2.7.9*

## Installation

```
pip install gaw
```

## Request Life Cycle

1. **Gaw Client** makes a connection and sends a request packet to a **Gaw Server**.
2. **Gaw Server**, knowing all the entrypoints, **Gaw Server** *inititates* an instance of a designated class.
3. **Gaw Server** invokes the requested method.
4. **Gaw Server** sends back the results to the calling **Gaw Client**.


## Topology

In the package, there are other two libraries that **Gaw** makes use of:

1. **Postoffice** - serves as a low-level TCP socket communicator.
2. **Json Web Server** - this's kinda like a http server for the mere socket world.

## Securities

Since version 0.5, **Gaw** has been suppporting pre-shared key *AES CBC* encryption and *HMAC SHA256* digital signature to provide data authenticity and data cofidentiality.

```
GawServer(ip=..., port=..., secret=..., is_encrypt=..)
GawClient(ip=..., port=..., secret=..., is_encrypt=..)
$ gaw <module_name> --secret=... [--is_encrypt]
```

## Serializable Library

Since version 0.6, **Gaw** has been shipped with **Serializable Library** with which you can return (0.6.4; you can supply methods with serializables) *any kind* of data types from your service method as long as it is a inheritance of the class `gaw.Serializable`

For example:

file: `datatypes.py`

```
from gaw import Serializable

class MathResult(Serializable):

    def __init__(self, header, result):
        self.header = header
        self.result = result

    def get_result(self):
        return self.result

    def get_header(self):
        return self.header
```

file: `server.py`

```
from gaw import GawServer, entrypoint
from datatypes import *

class MathService(object):
    name = 'math_service'

    def __init__(self, hello_message):
        self.hello = hello_message

    @entrypoint
    def plus(self, a, b):
        return MathResult(self.hello, a + b)

    @entrypoint
    def multiply(self, a, b):
        return MathResult(self.hello, a * b)


service = GawServer('127.0.0.1', 5555, verbose=True, secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True)
service.add(MathService, hello_message='Hello!')
service.run()
```

file: `client.py`

```
from __future__ import absolute_import
from gaw import GawClient
from datatypes import * # must import!! even you don't need it explicitly

client = GawClient('127.0.0.1', 5555, secret='Qx9XFxN17+zkUdcBIGZ0A1sQTkUSP4SZ', is_encrypt=True, verbose=True)
rpc = client.math_service

print(rpc.plus(a=10, b=20).__dict__)
print(rpc.multiply(10, 20).__dict__)
```