================
Extension: Geoff
================

Maintained by: Nigel Small <nigel@py2neo.org>

Geoff is a text-based interchange format for Neo4j graph data that should be instantly readable to
anyone familiar with Cypher, on which its syntax is based. For more information on the format
itself, see `here <http://nigelsmall.com/geoff>`_.

The Geoff extension for py2neo consists of a writer and a loader API. A command line tool is also
provided for easy access to the load functionality. The loader itself requires a server plugin to
be installed called `load2neo <http://nigelsmall.com/load2neo>`_.


Writer
======

.. autoclass:: py2neo.ext.geoff.GeoffWriter
   :members:


Loader
======

.. autoclass:: py2neo.ext.geoff.GeoffLoader
   :members:

.. autoclass:: py2neo.ext.geoff.NodeDictionary
   :members:


Command Line
============

A command line tool, ``geoff`` is installed as part of this extension. This gives access to the
:class:`GeoffLoader <py2neo.ext.geoff.GeoffLoader>` class and can be used as follows::

    $ geoff load '(alice:Person {"name":"Alice"})<-[:KNOWS]->(bob:Person {"name":"Bob"})'
    alice node/1
    bob   node/2

Instead of providing data inline, a file name can be specified instead using the ``-f`` option::

    $ geoff load -f abba.geoff
    abba     node/1648
    agnetha  node/1649
    benny    node/1655
    björn    node/1650
    frida    node/1653
    waterloo node/1654

XML files can also be passed using the ``-x`` option. These will be converted to Geoff before
loading::

    $ geoff load -x -f abba.xml
    abba     node/1668
    agnetha  node/1669
    benny    node/1670
    björn    node/1652
    frida    node/1664
    waterloo node/1665
