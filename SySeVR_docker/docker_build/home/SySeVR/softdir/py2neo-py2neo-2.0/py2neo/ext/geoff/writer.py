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


import json

from py2neo.core import Node, Rel, Rev, Path
from py2neo.lang import Writer
from py2neo.util import is_collection, ustr


__all__ = ["GeoffWriter"]


class GeoffWriter(Writer):
    """ Writer for Geoff data. This can be used to write to any
    file-like object, such as standard output::

        >>> from py2neo import Node
        >>> from py2neo.ext.geoff import GeoffWriter
        >>> import sys
        >>> writer = GeoffWriter(sys.stdout)
        >>> writer.write(Node("Person", name="Alice"))
        (139895901379856:Person {"name":"Alice"})

    """

    safe_chars = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_"

    default_sequence_separator = ","
    default_key_value_separator = ":"
    default_element_separator = "\n"

    def __init__(self, file=None, **kwargs):
        Writer.__init__(self, file)
        self.sequence_separator = kwargs.get("sequence_separator", self.default_sequence_separator)
        self.key_value_separator = \
            kwargs.get("key_value_separator", self.default_key_value_separator)
        self.element_separator = kwargs.get("element_separator", self.default_element_separator)

    def write(self, obj):
        """ Write any entity, value or collection.
        """
        if obj is None:
            pass
        elif isinstance(obj, Node):
            self.write_node(id(obj), obj.labels, obj.properties)
        elif isinstance(obj, Rev):
            self.write_rev(obj.type, obj.properties)
        elif isinstance(obj, Rel):
            self.write_rel(obj.type, obj.properties)
        elif isinstance(obj, Path):
            self.write_path(obj)
        elif isinstance(obj, dict):
            self.write_map(obj)
        elif is_collection(obj):
            self.write_list(obj)
        else:
            self.write_value(obj)

    def write_value(self, value):
        """ Write a value.
        """
        self.file.write(ustr(json.dumps(value, ensure_ascii=False)))

    def write_identifier(self, identifier):
        """ Write an identifier.
        """
        if not identifier:
            raise ValueError("Invalid identifier")
        identifier = ustr(identifier)
        safe = all(ch in self.safe_chars for ch in identifier)
        if not safe:
            self.file.write(json.dumps(identifier))
        else:
            self.file.write(identifier)

    def write_list(self, collection):
        """ Write a list.
        """
        self.file.write("[")
        link = ""
        for value in collection:
            self.file.write(link)
            self.write(value)
            link = self.sequence_separator
        self.file.write("]")

    def write_map(self, mapping):
        """ Write a map.
        """
        self.file.write("{")
        link = ""
        for key, value in sorted(mapping.items()):
            self.file.write(link)
            self.write_value(key)
            self.file.write(self.key_value_separator)
            self.write(value)
            link = self.sequence_separator
        self.file.write("}")

    def write_node(self, name, labels=None, properties=None, unique_label=None, unique_key=None):
        """ Write a node.
        """
        self.file.write("(")
        if name:
            self.write_identifier(name)
        for label in sorted(labels or []):
            self.file.write(":")
            self.write_identifier(label)
            if label == unique_label:
                self.file.write("!")
                if unique_key:
                    self.file.write(unique_key)
        if properties is not None:
            if name or labels:
                self.file.write(" ")
            self.write_map(properties)
        self.file.write(")")

    def write_rel(self, type_, properties=None, unique=False):
        """ Write a forward relationship (excluding nodes).
        """
        self.file.write("-[:")
        self.write_identifier(type_)
        if unique:
            self.file.write("!")
        if properties is not None:
            self.file.write(" ")
            self.write_map(properties)
        self.file.write("]->")

    def write_rev(self, type_, properties=None, unique=False):
        """ Write a reverse relationship (excluding nodes).
        """
        self.file.write("<-[:")
        self.write_identifier(type_)
        if unique:
            self.file.write("!")
        if properties is not None:
            self.file.write(" ")
            self.write_map(properties)
        self.file.write("]-")

    def write_path(self, path):
        """ Write a :class:`py2neo.Path`.
        """
        nodes = path.nodes
        self.write_node(id(nodes[0]))
        for i, rel in enumerate(path.rels):
            if isinstance(rel, Rev):
                self.write_rev(rel.type, rel.properties)
            else:
                self.write_rel(rel.type, rel.properties)
            self.write_node(id(nodes[i + 1]))

    def write_subgraph(self, subgraph):
        """ Write a :class:`py2neo.Subgraph`.
        """
        # TODO: uniqueness (in Subgraph)
        link = ""
        for node in subgraph.nodes:
            self.file.write(link)
            self.write_node(id(node), node.labels, node.properties)
            link = self.element_separator
        for relationship in subgraph.relationships:
            self.file.write(link)
            self.write_path(relationship)
            link = self.element_separator
