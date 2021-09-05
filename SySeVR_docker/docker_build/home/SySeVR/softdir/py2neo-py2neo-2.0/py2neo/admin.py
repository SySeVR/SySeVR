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


from collections import namedtuple
from datetime import datetime

from py2neo import Service, Resource, ServiceRoot
from py2neo.util import numberise


class Monitor(Service):

    __instances = {}

    def __new__(cls, uri=None):
        """ Fetch a cached instance if one is available, otherwise create,
        cache and return a new instance.

        :param uri: URI of the cached resource
        :return: a resource instance
        """
        inst = super(Monitor, cls).__new__(cls, uri)
        return cls.__instances.setdefault(uri, inst)

    def __init__(self, uri=None):
        if uri is None:
            service_root = ServiceRoot()
            manager = Resource(service_root.resource.metadata["management"])
            monitor = Monitor(manager.metadata["services"]["monitor"])
            uri = monitor.resource.uri
        Service.__init__(self)
        self.bind(uri)

    def fetch_latest_stats(self):
        """ Fetch the latest server statistics as a list of 2-tuples, each
        holding a `datetime` object and a named tuple of node, relationship and
        property counts.
        """
        counts = namedtuple("Stats", ("node_count",
                                      "relationship_count",
                                      "property_count"))
        uri = self.resource.metadata["resources"]["latest_data"]
        latest_data = Resource(uri).get().content
        timestamps = latest_data["timestamps"]
        data = latest_data["data"]
        data = zip(
            (datetime.fromtimestamp(t) for t in timestamps),
            (counts(*x) for x in zip(
                (numberise(n) for n in data["node_count"]),
                (numberise(n) for n in data["relationship_count"]),
                (numberise(n) for n in data["property_count"]),
            )),
        )
        return data
