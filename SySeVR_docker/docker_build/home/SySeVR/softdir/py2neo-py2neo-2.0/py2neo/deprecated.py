#/usr/bin/env python
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


""" Deprecated features for core module.
"""


from py2neo.core import Graph, PropertyContainer, Node, Rel, Path, Relationship
from py2neo.error import BindError, GraphError
from py2neo.packages.httpstream.numbers import BAD_REQUEST
from py2neo.util import deprecated, flatten, ustr


__all__ = []


@deprecated("Use `pull` instead")
def _graph_get_properties(self, *entities):
    self.pull(*entities)
    return [entity.properties for entity in entities]


Graph.get_properties = _graph_get_properties


@deprecated("Use `properties` attribute instead")
def _property_container_get_cached_properties(self):
    return self.properties

@deprecated("Use `pull` method on `properties` attribute instead")
def _property_container_get_properties(self):
    if self.bound:
        self.properties.pull()
    return self.properties

@deprecated("Use `push` method on `properties` attribute instead")
def _property_container_set_properties(self, properties):
    self.properties.replace(properties)
    if self.bound:
        self.properties.push()

@deprecated("Use `push` method on `properties` attribute instead")
def _property_container_delete_properties(self):
    self.properties.clear()
    try:
        self.properties.push()
    except BindError:
        pass


PropertyContainer.get_cached_properties = _property_container_get_cached_properties
PropertyContainer.get_properties = _property_container_get_properties
PropertyContainer.set_properties = _property_container_set_properties
PropertyContainer.delete_properties = _property_container_delete_properties


@deprecated("Use `add` or `update` method of `labels` property instead")
def _node_add_labels(self, *labels):
    labels = [ustr(label) for label in set(flatten(labels))]
    self.labels.update(labels)
    try:
        self.labels.push()
    except GraphError as err:
        if err.response.status_code == BAD_REQUEST and err.cause.exception == 'ConstraintViolationException':
            raise ValueError(err.cause.message)
        else:
            raise

@deprecated("Use graph.create(Path(node, ...)) instead")
def _node_create_path(self, *items):
    path = Path(self, *items)
    return _path_create(path, self.graph)

@deprecated("Use Graph.delete instead")
def _node_delete(self):
    self.graph.delete(self)

@deprecated("Use Cypher query instead")
def _node_delete_related(self):
    if self.graph.supports_foreach_pipe:
        query = ("START a=node({a}) "
                 "MATCH (a)-[rels*0..]-(z) "
                 "FOREACH(r IN rels| DELETE r) "
                 "DELETE a, z")
    else:
        query = ("START a=node({a}) "
                 "MATCH (a)-[rels*0..]-(z) "
                 "FOREACH(r IN rels: DELETE r) "
                 "DELETE a, z")
    self.graph.cypher.post(query, {"a": self._id})

@deprecated("Use `labels` property instead")
def _node_get_labels(self):
    self.labels.pull()
    return self.labels

@deprecated("Use graph.create_unique(Path(node, ...)) instead")
def _node_get_or_create_path(self, *items):
    path = Path(self, *items)
    return _path_get_or_create(path, self.graph)

@deprecated("Use Cypher query instead")
def _node_isolate(self):
    query = "START a=node({a}) MATCH a-[r]-b DELETE r"
    self.graph.cypher.post(query, {"a": self._id})

@deprecated("Use `remove` method of `labels` property instead")
def _node_remove_labels(self, *labels):
    from py2neo.batch import WriteBatch
    labels = [ustr(label) for label in set(flatten(labels))]
    batch = WriteBatch(self.graph)
    for label in labels:
        batch.remove_label(self, label)
    batch.run()

@deprecated("Use `clear` and `update` methods of `labels` property instead")
def _node_set_labels(self, *labels):
    labels = [ustr(label) for label in set(flatten(labels))]
    self.labels.clear()
    self.labels.add(*labels)


Node.add_labels = _node_add_labels
Node.create_path = _node_create_path
Node.delete = _node_delete
Node.delete_related = _node_delete_related
Node.get_labels = _node_get_labels
Node.get_or_create_path = _node_get_or_create_path
Node.isolate = _node_isolate
Node.remove_labels = _node_remove_labels
Node.set_labels = _node_set_labels


