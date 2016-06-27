import types
from functools import partial
import inspect

ENTRYPOINT_ATTR = 'microservice_entrypoint'

class Entrypoint(object):

    @staticmethod
    def get_entrypoints_from_class(cls):

        def is_method(obj):
            name, val = obj
            # in Python 2 it uses MetodType, in Python 3 it uses FunctionType
            return type(getattr(cls, name)) in {types.FunctionType, types.MethodType}

        methods = list(filter(is_method, inspect.getmembers(cls)))
        entry_methods = []
        for name, method in methods:
            if getattr(method, ENTRYPOINT_ATTR, None):
                entry_methods.append(name)
        return entry_methods

    @staticmethod
    def mark_method_as_entrypoint(meth):
        old_mark = getattr(meth, ENTRYPOINT_ATTR, None)

        if old_mark:
            raise ValueError('the method already marked as entrypoint')

        setattr(meth, ENTRYPOINT_ATTR, True)

    @classmethod
    def decorator(cls, *args, **kwargs):

        def registering_decorator(fn, args, kwargs):
            cls.mark_method_as_entrypoint(fn)
            return fn

        if len(args) == 1 and isinstance(args[0], types.FunctionType):
            # usage without arguments to the decorator:
            # @foobar
            # def spam():
            #     pass
            return registering_decorator(args[0], args=(), kwargs={})
        else:
            # usage with arguments to the decorator:
            # @foobar('shrub', ...)
            # def spam():
            #     pass
            return partial(registering_decorator, args=args, kwargs=kwargs)

entrypoint = Entrypoint.decorator