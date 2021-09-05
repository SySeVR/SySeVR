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

import logging
try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
import sys

import pytest

from py2neo import neo4j, Node, BindError, LegacyNode, GraphError, Path
from py2neo.packages.httpstream import ClientError, Resource as _Resource


PY3K = sys.version_info[0] >= 3
UNICODE_TEST_STR = ""

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.DEBUG,
)

for ch in [0x3053,0x308c,0x306f,0x30c6,0x30b9,0x30c8,0x3067,0x3059]:
    UNICODE_TEST_STR += chr(ch) if PY3K else unichr(ch)


class DodgyClientError(ClientError):
    status_code = 499


def test_can_get_node_by_id_when_cached(graph):
    node, = graph.create({})
    assert node.uri in Node.cache
    got = graph.node(node._id)
    assert got is node


def test_can_get_node_by_id_when_not_cached(graph):
    node, = graph.create({})
    Node.cache.clear()
    assert node.uri not in Node.cache
    got = graph.node(node._id)
    assert got._id == node._id


def test_node_cache_is_thread_local(graph):
    import threading
    node, = graph.create({})
    assert node.uri in Node.cache
    other_cache_keys = []

    def check_cache():
        other_cache_keys.extend(Node.cache.keys())

    thread = threading.Thread(target=check_cache)
    thread.start()
    thread.join()

    assert node.uri in Node.cache
    assert node.uri not in other_cache_keys


def test_can_get_node_by_id_even_when_id_does_not_exist(graph):
    node, = graph.create({})
    node_id = node._id
    graph.delete(node)
    Node.cache.clear()
    node = graph.node(node_id)
    assert not node.exists


def test_bound_node_equals_unbound_node_with_same_properties():
    alice_1 = Node(name="Alice")
    alice_1.bind("http://localhost:7474/db/data/node/1")
    alice_2 = Node(name="Alice")
    assert alice_1 == alice_2


def test_bound_node_equality():
    alice_1 = Node(name="Alice")
    alice_1.bind("http://localhost:7474/db/data/node/1")
    Node.cache.clear()
    alice_2 = Node(name="Alice")
    alice_2.bind(alice_1.uri)
    assert alice_1 == alice_2


def test_unbound_node_equality():
    alice_1 = Node("Person", name="Alice")
    alice_2 = Node("Person", name="Alice")
    assert alice_1 == alice_2


def test_binding_node_if_labels_not_supported_casts_to_legacy_node():
    with patch("py2neo.Graph.supports_node_labels") as mocked:
        mocked.__get__ = Mock(return_value=False)
        alice = Node(name="Alice Smith")
        assert isinstance(alice, Node)
        alice.bind("http://localhost:7474/db/data/node/1")
        assert isinstance(alice, LegacyNode)


def test_node_exists_will_raise_non_404_errors():
    with patch.object(_Resource, "get") as mocked:
        error = GraphError("bad stuff happened")
        error.response = DodgyClientError()
        mocked.side_effect = error
        alice = Node(name="Alice Smith")
        alice.bind("http://localhost:7474/db/data/node/1")
        try:
            _ = alice.exists
        except GraphError:
            assert True
        else:
            assert False


class TestAbstractNode(object):

    def test_can_create_unbound_node(self):
        alice = Node(name="Alice", age=34)
        assert isinstance(alice, Node)
        assert not alice.bound
        assert alice["name"] == "Alice"
        assert alice["age"] == 34

    def test_node_equality(self):
        alice_1 = Node(name="Alice", age=34)
        alice_2 = Node(name="Alice", age=34)
        assert alice_1 == alice_2

    def test_node_inequality(self):
        alice = Node(name="Alice", age=34)
        bob = Node(name="Bob", age=56)
        assert alice != bob

    def test_node_is_never_equal_to_none(self):
        alice = Node(name="Alice", age=34)
        assert alice != None


class TestConcreteNode(object):

    data = {
        "true": True,
        "false": False,
        "int": 42,
        "float": 3.141592653589,
        "long": 9223372036854775807 if PY3K else long("9223372036854775807"),
        "str": "This is a test",
        "unicode": UNICODE_TEST_STR,
        "boolean_list": [True, False, True, True, False],
        "int_list": [1, 1, 2, 3, 5, 8, 13, 21, 35],
        "str_list": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    }

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_can_create_concrete_node(self):
        alice, = self.graph.create({"name": "Alice", "age": 34})
        assert isinstance(alice, neo4j.Node)
        assert alice.bound
        assert alice["name"] == "Alice"
        assert alice["age"] == 34

    def test_all_property_types(self):
        data = {
            "nun": None,
            "yes": True,
            "no": False,
            "int": 42,
            "float": 3.141592653589,
            "long": 9223372036854775807 if PY3K else long("9223372036854775807"),
            "str": "This is a test",
            "unicode": UNICODE_TEST_STR,
            "boolean_list": [True, False, True, True, False],
            "int_list": [1, 1, 2, 3, 5, 8, 13, 21, 35],
            "str_list": ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
        }
        foo, = self.graph.create(data)
        for key, value in data.items():
            assert foo[key] == value

    def test_cannot_assign_oversized_long(self):
        foo, = self.graph.create({})
        try:
            if PY3K:
                foo["long"] = 9223372036854775808
            else:
                foo["long"] = long("9223372036854775808")
        except:
            assert True
        else:
            assert False

    def test_cannot_assign_mixed_list(self):
        foo, = self.graph.create({})
        try:
            foo["mixed_list"] = [42, "life", "universe", "everything"]
        except:
            assert True
        else:
            assert False

    def test_cannot_assign_dict(self):
        foo, = self.graph.create({})
        try:
            foo["dict"] = {"foo": 3, "bar": 4, "baz": 5}
        except:
            assert True
        else:
            assert False

    def test_relative_uri_of_bound_node(self):
        node, = self.graph.create({})
        relative_uri_string = node.ref
        assert node.uri.string.endswith(relative_uri_string)
        assert relative_uri_string.startswith("node/")

    def test_relative_uri_of_unbound_node(self):
        node = Node()
        try:
            _ = node.ref
        except BindError:
            assert True
        else:
            assert False


