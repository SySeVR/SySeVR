==========================
Introduction to Py2neo 2.0
==========================

In this introduction, you will see how to get connected to a `Neo4j <http://neo4j.com/>`_ graph
database and how to carry out basic operations. You will also be introduced to many of the core
concepts needed when working with py2neo.


Getting Connected
=================

The simplest way to try out a connection to the Neo4j server is via the console. Once you have
started a local Neo4j server, open a new Python console and enter the following::

    >>> from py2neo import Graph
    >>> graph = Graph()

This imports the :class:`Graph <py2neo.Graph>` class from py2neo and creates a instance bound to
the default Neo4j server URI, ``http://localhost:7474/db/data/``.

To connect to a server at an alternative address, simply pass in the URI value as a string argument
to the Graph constructor::

    >>> remote_graph = Graph("http://remotehost.com:6789/db/data/")

For a database behind a secure proxy, a user name and password can also be supplied to the
constructor URI. These credentials will then be applied to any subsequent HTTP requests made to the
host and port combination specified (in this case, ``camelot:1150``)::

    >>> secure_graph = Graph("https://arthur:excalibur@camelot:1150/db/data/")

A :class:`Graph <py2neo.Graph>` object provides a basis for most of the interaction with the Neo4j
server that a typical client application will need to make. The database URI is therefore generally
the only URI that needs to be provided explicitly.


Nodes & Relationships
=====================

`Nodes <http://neo4j.com/docs/2.1.5/javadocs/org/neo4j/graphdb/Node.html>`_ and
`relationships <http://neo4j.com/docs/2.1.5/javadocs/org/neo4j/graphdb/Relationship.html>`_ are the
fundamental building blocks of a Neo4j graph and both have a corresponding class in py2neo.
Assuming we've already established a connection to the server (as above) let's build a simple graph
with two nodes and one relationship::

    >>> from py2neo import Node, Relationship
    >>> alice = Node("Person", name="Alice")
    >>> bob = Node("Person", name="Bob")
    >>> alice_knows_bob = Relationship(alice, "KNOWS", bob)
    >>> graph.create(alice_knows_bob)

When first created, :class:`Node <py2neo.Node>` and :class:`Relationship <py2neo.Relationship>`
objects exist only in the client; nothing has yet been written to the server. The
:func:`Graph.create <py2neo.Graph.create>` method shown above creates corresponding server-side
objects and automatically binds each local object to its remote counterpart. Within py2neo,
*binding* is the process of applying a URI to a client object thereby allowing future
client-server synchonisation operations to occur.

.. note::
   Entity binding can be managed directly by using the :func:`bind <py2neo.Node.bind>`
   and :func:`unbind <py2neo.Node.unbind>` methods and observed through the
   :attr:`bound <py2neo.Node.bound>` boolean attribute.


Pushing & Pulling
=================

Client-server communication over `REST <http://neo4j.com/docs/2.1.4/rest-api/>`_ can be chatty if
not used carefully. Whenever possible, py2neo attempts to minimise the amount of chatter between
the client and the server by batching and lazily retrieving data. Most read and write operations
are explicit, allowing the Python application developer a high degree of control over network
traffic.

.. note::
   Previous versions of py2neo have synchronised data between client and server automatically,
   such as when setting a single property value. Py2neo 2.0 will not carry out updates to client
   or server objects until this is explicitly requested.

To illustrate synchronisation, let's give Alice and Bob an ``age`` property each. Longhand, this is
done as follows::

    >>> alice.properties["age"] = 33
    >>> bob.properties["age"] = 44
    >>> alice.push()
    >>> bob.push()

Here, we add a new property to each of the two local nodes and :func:`push <py2neo.Node.push>` the
changes in turn. This results in two separate HTTP calls being made to the server which can be seen
more clearly with the debugging function, :func:`watch <py2neo.watch>`::

    >>> from py2neo import watch
    >>> watch("httpstream")
    >>> alice.push()
    > POST http://localhost:7474/db/data/batch [146]
    < 200 OK [119]
    >>> bob.push()
    > POST http://localhost:7474/db/data/batch [146]
    < 200 OK [119]

.. note::
   The watch function comes with the bundled `httpstream <http://github.com/nigelsmall/httpstream>`_
   library and simply dumps log entries to standard output.

To squash these two separate push operations into one, we can use the
:func:`Graph.push <py2neo.Graph.push>` method instead::

    >>> graph.push(alice, bob)
    > POST http://localhost:7474/db/data/batch [289]
    < 200 OK [237]

Not only does this method reduce the activity down to a single HTTP call but it wraps both updates
in a single atomic transaction.

Pulling updates from server to client is similar: either call the :func:`pull <py2neo.Node.pull>`
method on an individual entity or batch together several updates by using
:func:`Graph.pull <py2neo.Graph.pull>`.


Cypher
======

Single Statements
-----------------

Neo4j has a built-in data query and manipulation language called
`Cypher <http://neo4j.com/guides/basic-cypher/>`_. To execute Cypher from within py2neo, simply use
the :attr:`cypher <py2neo.Graph.cypher>` attribute of a :class:`Graph <py2neo.Graph>` instance and
call the :func:`execute <py2neo.cypher.CypherResource.execute>` method::

    >>> graph.cypher.execute("CREATE (c:Person {name:{N}}) RETURN c", {"N": Carol})
       | c
    ---+----------------------------
     1 | (n2:Person {name:"Carol"})


