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

from py2neo.core import Resource, UnmanagedExtension
from py2neo.util import version_tuple

from py2neo.ext.geoff.xmlutil import xml_to_geoff


__all__ = ["GeoffLoader", "NodeDictionary"]


class GeoffLoader(UnmanagedExtension):
    """ A wrapper for the `load2neo <http://nigelsmall.com/load2neo>`_
    unmanaged extension.
    """

    DEFAULT_PATH = "/load2neo/"

    def __init__(self, graph, path=DEFAULT_PATH):
        UnmanagedExtension.__init__(self, graph, path)
        self.geoff_loader = Resource(self.resource.metadata["geoff_loader"])

    @property
    def load2neo_version(self):
        """ The version of server extension currently installed.
        """
        return version_tuple(self.resource.metadata["load2neo_version"])

    def load(self, string):
        """ Load Geoff data from a string.
        """
        rs = self.geoff_loader.post(string)
        return [NodeDictionary(self.graph, json.loads(line))
                for line in rs.content.splitlines(False)]

    def load_xml(self, string):
        """ Load XML data by first converting to Geoff format.
        """
        return self.load(xml_to_geoff(string))


class NodeDictionary(object):
    """ A set of nodes returned from a successful Geoff load operation.
    Each node is keyed by the identifier used in the original Geoff
    data.
    """

    def __init__(self, graph, data):
        self.graph = graph
        self.__data = data

    def __len__(self):
        return len(self.__data)

    def __iter__(self):
        return iter(self.__data)

    def __getitem__(self, key):
        return self.graph.node(self.__data[key])

    def get_ref(self, key):
        """ Get the node reference string for the node identified by
        the given key.
        """
        return "node/%s" % self.__data[key]

    def keys(self):
        """ Fetch a list of all node keys.
        """
        return self.__data.keys()

    def values(self):
        """ Fetch a list of all nodes.
        """
        return self.__data.values()

    def items(self):
        """ Fetch a list of all key-node pairs, each returned as a 2-tuple.
        """
        return self.__data.items()
