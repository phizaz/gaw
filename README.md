# Gaw
 
*"gaw" means "glue" in Thai*

**Gaw** is a small library that helps you developing microservices over simple TCP socket with ease.

This is how it works!

On the server side

```
from gaw import GawServer, entrypoint

class MathService(object):
    name = 'math_service'

    def __init__(self, hello_message):
        self.hello = hello_message

    @entrypoint # expose this method to the rest of the world
    def plus(self, a, b):
        return '{}: {}'.format(self.hello, a + b)

    @entrypoint
    def multiply(self, a, b):
        return '{}: {}'.format(self.hello, a * b)


service = GawServer('127.0.0.1', 5555)
service.add(MathService, hello_message='Hello!')
service.run() # runs forever
```

On the client side

```
from gaw import GawClient

client = GawClient('127.0.0.1', 5555)
rpc = client.math_service
print(rpc.plus(10, 20)) # Hello!: 30
print(rpc.multiply(10, 20)) # Hello!: 200
```

In some scenario, you might need this

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

*Note: it supports python 3.4, and tested with python 2.7.9 2*

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
