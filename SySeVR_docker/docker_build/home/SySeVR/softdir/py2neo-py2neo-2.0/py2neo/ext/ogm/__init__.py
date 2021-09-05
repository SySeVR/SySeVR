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

""" The ogm module provides Object to Graph Mapping features similar to ORM
facilities available for relational databases. All functionality is available
through the :class:`Store` class which is bound to a specific
:class:`~py2neo.Graph` instance on creation.

Conceptually, a mapped object *owns* a single node within the graph along with
all of that node's outgoing relationships. These features are managed via a
pair of attributes called ``__node__`` and ``__rel__`` which store details of the
mapped node and the outgoing relationships respectively. The only specific
requirement for a mapped object is that it has a nullary constructor which can
be used to create new instances.

The ``__node__`` attribute holds a :class:`~py2neo.Node` object which is the
node to which this object is mapped. If the attribute does not exist, or is
:const:`None`, the object is considered *unsaved*.

The ``__rel__`` attribute holds a dictionary of outgoing relationship details.
Each key corresponds to a relationship type and each value to a list of
2-tuples representing the outgoing relationships of that type. Within each
2-tuple, the first value holds a dictionary of relationship properties (which
may be empty) and the second value holds the endpoint. The endpoint may be
either a :class:`~py2neo.Node` instance or another mapped object. Any such
objects which are unsaved will be lazily saved as required by creation of the
relationship itself. The following data structure outline shows an example of
a ``__rel__`` attribute (where `alice` and `bob` represent other mapped objects::

    {
        "LIKES": [
            ({}, alice),
            ({"since": 1999}, bob)
        ]
    }

To manage relationships, use the :func:`Store.relate` and :func:`Store.separate`
methods. Neither method makes any calls to the database and operates only on the
local ``__rel__`` attribute. Changes must be explicitly saved via one of the
available save methods. The :func:`Store.load_related` method loads all objects
marked as related by the ``__rel__`` attribute.

The code below shows an example of usage::

    from py2neo import Graph
    from py2neo.ext.ogm import Store

    class Person(object):

        def __init__(self, email=None, name=None, age=None):
            self.email = email
            self.name = name
            self.age = age

        def __str__(self):
            return self.name

    graph = Graph()
    store = Store(graph)

    alice = Person("alice@example.com", "Alice", 34)
    store.save_unique("People", "email", alice.email, alice)

    bob = Person("bob@example.org", "Bob", 66)
    carol = Person("carol@example.net", "Carol", 42)
    store.relate(alice, "LIKES", bob)     # these relationships are not saved
    store.relate(alice, "LIKES", carol)   # until `alice` is saved
    store.save(alice)

    friends = store.load_related(alice, "LIKES", Person)
    print("Alice likes {0}".format(" and ".join(str(f) for f in friends)))

"""


from py2neo.ext.ogm.store import *


__all__ = ["Store", "NotSaved"]
