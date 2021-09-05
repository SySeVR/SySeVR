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


from py2neo.core import Node, Relationship, Path, PropertySet, LabelSet
from py2neo.batch.core import Batch, Job, CypherJob, Target
from py2neo.batch.push import PushNodeLabelsJob, PushPropertiesJob, PushPropertyJob


__all__ = ["CreateNodeJob", "CreateRelationshipJob", "CreatePathJob", "CreateUniquePathJob",
           "DeleteEntityJob", "DeletePropertyJob", "DeletePropertiesJob",
           "AddNodeLabelsJob", "RemoveNodeLabelJob", "WriteBatch"]


def _create_query(p, unique=False):
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
            params["q{0}".format(i)] = PropertySet(rel.properties)
            values.append("r{0}".format(i))
        else:
            path.append("-[r{0}:`{1}`]->".format(i, rel.type))
            values.append("r{0}".format(i))

    append_node(0, p.nodes[0])
    for i, rel in enumerate(p.rels):
        append_rel(i, rel)
        append_node(i + 1, p.nodes[i + 1])
    clauses = []
    if nodes:
        clauses.append("START {0}".format(",".join(nodes)))
    if unique:
        clauses.append("CREATE UNIQUE p={0}".format("".join(path)))
    else:
        clauses.append("CREATE p={0}".format("".join(path)))
    #clauses.append("RETURN {0}".format(",".join(values)))
    clauses.append("RETURN p")
    query = " ".join(clauses)
    return query, params


class CreateNodeJob(Job):

    target = Target("node")

    def __init__(self, **properties):
        Job.__init__(self, "POST", self.target, properties)


class CreateRelationshipJob(Job):

    def __init__(self, start_node, rel, end_node, **properties):
        body = {"type": rel.type, "to": Target(end_node).uri_string}
        if rel.properties or properties:
            body["data"] = dict(rel.properties, **properties)
        Job.__init__(self, "POST", Target(start_node, "relationships"), body)


class CreatePathJob(CypherJob):

    def __init__(self, *entities):
        CypherJob.__init__(self, *_create_query(Path(*entities)))


class CreateUniquePathJob(CypherJob):

    def __init__(self, *entities):
        CypherJob.__init__(self, *_create_query(Path(*entities), unique=True))


class DeleteEntityJob(Job):

    def __init__(self, entity):
        Job.__init__(self, "DELETE", Target(entity))


class DeletePropertyJob(Job):

    def __init__(self, entity, key):
        Job.__init__(self, "DELETE", Target(entity, "properties", key))


class DeletePropertiesJob(Job):

    def __init__(self, entity):
        Job.__init__(self, "DELETE", Target(entity, "properties"))


class AddNodeLabelsJob(Job):

    def __init__(self, node, *labels):
        Job.__init__(self, "POST", Target(node, "labels"), list(LabelSet(labels)))


class RemoveNodeLabelJob(Job):

    def __init__(self, entity, label):
        Job.__init__(self, "DELETE", Target(entity, "labels", label))