class TestNode(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.gdb = graph
        self.fred, self.wilma, self.fred_and_wilma = self.gdb.create(
            {"name": "Fred"}, {"name": "Wilma"}, (0, "REALLY LOVES", 1)
        )

    def test_get_all_relationships(self):
        rels = list(self.fred.match())
        assert len(rels) == 1
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_all_outgoing_relationships(self):
        rels = list(self.fred.match_outgoing())
        assert len(rels) == 1
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_all_incoming_relationships(self):
        #rels = self.wilma.get_relationships(neo4j.Direction.INCOMING)
        rels = list(self.wilma.match_incoming())
        assert len(rels) == 1
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_all_relationships_of_type(self):
        #rels = self.fred.get_relationships(neo4j.Direction.EITHER, "REALLY LOVES")
        rels = list(self.fred.match("REALLY LOVES"))
        assert len(rels) == 1
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_single_relationship(self):
        #rel = self.fred.get_single_relationship(neo4j.Direction.EITHER, "REALLY LOVES")
        rels = list(self.fred.match("REALLY LOVES", limit=1))
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_single_outgoing_relationship(self):
        #rel = self.fred.get_single_relationship(neo4j.Direction.OUTGOING, "REALLY LOVES")
        rels = list(self.fred.match_outgoing("REALLY LOVES", limit=1))
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_get_single_incoming_relationship(self):
        #rel = self.wilma.get_single_relationship(neo4j.Direction.INCOMING, "REALLY LOVES")
        rels = list(self.wilma.match_incoming("REALLY LOVES",
                                              start_node=self.fred, limit=1))
        assert isinstance(rels[0], neo4j.Relationship)
        assert rels[0].type == "REALLY LOVES"
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def test_explicit_is_related_to(self):
        #self.assertTrue(self.fred.is_related_to(self.wilma, neo4j.Direction.EITHER, "REALLY LOVES"))
        matched = list(self.fred.match("REALLY LOVES", other_node=self.wilma,
                                       limit=1))
        assert matched

    def test_explicit_is_related_to_outgoing(self):
        #self.assertTrue(self.fred.is_related_to(self.wilma, neo4j.Direction.OUTGOING, "REALLY LOVES"))
        matched = list(self.fred.match_outgoing("REALLY LOVES",
                                                end_node=self.wilma, limit=1))
        assert matched

    def test_explicit_is_related_to_incoming(self):
        #self.assertFalse(self.fred.is_related_to(self.wilma, neo4j.Direction.INCOMING, "REALLY LOVES"))
        matched = list(self.fred.match_incoming("REALLY LOVES",
                                                 start_node=self.wilma, limit=1))
        assert not matched

    def test_implicit_is_related_to(self):
        #self.assertTrue(self.fred.is_related_to(self.wilma))
        matches = list(self.fred.match(other_node=self.wilma))
        assert matches

    def test_is_not_related_to(self):
        homer, = self.gdb.create({"name": "Homer"})
        #self.assertFalse(self.fred.is_related_to(homer))
        matches = list(self.fred.match(other_node=homer))
        assert not matches

    def test_get_relationships_with(self):
        #rels = self.fred.get_relationships_with(self.wilma, neo4j.Direction.EITHER, "REALLY LOVES")
        rels = list(self.fred.match("REALLY LOVES", other_node=self.wilma))
        assert len(rels) == 1
        assert rels[0].start_node == self.fred
        assert rels[0].end_node == self.wilma

    def tearDown(self):
        self.gdb.delete(self.fred_and_wilma, self.fred, self.wilma)


def test_node_degree(graph):
    alice = Node("Person", name="Alice")
    bob = Node("Person", name="Bob")
    carol = Node("Person", name="Carol")
    try:
        _ = alice.degree
    except BindError:
        assert True
    else:
        assert False
    graph.create(alice)
    assert alice.degree == 0
    graph.create(Path(alice, "KNOWS", bob))
    assert alice.degree == 1
    graph.create(Path(alice, "KNOWS", carol))
    assert alice.degree == 2
    graph.create(Path(carol, "KNOWS", alice))
    assert alice.degree == 3


def test_can_merge_unsaved_changes_when_querying_node(graph):
    alice, _, _ = graph.create(Node("Person", name="Alice"), {}, (0, "KNOWS", 1))
    assert alice.properties == {"name": "Alice"}
    alice["age"] = 33
    assert alice.properties == {"name": "Alice", "age": 33}
    _ = list(alice.match_outgoing("KNOWS"))
    assert alice.properties == {"name": "Alice", "age": 33}

