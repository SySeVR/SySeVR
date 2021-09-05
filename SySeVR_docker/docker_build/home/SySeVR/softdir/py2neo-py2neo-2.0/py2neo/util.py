#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2011-2014, Nigel Small
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Utility module
"""


from __future__ import unicode_literals

try:
    from configparser import SafeConfigParser
except ImportError:
    from ConfigParser import SafeConfigParser
from itertools import cycle, islice
import os
import re
import sys
from threading import local
import warnings
from weakref import WeakValueDictionary


__all__ = ["numberise", "compact", "flatten", "round_robin", "deprecated",
           "version_tuple", "is_collection", "has_all", "pendulate",
           "is_integer", "is_string", "is_numeric", "ustr", "xstr",
           "PropertiesParser", "ThreadLocalWeakValueDictionary"]


def numberise(n):
    """ Convert a value to an integer if possible. If not, simply return
        the input value.
    """
    if n == "NaN":
        return None
    try:
        return int(n)
    except ValueError:
        return n


def compact(obj):
    """ Return a copy of an object with all :py:const:`None` values removed.
    """
    if isinstance(obj, dict):
        return dict((key, value) for key, value in obj.items() if value is not None)
    else:
        return obj.__class__(value for value in obj if value is not None)


def flatten(*values):
    for value in values:
        if hasattr(value, "__iter__"):
            for val in value:
                yield val
        else:
            yield value


def round_robin(*iterables):
    """ Cycle through a number of iterables, returning
        the next item from each in turn.

        round_robin('ABC', 'D', 'EF') --> A D E B F C

        Original recipe credited to George Sakkis
        Python 2/3 cross-compatibility tweak by Nigel Small
    """
    pending = len(iterables)
    nexts = cycle(iter(it) for it in iterables)
    while pending:
        try:
            for n in nexts:
                yield next(n)
        except StopIteration:
            pending -= 1
            nexts = cycle(islice(nexts, pending))


def deprecated(message):
    """ Decorator for deprecating functions and methods.

    ::

        @deprecated("'foo' has been deprecated in favour of 'bar'")
        def foo(x):
            pass

    """
    def f__(f):
        def f_(*args, **kwargs):
            warnings.warn(message, category=DeprecationWarning, stacklevel=2)
            return f(*args, **kwargs)
        f_.__name__ = f.__name__
        f_.__doc__ = f.__doc__
        f_.__dict__.update(f.__dict__)
        return f_
    return f__


VERSION = re.compile("(\d+\.\d+(\.\d+)?)")


def version_tuple(string):
    numbers = VERSION.match(string)
    if numbers:
        version = [int(n) for n in numbers.group(0).split(".")]
        extra = string[len(numbers.group(0)):]
        while extra.startswith(".") or extra.startswith("-"):
            extra = extra[1:]
    else:
        version = []
        extra = string
    while len(version) < 3:
        version += [0]
    if extra:
        version += [extra]
    return tuple(version)


def is_collection(obj):
    """ Returns true for any iterable which is not a string or byte sequence.
    """
    try:
        if isinstance(obj, unicode):
            return False
    except NameError:
        pass
    if isinstance(obj, bytes):
        return False
    try:
        iter(obj)
    except TypeError:
        return False
    try:
        hasattr(None, obj)
    except TypeError:
        return True
    return False


has_all = lambda iterable, items: all(item in iterable for item in items)


if sys.version_info >= (3,):

    is_integer = lambda x: isinstance(x, int)
    is_numeric = lambda x: isinstance(x, (int, float, complex))
    is_string = lambda x: isinstance(x, str)

    def ustr(s, encoding="utf-8"):
        """ Convert argument to unicode string.
        """
        if isinstance(s, str):
            return s
        try:
            return s.decode(encoding)
        except AttributeError:
            return str(s)

    def xstr(s, encoding="utf-8"):
        """ Convert argument to string type returned by __str__.
        """
        return ustr(s, encoding)

else:

    is_integer = lambda x: isinstance(x, (int, long))
    is_numeric = lambda x: isinstance(x, (int, float, long, complex))
    is_string = lambda x: isinstance(x, (str, unicode))

    def ustr(s, encoding="utf-8"):
        """ Convert argument to unicode string.
        """
        if isinstance(s, str):
            return s.decode(encoding)
        else:
            return unicode(s)

    def xstr(s, encoding="utf-8"):
        """ Convert argument to string type returned by __str__.
        """
        if isinstance(s, str):
            return s
        else:
            return unicode(s).encode(encoding)


def pendulate(collection):
    count = len(collection)
    for i in range(count):
        if i % 2 == 0:
            index = i // 2
        else:
            index = count - ((i + 1) // 2)
        yield index, collection[index]


def raise_from(exception, cause):
    exception.__cause__ = cause
    raise exception


if sys.version_info >= (3,):

    class PropertiesParser(SafeConfigParser):

        def read_properties(self, filename, section=None):
            if not section:
                basename = os.path.basename(filename)
                if basename.endswith(".properties"):
                    section = basename[:-11]
                else:
                    section = basename
            with open(filename) as f:
                data = f.read()
            self.read_string("[%s]\n%s" % (section, data), filename)

else:

    import codecs
    from io import StringIO

    class PropertiesParser(SafeConfigParser):

        def read_properties(self, filename, section=None):
            if not section:
                basename = os.path.basename(filename)
                if basename.endswith(".properties"):
                    section = basename[:-11]
                else:
                    section = basename
            data = StringIO()
            data.write("[%s]\n" % section)
            with codecs.open(filename, encoding="utf-8") as f:
                data.write(f.read())
            data.seek(0, os.SEEK_SET)
            self.readfp(data)


class ThreadLocalWeakValueDictionary(WeakValueDictionary, local):
    pass