class WriteBatch(Batch):
    """ Generic batch execution facility for data write requests. Most methods
    return a :py:class:`BatchRequest <py2neo.neo4j.BatchRequest>` object that
    can be used as a reference in other methods. See the
    :py:meth:`create <py2neo.neo4j.WriteBatch.create>` method for an example
    of this.
    """

    def __init__(self, graph):
        Batch.__init__(self, graph)

    def run(self):
        self.graph.batch.run(self)

    def stream(self):
        for result in self.graph.batch.stream(self):
            yield result.content

    def submit(self):
        return [result.content for result in self.graph.batch.submit(self)]

    def create(self, abstract):
        """ Create a node or relationship based on the abstract entity
        provided. For example::

            batch = WriteBatch(graph)
            a = batch.create(node(name="Alice"))
            b = batch.create(node(name="Bob"))
            batch.create(rel(a, "KNOWS", b))
            results = batch.submit()

        :param abstract: node or relationship
        :type abstract: abstract
        :return: batch request object
        """
        entity = self.graph.cast(abstract)
        if isinstance(entity, Node):
            return self.append(CreateNodeJob(**entity.properties))
        elif isinstance(entity, Relationship):
            start_node = self.resolve(entity.start_node)
            end_node = self.resolve(entity.end_node)
            return self.append(CreateRelationshipJob(start_node, entity.rel, end_node))
        else:
            raise TypeError(entity)

    def create_path(self, node, *rels_and_nodes):
        """ Construct a path across a specified set of nodes and relationships.
        Nodes may be existing concrete node instances, abstract nodes or
        :py:const:`None` but references to other requests are not supported.

        :param node: start node
        :type node: concrete, abstract or :py:const:`None`
        :param rels_and_nodes: alternating relationships and nodes
        :type rels_and_nodes: concrete, abstract or :py:const:`None`
        :return: batch request object
        """
        return self.append(CreatePathJob(node, *rels_and_nodes))

    def get_or_create_path(self, node, *rels_and_nodes):
        """ Construct a unique path across a specified set of nodes and
        relationships, adding only parts that are missing. Nodes may be
        existing concrete node instances, abstract nodes or :py:const:`None`
        but references to other requests are not supported.

        :param node: start node
        :type node: concrete, abstract or :py:const:`None`
        :param rels_and_nodes: alternating relationships and nodes
        :type rels_and_nodes: concrete, abstract or :py:const:`None`
        :return: batch request object
        """
        return self.append(CreateUniquePathJob(node, *rels_and_nodes))

    def delete(self, entity):
        """ Delete a node or relationship from the graph.

        :param entity: node or relationship to delete
        :type entity: concrete or reference
        :return: batch request object
        """
        return self.append(DeleteEntityJob(self.resolve(entity)))

    def set_property(self, entity, key, value):
        """ Set a single property on a node or relationship.

        :param entity: node or relationship on which to set property
        :type entity: concrete or reference
        :param key: property key
        :type key: :py:class:`str`
        :param value: property value
        :return: batch request object
        """
        return self.append(PushPropertyJob(self.resolve(entity), key, value))

    def set_properties(self, entity, properties):
        """ Replace all properties on a node or relationship.

        :param entity: node or relationship on which to set properties
        :type entity: concrete or reference
        :param properties: properties
        :type properties: :py:class:`dict`
        :return: batch request object
        """
        return self.append(PushPropertiesJob(self.resolve(entity), properties))

    def delete_property(self, entity, key):
        """ Delete a single property from a node or relationship.

        :param entity: node or relationship from which to delete property
        :type entity: concrete or reference
        :param key: property key
        :type key: :py:class:`str`
        :return: batch request object
        """
        return self.append(DeletePropertyJob(self.resolve(entity), key))

    def delete_properties(self, entity):
        """ Delete all properties from a node or relationship.

        :param entity: node or relationship from which to delete properties
        :type entity: concrete or reference
        :return: batch request object
        """
        return self.append(DeletePropertiesJob(self.resolve(entity)))

    def add_labels(self, node, *labels):
        """ Add labels to a node.

        :param node: node to which to add labels
        :type entity: concrete or reference
        :param labels: text labels
        :type labels: :py:class:`str`
        :return: batch request object
        """
        return self.append(AddNodeLabelsJob(self.resolve(node), *labels))

    def remove_label(self, node, label):
        """ Remove a label from a node.

        :param node: node from which to remove labels (can be a reference to
            another request within the same batch)
        :param label: text label
        :type label: :py:class:`str`
        :return: batch request object
        """
        return self.append(RemoveNodeLabelJob(self.resolve(node), label))

    def set_labels(self, node, *labels):
        """ Replace all labels on a node.

        :param node: node on which to replace labels (can be a reference to
            another request within the same batch)
        :param labels: text labels
        :type labels: :py:class:`str`
        :return: batch request object
        """
        return self.append(PushNodeLabelsJob(self.resolve(node), labels))
