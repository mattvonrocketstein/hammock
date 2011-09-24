from flask import render_template_string
def use_local_template(func):
    def fxn(*args, **kargs):
        context = func(*args, **kargs)
        template = '{%extends "layout.html" %}{%block body%}<center>' + \
                   func.__doc__ + '</center>{%endblock%}'
        return render_template_string(template, **context)
    return fxn


from types import FunctionType
from report import report, getReporter
report2 = getReporter(label=False)


def authorization_required(func):
    def newfunc(self, *args, **kargs):
        if not self.authorized:
            return redirect(self.url)
        return func(self, *args, **kargs)
    return newfunc

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
