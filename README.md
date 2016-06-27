# Gaw
 
*"gaw" means "glue" in Thai*

**Gaw** is a small library that helps you developing microservices with ease.

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