The object returned from this call is a :class:`RecordList <py2neo.cypher.RecordList>` which is
rendered by default as a table of results. Each item in this list is a
:class:`Record <py2neo.cypher.Record>` instance::

    >>> for record in graph.cypher.execute("CREATE (d:Person {name:'Dave'}) RETURN d"):
    ...     print(record)
    ...
     d
    ---------------------------
     (n3:Person {name:"Dave"})


A :class:`Record <py2neo.cypher.Record>` exposes its values through both named attributes and
numeric indexes. Therefore, if a Cypher query returns a column called ``name``, that column can be
accessed through the record attribute called ``name``::

    >>> for record in graph.cypher.execute("MATCH (p:Person) RETURN p.name AS name"):
    ...     print(record.name)
    ...
    Alice
    Bob
    Carol
    Dave


Similarly, the first column returned can be accessed as column 0::

    >>> for record in graph.cypher.execute("MATCH (p:Person) RETURN p.name AS name"):
    ...     print(record[0])
    ...
    Alice
    Bob
    Carol
    Dave


Transactions
------------

Neo4j 2.0 extended the REST interface to allow multiple Cypher statements to be sent to the server
as part of a single transaction. Transactions such as these allow far more control over the
logical grouping of statements and can also offer vastly better performance compared to individual
statements by submitting multiple statements in a single HTTP request.

To use this endpoint, firstly call the :func:`begin <py2neo.cypher.CypherResource.begin>` method on
the :attr:`Graph.cypher <py2neo.Graph.cypher>` resource to create a transaction, then use the
methods listed below on the new :class:`CypherTransaction <py2neo.cypher.CypherTransaction>`
object:

- :func:`append(statement, [parameters]) <py2neo.cypher.CypherTransaction.append>` - add a
  statement to the queue of statements to be executed (this does not pass any statements to the
  server)
- :func:`process() <py2neo.cypher.CypherTransaction.process>` - push all queued statements to the
  server for execution and return the results from those statements
- :func:`commit() <py2neo.cypher.CypherTransaction.commit>` - push all queued statements to the
  server for execution and commit the transaction (returns the results from all queued statements)
- :func:`rollback() <py2neo.cypher.CypherTransaction.rollback>` - roll the transaction back

For example::

    >>> tx = graph.cypher.begin()
    >>> statement = "MATCH (a {name:{A}}), (b {name:{B}}) CREATE (a)-[:KNOWS]->(b)"
    >>> for person_a, person_b in [("Alice", "Bob"), ("Bob", "Dave"), ("Alice", "Carol")]:
    ...     tx.append(statement, {"A": person_a, "B": person_b})
    ...
    >>> tx.commit()


Command Line
------------

Py2neo also provides a convenient command line tool for executing Cypher statements::

    $ cypher -p N Alice "MATCH (p:Person {name:{N}}) RETURN p"
       | p
    ---+----------------------------
     1 | (n1:Person {name:"Alice"})


This tool uses the ``NEO4J_URI`` environment variable to determine the location of the underlying
graph database. Support is also provided for a variety of output formats.


Unique Nodes
============

Many applications require some form of uniqueness to be maintained for the data they manage.
Neo4j's `optional schema feature <http://neo4j.com/docs/2.1.5/graphdb-neo4j-schema.html>`_ allows
such uniqueness constraints to be applied to a graph based on a combination of label and property
and py2neo exposes this capability through the
:func:`create_uniqueness_constraint <py2neo.schema.SchemaResource.create_uniqueness_constraint>`
method of the :attr:`Graph.schema <py2neo.Graph.schema>` attribute::

    >>> graph.schema.create_uniqueness_constraint("Person", "email")

If an attempt is made to create two nodes with similar unique property values, an exception will
be raised and no new node will be created. To 'get or create' a node with a particular
label and property, the :func:`merge_one <py2neo.Graph.merge_one>` method can be used instead::

    >>> xavier = graph.merge_one("Person", "email", "charles@x.men")

This method is idempotent and uses a Cypher `MERGE <http://neo4j.com/docs/stable/query-merge.html>`_
clause to only create a node if one does not already exist. If no uniqueness constraint has been
created for a particular label and property combination however, it is possible for a MERGE to
return multiple nodes. For this case, py2neo provides the related :func:`merge <py2neo.Graph.merge>`
method.


Unique Paths
============

When it comes to building unique relationships, the :func:`Graph.create_unique <py2neo.Graph.create_unique>`
method is a handy wrapper for the Cypher `CREATE UNIQUE <http://neo4j.com/docs/stable/query-create-unique.html>`_ clause.
This method can accept one or more :class:`Path <py2neo.Path>` objects, including
:class:`Relationship <py2neo.Relationship>` objects (which are simply a subclass of
:class:`Path <py2neo.Path>`).

Let's assume we want to pick up two nodes based on their email address properties and ensure they
are connected by a ``KNOWS`` relationship::

    >>> alice = graph.merge_one("Person", "email", "alice@example.com")
    >>> bob = graph.merge_one("Person", "email", "bob@email.net")
    >>> graph.create_unique(Relationship(alice, "KNOWS", bob))

We could of course extend this to create a unique chain of relationships::

    >>> carol = graph.merge_one("Person", "email", "carol@foo.us")
    >>> dave = graph.merge_one("Person", "email", "dave@dave.co.uk")
    >>> graph.create_unique(Path(alice, "KNOWS", bob, "KNOWS", carol, "KNOWS", dave))

Here, only relationships that do not already exist will be created although the whole path will be
returned.
