from __future__ import absolute_import
from gaw.serializable.serializable import Serializable

class RequestDataType(Serializable):

    def __init__(self,
                 id,
                 path,
                 payload):
        self.id = id
        self.path = path
        self.payload = payload

class ResponseDataType(Serializable):

    def __init__(self,
                 resp_to,
                 success,
                 payload):
        self.resp_to = resp_to
        self.success = success
        self.payload = payload