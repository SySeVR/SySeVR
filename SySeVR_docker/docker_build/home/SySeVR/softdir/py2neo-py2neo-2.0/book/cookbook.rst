========
Cookbook
========


Monitoring Client-Server Interaction
====================================

The :func:`py2neo.watch` function dumps log messages to standard output for various operations
within the library.

To watch HTTP traffic::

    >>> from py2neo import watch
    >>> watch("httpstream")

To watch Cypher traffic::

    >>> from py2neo import watch
    >>> watch("py2neo.cypher")

To watch batch traffic::

    >>> from py2neo import watch
    >>> watch("py2neo.batch")


.. autofunction:: py2neo.watch


Escaping Values in Cypher
=========================

    >>> from py2neo.cypher import cypher_escape
    >>> rel_type = "KNOWS WELL"
    >>> statement = "CREATE (a)-[ab:%s]->(b) RETURN ab" % cypher_escape(rel_type)
    >>> statement
    'CREATE (a)-[ab:`KNOWS WELL`]->(b) RETURN ab'


Authentication
==============

.. autofunction:: py2neo.authenticate


URI Rewriting
=============

.. autofunction:: py2neo.rewrite
