class memoized_property(object):
    """
    A read-only @property that is only evaluated once.

    From: http://www.reddit.com/r/Python/comments/ejp25/cached_property_decorator_that_is_memory_friendly/
    """
    def __init__(self, fget, doc=None):
        self.fget = fget
        self.__doc__ = doc or fget.__doc__
        self.__name__ = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return self
        obj.__dict__[self.__name__] = result = self.fget(obj)
        return result

from types import FunctionType

is_property           = lambda obj: type(obj)==property
is_function           = lambda obj: type(obj)==FunctionType
is_nonprivatefunction = lambda name, obj: (not name.startswith('_')) and is_function(obj)


class AllStaticMethods(type):
    """ AllStaticMethods:
         set this class as your metaclass in order to build a
         module-like class.. all methods inside the class will
         be turned into static methods.
    """
    def __new__(mcs, name, bases, dct, finished=True):
        """
            NOTE: the 'finished' flag is used for chaining..
                  make sure you know what you're doing if you use it.
        """
        for x, func in dct.items():
            if is_nonprivatefunction(x, func):
                dct[x] = staticmethod(func)
        if finished:
            return type.__new__(mcs, name, bases, dct)
        else:
            return (mcs, name, bases, dct)
