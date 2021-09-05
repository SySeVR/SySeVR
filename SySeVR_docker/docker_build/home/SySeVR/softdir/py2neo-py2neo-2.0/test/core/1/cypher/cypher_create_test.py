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


from py2neo.core import Node, Relationship, Path, Rel, Rev
from py2neo.cypher import CreateStatement, CypherError


def test_statement_representation_returns_cypher(graph):
    node = Node()
    statement = CreateStatement(graph)
    statement.create(node)
    rep = repr(statement)
    assert rep == 'CREATE (_0)\nRETURN _0'


def test_empty_statement_returns_empty_tuple(graph):
    statement = CreateStatement(graph)
    created = statement.execute()
    assert created == ()


def test_cannot_create_uncastable_type(graph):
    statement = CreateStatement(graph)
    try:
        statement.create("this is not a valid thing to create")
    except TypeError:
        assert True
    else:
        assert False


def test_cannot_create_none(graph):
    statement = CreateStatement(graph)
    try:
        statement.create(None)
    except TypeError:
        assert True
    else:
        assert False


def test_can_create_naked_node(graph):
    node = Node()
    statement = CreateStatement(graph)
    statement.create(node)
    created = statement.execute()
    assert created == (node,)
    assert node.bound


def test_can_create_node_with_properties(graph):
    node = Node(name="Alice")
    statement = CreateStatement(graph)
    statement.create(node)
    created = statement.execute()
    assert created == (node,)
    assert node.bound


def test_can_create_node_with_label(graph):
    if not graph.supports_node_labels:
        return
    node = Node("Person", name="Alice")
    statement = CreateStatement(graph)
    statement.create(node)
    created = statement.execute()
    assert created == (node,)
    assert node.bound


def test_cannot_create_unique_node(graph):
    node = Node(name="Alice")
    statement = CreateStatement(graph)
    try:
        statement.create_unique(node)
    except TypeError:
        assert True
    else:
        assert False


