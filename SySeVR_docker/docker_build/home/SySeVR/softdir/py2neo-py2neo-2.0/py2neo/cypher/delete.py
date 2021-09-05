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


from py2neo.core import Graph, Node, Path, Relationship
from py2neo.util import ustr, xstr


__all__ = ["DeleteStatement"]


def _(*args):
    return "".join("_" + ustr(arg) for arg in args)


class DeleteStatement(object):
    """ Builder for a Cypher DELETE statement.
    """

    #: The graph against which this statement is to be executed.
    graph = None

    #: The parameters to inject into this statement.
    parameters = None

    def __init__(self, graph):
        self.graph = graph
        self.supports_node_labels = self.graph.supports_node_labels
        self.entities = []
        self.start_clause = []
        self.delete_rels_clause = []
        self.delete_nodes_clause = []
        self.parameters = {}

    def __repr__(self):
        return self.string

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        return self.string

    def __contains__(self, entity):
        return any(e is entity for e in self.entities)

    @property
    def string(self):
        """ The full Cypher statement as a string.
        """
        clauses = []
        if self.start_clause:
            clauses.append("START " + ",".join(self.start_clause))
        if self.delete_rels_clause:
            clauses.append("DELETE " + ",".join(self.delete_rels_clause))
        if self.delete_nodes_clause:
            clauses.append("DELETE " + ",".join(self.delete_nodes_clause))
        return "\n".join(clauses)

    def post(self):
        return self.graph.cypher.post(self.string, self.parameters)

    def execute(self):
        """ Execute this statement.
        """
        if self.string:
            self.post().close()

    def delete(self, entity):
        """ Append an entity to the DELETE clause of this statement.

        :arg entity: The entity to delete.

        """
        entity = Graph.cast(entity)
        index = len(self.entities)
        name = _(index)
        if isinstance(entity, Node):
            self._delete_node(entity, name)
        elif isinstance(entity, Relationship):
            self._delete_relationship(entity, name)
        elif isinstance(entity, Path):
            self._delete_path(entity, name)
        self.entities.append(entity)

    def _delete_node(self, node, name):
        if node.bound:
            self.start_clause.append("{name}=node({{{name}}})".format(name=name))
            self.delete_nodes_clause.append(name)
            self.parameters[name] = node._id

    def _delete_relationship(self, relationship, name):
        if relationship.bound:
            self.start_clause.append("{name}=rel({{{name}}})".format(name=name))
            self.delete_rels_clause.append(name)
            self.parameters[name] = relationship._id

    def _delete_path(self, path, name):
        for i, rel in enumerate(path.relationships):
            self._delete_relationship(rel, name + "r" + ustr(i))
        for i, node in enumerate(path.nodes):
            self._delete_node(node, name + "n" + ustr(i))
