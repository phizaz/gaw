from gaw.serializable.serializable import Serializable
from datetime import datetime

class A(Serializable):

    def __init__(self, a, b):
        self.a = a
        self.b = b

class B(Serializable):

    def __init__(self, c):
        self.c = c

# test nested object
a = A(10, B(datetime.now()))
da = a.dict()
print(da)
aa = Serializable.parse(da)
print(aa.a, aa.b.c)

# test list
a = [10, ['aoeu', B(10)], 10.10, A(10, 20)]
sa = Serializable.serialize(a)
print(sa)
b = Serializable.parse(sa)
print(b)


# test tuple
a = tuple([10, 'aoeu', 10.10, A(10, 20)])
sa = Serializable.serialize(a)
print(sa)
b = Serializable.parse(sa)
print(b)

# test dict
a = dict(a=10,
         b=20,
         c=dict(
             a=A(10,[1,2,3, B(40)]),
             b=B(30)),
         d=A(30,40))
sa = Serializable.serialize(a)
print(sa)
b = Serializable.parse(sa)
print(b)
print(b['c'])
print(b['c']['a'].__dict__)
print(b['c']['b'].__dict__)
print(b['d'].__dict__)