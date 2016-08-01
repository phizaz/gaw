# Gaw
 
*"gaw" means "glue" in Thai*

**Gaw** is a small library that helps you developing microservices over simple TCP socket with ease.

**Gaw** now comes with 2 flavors (version 0.7).

1. Simple (without code suggestion)
2. Improved (with code suggestion)

## Simple Gaw

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
		return '{}: {}'.format(self.msg, a + b)

    @entrypoint
    def multiply(self, a, b):
		return '{}: {}'.format(self.msg, a * b)
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
print(rpc.plus(10, 20)) # hello!: 30
print(rpc.multiply(10, 20)) # half-dayello!: 200
```

In some scenarios, you might need this

```
from gaw import GawServer, entrypoint
from somewhere import MathEngine

class MathService(object):
    name = 'math_service'
    math_engine = MathEngine() # only one instance

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

Note that you can put an `after_start_cb` to the `service.run()` such that the callback will be called when the start has jast been started like:

```
def started():
	print('server is up')

service.run(started) # will be trigged after the server is up and running
```

In the example above, you can guarantee that there should be only one MathEngine initiated.

## Improved Gaw

(version 0.7) For better code suggestion (and IDE support), you can define an `@interface_class`, `@service_class` and `@client_class` as follows:

**On the server side**

file: `server.py`

```
from gaw import GawServer, interface_class, service_class

@interface_class
class Interface(object):
    name = 'Service'

    def plus(self, a, b): pass

@service_class
class Service(Interface):

    def plus(self, a, b):
        return a + b
        
GawServer(ip='0.0.0.0', port=5555).add(Service).run()
```

**On the client side**

```
from server import Interface
from gaw import client_class

@client_class(ip='localhost', port=5555)
class Service(Interface): pass

service = Service()

print(service.plus(10, 20)) # outputs: 30
```

Now, IDE's code suggestion will work normally on the remote service (of course, because we define the "template", aka `@interface_class`, first).

**Gaw** is heavily influenced by **Nameko**, another python microservice framework.

*Note: it supports python 3.4, and tested with python 2.7.9*

## Installation

```
pip install gaw
```

Due to my limited skills (to support both Python 2 and 3) and hurries, some bugs can really get through my poor testing. However, since I'm also using this library for production, bug fixes should be fast, and `pip install --upgrade --no-cache-dir gaw` should do it.

## Request Life Cycle

1. **Gaw Client** makes a connection and sends a request packet to a **Gaw Server**.
2. **Gaw Server**, knowing all the entrypoints, **Gaw Server** *inititates* an instance of a designated class.
3. **Gaw Server** invokes the requested method.
4. **Gaw Server** sends back the results to the calling **Gaw Client**.


## Topology

In the package, there are other two libraries that **Gaw** makes use of:

1. **Postoffice** - serves as a low-level TCP socket communicator.
2. **Json Web Server** - this's kinda like a http server for the mere socket world.

## Data Authenticity and Data Confidentiality

Since version 0.5, **Gaw** has been suppporting pre-shared key *AES CBC* encryption and *HMAC SHA256* digital signature to provide data authenticity and data cofidentiality.

```
GawServer(ip=..., port=..., secret=..., is_encrypt=..)
GawClient(ip=..., port=..., secret=..., is_encrypt=..)
$ gaw <module_name> --secret=... [--is_encrypt]
```

Note [1] : `secret` parameters are all *base64* encoded strings with the size of 128, 192 or 256 bits.

Note [2] : Keep in mind that adding security and signature verification layers also adds up the overall latency of the server (including loads). However, if a very low latency is not your case, enabling these should not mind you much (latency from 0.3 ms increased to 0.6 ms for small request).

Note [3] : You can enable only the digital signature but not the encryption `is_encrypt=False`. This will not cost your valuable latency that much (from 0.3 ms to ~0.45 ms), yet gives you data authenticity. 

## Serializable Library

Since version 0.6, **Gaw** has been being shipped with **Serializable Library** with which you can return (0.6.4; you can supply methods with serializables) *any kind* of data types from your service method as long as it is a inheritance of the class `gaw.Serializable`

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