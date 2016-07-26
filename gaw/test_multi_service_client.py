from gaw import GawClient

print(GawClient(ip='localhost', port=12345).A.home())
print(GawClient(ip='localhost', port=12345).B.home())
print(GawClient(ip='localhost', port=12345).Both.home())