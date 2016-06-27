from __future__ import absolute_import
from abc import ABCMeta, abstractmethod

class Serializable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def dict(self):
        raise NotImplementedError()

    def __iter__(self):
        for key, val in self.dict().items():
            yield key, val

    @classmethod
    def parse(cls, dictionary):
        raise NotImplementedError()