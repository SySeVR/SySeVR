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


from py2neo import Service, ResourceTemplate, GraphError
from py2neo.packages.httpstream import Response
from py2neo.packages.httpstream.numbers import NOT_FOUND


__all__ = ["SchemaResource"]


class SchemaResource(Service):
    """ The schema resource attached to a `Graph` instance.
    """

    __instances = {}

    def __new__(cls, uri):
        try:
            inst = cls.__instances[uri]
        except KeyError:
            inst = super(SchemaResource, cls).__new__(cls)
            inst.bind(uri)
            if not inst.graph.supports_schema_indexes:
                raise NotImplementedError("Schema index support requires version 2.0 or above")
            inst._index_template = ResourceTemplate(uri + "/index/{label}")
            inst._index_key_template = ResourceTemplate(uri + "/index/{label}/{property_key}")
            inst._uniqueness_constraint_template = \
                ResourceTemplate(uri + "/constraint/{label}/uniqueness")
            inst._uniqueness_constraint_key_template = \
                ResourceTemplate(uri + "/constraint/{label}/uniqueness/{property_key}")
            cls.__instances[uri] = inst
        return inst

    def create_index(self, label, property_key):
        """ Create a schema index for a label and property
        key combination.
        """
        self._index_template.expand(label=label).post({"property_keys": [property_key]})

    def create_uniqueness_constraint(self, label, property_key):
        """ Create a uniqueness constraint for a label.
        """
        self._uniqueness_constraint_template.expand(label=label).post(
            {"property_keys": [property_key]})

    def drop_index(self, label, property_key):
        """ Remove label index for a given property key.
        """
        try:
            self._index_key_template.expand(label=label, property_key=property_key).delete()
        except GraphError as error:
            cause = error.__cause__
            if isinstance(cause, Response):
                if cause.status_code == NOT_FOUND:
                    raise GraphError("No such schema index (label=%r, key=%r)" % (
                        label, property_key))
            raise

    def drop_uniqueness_constraint(self, label, property_key):
        """ Remove the uniqueness constraint for a given property key.
        """
        try:
            self._uniqueness_constraint_key_template.expand(
                label=label, property_key=property_key).delete()
        except GraphError as error:
            cause = error.__cause__
            if isinstance(cause, Response):
                if cause.status_code == NOT_FOUND:
                    raise GraphError("No such unique constraint (label=%r, key=%r)" % (
                        label, property_key))
            raise

    def get_indexes(self, label):
        """ Fetch a list of indexed property keys for a label.
        """
        return [
            indexed["property_keys"][0]
            for indexed in self._index_template.expand(label=label).get().content
        ]

    def get_uniqueness_constraints(self, label):
        """ Fetch a list of unique constraints for a label.
        """
        return [
            unique["property_keys"][0]
            for unique in self._uniqueness_constraint_template.expand(label=label).get().content
        ]
