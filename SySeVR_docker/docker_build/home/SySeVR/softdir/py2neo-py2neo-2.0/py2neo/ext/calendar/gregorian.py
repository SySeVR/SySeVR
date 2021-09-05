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


from py2neo import Node, Path, GraphError


__all__ = ["GregorianCalendar", "GregorianDate"]


class GregorianCalendar(object):
    """ A Gregorian calendar stored in a graph as a tree
    of ``(year)->(month)->(day)``.
    """

    #: The graph associated with this calendar.
    graph = None

    __instances = {}

    def __new__(cls, graph):
        if not graph.supports_node_labels:
            raise ValueError("Graph does not support node labels")
        try:
            inst = cls.__instances[graph]
        except KeyError:
            inst = super(GregorianCalendar, cls).__new__(cls)
            inst.graph = graph
            try:
                inst.graph.schema.create_uniqueness_constraint("Calendar", "name")
            except GraphError as error:
                if error.__class__.__name__ == "ConstraintViolationException":
                    pass
                else:
                    raise
            inst.root = inst.graph.merge_one("Calendar", "name", "Gregorian")
            cls.__instances[graph] = inst
        return inst

    def date(self, year, month=1, day=1):
        """ Pick a date from this calendar.

        :rtype: :class:`.GregorianDate`

        """
        return GregorianDate(self, year, month, day)


class GregorianDate(object):
    """ A date picked from a :class:`.GregorianCalendar`.
    """

    #: The calendar from which this date was picked.
    calendar = None

    #: The graph associated with this date.
    graph = None

    #: Full :class:`Path <py2neo.Path>` representing this date.
    path = None

    def __init__(self, calendar, year, month=1, day=1):
        self.calendar = calendar
        self.graph = self.calendar.graph
        self.path = Path(self.calendar.root,
                         "YEAR", Node("Year", key='%04d' % year, year=year),
                         "MONTH", Node("Month", key='%04d-%02d' % (year, month), year=year, month=month),
                         "DAY", Node("Day", key='%04d-%02d-%02d' % (year, month, day), year=year, month=month, day=day))
        self.graph.create_unique(self.path)

    @property
    def year(self):
        """ The year node for this date.

        :rtype: :class:`py2neo.Node`

        """
        return self.path.nodes[1]

    @property
    def month(self):
        """ The month node for this date.

        :rtype: :class:`py2neo.Node`

        """
        return self.path.nodes[2]

    @property
    def day(self):
        """ The day node for this date.

        :rtype: :class:`py2neo.Node`

        """
        return self.path.nodes[3]
