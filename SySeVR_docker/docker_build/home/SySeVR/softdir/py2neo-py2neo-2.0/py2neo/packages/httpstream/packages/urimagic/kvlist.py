#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2014, Nigel Small
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


try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping


class KeyValueList(list):
    """ A KeyValueList is a list of key-value pairs that functions as an
    ordered dictionary with support for duplicate keys.

    An instance can be created using either an iterable sequence of pairs or a
    mapping plus an optional set of keyword arguments:

    >>> kvl = KeyValueList([('a', 1), ('c', 7), 'cx', ('b', [8, 9])], c='b')
    >>> kvl
    KeyValueList([('a', 1), ('c', 7), ('c', 'x'), ('b', [8, 9]), ('c', 'b')])

    This creates a list of values that have both an associated key and a
    positional index:

     index | key | value
    -------+-----+--------
     0     | 'a' | 1
     1     | 'c' | 7
     2     | 'c' | 1
     3     | 'b' | [8, 9]
     4     | 'c' | 'b'

    """

    def __init__(self, iterable=(), **kwargs):
        list.__init__(self)
        self.extend(iterable)
        self.extend(kwargs)

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__, list.__repr__(self))

    def __getitem__(self, index):
        """ Get a single item.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl[2]
        ('green', 'grass')
        >>> kvl[9]
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        IndexError: list index out of range

        """
        got = list.__getitem__(self, index)
        if isinstance(index, slice):
            return KeyValueList(got)
        else:
            return got

    def __getslice__(self, start, end):
        """ Get a slice of items.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl[1:3]
        KeyValueList([('blue', 'sea'), ('green', 'grass')])

        """
        try:
            return KeyValueList(list.__getslice__(self, start, end))
        except AttributeError:
            return KeyValueList(list.__getitem__(self, slice(start, end)))

    def __setitem__(self, index, item):
        """ Set a single item.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl[1] = ('yellow', 'sun')
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('yellow', 'sun')
        ('green', 'grass')
        ('blue', 'sky')
        >>> kvl[9] = ('orange', 'orange')
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        IndexError: list assignment index out of range

        """
        list.__setitem__(self, index, item)

    def __setslice__(self, start, stop, items):
        """ Set a slice of items.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl[1:3] = [('yellow', 'sun'), ('grey', 'stone'), ('red', 'berry')]
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('yellow', 'sun')
        ('grey', 'stone')
        ('red', 'berry')
        ('blue', 'sky')

        """
        list.__setslice__(self, start, stop, items)

    def __delitem__(self, index):
        """ Delete a single item.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> del kvl[1]
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('green', 'grass')
        ('blue', 'sky')
        >>> del kvl[9]
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        IndexError: list assignment index out of range

        """
        list.__delitem__(self, index)

    def __delslice__(self, start, end):
        """ Delete a slice of items.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> del kvl[1:3]
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('blue', 'sky')

        """
        list.__delslice__(self, start, end)

    def __contains__(self, item):
        """ Check for the presence of a particular key-value pair within this
        list. This is equivalent to the `has_item` method.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> ('blue', 'sea') in kvl
        True
        >>> ('yellow', 'sun') in kvl
        False
        >>> ('purple', 'grape') not in kvl
        True
        >>> ('red', 'rose') not in kvl
        False

        """
        key, value = item
        return self.has_item(key, value)

    def __iter__(self):
        """ Iterate through all items in this list. This is equivalent to the
        `items` method with `collect` set to False.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for key, value in kvl:
        ...     print("{0} -> {1}".format(key, value))
        red -> rose
        blue -> sea
        green -> grass
        blue -> sky

        """
        return list.__iter__(self)

    def append(self, key, value):
        """ Append a single key-value pair to the end of this list.

        >>> kvl = KeyValueList()
        >>> kvl.append('one', 'eins')
        >>> kvl.append('two', 'zwei')
        >>> kvl.append('three', 'drei')
        >>> for item in kvl:
        ...     print(item)
        ('one', 'eins')
        ('two', 'zwei')
        ('three', 'drei')

        """
        list.append(self, (key, value))

    def extend(self, iterable):
        """ Concatenate two lists by adding a list of extra items to the end
        of this list. Each item added must be capable of being unpacked into a
        key-value pair.

        >>> kvl = KeyValueList([('one', 'eins'), ('two', 'zwei')])
        >>> kvl.extend([('three', 'drei'), ('four', 'vier')])
        >>> for item in kvl:
        ...     print(item)
        ('one', 'eins')
        ('two', 'zwei')
        ('three', 'drei')
        ('four', 'vier')
        >>> kvl.extend(['five', 'six'])
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        ValueError: KeyValueList items must be pairs

        """
        if isinstance(iterable, Mapping):
            list.extend(self, iterable.items())
        else:
            try:
                list.extend(self, ((k, v) for k, v in iterable))
            except ValueError:
                raise ValueError("KeyValueList items must be pairs")

    def insert(self, index, key, value):
        """ Insert a key-value pair at a particular position within the list:

        >>> kvl = KeyValueList({'three': 'drei'})
        >>> kvl.insert(0, 'one', 'eins')
        >>> kvl.insert(1, 'two', 'zwei')
        >>> for item in kvl:
        ...     print(item)
        ('one', 'eins')
        ('two', 'zwei')
        ('three', 'drei')

        """
        list.insert(self, index, (key, value))

    def has_item(self, key, value):
        """ Check for the presence of a particular key-value pair within this
        list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl.has_item('green', 'grass')
        True
        >>> kvl.has_item('pink', 'rose')
        False

        """
        for k, v in self:
            if k == key and v == value:
                return True
        return False

    def has_key(self, key):
        """ Check for the presence of a particular key within this list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl.has_key('blue')
        True
        >>> kvl.has_key('yellow')
        False

        """
        for k, v in self:
            if k == key:
                return True
        return False

    def has_value(self, value):
        """ Check for the presence of a particular value within this list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl.has_value('grass')
        True
        >>> kvl.has_value('sun')
        False

        """
        for k, v in self:
            if v == value:
                return True
        return False

    def get(self, key):
        """ Iterate through all values associated with the specified key.
        Non-existent keys return empty iterators.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for value in kvl.get('blue'):
        ...     print(value)
        sea
        sky
        >>> for value in kvl.get('yellow'):
        ...     print(value)

        """
        return (v for k, v in self if k == key)

    def put(self, key, *values):
        """ Replace all values associated with the specified key with the
        value arguments provided. If fewer values are specified than currently
        exist, remaining items will be removed; if more items are specified,
        these will be appended to the end of the list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('blue', 'sky')])
        >>> kvl.put('blue', 'jeans')
        >>> kvl
        KeyValueList([('red', 'rose'), ('blue', 'jeans')])
        >>> kvl.put('red', 'heart', 'berry')
        >>> kvl
        KeyValueList([('red', 'heart'), ('blue', 'jeans'), ('red', 'berry')])

        """
        new_values = list(values)
        self[:] = [
            (k, value) if k != key else (k, new_values.pop(0))
            for k, value in self
            if k != key or new_values
        ]
        self.extend([(key, value) for value in new_values])

    def remove(self, key):
        """ Remove all items from this list that contain the key specified. If
        the key is not found, a ValueError is raised.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl.remove('blue')
        >>> kvl
        KeyValueList([('red', 'rose'), ('green', 'grass')])
        >>> kvl.remove('yellow')
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        ValueError: Key 'yellow' not in list

        """
        length = len(self)
        self[:] = ((k, v) for k, v in self if k != key)
        if len(self) == length:
            raise ValueError("Key {0} not in list".format(repr(key)))

    def pop(self, index=None):
        """ Remove the item at the index specified and return it. If no index
        is specified, the last item is popped. If the index is out of range, an
        IndexError is raised.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> kvl.pop(2)
        ('green', 'grass')
        >>> kvl.pop()
        ('blue', 'sky')
        >>> kvl.pop(6)
        Traceback (most recent call last):
          File "<stdin>", line 1, in ?
        IndexError: pop index out of range

        """
        if index is None:
            return list.pop(self)
        else:
            return list.pop(self, index)

    def clear(self):
        """ Remove all items from this list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> len(kvl)
        4
        >>> kvl.clear()
        >>> len(kvl)
        0

        """
        del self[:]

    def sort(self, *args, **kwargs):
        """ Sort the items in this list into ascending order.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('blue', 'sea')
        ('green', 'grass')
        ('blue', 'sky')
        >>> kvl.sort()
        >>> for item in kvl:
        ...     print(item)
        ('blue', 'sea')
        ('blue', 'sky')
        ('green', 'grass')
        ('red', 'rose')

        """
        list.sort(self, *args, **kwargs)

    def reverse(self):
        """ Reverse the order of items in this list.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for item in kvl:
        ...     print(item)
        ('red', 'rose')
        ('blue', 'sea')
        ('green', 'grass')
        ('blue', 'sky')
        >>> kvl.reverse()
        >>> for item in kvl:
        ...     print(item)
        ('blue', 'sky')
        ('green', 'grass')
        ('blue', 'sea')
        ('red', 'rose')

        """
        list.reverse(self)

    def copy(self):
        """ Create and return a shallow copy of this list instance.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea')])
        >>> kvl
        KeyValueList([('red', 'rose'), ('blue', 'sea')])
        >>> kvl2 = kvl.copy()
        >>> kvl2.append('green', 'grass')
        >>> kvl
        KeyValueList([('red', 'rose'), ('blue', 'sea')])
        >>> kvl2
        KeyValueList([('red', 'rose'), ('blue', 'sea'), ('green', 'grass')])

        """
        return KeyValueList(self)

    def iterkeys(self, collect=False):
        """ Iterate through the keys in this list. If `collect` is True,
        yield only unique keys.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for key in kvl.iterkeys():
        ...     print(key)
        red
        blue
        green
        blue
        >>> for key in kvl.iterkeys(collect=True):
        ...     print(key)
        red
        blue
        green

        """
        if collect:
            keys = []
            for k, v in self:
                if k not in keys:
                    keys.append(k)
                    yield k
        else:
            for k, v in self:
                yield k

    def itervalues(self, collect=False):
        """ Iterate through the values in this list. If `collect` is True,
        yield a list of values for each unique key.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for key in kvl.itervalues():
        ...     print(key)
        rose
        sea
        grass
        sky
        >>> for key in kvl.itervalues(collect=True):
        ...     print(key)
        ['rose']
        ['sea', 'sky']
        ['grass']

        """
        if collect:
            keys, values = [], []
            for k, v in self:
                try:
                    index = keys.index(k)
                except ValueError:
                    keys.append(k)
                    values.append([v])
                else:
                    values[index].append((v))
            for value in values:
                yield value
        else:
            for k, v in self:
                yield v

    def iteritems(self, collect=False):
        """ Iterate through the items in this list. If `collect` is True,
        yield only one item for each unique key, each with a list of
        associated values.

        >>> kvl = KeyValueList([('red', 'rose'), ('blue', 'sea'),
        ... ('green', 'grass'), ('blue', 'sky')])
        >>> for key in kvl.iteritems():
        ...     print(key)
        ('red', 'rose')
        ('blue', 'sea')
        ('green', 'grass')
        ('blue', 'sky')
        >>> for key in kvl.iteritems(collect=True):
        ...     print(key)
        ('red', ['rose'])
        ('blue', ['sea', 'sky'])
        ('green', ['grass'])

        """
        if collect:
            keys, items = [], []
            for k, v in self:
                try:
                    index = keys.index(k)
                except ValueError:
                    keys.append(k)
                    items.append((k, [v]))
                else:
                    items[index][1].append((v))
            for item in items:
                yield item
        else:
            for item in self:
                yield item
