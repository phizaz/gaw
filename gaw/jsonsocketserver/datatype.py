from __future__ import absolute_import
from gaw.jsonsocketserver.serializable import Serializable

class RequestDataType(Serializable):

    def __init__(self,
                 id,
                 path,
                 payload):
        self.id = id
        self.path = path
        self.payload = payload

    def dict(self):
        if hasattr(self.payload, 'dict'):
            payload = self.payload.dict()
        else:
            payload = self.payload

        return dict(id=self.id,
                    path=self.path,
                    payload=payload)

    @classmethod
    def parse(cls, d):
        assert isinstance(d, dict)
        return cls(id=d['id'],
                   path=d['path'],
                   payload=d['payload'])

class ResponseDataType(Serializable):

    def __init__(self,
                 resp_to,
                 success,
                 payload):
        self.resp_to = resp_to
        self.success = success
        self.payload = payload

    def dict(self):
        if hasattr(self.payload, 'dict'):
            payload = self.payload.dict()
        else:
            payload = self.payload

        return dict(resp_to=self.resp_to,
                    success=self.success,
                    payload=payload)

    @classmethod
    def parse(cls, d):
        assert isinstance(d, dict)
        return cls(resp_to=d['resp_to'],
                   success=d['success'],
                   payload=d['payload'])