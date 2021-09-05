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


import pytest

from py2neo import node, rel, Finished
from py2neo.core import Node, Relationship
from py2neo.batch import BatchError, WriteBatch, CypherJob, Batch
from py2neo.legacy import LegacyWriteBatch


class TestNodeCreation(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.batch = WriteBatch(graph)
        self.graph = graph

    def test_can_create_single_empty_node(self):
        self.batch.create(node())
        a, = self.batch.submit()
        assert isinstance(a, Node)
        assert a.properties == {}

    def test_can_create_single_node_with_streaming(self):
        self.batch.create(Node(name="Alice"))
        for result in self.batch.stream():
            assert isinstance(result, Node)
            assert result.properties == {"name": "Alice"}

    def test_can_create_multiple_nodes(self):
        self.batch.create({"name": "Alice"})
        self.batch.create(node({"name": "Bob"}))
        self.batch.create(node(name="Carol"))
        alice, bob, carol = self.batch.submit()
        assert isinstance(alice, Node)
        assert isinstance(bob, Node)
        assert isinstance(carol, Node)
        assert alice["name"] == "Alice"
        assert bob["name"] == "Bob"
        assert carol["name"] == "Carol"


class TestRelationshipCreation(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.batch = LegacyWriteBatch(graph)

    def test_can_create_relationship_with_new_nodes(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create((0, "KNOWS", 1))
        alice, bob, knows = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows.properties == {}
        self.recycling = [knows, alice, bob]

    def test_can_create_relationship_with_new_indexed_nodes(self, graph):
        try:
            graph.legacy.delete_index(Node, "people")
        except LookupError:
            pass
        try:
            graph.legacy.delete_index(Relationship, "friendships")
        except LookupError:
            pass
        self.batch.get_or_create_in_index(Node, "people", "name", "Alice", {"name": "Alice"})
        self.batch.get_or_create_in_index(Node, "people", "name", "Bob", {"name": "Bob"})
        self.batch.get_or_create_in_index(Relationship, "friendships",
                                          "names", "alice_bob", (0, "KNOWS", 1))
        #self.batch.create((0, "KNOWS", 1))
        alice, bob, knows = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows.properties == {}
        self.recycling = [knows, alice, bob]

    def test_can_create_relationship_with_existing_nodes(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        alice, bob = self.batch.submit()
        self.batch.jobs = []
        self.batch.create((alice, "KNOWS", bob))
        knows, = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows.properties == {}
        self.recycling = [knows, alice, bob]

    def test_can_create_relationship_with_existing_start_node(self):
        self.batch.create({"name": "Alice"})
        alice, = self.batch.submit()
        self.batch.jobs = []
        self.batch.create({"name": "Bob"})
        self.batch.create((alice, "KNOWS", 0))
        bob, knows = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows.properties == {}
        self.recycling = [knows, alice, bob]

    def test_can_create_relationship_with_existing_end_node(self):
        self.batch.create({"name": "Bob"})
        bob, = self.batch.submit()
        self.batch.jobs = []
        self.batch.create({"name": "Alice"})
        self.batch.create((0, "KNOWS", bob))
        alice, knows = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows.properties == {}
        self.recycling = [knows, alice, bob]

    def test_can_create_multiple_relationships(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create({"name": "Carol"})
        self.batch.create((0, "KNOWS", 1))
        self.batch.create((1, "KNOWS", 2))
        self.batch.create((2, "KNOWS", 0))
        alice, bob, carol, ab, bc, ca = self.batch.submit()
        for relationship in [ab, bc, ca]:
            assert isinstance(relationship, Relationship)
            assert relationship.type == "KNOWS"

    def test_can_create_overlapping_relationships(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create((0, "KNOWS", 1))
        self.batch.create((0, "KNOWS", 1))
        alice, bob, knows1, knows2 = self.batch.submit()
        assert isinstance(knows1, Relationship)
        assert knows1.start_node == alice
        assert knows1.type == "KNOWS"
        assert knows1.end_node == bob
        assert knows1.properties == {}
        assert isinstance(knows2, Relationship)
        assert knows2.start_node == alice
        assert knows2.type == "KNOWS"
        assert knows2.end_node == bob
        assert knows2.properties == {}
        self.recycling = [knows1, knows2, alice, bob]

    def test_can_create_relationship_with_properties(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create((0, "KNOWS", 1, {"since": 2000}))
        alice, bob, knows = self.batch.submit()
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows["since"] == 2000
        self.recycling = [knows, alice, bob]

    def test_create_function(self):
        self.batch.create(node(name="Alice"))
        self.batch.create(node(name="Bob"))
        self.batch.create(rel(0, "KNOWS", 1))
        alice, bob, ab = self.batch.submit()
        assert isinstance(alice, Node)
        assert alice["name"] == "Alice"
        assert isinstance(bob, Node)
        assert bob["name"] == "Bob"
        assert isinstance(ab, Relationship)
        assert ab.start_node == alice
        assert ab.type == "KNOWS"
        assert ab.end_node == bob
        self.recycling = [ab, alice, bob]


class TestUniqueRelationshipCreation(object):
    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.batch = WriteBatch(graph)

    def test_can_create_relationship_if_none_exists(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        alice, bob = self.batch.submit()
        self.batch.jobs = []
        self.batch.get_or_create_path(
            alice, ("KNOWS", {"since": 2000}), bob)
        path, = self.batch.submit()
        knows = path.relationships[0]
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        assert knows["since"] == 2000
        self.recycling = [knows, alice, bob]

    def test_will_get_relationship_if_one_exists(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        alice, bob = self.batch.submit()
        self.batch.jobs = []
        self.batch.get_or_create_path(
            alice, ("KNOWS", {"since": 2000}), bob)
        self.batch.get_or_create_path(
            alice, ("KNOWS", {"since": 2000}), bob)
        path1, path2 = self.batch.submit()
        assert path1 == path2

    def test_will_fail_batch_if_more_than_one_exists(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create((0, "KNOWS", 1))
        self.batch.create((0, "KNOWS", 1))
        alice, bob, k1, k2 = self.batch.submit()
        self.batch.jobs = []
        self.batch.get_or_create_path(alice, "KNOWS", bob)
        try:
            self.batch.submit()
        except BatchError as error:
            cause = error.__cause__
            assert cause.__class__.__name__ == "UniquePathNotUniqueException"
        else:
            assert False

    def test_can_create_relationship_and_start_node(self):
        self.batch.create({"name": "Bob"})
        bob, = self.batch.submit()
        self.batch.jobs = []
        self.batch.get_or_create_path(None, "KNOWS", bob)
        path, = self.batch.submit()
        knows = path.relationships[0]
        alice = knows.start_node
        assert isinstance(knows, Relationship)
        assert isinstance(alice, Node)
        assert knows.type == "KNOWS"
        assert knows.end_node == bob
        self.recycling = [knows, alice, bob]

    def test_can_create_relationship_and_end_node(self):
        self.batch.create({"name": "Alice"})
        alice, = self.batch.submit()
        self.batch.jobs = []
        self.batch.get_or_create_path(alice, "KNOWS", None)
        path, = self.batch.submit()
        knows = path.relationships[0]
        bob = knows.end_node
        assert isinstance(knows, Relationship)
        assert knows.start_node == alice
        assert knows.type == "KNOWS"
        assert isinstance(bob, Node)
        self.recycling = [knows, alice, bob]


class TestDeletion(object):
    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.batch = WriteBatch(graph)
        self.graph = graph

    def test_can_delete_relationship_and_related_nodes(self):
        self.batch.create({"name": "Alice"})
        self.batch.create({"name": "Bob"})
        self.batch.create((0, "KNOWS", 1))
        alice, bob, ab = self.batch.submit()
        assert alice.exists
        assert bob.exists
        assert ab.exists
        self.batch.jobs = []
        self.batch.delete(ab)
        self.batch.delete(alice)
        self.batch.delete(bob)
        self.batch.run()
        assert not alice.exists
        assert not bob.exists
        assert not ab.exists


class TestPropertyManagement(object):
    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.batch = WriteBatch(graph)
        self.alice, self.bob, self.friends = graph.create(
            {"name": "Alice", "surname": "Allison"},
            {"name": "Bob", "surname": "Robertson"},
            (0, "KNOWS", 1, {"since": 2000}),
        )
        self.graph = graph

    def _check_properties(self, entity, expected_properties):
        entity.pull()
        actual_properties = entity.properties
        assert len(actual_properties) == len(expected_properties)
        for key, value in expected_properties.items():
            assert key in actual_properties
            assert str(actual_properties[key]) == str(value)

    def test_can_add_new_node_property(self):
        self.batch.set_property(self.alice, "age", 33)
        self.batch.run()
        self._check_properties(self.alice, {"name": "Alice", "surname": "Allison", "age": 33})

    def test_can_overwrite_existing_node_property(self):
        self.batch.set_property(self.alice, "name", "Alison")
        self.batch.run()
        self._check_properties(self.alice, {"name": "Alison", "surname": "Allison"})

    def test_can_replace_all_node_properties(self):
        props = {"full_name": "Alice Allison", "age": 33}
        self.batch.set_properties(self.alice, props)
        self.batch.run()
        self._check_properties(self.alice, props)

    def test_can_add_delete_node_property(self):
        self.batch.delete_property(self.alice, "surname")
        self.batch.run()
        self._check_properties(self.alice, {"name": "Alice"})

    def test_can_add_delete_all_node_properties(self):
        self.batch.delete_properties(self.alice)
        self.batch.run()
        self._check_properties(self.alice, {})

    def test_can_add_new_relationship_property(self):
        self.batch.set_property(self.friends, "foo", "bar")
        self.batch.run()
        self._check_properties(self.friends, {"since": 2000, "foo": "bar"})


class TestIndexedNodeCreation(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        try:
            graph.legacy.delete_index(Node, "People")
        except LookupError:
            pass
        self.people = graph.legacy.get_or_create_index(Node, "People")
        self.batch = LegacyWriteBatch(graph)
        self.graph = graph

    def test_can_create_single_indexed_node(self):
        properties = {"name": "Alice Smith"}
        # need to execute a pair of commands as "create in index" not available
        self.batch.create(properties)
        self.batch.add_to_index(Node, self.people, "surname", "Smith", 0)
        alice, index_entry = self.batch.submit()
        assert isinstance(alice, Node)
        assert alice.properties == properties
        self.graph.delete(alice)

    def test_can_create_two_similarly_indexed_nodes(self):
        # create Alice
        alice_props = {"name": "Alice Smith"}
        # need to execute a pair of commands as "create in index" not available
        self.batch.create(alice_props)
        self.batch.add_to_index(Node, self.people, "surname", "Smith", 0)
        alice, alice_index_entry = self.batch.submit()
        assert isinstance(alice, Node)
        assert alice.properties == alice_props
        self.batch.jobs = []
        # create Bob
        bob_props = {"name": "Bob Smith"}
        # need to execute a pair of commands as "create in index" not available
        self.batch.create(bob_props)
        self.batch.add_to_index(Node, self.people, "surname", "Smith", 0)
        bob, bob_index_entry = self.batch.submit()
        assert isinstance(bob, Node)
        assert bob.properties == bob_props
        # check entries
        smiths = self.people.get("surname", "Smith")
        assert len(smiths) == 2
        assert alice in smiths
        assert bob in smiths
        # done
        self.graph.delete(alice, bob)

    def test_can_get_or_create_uniquely_indexed_node(self):
        # create Alice
        alice_props = {"name": "Alice Smith"}
        self.batch.get_or_create_in_index(Node, self.people, "surname", "Smith", alice_props)
        alice, = self.batch.submit()
        assert isinstance(alice, Node)
        assert alice.properties == alice_props
        self.batch.jobs = []
        # create Bob
        bob_props = {"name": "Bob Smith"}
        self.batch.get_or_create_in_index(Node, self.people, "surname", "Smith", bob_props)
        bob, = self.batch.submit()
        assert isinstance(bob, Node)
        assert bob.properties != bob_props
        assert bob.properties == alice_props
        assert bob == alice
        # check entries
        smiths = self.people.get("surname", "Smith")
        assert len(smiths) == 1
        assert alice in smiths
        # done
        self.graph.delete(alice, bob)


class TestIndexedNodeAddition(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        try:
            graph.legacy.delete_index(Node, "People")
        except LookupError:
            pass
        self.people = graph.legacy.get_or_create_index(Node, "People")
        self.batch = LegacyWriteBatch(graph)
        self.graph = graph

    def test_can_add_single_node(self):
        alice, = self.graph.create({"name": "Alice Smith"})
        self.batch.add_to_index(Node, self.people, "surname", "Smith", alice)
        self.batch.run()
        # check entries
        smiths = self.people.get("surname", "Smith")
        assert len(smiths) == 1
        assert alice in smiths
        # done
        self.graph.delete(alice)

    def test_can_add_two_similar_nodes(self):
        alice, bob = self.graph.create(
            {"name": "Alice Smith"}, {"name": "Bob Smith"})
        self.batch.add_to_index(Node, self.people, "surname", "Smith", alice)
        self.batch.add_to_index(Node, self.people, "surname", "Smith", bob)
        nodes = self.batch.submit()
        assert nodes[0] != nodes[1]
        # check entries
        smiths = self.people.get("surname", "Smith")
        assert len(smiths) == 2
        assert alice in smiths
        assert bob in smiths
        # done
        self.graph.delete(alice, bob)

    def test_can_add_nodes_only_if_none_exist(self):
        alice, bob = self.graph.create(
            {"name": "Alice Smith"}, {"name": "Bob Smith"})
        self.batch.get_or_add_to_index(Node, self.people, "surname", "Smith", alice)
        self.batch.get_or_add_to_index(Node, self.people, "surname", "Smith", bob)
        nodes = self.batch.submit()
        assert nodes[0] == nodes[1]
        # check entries
        smiths = self.people.get("surname", "Smith")
        assert len(smiths) == 1
        assert alice in smiths
        # done
        self.graph.delete(alice, bob)


#class TestIndexedRelationshipCreation(object):
#
#    @pytest.fixture(autouse=True)
#    def setup(self, graph):
#        try:
#            graph.delete_index(Relationship, "friendships")
#        except LookupError:
#            pass
#        self.friendships = graph.get_or_create_index(Relationship, "Friendships")
#        self.alice, self.bob = graph.create({"name": "Alice"}, {"name": "Bob"})
#        self.batch = LegacyWriteBatch(graph)
#        self.graph = graph
#
#    def test_can_create_single_indexed_relationship(self, graph):
#        self.batch.get_or_create_indexed_relationship(
#            self.friendships, "friends", "alice_&_bob",
#            self.alice, "KNOWS", self.bob)
#        rels = self.batch.submit()
#        assert len(rels) == 1
#        assert isinstance(rels[0], Relationship)
#        assert rels[0].start_node == self.alice
#        assert rels[0].type == "KNOWS"
#        assert rels[0].end_node == self.bob
#        assert rels[0].properties == {}
#        graph.delete(rels)
#        graph.delete(self.alice, self.bob)
#
#    def test_can_get_or_create_uniquely_indexed_relationship(self, graph):
#        self.batch.get_or_create_indexed_relationship(
#            self.friendships, "friends", "alice_&_bob",
#            self.alice, "KNOWS", self.bob)
#        self.batch.get_or_create_indexed_relationship(
#            self.friendships, "friends", "alice_&_bob",
#            self.alice, "KNOWS", self.bob)
#        rels = self.batch.submit()
#        assert len(rels) == 2
#        assert isinstance(rels[0], Relationship)
#        assert isinstance(rels[1], Relationship)
#        assert rels[0] == rels[1]
#        graph.delete(rels)
#        graph.delete(self.alice, self.bob)


class TestIndexedRelationshipAddition(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        try:
            graph.legacy.delete_index(Relationship, "Friendships")
        except LookupError:
            pass
        self.friendships = graph.legacy.get_or_create_index(Relationship, "Friendships")
        self.batch = LegacyWriteBatch(graph)
        self.graph = graph

    def test_can_add_single_relationship(self, graph):
        alice, bob, ab = self.graph.create({"name": "Alice"}, {"name": "Bob"}, (0, "KNOWS", 1))
        self.batch.add_to_index(Relationship, self.friendships, "friends", "alice_&_bob", ab)
        self.batch.run()
        # check entries
        rels = self.friendships.get("friends", "alice_&_bob")
        assert len(rels) == 1
        assert ab in rels
        # done
        self.recycling = [ab, alice, bob]

    def test_can_add_two_similar_relationships(self, graph):
        alice, bob, ab1, ab2 = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"},
            (0, "KNOWS", 1), (0, "KNOWS", 1))
        self.batch.add_to_index(Relationship, self.friendships, "friends", "alice_&_bob", ab1)
        self.batch.add_to_index(Relationship, self.friendships, "friends", "alice_&_bob", ab2)
        self.batch.run()
        # check entries
        entries = self.friendships.get("friends", "alice_&_bob")
        assert len(entries) == 2
        assert ab1 in entries
        assert ab2 in entries
        # done
        self.recycling = [ab1, ab2, alice, bob]

    def test_can_add_relationships_only_if_none_exist(self):
        alice, bob, ab1, ab2 = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"},
            (0, "KNOWS", 1), (0, "KNOWS", 1))
        self.batch.get_or_add_to_index(Relationship, self.friendships,
                                       "friends", "alice_&_bob", ab1)
        self.batch.get_or_add_to_index(Relationship, self.friendships,
                                       "friends", "alice_&_bob", ab2)
        results = self.batch.submit()
        assert results[0] == results[1]
        # check entries
        entries = self.friendships.get("friends", "alice_&_bob")
        assert len(entries) == 1
        assert ab1 in entries
        # done
        self.recycling = [ab1, ab2, alice, bob]


class TestIndexedNodeRemoval(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        try:
            graph.legacy.delete_index(Node, "node_removal_test_index")
        except LookupError:
            pass
        self.index = graph.legacy.get_or_create_index(Node, "node_removal_test_index")
        self.fred, self.wilma, = graph.create(
            {"name": "Fred Flintstone"}, {"name": "Wilma Flintstone"},
        )
        self.index.add("name", "Fred", self.fred)
        self.index.add("name", "Wilma", self.wilma)
        self.index.add("name", "Flintstone", self.fred)
        self.index.add("name", "Flintstone", self.wilma)
        self.index.add("flintstones", "%", self.fred)
        self.index.add("flintstones", "%", self.wilma)
        self.batch = LegacyWriteBatch(graph)

    def check(self, key, value, *entities):
        e = self.index.get(key, value)
        assert len(entities) == len(e)
        for entity in entities:
            assert entity in e

    def test_remove_key_value_entity(self):
        self.batch.remove_from_index(Node, self.index, key="name",
                                     value="Flintstone", entity=self.fred)
        self.batch.run()
        self.check("name", "Fred", self.fred)
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.fred, self.wilma)

    def test_remove_key_entity(self):
        self.batch.remove_from_index(Node, self.index, key="name", entity=self.fred)
        self.batch.run()
        self.check("name", "Fred")
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.fred, self.wilma)

    def test_remove_entity(self):
        self.batch.remove_from_index(Node, self.index, entity=self.fred)
        self.batch.run()
        self.check("name", "Fred")
        self.check("name", "Wilma", self.wilma)
        self.check("name", "Flintstone", self.wilma)
        self.check("flintstones", "%", self.wilma)


def test_can_use_return_values_as_references(graph):
    batch = WriteBatch(graph)
    a = batch.create(node(name="Alice"))
    b = batch.create(node(name="Bob"))
    batch.create(rel(a, "KNOWS", b))
    results = batch.submit()
    ab = results[2]
    assert isinstance(ab, Relationship)
    assert ab.start_node["name"] == "Alice"
    assert ab.end_node["name"] == "Bob"


def test_can_handle_json_response_with_no_content(graph):
    # This example might fail if the server bug is fixed that returns
    # a 200 response with application/json content-type and no content.
    batch = WriteBatch(graph)
    batch.create((0, "KNOWS", 1))
    results = batch.submit()
    assert results == []


def test_cypher_job_with_bad_syntax(graph):
    batch = WriteBatch(graph)
    batch.append(CypherJob("X"))
    try:
        batch.submit()
    except BatchError as error:
        assert error.batch is batch
        assert error.job_id == 0
        assert error.status_code == 400
        assert error.uri == "cypher"
    else:
        assert False


def test_cypher_job_with_non_existent_node_id(graph):
    node = Node()
    graph.create(node)
    node_id = node._id
    graph.delete(node)
    batch = WriteBatch(graph)
    batch.append(CypherJob("START n=node({N}) RETURN n", {"N": node_id}))
    try:
        batch.submit()
    except BatchError as error:
        assert error.batch is batch
        assert error.job_id == 0
        assert error.status_code == 400
        assert error.uri == "cypher"
    else:
        assert False


def test_cannot_resubmit_finished_job(graph):
    batch = Batch(graph)
    batch.append(CypherJob("CREATE (a)"))
    graph.batch.submit(batch)
    try:
        graph.batch.submit(batch)
    except Finished:
        assert True
    else:
        assert False
