===================
Extension: Calendar
===================

Maintained by: Nigel Small <nigel@py2neo.org>

The `calendar` module provides standardised date management functionality based on a calendar
subgraph::

    from py2neo import Graph, Node, Relationship
    from py2neo.ext.calendar import GregorianCalendar

    graph = Graph()
    calendar = GregorianCalendar(graph)

    alice = Node("Person", name="Alice")
    birth = Relationship(alice, "BORN", calendar.date(1800, 1, 1).day)
    death = Relationship(alice, "DIED", calendar.date(1900, 12, 31).day)
    graph.create(alice, birth, death)


All dates managed by the :class:`GregorianCalendar <py2neo.ext.calendar.GregorianCalendar>` class
adhere to a hierarchy such as::

    (calendar)-[:YEAR]->(2000)-[:MONTH]->(12)-[:DAY]->(25)


.. autoclass:: py2neo.ext.calendar.GregorianCalendar
   :members:

.. autoclass:: py2neo.ext.calendar.GregorianDate
   :members:
