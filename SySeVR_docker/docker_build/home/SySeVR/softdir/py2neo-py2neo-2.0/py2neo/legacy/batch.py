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


from py2neo.batch import ReadBatch, WriteBatch, Job, Target
from py2neo.core import Node, Relationship, NodePointer
from py2neo.packages.httpstream.packages.urimagic import percent_encode


__all__ = ["LegacyReadBatch", "LegacyWriteBatch"]


class LegacyReadBatch(ReadBatch):
    """ Generic batch execution facility for data read requests,
    """

    def append_get(self, uri):
        return self.append(Job("GET", Target(uri)))

    def _index(self, content_type, index):
        """ Fetch an Index object.
        """
        from py2neo.legacy.index import Index
        if isinstance(index, Index):
            if content_type == index._content_type:
                return index
            else:
                raise TypeError("Index is not for {0}s".format(content_type))
        else:
            return self.graph.legacy.get_or_create_index(content_type, str(index))

    def get_indexed_nodes(self, index, key, value):
        """ Fetch all nodes indexed under a given key-value pair.

        :param index: index name or instance
        :type index: :py:class:`str` or :py:class:`Index`
        :param key: key under which nodes are indexed
        :type key: :py:class:`str`
        :param value: value under which nodes are indexed
        :return: batch request object
        """
        index = self._index(Node, index)
        uri = index._searcher_stem_for_key(key) + percent_encode(value)
        return self.append_get(uri)


class LegacyWriteBatch(WriteBatch):
    """ Generic batch execution facility for data write requests. Most methods
    return a :py:class:`BatchRequest <py2neo.neo4j.BatchRequest>` object that
    can be used as a reference in other methods. See the
    :py:meth:`create <py2neo.neo4j.WriteBatch.create>` method for an example
    of this.
    """

    def append_post(self, uri, body=None):
        return self.append(Job("POST", Target(uri), body))

    def append_delete(self, uri):
        return self.append(Job("DELETE", Target(uri)))

    def _uri_for(self, resource, *segments, **kwargs):
        """ Return a relative URI in string format for the entity specified
        plus extra path segments.
        """
        if isinstance(resource, int):
            uri = "{{{0}}}".format(resource)
        elif isinstance(resource, NodePointer):
            uri = "{{{0}}}".format(resource.address)
        elif isinstance(resource, Job):
            uri = "{{{0}}}".format(self.find(resource))
        else:
            uri = resource.ref
        if segments:
            if not uri.endswith("/"):
                uri += "/"
            uri += "/".join(map(percent_encode, segments))
        query = kwargs.get("query")
        if query is not None:
            uri += "?" + query
        return uri

    def _index(self, content_type, index):
        """ Fetch an Index object.
        """
        from py2neo.legacy.index import Index
        if isinstance(index, Index):
            if content_type == index._content_type:
                return index
            else:
                raise TypeError("Index is not for {0}s".format(content_type))
        else:
            return self.graph.legacy.get_or_create_index(content_type, str(index))

    def __init__(self, graph):
        super(LegacyWriteBatch, self).__init__(graph)
        self.__new_uniqueness_modes = None

    @property
    def supports_index_uniqueness_modes(self):
        return self.graph.legacy.supports_index_uniqueness_modes

    def _assert_can_create_or_fail(self):
        if not self.supports_index_uniqueness_modes:
            raise NotImplementedError("Uniqueness mode `create_or_fail` "
                                      "requires version 1.9 or above")

    ### ADD TO INDEX ###

    def _add_to_index(self, cls, index, key, value, entity, query=None):
        uri = self._uri_for(self._index(cls, index), query=query)
        return self.append_post(uri, {
            "key": key,
            "value": value,
            "uri": self._uri_for(entity),
        })

    def add_to_index(self, cls, index, key, value, entity):
        """ Add an existing node or relationship to an index.

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param entity: node or relationship to add to the index
        :type entity: concrete or reference
        :return: batch request object
        """
        return self._add_to_index(cls, index, key, value, entity)

    def add_to_index_or_fail(self, cls, index, key, value, entity):
        """ Add an existing node or relationship uniquely to an index, failing
        the entire batch if such an entry already exists.

        .. warning::
            Uniqueness modes for legacy indexes have been broken in recent
            server versions and therefore this method may not work as expected.

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param entity: node or relationship to add to the index
        :type entity: concrete or reference
        :return: batch request object
        """
        self._assert_can_create_or_fail()
        query = "uniqueness=create_or_fail"
        return self._add_to_index(cls, index, key, value, entity, query)

    def get_or_add_to_index(self, cls, index, key, value, entity):
        """ Fetch a uniquely indexed node or relationship if one exists,
        otherwise add an existing entity to the index.

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param entity: node or relationship to add to the index
        :type entity: concrete or reference
        :return: batch request object
        """
        if self.supports_index_uniqueness_modes:
            query = "uniqueness=get_or_create"
        else:
            query = "unique"
        return self._add_to_index(cls, index, key, value, entity, query)

    ### CREATE IN INDEX ###

    def _create_in_index(self, cls, index, key, value, abstract, query=None):
        uri = self._uri_for(self._index(cls, index), query=query)
        if cls is Node:
            node = Node.cast(abstract)
            return self.append_post(uri, {
                "key": key,
                "value": value,
                "properties": node.properties,
            })
        elif cls is Relationship:
            relationship = Relationship.cast(abstract)
            return self.append_post(uri, {
                "key": key,
                "value": value,
                "start": self._uri_for(abstract.start_node),
                "type": str(abstract.type),
                "end": self._uri_for(abstract.end_node),
                "properties": relationship.properties,
            })
        else:
            raise TypeError(cls)

    # Removed create_in_index as parameter combination not supported by server

    def create_in_index_or_fail(self, cls, index, key, value, abstract=None):
        """ Create a new node or relationship and add it uniquely to an index,
        failing the entire batch if such an entry already exists.

        .. warning::
            Uniqueness modes for legacy indexes have been broken in recent
            server versions and therefore this method may not work as expected.

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param abstract: abstract node or relationship to create
        :return: batch request object
        """
        self._assert_can_create_or_fail()
        query = "uniqueness=create_or_fail"
        return self._create_in_index(cls, index, key, value, abstract, query)

    def get_or_create_in_index(self, cls, index, key, value, abstract=None):
        """ Fetch a uniquely indexed node or relationship if one exists,
        otherwise create a new entity and add that to the index.

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param abstract: abstract node or relationship to create
        :return: batch request object
        """
        if self.supports_index_uniqueness_modes:
            query = "uniqueness=get_or_create"
        else:
            query = "unique"
        return self._create_in_index(cls, index, key, value, cls.cast(abstract), query)

    ### REMOVE FROM INDEX ###

    def remove_from_index(self, cls, index, key=None, value=None, entity=None):
        """ Remove any nodes or relationships from an index that match a
        particular set of criteria. Allowed parameter combinations are:

        `key`, `value`, `entity`
            remove a specific node or relationship indexed under a given
            key-value pair

        `key`, `entity`
            remove a specific node or relationship indexed against a given key
            and with any value

        `entity`
            remove all occurrences of a specific node or relationship
            regardless of key or value

        :param cls: the type of indexed entity
        :type cls: :py:class:`Node <py2neo.neo4j.Node>` or
                   :py:class:`Relationship <py2neo.neo4j.Relationship>`
        :param index: index or index name
        :type index: :py:class:`Index <py2neo.neo4j.Index>` or :py:class:`str`
        :param key: index entry key
        :type key: :py:class:`str`
        :param value: index entry value
        :param entity: node or relationship to remove from the index
        :type entity: concrete or reference
        :return: batch request object
        """
        index = self._index(cls, index)
        if key and value and entity:
            uri = self._uri_for(index, key, value, entity._id)
        elif key and entity:
            uri = self._uri_for(index, key, entity._id)
        elif entity:
            uri = self._uri_for(index, entity._id)
        else:
            raise TypeError("Illegal parameter combination for index removal")
        return self.append_delete(uri)
