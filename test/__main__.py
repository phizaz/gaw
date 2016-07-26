from gaw import GawServer, entrypoint

'''
there is no problem of port left binded after quit
'''

class Test(object):

    name = 'Test'

    @entrypoint
    def home(self):
        return 'home'


GawServer(ip='127.0.0.1', port=4000).add(Test).run()