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


from __future__ import unicode_literals

import logging
from uuid import uuid4

import pytest
from py2neo import neo4j


logging.basicConfig(level=logging.DEBUG)


class TestCreationAndDeletion(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_can_create_index_object_with_colon_in_name(self):
        uri = 'http://localhost:7474/db/data/index/node/foo%3Abar/{key}/{value}'
        neo4j.Index(neo4j.Node, uri)

    def test_can_delete_create_and_delete_index(self):
        try:
            self.graph.legacy.delete_index(neo4j.Node, "foo")
        except LookupError:
            pass
        foo = self.graph.legacy.get_index(neo4j.Node, "foo")
        assert foo is None
        foo = self.graph.legacy.get_or_create_index(neo4j.Node, "foo")
        assert foo is not None
        assert isinstance(foo, neo4j.Index)
        assert foo.name == "foo"
        assert foo.content_type is neo4j.Node
        self.graph.legacy.delete_index(neo4j.Node, "foo")
        foo = self.graph.legacy.get_index(neo4j.Node, "foo")
        assert foo is None

    def test_can_delete_create_and_delete_index_with_colon_in_name(self):
        try:
            self.graph.legacy.delete_index(neo4j.Node, "foo:bar")
        except LookupError:
            pass
        foo = self.graph.legacy.get_index(neo4j.Node, "foo:bar")
        assert foo is None
        foo = self.graph.legacy.get_or_create_index(neo4j.Node, "foo:bar")
        assert foo is not None
        assert isinstance(foo, neo4j.Index)
        assert foo.name == "foo:bar"
        assert foo.content_type is neo4j.Node
        self.graph.legacy.delete_index(neo4j.Node, "foo:bar")
        foo = self.graph.legacy.get_index(neo4j.Node, "foo:bar")
        assert foo is None


class TestNodeIndex(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.index = self.graph.legacy.get_or_create_index(neo4j.Node, "node_test_index")

    def test_add_existing_node_to_index(self):
        alice, = self.graph.create({"name": "Alice Smith"})
        self.index.add("surname", "Smith", alice)
        entities = self.index.get("surname", "Smith")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == alice
        self.graph.delete(alice)

    def test_add_existing_node_to_index_with_spaces_in_key_and_value(self):
        alice, = self.graph.create({"name": "Alice von Schmidt"})
        self.index.add("family name", "von Schmidt", alice)
        entities = self.index.get("family name", "von Schmidt")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == alice
        self.graph.delete(alice)

    def test_add_existing_node_to_index_with_odd_chars_in_key_and_value(self):
        alice, = self.graph.create({"name": "Alice Smith"})
        self.index.add("@!%#", "!\"$%^&*()", alice)
        entities = self.index.get("@!%#", "!\"$%^&*()")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == alice
        self.graph.delete(alice)

    def test_add_existing_node_to_index_with_slash_in_key(self):
        node, = self.graph.create({"foo": "bar"})
        key = "foo/bar"
        value = "bar"
        self.index.add(key, value, node)
        entities = self.index.get(key, value)
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == node
        self.graph.delete(node)

    def test_add_existing_node_to_index_with_slash_in_value(self):
        node, = self.graph.create({"foo": "bar"})
        key = "foo"
        value = "foo/bar"
        self.index.add(key, value, node)
        entities = self.index.get(key, value)
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == node
        self.graph.delete(node)

    def test_add_multiple_existing_nodes_to_index_under_same_key_and_value(self):
        alice, bob, carol = self.graph.create(
            {"name": "Alice Smith"},
            {"name": "Bob Smith"},
            {"name": "Carol Smith"}
        )
        self.index.add("surname", "Smith", alice)
        self.index.add("surname", "Smith", bob)
        self.index.add("surname", "Smith", carol)
        entities = self.index.get("surname", "Smith")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 3
        for entity in entities:
            assert entity in (alice, bob, carol)
        self.graph.delete(alice, bob, carol)

    def test_create_node(self):
        alice = self.index.create("surname", "Smith", {"name": "Alice Smith"})
        assert alice is not None
        assert isinstance(alice, neo4j.Node)
        assert alice["name"] == "Alice Smith"
        smiths = self.index.get("surname", "Smith")
        assert alice in smiths
        self.graph.delete(alice)

    def test_get_or_create_node(self):
        alice = self.index.get_or_create("surname", "Smith", {"name": "Alice Smith"})
        assert alice is not None
        assert isinstance(alice, neo4j.Node)
        assert alice["name"] == "Alice Smith"
        alice_id = alice._id
        for i in range(10):
            # subsequent calls return the same object as node already exists
            alice = self.index.get_or_create("surname", "Smith", {"name": "Alice Smith"})
            assert alice is not None
            assert isinstance(alice, neo4j.Node)
            assert alice["name"] == "Alice Smith"
            assert alice_id == alice._id
        self.graph.delete(alice)

    def test_create_if_none(self):
        alice = self.index.create_if_none("surname", "Smith", {"name": "Alice Smith"})
        assert alice is not None
        assert isinstance(alice, neo4j.Node)
        assert alice["name"] == "Alice Smith"
        for i in range(10):
            # subsequent calls fail as node already exists
            alice = self.index.create_if_none("surname", "Smith", {"name": "Alice Smith"})
            assert alice is None

    def test_add_node_if_none(self):
        self.graph.delete(*self.index.get("surname", "Smith"))
        alice, bob = self.graph.create(
            {"name": "Alice Smith"}, {"name": "Bob Smith"}
        )
        # add Alice to the index - this should be successful
        result = self.index.add_if_none("surname", "Smith", alice)
        assert result == alice
        entities = self.index.get("surname", "Smith")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == alice
        # add Bob to the index - this should fail as Alice is already there
        result = self.index.add_if_none("surname", "Smith", bob)
        assert result is None
        entities = self.index.get("surname", "Smith")
        assert entities is not None
        assert isinstance(entities, list)
        assert len(entities) == 1
        assert entities[0] == alice
        self.graph.delete(alice, bob)

    def test_node_index_query(self):
        red, green, blue = self.graph.create({}, {}, {})
        self.index.add("colour", "red", red)
        self.index.add("colour", "green", green)
        self.index.add("colour", "blue", blue)
        colours_containing_R = self.index.query("colour:*r*")
        assert red in colours_containing_R
        assert green in colours_containing_R
        assert blue not in colours_containing_R
        self.graph.delete(red, green, blue)

    def test_node_index_query_utf8(self):
        red, green, blue = self.graph.create({}, {}, {})
        self.index.add("colour", "красный", red)
        self.index.add("colour", "зеленый", green)
        self.index.add("colour", "синий", blue)
        colours_containing_R = self.index.query("colour:*ный*")
        assert red in colours_containing_R
        assert green in colours_containing_R
        assert blue not in colours_containing_R
        self.graph.delete(red, green, blue)


class TestRemoval(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        try:
            self.graph.legacy.delete_index(neo4j.Node, "node_removal_test_index")
        except LookupError:
            pass
        self.index = self.graph.legacy.get_or_create_index(neo4j.Node, "node_removal_test_index")
        self.fred, self.wilma, = self.graph.create(
            {"name": "Fred Flintstone"}, {"name": "Wilma Flintstone"},
        )
        self.index.add("name", "Fred", self.fred)
        self.index.add("name", "Wilma", self.wilma)
        self.index.add("name", "Flintstone", self.fred)
        self.index.add("name", "Flintstone", self.wilma)
        self.index.add("flintstones", "%", self.fred)
        self.index.add("flintstones", "%", self.wilma)

    def check(self, key, value, *entities):
        e = self.index.get(key, value)
        assert len(entities) == len(e)
        for entity in entities:
            assert entity in e

    def test_remove_key_value_entity(self):
        self.index.remove(key="name", value="Flintstone", entity=self.fred)
        self.check("name", "Fred", self.fred)
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.fred, self.wilma)

    def test_remove_key_value(self):
        self.index.remove(key="name", value="Flintstone")
        self.check("name", "Fred", self.fred)
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone")
        self.check("flintstones", "%", self.fred, self.wilma)

    def test_remove_key_entity(self):
        self.index.remove(key="name", entity=self.fred)
        self.check("name", "Fred")
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.fred, self.wilma)

    def test_remove_entity(self):
        self.index.remove(entity=self.fred)
        self.check("name", "Fred")
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.wilma)


class TestIndexedNode(object):

    def test_get_or_create_indexed_node_with_int_property(self, graph):
        fred = graph.legacy.get_or_create_indexed_node(
            index_name="person", key="name", value="Fred", properties={"level" : 1})
        assert isinstance(fred, neo4j.Node)
        assert fred["level"] == 1
        graph.delete(fred)
