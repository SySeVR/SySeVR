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
from py2neo import Node

from py2neo.batch.write import WriteBatch


def test_cannot_create_with_bad_type(graph):
    batch = WriteBatch(graph)
    try:
        batch.create("")
    except TypeError:
        assert True
    else:
        assert False


def test_cannot_create_with_none(graph):
    batch = WriteBatch(graph)
    try:
        batch.create(None)
    except TypeError:
        assert True
    else:
        assert False


def test_can_create_path_with_new_nodes(graph):
    batch = WriteBatch(graph)
    batch.create_path({"name": "Alice"}, "KNOWS", {"name": "Bob"})
    results = batch.submit()
    path = results[0]
    assert len(path) == 1
    assert path.nodes[0]["name"] == "Alice"
    assert path.relationships[0].type == "KNOWS"
    assert path.nodes[1]["name"] == "Bob"


def test_can_create_path_with_existing_nodes(graph):
    alice, bob = graph.create({"name": "Alice"}, {"name": "Bob"})
    batch = WriteBatch(graph)
    batch.create_path(alice, "KNOWS", bob)
    results = batch.submit()
    path = results[0]
    assert len(path) == 1
    assert path.nodes[0] == alice
    assert path.relationships[0].type == "KNOWS"
    assert path.nodes[1] == bob


def test_path_creation_is_not_idempotent(graph):
    alice, = graph.create({"name": "Alice"})
    batch = WriteBatch(graph)
    batch.create_path(alice, "KNOWS", {"name": "Bob"})
    results = batch.submit()
    path = results[0]
    bob = path.nodes[1]
    assert path.nodes[0] == alice
    assert bob["name"] == "Bob"
    batch = WriteBatch(graph)
    batch.create_path(alice, "KNOWS", {"name": "Bob"})
    results = batch.submit()
    path = results[0]
    assert path.nodes[0] == alice
    assert path.nodes[1] != bob


def test_can_get_or_create_path_with_existing_nodes(graph):
    alice, bob = graph.create({"name": "Alice"}, {"name": "Bob"})
    batch = WriteBatch(graph)
    batch.get_or_create_path(alice, "KNOWS", bob)
    results = batch.submit()
    path = results[0]
    assert len(path) == 1
    assert path.nodes[0] == alice
    assert path.relationships[0].type == "KNOWS"
    assert path.nodes[1] == bob


def test_path_merging_is_idempotent(graph):
    alice, = graph.create({"name": "Alice"})
    batch = WriteBatch(graph)
    batch.get_or_create_path(alice, "KNOWS", {"name": "Bob"})
    results = batch.submit()
    path = results[0]
    bob = path.nodes[1]
    assert path.nodes[0] == alice
    assert bob["name"] == "Bob"
    batch = WriteBatch(graph)
    batch.get_or_create_path(alice, "KNOWS", {"name": "Bob"})
    results = batch.submit()
    path = results[0]
    assert path.nodes[0] == alice
    assert path.nodes[1] == bob


def test_can_set_property_on_preexisting_node(graph):
    alice, = graph.create({"name": "Alice"})
    batch = WriteBatch(graph)
    batch.set_property(alice, "age", 34)
    batch.run()
    alice.pull()
    assert alice["age"] == 34


def test_can_set_property_on_node_in_same_batch(graph):
    batch = WriteBatch(graph)
    alice = batch.create({"name": "Alice"})
    batch.set_property(alice, "age", 34)
    results = batch.submit()
    alice = results[batch.find(alice)]
    alice.auto_sync_properties = True
    assert alice["age"] == 34


def test_can_set_properties_on_preexisting_node(graph):
    alice, = graph.create({})
    batch = WriteBatch(graph)
    batch.set_properties(alice, {"name": "Alice", "age": 34})
    batch.run()
    alice.pull()
    assert alice["name"] == "Alice"
    assert alice["age"] == 34


def test_can_set_properties_on_node_in_same_batch(graph):
    batch = WriteBatch(graph)
    alice = batch.create({})
    batch.set_properties(alice, {"name": "Alice", "age": 34})
    results = batch.submit()
    alice = results[batch.find(alice)]
    alice.auto_sync_properties = True
    assert alice["name"] == "Alice"
    assert alice["age"] == 34


def test_can_delete_property_on_preexisting_node(graph):
    alice, = graph.create({"name": "Alice", "age": 34})
    batch = WriteBatch(graph)
    batch.delete_property(alice, "age")
    batch.run()
    alice.pull()
    assert alice["name"] == "Alice"
    assert alice["age"] is None


def test_can_delete_property_on_node_in_same_batch(graph):
    batch = WriteBatch(graph)
    alice = batch.create({"name": "Alice", "age": 34})
    batch.delete_property(alice, "age")
    results = batch.submit()
    alice = results[batch.find(alice)]
    alice.auto_sync_properties = True
    assert alice["name"] == "Alice"
    assert alice["age"] is None


def test_can_delete_properties_on_preexisting_node(graph):
    alice, = graph.create({"name": "Alice", "age": 34})
    batch = WriteBatch(graph)
    batch.delete_properties(alice)
    batch.run()
    alice.pull()
    assert alice.properties == {}


def test_can_delete_properties_on_node_in_same_batch(graph):
    batch = WriteBatch(graph)
    alice = batch.create({"name": "Alice", "age": 34})
    batch.delete_properties(alice)
    results = batch.submit()
    alice = results[batch.find(alice)]
    alice.pull()
    assert alice.properties == {}


def test_can_add_labels_to_preexisting_node(graph):
    if not graph.supports_node_labels:
        return
    alice, = graph.create({"name": "Alice"})
    batch = WriteBatch(graph)
    batch.add_labels(alice, "human", "female")
    batch.run()
    alice.pull()
    assert alice.labels == {"human", "female"}


def test_can_add_labels_to_node_in_same_batch(graph):
    if not graph.supports_node_labels:
        return
    batch = WriteBatch(graph)
    a = batch.create({"name": "Alice"})
    batch.add_labels(a, "human", "female")
    results = batch.submit()
    alice = results[batch.find(a)]
    alice.pull()
    assert alice.labels == {"human", "female"}


def test_can_remove_labels_from_preexisting_node(graph):
    if not graph.supports_node_labels:
        return
    alice, = graph.create(Node("human", "female", name="Alice"))
    batch = WriteBatch(graph)
    batch.remove_label(alice, "human")
    batch.run()
    alice.pull()
    assert alice.labels == {"female"}


def test_can_add_and_remove_labels_on_node_in_same_batch(graph):
    if not graph.supports_node_labels:
        return
    batch = WriteBatch(graph)
    alice = batch.create({"name": "Alice"})
    batch.add_labels(alice, "human", "female")
    batch.remove_label(alice, "female")
    results = batch.submit()
    alice = results[batch.find(alice)]
    alice.pull()
    assert alice.labels == {"human"}


def test_can_set_labels_on_preexisting_node(graph):
    if not graph.supports_node_labels:
        return
    alice, = graph.create(Node("human", "female", name="Alice"))
    batch = WriteBatch(graph)
    batch.set_labels(alice, "mystery", "badger")
    batch.run()
    alice.pull()
    assert alice.labels == {"mystery", "badger"}


def test_can_set_labels_on_node_in_same_batch(graph):
    if not graph.supports_node_labels:
        return
    batch = WriteBatch(graph)
    batch.create({"name": "Alice"})
    batch.add_labels(0, "human", "female")
    batch.set_labels(0, "mystery", "badger")
    results = batch.submit()
    alice = results[0]
    alice.pull()
    assert alice.labels == {"mystery", "badger"}
