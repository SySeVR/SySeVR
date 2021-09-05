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

import pytest

from py2neo import node
from py2neo.core import authenticate, _get_headers, Graph, Node, Relationship


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    level=logging.DEBUG,
)


def test_can_use_graph_if_no_trailing_slash_supplied(graph):
    alice, = graph.create(node(name="Alice"))
    assert isinstance(alice, Node)
    assert alice["name"] == "Alice"


def test_authentication_adds_the_correct_header():
    from py2neo.core import _headers
    _headers.clear()
    _headers.update({None: [("X-Stream", "true")]})
    authenticate("localhost:7474", "arthur", "excalibur")
    headers = _get_headers("localhost:7474")
    assert headers['Authorization'] == 'Basic YXJ0aHVyOmV4Y2FsaWJ1cg=='


def test_can_add_same_header_twice():
    from py2neo.core import _headers
    _headers.clear()
    _headers.update({None: [("X-Stream", "true")]})
    authenticate("localhost:7474", "arthur", "excalibur")
    authenticate("localhost:7474", "arthur", "excalibur")
    headers = _get_headers("localhost:7474")
    assert headers['Authorization'] == 'Basic YXJ0aHVyOmV4Y2FsaWJ1cg=='


def test_implicit_authentication_through_resource_constructor():
    from py2neo.core import _headers, Resource
    _headers.clear()
    _headers.update({None: [("X-Stream", "true")]})
    resource = Resource("http://arthur:excalibur@localhost:7474/")
    headers = _get_headers("localhost:7474")
    assert headers['Authorization'] == 'Basic YXJ0aHVyOmV4Y2FsaWJ1cg=='
    assert resource.headers['Authorization'] == 'Basic YXJ0aHVyOmV4Y2FsaWJ1cg=='