def test_can_create_two_nodes_and_a_relationship(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(alice, "KNOWS", bob)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (alice, bob, alice_knows_bob)
    assert alice.bound
    assert bob.bound
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_can_create_two_nodes_and_a_unique_relationship(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(alice, "KNOWS", bob)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create_unique(alice_knows_bob)
    created = statement.execute()
    assert created == (alice, bob, alice_knows_bob)
    assert alice.bound
    assert bob.bound
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_can_create_two_nodes_and_a_relationship_with_properties(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(alice, Rel("KNOWS", since=1999), bob)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (alice, bob, alice_knows_bob)
    assert alice.bound
    assert bob.bound
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_can_create_two_nodes_and_a_relationship_using_pointers(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(0, "KNOWS", 1)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (alice, bob, alice_knows_bob)
    assert alice.bound
    assert bob.bound
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_cannot_use_a_pointer_that_does_not_refer_to_a_node(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(0, "KNOWS", 1)
    broken_relationship = Relationship(0, "KNOWS", 2)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create(alice_knows_bob)
    try:
        statement.create(broken_relationship)
    except ValueError:
        assert True
    else:
        assert False


def test_cannot_use_a_pointer_that_is_out_of_range(graph):
    broken_relationship = Relationship(10, "KNOWS", 11)
    statement = CreateStatement(graph)
    try:
        statement.create(broken_relationship)
    except IndexError:
        assert True
    else:
        assert False


def test_can_create_one_node_and_a_relationship_to_an_existing_node(graph):
    alice = graph.cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a")
    bob = Node(name="Bob")
    alice_knows_bob = Relationship(alice, "KNOWS", bob)
    statement = CreateStatement(graph)
    statement.create(bob)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (bob, alice_knows_bob)
    assert bob.bound
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_can_create_a_relationship_to_two_existing_nodes(graph):
    alice = graph.cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a")
    bob = graph.cypher.execute_one("CREATE (b {name:'Bob'}) RETURN b")
    alice_knows_bob = Relationship(alice, "KNOWS", bob)
    statement = CreateStatement(graph)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (alice_knows_bob,)
    assert alice_knows_bob.bound
    assert alice_knows_bob.start_node is alice
    assert alice_knows_bob.end_node is bob


def test_can_pass_entities_that_already_exist(graph):
    results = graph.cypher.stream("CREATE (a)-[ab:KNOWS]->(b) RETURN a, ab, b")
    alice, alice_knows_bob, bob = next(results)
    statement = CreateStatement(graph)
    statement.create(alice)
    statement.create(bob)
    statement.create(alice_knows_bob)
    created = statement.execute()
    assert created == (alice, bob, alice_knows_bob)


def test_a_unique_relationship_is_really_unique(graph):
    results = graph.cypher.stream("CREATE (a)-[ab:KNOWS]->(b) RETURN a, ab, b")
    alice, alice_knows_bob, bob = next(results)
    assert alice.degree == 1
    assert bob.degree == 1
    statement = CreateStatement(graph)
    statement.create_unique(Relationship(alice, "KNOWS", bob))
    statement.execute()
    assert alice.degree == 1
    assert bob.degree == 1


def test_unique_path_creation_can_pick_up_existing_entities(graph):
    results = graph.cypher.stream("CREATE (a)-[ab:KNOWS]->(b) RETURN a, ab, b")
    alice, alice_knows_bob, bob = next(results)
    statement = CreateStatement(graph)
    statement.create_unique(Relationship(alice, "KNOWS", Node()))
    created = statement.execute()
    assert created == (alice_knows_bob,)
    assert alice_knows_bob.start_node == alice
    assert alice_knows_bob.end_node == bob


def test_unique_path_not_unique_exception(graph):
    results = graph.cypher.stream("CREATE (a)-[ab:KNOWS]->(b), (a)-[:KNOWS]->(b) RETURN a, ab, b")
    alice, alice_knows_bob, bob = next(results)
    assert alice.degree == 2
    assert bob.degree == 2
    statement = CreateStatement(graph)
    statement.create_unique(Relationship(alice, "KNOWS", bob))
    try:
        statement.execute()
    except CypherError as error:
        assert error.exception == "UniquePathNotUniqueException"
        assert error.fullname in [None, "org.neo4j.cypher.UniquePathNotUniqueException"]
        assert error.statement == ("START _0n0=node({_0n0}),_0n1=node({_0n1})\n"
                                   "CREATE UNIQUE (_0n0)-[_0r0:KNOWS]->(_0n1)\n"
                                   "RETURN _0n0,_0n1,_0r0")
    else:
        assert False


def test_can_create_an_entirely_new_path(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    statement = CreateStatement(graph)
    statement.create(path)
    created = statement.execute()
    assert created == (path,)
    assert alice.bound
    assert bob.bound
    assert carol.bound
    assert dave.bound
    ab, cb, cd = path.relationships
    assert ab.start_node is alice
    assert ab.end_node is bob
    assert cb.start_node is carol
    assert cb.end_node is bob
    assert cd.start_node is carol
    assert cd.end_node is dave


def test_can_create_a_path_with_existing_nodes(graph):
    alice = graph.cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a")
    alice_id = alice._id
    bob = Node(name="Bob")
    carol = graph.cypher.execute_one("CREATE (c {name:'Carol'}) RETURN c")
    carol_id = carol._id
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    statement = CreateStatement(graph)
    statement.create(path)
    created = statement.execute()
    assert created == (path,)
    assert path.nodes[0]._id == alice_id
    assert path.nodes[2]._id == carol_id
    assert bob.bound
    assert dave.bound
    ab, cb, cd = path.relationships
    assert ab.start_node is alice
    assert ab.end_node is bob
    assert cb.start_node is carol
    assert cb.end_node is bob
    assert cd.start_node is carol
    assert cd.end_node is dave


def test_cannot_create_unique_zero_length_path(graph):
    path = Path(Node())
    statement = CreateStatement(graph)
    try:
        statement.create_unique(path)
    except ValueError:
        assert True
    else:
        assert False


def test_cannot_create_unique_path_with_no_bound_nodes(graph):
    path = Path(Node(), "KNOWS", Node())
    statement = CreateStatement(graph)
    try:
        statement.create_unique(path)
    except ValueError:
        assert True
    else:
        assert False
