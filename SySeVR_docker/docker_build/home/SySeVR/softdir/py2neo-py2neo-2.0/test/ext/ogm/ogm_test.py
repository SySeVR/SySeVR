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

from py2neo import Graph, Node
from py2neo.ext.ogm import Store


class Person(object):

    __primarykey__ = "email"

    def __init__(self, email=None, name=None, age=None):
        self.email = email
        self.name = name
        self.age = age

    def __eq__(self, other):
        return self.email == other.email

    def __ne__(self, other):
        return self.email != other.email

    def __repr__(self):
        return "{0} <{1}>".format(self.name, self.email)


class TestExampleCode(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_can_execute_example_code(self):

        class Person(object):

            def __init__(self, email=None, name=None, age=None):
                self.email = email
                self.name = name
                self.age = age

            def __str__(self):
                return self.name

        graph = Graph()
        store = Store(graph)

        alice = Person("alice@example.com", "Alice", 34)
        store.save_unique("People", "email", alice.email, alice)

        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        store.relate(alice, "LIKES", bob)
        store.relate(alice, "LIKES", carol)
        store.save(alice)

        friends = store.load_related(alice, "LIKES", Person)
        print("Alice likes {0}".format(" and ".join(str(f) for f in friends)))


class TestRelate(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_relate_to_other_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        assert hasattr(alice, "__rel__")
        assert isinstance(alice.__rel__, dict)
        assert "LIKES" in alice.__rel__
        assert alice.__rel__["LIKES"] == [({}, bob)]

    def test_can_relate_to_other_object_with_properties(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob, {"since": 1999})
        assert hasattr(alice, "__rel__")
        assert isinstance(alice.__rel__, dict)
        assert "LIKES" in alice.__rel__
        assert alice.__rel__["LIKES"] == [({"since": 1999}, bob)]


class TestSeparate(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_separate_from_other_objects(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.separate(alice, "LIKES", carol)
        assert alice.__rel__["LIKES"] == [({}, bob)]
        self.store.separate(alice, "LIKES", bob)
        assert alice.__rel__["LIKES"] == []

    def test_can_separate_without_previous_relate(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        assert not hasattr(alice, "__rel__")
        self.store.separate(alice, "LIKES", bob)
        assert not hasattr(alice, "__rel__")

    def test_nothing_happens_if_unknown_rel_type_supplied(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        self.store.separate(alice, "DISLIKES", bob)
        assert alice.__rel__["LIKES"] == [({}, bob)]

    def test_nothing_happens_if_unknown_endpoint_supplied(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.separate(alice, "LIKES", carol)
        assert alice.__rel__["LIKES"] == [({}, bob)]


class TestLoadRelated(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_load_single_related_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        self.store.relate(alice, "LIKES", bob)
        self.store.save(alice)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob]

    def test_can_load_multiple_related_objects(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.save(alice)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob, carol]

    def test_can_load_related_objects_among_other_relationships(self):
        alice = Person("alice@example.com", "Alice", 34)
        bob = Person("bob@example.org", "Bob", 66)
        carol = Person("carol@example.net", "Carol", 42)
        dave = Person("dave@example.co.uk", "Dave", 18)
        self.store.relate(alice, "LIKES", bob)
        self.store.relate(alice, "LIKES", carol)
        self.store.relate(alice, "DISLIKES", dave)
        self.store.save(alice)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == [bob, carol]
        enemies = self.store.load_related(alice, "DISLIKES", Person)
        assert enemies == [dave]

    def test_can_load_related_when_never_related(self):
        alice = Person("alice@example.com", "Alice", 34)
        friends = self.store.load_related(alice, "LIKES", Person)
        assert friends == []


class TestLoad(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_load(self):
        alice_node, = self.graph.create({
            "email": "alice@example.com",
            "name": "Alice",
            "age": 34,
        })
        alice = self.store.load(Person, alice_node)
        assert alice.email == "alice@example.com"
        assert alice.name == "Alice"
        assert alice.age == 34


class TestLoadIndexed(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        try:
            self.graph.legacy.delete_index(Node, "People")
        except LookupError:
            pass
        self.store = Store(self.graph)

    def test_can_load(self):
        people = self.graph.legacy.get_or_create_index(Node, "People")
        alice_node, bob_node = self.graph.create({
            "email": "alice@example.com",
            "name": "Alice Smith",
            "age": 34,
        }, {
            "email": "bob@example.org",
            "name": "Bob Smith",
            "age": 66,
        })
        people.add("family_name", "Smith", alice_node)
        people.add("family_name", "Smith", bob_node)
        smiths = self.store.load_indexed("People", "family_name", "Smith", Person)
        assert len(smiths) == 2
        for i, smith in enumerate(smiths):
            assert smiths[i].email in ("alice@example.com", "bob@example.org")
            assert smiths[i].name in ("Alice Smith", "Bob Smith")
            assert smiths[i].age in (34, 66)


class TestLoadUnique(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        try:
            self.graph.legacy.delete_index(Node, "People")
        except LookupError:
            pass
        self.graph.legacy.get_or_create_index(Node, "People")
        self.store = Store(self.graph)

    def test_can_load_simple_object(self):
        alice_node = self.graph.legacy.get_or_create_indexed_node(
            "People", "email", "alice@example.com", {
                "email": "alice@example.com",
                "name": "Alice Allison",
                "age": 34,
            }
        )
        alice = self.store.load_unique("People", "email", "alice@example.com", Person)
        assert isinstance(alice, Person)
        assert hasattr(alice, "__node__")
        assert alice.__node__ == alice_node
        assert hasattr(alice, "__rel__")
        assert alice.__rel__ == {}
        assert alice.email == "alice@example.com"
        assert alice.name == "Alice Allison"
        assert alice.age == 34

    def test_can_load_object_with_relationships(self):
        alice_node = self.graph.legacy.get_or_create_indexed_node(
            "People", "email", "alice@example.com", {
                "email": "alice@example.com",
                "name": "Alice Allison",
                "age": 34,
            }
        )
        path = alice_node.create_path("LIKES", {"name": "Bob Robertson"})
        bob_node = path.nodes[1]
        alice = self.store.load_unique("People", "email", "alice@example.com", Person)
        assert isinstance(alice, Person)
        assert hasattr(alice, "__node__")
        assert alice.__node__ == alice_node
        assert hasattr(alice, "__rel__")
        assert alice.__rel__ == {
            "LIKES": [({}, bob_node)],
        }
        assert alice.email == "alice@example.com"
        assert alice.name == "Alice Allison"
        assert alice.age == 34
        friends = self.store.load_related(alice, "LIKES", Person)
        assert isinstance(friends, list)
        assert len(friends) == 1
        friend = friends[0]
        assert isinstance(friend, Person)
        assert friend.__node__ == bob_node
        enemies = self.store.load_related(alice, "DISLIKES", Person)
        assert isinstance(enemies, list)
        assert len(enemies) == 0

    def test_will_not_load_when_none_exists(self):
        alice = self.store.load_unique("People", "email", "alice@example.com", Person)
        assert alice is None


class TestReload(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_reload(self):
        alice = Person("alice@example.com", "Alice", 34)
        self.store.save_unique("People", "email", "alice@example.com", alice)
        assert alice.__node__["name"] == "Alice"
        assert alice.__node__["age"] == 34
        alice.__node__["name"] = "Alice Smith"
        alice.__node__["age"] = 35
        alice.__node__.push()
        self.store.reload(alice)
        assert alice.name == "Alice Smith"
        assert alice.age == 35


class TestSave(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_save_simple_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        assert not self.store.is_saved(alice)
        self.store.save_unique("People", "email", "alice@example.com", alice)
        assert self.store.is_saved(alice)
        assert alice.__node__["name"] == "Alice"
        assert alice.__node__["age"] == 34
        alice.name = "Alice Smith"
        alice.age = 35
        self.store.save(alice)
        assert alice.__node__["name"] == "Alice Smith"
        assert alice.__node__["age"] == 35


class TestSaveIndexed(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        try:
            self.graph.legacy.delete_index(Node, "People")
        except LookupError:
            pass
        self.store = Store(self.graph)

    def test_can_save(self):
        alice = Person("alice@example.com", "Alice Smith", 34)
        bob = Person("bob@example.org", "Bob Smith", 66)
        self.store.save_indexed("People", "family_name", "Smith", alice, bob)
        people = self.graph.legacy.get_index(Node, "People")
        smiths = people.get("family_name", "Smith")
        assert len(smiths) == 2
        assert alice.__node__ in smiths
        assert bob.__node__ in smiths
        carol = Person("carol@example.net", "Carol Smith", 42)
        self.store.save_indexed("People", "family_name", "Smith", carol)
        smiths = people.get("family_name", "Smith")
        assert len(smiths) == 3
        assert alice.__node__ in smiths
        assert bob.__node__ in smiths
        assert carol.__node__ in smiths


class TestSaveUnique(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_save_simple_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        self.store.save_unique("People", "email", "alice@example.com", alice)
        assert hasattr(alice, "__node__")
        assert isinstance(alice.__node__, Node)
        assert alice.__node__ == self.graph.legacy.get_indexed_node(
            "People", "email", "alice@example.com")

    def test_can_save_object_with_rels(self):
        alice = Person("alice@example.com", "Alice Allison", 34)
        bob_node, carol_node = self.graph.create(
            {"name": "Bob"},
            {"name": "Carol"},
        )
        alice.__rel__ = {"KNOWS": [({}, bob_node)]}
        self.store.save_unique("People", "email", "alice@example.com", alice)
        assert hasattr(alice, "__node__")
        assert isinstance(alice.__node__, Node)
        assert alice.__node__ == self.graph.legacy.get_indexed_node(
            "People", "email", "alice@example.com")
        friend_rels = list(alice.__node__.match_outgoing("KNOWS"))
        assert len(friend_rels) == 1
        assert bob_node in (rel.end_node for rel in friend_rels)
        alice.__rel__ = {"KNOWS": [({}, bob_node), ({}, carol_node)]}
        self.store.save_unique("People", "email", "alice@example.com", alice)
        friend_rels = list(alice.__node__.match_outgoing("KNOWS"))
        assert len(friend_rels) == 2
        assert bob_node in (rel.end_node for rel in friend_rels)
        assert carol_node in (rel.end_node for rel in friend_rels)


class TestDelete(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        self.store = Store(self.graph)

    def test_can_delete_object(self):
        alice = Person("alice@example.com", "Alice", 34)
        self.store.save_unique("People", "email", "alice@example.com", alice)
        node = alice.__node__
        assert node.exists
        self.store.delete(alice)
        assert not node.exists

