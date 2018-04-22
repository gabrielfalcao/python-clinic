# -*- coding: utf-8 -*-
from functools import wraps


def interface_method(method):
    @wraps(method)
    def wrapper(self, *args, **kw):  # pragma: no cover
        Class = self.__class__
        class_name, method_name = Class.__name__, method.__name__
        raise NotImplementedError('{}.{} must be implemented'.format(class_name, method_name))

    return wrapper