class TestGraph(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_can_get_same_instance(self):
        graph_1 = Graph()
        graph_2 = Graph()
        assert graph_1 is graph_2

    def test_neo4j_version_format(self):
        version = self.graph.neo4j_version
        print(version)
        assert isinstance(version, tuple)
        assert 3 <= len(version) <= 4
        assert isinstance(version[0], int)
        assert isinstance(version[1], int)
        assert isinstance(version[2], int)

    def test_create_single_empty_node(self):
        a, = self.graph.create({})

    def test_get_node_by_id(self):
        a1, = self.graph.create({"foo": "bar"})
        a2 = self.graph.node(a1._id)
        assert a1 == a2

    def test_create_node_with_property_dict(self):
        node, = self.graph.create({"foo": "bar"})
        assert node["foo"] == "bar"

    def test_create_node_with_mixed_property_types(self):
        node, = self.graph.create(
            {"number": 13, "foo": "bar", "true": False, "fish": "chips"}
        )
        assert len(node.properties) == 4
        assert node["fish"] == "chips"
        assert node["foo"] == "bar"
        assert node["number"] == 13
        assert not node["true"]

    def test_create_node_with_null_properties(self):
        node, = self.graph.create({"foo": "bar", "no-foo": None})
        assert node["foo"] == "bar"
        assert node["no-foo"] is None

    def test_create_multiple_nodes(self):
        nodes = self.graph.create(
                {},
                {"foo": "bar"},
                {"number": 42, "foo": "baz", "true": True},
                {"fish": ["cod", "haddock", "plaice"], "number": 109}
        )
        assert len(nodes) == 4
        assert len(nodes[0].properties) == 0
        assert len(nodes[1].properties) == 1
        assert nodes[1]["foo"] == "bar"
        assert len(nodes[2].properties) == 3
        assert nodes[2]["number"] == 42
        assert nodes[2]["foo"] == "baz"
        assert nodes[2]["true"]
        assert len(nodes[3].properties) == 2
        assert nodes[3]["fish"][0] == "cod"
        assert nodes[3]["fish"][1] == "haddock"
        assert nodes[3]["fish"][2] == "plaice"
        assert nodes[3]["number"] == 109

    def test_batch_pull_and_check_properties(self):
        nodes = self.graph.create(
            {},
            {"foo": "bar"},
            {"number": 42, "foo": "baz", "true": True},
            {"fish": ["cod", "haddock", "plaice"], "number": 109}
        )
        self.graph.pull(*nodes)
        props = [n.properties for n in nodes]
        assert len(props) == 4
        assert len(props[0]) == 0
        assert len(props[1]) == 1
        assert props[1]["foo"] == "bar"
        assert len(props[2]) == 3
        assert props[2]["number"] == 42
        assert props[2]["foo"] == "baz"
        assert props[2]["true"]
        assert len(props[3]) == 2
        assert props[3]["fish"][0] == "cod"
        assert props[3]["fish"][1] == "haddock"
        assert props[3]["fish"][2] == "plaice"
        assert props[3]["number"] == 109


class TestNewCreate(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_can_create_single_node(self):
        results = self.graph.create(
            {"name": "Alice"}
        )
        assert results is not None
        assert len(results) == 1
        assert isinstance(results[0], Node)
        assert "name" in results[0]
        assert results[0]["name"] == "Alice"

    def test_can_create_simple_graph(self):
        results = self.graph.create(
            {"name": "Alice"},
            {"name": "Bob"},
            (0, "KNOWS", 1)
        )
        assert results is not None
        assert len(results) == 3
        assert isinstance(results[0], Node)
        assert "name" in results[0]
        assert results[0]["name"] == "Alice"
        assert isinstance(results[1], Node)
        assert "name" in results[1]
        assert results[1]["name"] == "Bob"
        assert isinstance(results[2], Relationship)
        assert results[2].type == "KNOWS"
        assert results[2].start_node == results[0]
        assert results[2].end_node == results[1]

    def test_can_create_simple_graph_with_rel_data(self):
        results = self.graph.create(
            {"name": "Alice"},
            {"name": "Bob"},
            (0, "KNOWS", 1, {"since": 1996})
        )
        assert results is not None
        assert len(results) == 3
        assert isinstance(results[0], Node)
        assert "name" in results[0]
        assert results[0]["name"] == "Alice"
        assert isinstance(results[1], Node)
        assert "name" in results[1]
        assert results[1]["name"] == "Bob"
        assert isinstance(results[2], Relationship)
        assert results[2].type == "KNOWS"
        assert results[2].start_node == results[0]
        assert results[2].end_node == results[1]
        assert "since" in results[2]
        assert results[2]["since"] == 1996

    def test_can_create_graph_against_existing_node(self):
        ref_node, = self.graph.create({})
        results = self.graph.create(
            {"name": "Alice"},
            (ref_node, "PERSON", 0)
        )
        assert results is not None
        assert len(results) == 2
        assert isinstance(results[0], Node)
        assert "name" in results[0]
        assert results[0]["name"] == "Alice"
        assert isinstance(results[1], Relationship)
        assert results[1].type == "PERSON"
        assert results[1].start_node == ref_node
        assert results[1].end_node == results[0]
        self.graph.delete(results[1], results[0], ref_node)

    def test_fails_on_bad_reference(self):
        with pytest.raises(Exception):
            self.graph.create({"name": "Alice"}, (0, "KNOWS", 1))

    def test_can_create_big_graph(self):
        size = 40
        nodes = [
            {"number": i}
            for i in range(size)
        ]
        results = self.graph.create(*nodes)
        assert results is not None
        assert len(results) == size
        for i in range(size):
            assert isinstance(results[i], Node)


class TestMultipleNode(object):

    flintstones = [
        {"name": "Fred"},
        {"name": "Wilma"},
        {"name": "Barney"},
        {"name": "Betty"}
    ]

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.ref_node, = self.graph.create({})
        self.nodes = self.graph.create(*self.flintstones)

    def test_is_created(self):
        assert self.nodes is not None
        assert len(self.nodes) == len(self.flintstones)

    def test_has_correct_properties(self):
        assert [
            node.properties
            for node in self.nodes
        ] == self.flintstones

    def test_create_relationships(self):
        rels = self.graph.create(*[
            (self.ref_node, "FLINTSTONE", node)
            for node in self.nodes
        ])
        self.graph.delete(*rels)
        assert len(self.nodes) == len(rels)

    def tearDown(self):
        self.graph.delete(*self.nodes)
        self.graph.delete(self.ref_node)
