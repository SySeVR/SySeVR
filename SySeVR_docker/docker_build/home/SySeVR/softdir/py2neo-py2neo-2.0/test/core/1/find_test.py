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


try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock
from uuid import uuid4

from py2neo import Node


def test_will_find_no_nodes_with_non_existent_label(graph):
    if not graph.supports_node_labels:
        return
    nodes = list(graph.find(uuid4().hex))
    assert nodes == []


def test_can_find_nodes_with_label(graph):
    if not graph.supports_node_labels:
        return
    alice, = graph.create(Node("Person", name="Alice"))
    nodes = list(graph.find("Person"))
    assert alice in nodes


def test_can_find_nodes_with_label_and_property(graph):
    if not graph.supports_node_labels:
        return
    alice, = graph.create(Node("Person", name="Alice"))
    nodes = list(graph.find("Person", "name", "Alice"))
    assert alice in nodes


def test_cannot_find_empty_label(graph):
    if not graph.supports_node_labels:
        return
    try:
        _ = list(graph.find(""))
    except ValueError:
        assert True
    else:
        assert False


def test_can_find_one_node_with_label_and_property(graph):
    if not graph.supports_node_labels:
        return
    name = uuid4().hex
    thing = Node("Thing", name=name)
    graph.create(thing)
    found = graph.find_one("Thing", "name", name)
    assert found is thing
