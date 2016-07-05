from abc import ABCMeta
from datetime import datetime
from builtins import str, bytes
import types
from numbers import Number
import dateutil.parser
from gaw.serializable.exceptions import SerializeError

'''
{
    _v: {
        key: val,
        key: {_v: val, _t: type},
        key: [
            val, val, {_v: val, _t: type}
        ]
    },
    _t: type
}
'''

class Serializable(object):

    __metaclass__ = ABCMeta

    _serializable_types = {types.NoneType,
                           types.IntType,
                           types.LongType,
                           types.FloatType,
                           types.StringType,
                           types.UnicodeType,}

    _default_support_types = {
        'datetime': (lambda x: isinstance(x, datetime),
                     lambda x: x.__str__(),
                     lambda x: dateutil.parser.parse(x)),
        'tuple': (lambda x: isinstance(x, tuple),
                  lambda x: list(map(Serializable.serialize, x)),
                  lambda x: tuple(Serializable.parse(x)))
    }

    def dict(self):
        return self.serialize(self)

    def __iter__(self):
        for k, v in self.dict().items():
            yield k, v

    @classmethod
    def get_subclasses(cls):
        subclasses = set()
        work = [cls]
        while work:
            parent = work.pop()
            for child in parent.__subclasses__():
                if child not in subclasses:
                    subclasses.add(child)
                    work.append(child)
        return subclasses

    @classmethod
    def serialize_default_support_types(cls, obj):
        for type_name, (test_fn, serial_fn, parse_fn) in cls._default_support_types.items():
            if test_fn(obj):
                return dict(_v=serial_fn(obj),
                            _t=type_name)
        return None

    @classmethod
    def parse_default_support_types(cls, val, type):
        test_fn, serial_fn, parse_fn = cls._default_support_types.get(type)
        return parse_fn(val)

    @classmethod
    def serialize(cls, obj):
        # test default serializable types
        if type(obj) in cls._serializable_types:
            return obj

        # if it is a list
        if isinstance(obj, list):
            out_list = list(map(cls.serialize, obj))
            return out_list

        # a dict
        if isinstance(obj, dict):
            out_dict = dict(zip(obj.keys(), map(cls.serialize, obj.values())))
            return out_dict

        # test default supported types
        default_serial = cls.serialize_default_support_types(obj)
        if default_serial:
            return default_serial

        # must be a subclass of Serializable
        subclasses = Serializable.get_subclasses()
        for subclass in subclasses:
            if isinstance(obj, subclass):
                out_dict = dict()
                for key, val in obj.__dict__.items():
                    out_dict[key] = cls.serialize(val)
                return dict(_v=out_dict,
                            _t=subclass.__name__)

        # must be an unknown !
        raise SerializeError('cannot serialize an unknown type of {}'.format(type(obj)))

    @classmethod
    def parse(cls, obj):
        # a list
        if isinstance(obj, list):
            out_list = list(map(cls.parse, obj))
            return out_list

        # premitive types
        if not isinstance(obj, dict):
            return obj

        v = obj.get('_v', None)
        t = obj.get('_t', None)
        if not v and not t:
            # normal dict
            out_dict = dict(zip(obj.keys(), map(cls.parse, obj.values())))
            return out_dict
        elif v and t:
            if t in cls._default_support_types:
                # default types
                return cls.parse_default_support_types(v, t)

            # a subclass of Serializable
            subclasses = Serializable.get_subclasses()
            for subclass in subclasses:
                if t == subclass.__name__:
                    params = dict()
                    for key, val in v.items():
                        params[key] = cls.parse(val)
                    class_instace = subclass(**params)
                    return class_instace

            raise SerializeError('subclass not found {}'.format(t))
        else:
            raise SerializeError('cannot parse a dict with wrong _v or _t')