@deprecated("Use graph.delete instead")
def _rel_delete(self):
    self.resource.delete()


Rel.delete = _rel_delete


def _path__create_query(self, unique):
    nodes, path, values, params = [], [], [], {}

    def append_node(i, node):
        if node is None:
            path.append("(n{0})".format(i))
            values.append("n{0}".format(i))
        elif node.bound:
            path.append("(n{0})".format(i))
            nodes.append("n{0}=node({{i{0}}})".format(i))
            params["i{0}".format(i)] = node._id
            values.append("n{0}".format(i))
        else:
            path.append("(n{0} {{p{0}}})".format(i))
            params["p{0}".format(i)] = node.properties
            values.append("n{0}".format(i))

    def append_rel(i, rel):
        if rel.properties:
            path.append("-[r{0}:`{1}` {{q{0}}}]->".format(i, rel.type))
            params["q{0}".format(i)] = rel.properties
            values.append("r{0}".format(i))
        else:
            path.append("-[r{0}:`{1}`]->".format(i, rel.type))
            values.append("r{0}".format(i))

    append_node(0, self._Path__nodes[0])
    for i, rel in enumerate(self._Path__rels):
        append_rel(i, rel)
        append_node(i + 1, self._Path__nodes[i + 1])
    clauses = []
    if nodes:
        clauses.append("START {0}".format(",".join(nodes)))
    if unique:
        clauses.append("CREATE UNIQUE p={0}".format("".join(path)))
    else:
        clauses.append("CREATE p={0}".format("".join(path)))
    clauses.append("RETURN p")
    query = " ".join(clauses)
    return query, params


def _path__create(self, graph, unique):
    query, params = _path__create_query(self, unique=unique)
    try:
        results = graph.cypher.execute(query, params)
    except GraphError:
        raise NotImplementedError(
            "The Neo4j server at <{0}> does not support "
            "Cypher CREATE UNIQUE clauses or the query contains "
            "an unsupported property type".format(graph.uri)
        )
    else:
        for row in results:
            return row.p

@deprecated("Use Graph.create(Path(...)) instead")
def _path_create(self, graph):
    return _path__create(self, graph, unique=False)

@deprecated("Use Graph.create_unique(Path(...)) instead")
def _path_get_or_create(self, graph):
    return _path__create(self, graph, unique=True)


Path.create = _path_create
Path.get_or_create = _path_get_or_create


@deprecated("Use Graph.delete instead")
def _relationship_delete(self):
    self.graph.delete(self)

@deprecated("Use `push` method on `properties` attribute instead")
def _relationship_delete_properties(self):
    self.properties.clear()
    try:
        self.properties.push()
    except BindError:
        pass

@deprecated("Use `properties` attribute instead")
def _relationship_get_cached_properties(self):
    return self.properties

@deprecated("Use `pull` method on `properties` attribute instead")
def _relationship_get_properties(self):
    if self.bound:
        self.properties.pull()
    return self.properties

@deprecated("Use `push` method on `properties` attribute instead")
def _relationship_set_properties(self, properties):
    self.properties.replace(properties)
    if self.bound:
        self.properties.push()

@deprecated("Use properties.update and push instead")
def _relationship_update_properties(self, properties):
    if self.bound:
        query, params = ["START a=rel({A})"], {"A": self._id}
        for i, (key, value) in enumerate(properties.items()):
            value_tag = "V" + str(i)
            query.append("SET a.`" + key + "`={" + value_tag + "}")
            params[value_tag] = value
        query.append("RETURN a")
        rel = self.graph.cypher.execute_one(" ".join(query), params)
        self._properties = rel.__metadata__["data"]
    else:
        self._properties.update(properties)


Relationship.delete = _relationship_delete
Relationship.delete_properties = _relationship_delete_properties
Relationship.get_cached_properties = _relationship_get_cached_properties
Relationship.get_properties = _relationship_get_properties
Relationship.set_properties = _relationship_set_properties
Relationship.update_properties = _relationship_update_properties
