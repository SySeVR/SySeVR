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
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

import pytest

from py2neo import Graph, Relationship, Rel, Rev, GraphError, ServiceRoot, BindError
from py2neo.batch import WriteBatch
from py2neo.packages.httpstream import ClientError, Resource as _Resource


class DodgyClientError(ClientError):
    status_code = 499


def test_can_get_all_relationship_types(graph):
    types = graph.relationship_types
    assert isinstance(types, frozenset)


def test_can_get_relationship_by_id_when_cached(graph):
    _, _, relationship = graph.create({}, {}, (0, "KNOWS", 1))
    got = graph.relationship(relationship._id)
    assert got is relationship


def test_can_get_relationship_by_id_when_not_cached(graph):
    _, _, relationship = graph.create({}, {}, (0, "KNOWS", 1))
    Relationship.cache.clear()
    got = graph.relationship(relationship._id)
    assert got._id == relationship._id


def test_rel_and_relationship_caches_are_thread_local(graph):
    import threading
    _, _, relationship = graph.create({}, {}, (0, "KNOWS", 1))
    assert relationship.uri in Rel.cache
    assert relationship.uri in Relationship.cache
    other_rel_cache_keys = []
    other_relationship_cache_keys = []

    def check_cache():
        other_rel_cache_keys.extend(Rel.cache.keys())
        other_relationship_cache_keys.extend(Relationship.cache.keys())

    thread = threading.Thread(target=check_cache)
    thread.start()
    thread.join()

    assert relationship.uri in Rel.cache
    assert relationship.uri in Relationship.cache
    assert relationship.uri not in other_rel_cache_keys
    assert relationship.uri not in other_relationship_cache_keys


def test_cannot_get_relationship_by_id_when_id_does_not_exist(graph):
    _, _, relationship = graph.create({}, {}, (0, "KNOWS", 1))
    rel_id = relationship._id
    graph.delete(relationship)
    Relationship.cache.clear()
    try:
        _ = graph.relationship(rel_id)
    except ValueError:
        assert True
    else:
        assert False


class TestIsolate(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        Graph.auto_sync_properties = True

    def test_can_isolate_node(self):
        posse = self.graph.create(
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Carol"},
            {"name": "Dave"},
            {"name": "Eve"},
            {"name": "Frank"},
            (0, "KNOWS", 1),
            (0, "KNOWS", 2),
            (0, "KNOWS", 3),
            (0, "KNOWS", 4),
            (2, "KNOWS", 0),
            (3, "KNOWS", 0),
            (4, "KNOWS", 0),
            (5, "KNOWS", 0),
        )
        alice = posse[0]
        friendships = list(alice.match())
        assert len(friendships) == 8
        alice.isolate()
        friendships = list(alice.match())
        assert len(friendships) == 0


class TestRelationship(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        Graph.auto_sync_properties = True

    def test_create_relationship_to(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        ab = alice.create_path("KNOWS", bob).relationships[0]
        assert ab is not None
        assert isinstance(ab, Relationship)
        assert ab.start_node == alice
        assert ab.type == "KNOWS"
        assert ab.end_node == bob

    def test_create_relationship_from(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        ba = bob.create_path("LIKES", alice).relationships[0]
        assert ba is not None
        assert isinstance(ba, Relationship)
        assert ba.start_node == bob
        assert ba.type == "LIKES"
        assert ba.end_node == alice

    def test_getting_no_relationships(self):
        alice, = self.graph.create({"name": "Alice"})
        rels = list(alice.match())
        assert rels is not None
        assert isinstance(rels, list)
        assert len(rels) == 0

    def test_get_relationship(self):
        alice, bob, ab = self.graph.create({"name": "Alice"}, {"name": "Bob"}, (0, "KNOWS", 1))
        rel = self.graph.relationship(ab._id)
        assert rel == ab

    def test_create_relationship_with_properties(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        ab = alice.create_path(("KNOWS", {"since": 1999}), bob).relationships[0]
        assert ab is not None
        assert isinstance(ab, Relationship)
        assert ab.start_node == alice
        assert ab.type == "KNOWS"
        assert ab.end_node == bob
        assert len(ab.properties) == 1
        assert ab["since"] == 1999
        assert ab.properties == {"since": 1999}
        ab["foo"] = "bar"
        assert len(ab.properties) == 2
        assert ab["foo"] == "bar"
        assert ab.properties == {"since": 1999, "foo": "bar"}
        del ab["foo"]
        assert len(ab.properties) == 1
        assert ab["since"] == 1999
        assert ab.properties == {"since": 1999}
        ab.properties.clear()
        assert len(ab.properties) == 0
        assert ab.properties == {}


class TestRelate(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        Graph.auto_sync_properties = True

    def test_relate(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        rel = alice.get_or_create_path("KNOWS", bob).relationships[0]
        assert rel is not None
        assert isinstance(rel, Relationship)
        assert rel.start_node == alice
        assert rel.type == "KNOWS"
        assert rel.end_node == bob

    def test_repeated_relate(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        rel1 = alice.get_or_create_path("KNOWS", bob).relationships[0]
        assert rel1 is not None
        assert isinstance(rel1, Relationship)
        assert rel1.start_node == alice
        assert rel1.type == "KNOWS"
        assert rel1.end_node == bob
        rel2 = alice.get_or_create_path("KNOWS", bob).relationships[0]
        assert rel1  == rel2
        rel3 = alice.get_or_create_path("KNOWS", bob).relationships[0]
        assert rel1 == rel3

    def test_relate_with_no_end_node(self):
        alice, = self.graph.create(
            {"name": "Alice"}
        )
        rel = alice.get_or_create_path("KNOWS", None).relationships[0]
        assert rel is not None
        assert isinstance(rel, Relationship)
        assert rel.start_node == alice
        assert rel.type == "KNOWS"

    def test_relate_with_data(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        rel = alice.get_or_create_path(("KNOWS", {"since": 2006}), bob).relationships[0]
        assert rel is not None
        assert isinstance(rel, Relationship)
        assert rel.start_node == alice
        assert rel.type == "KNOWS"
        assert rel.end_node == bob
        assert "since" in rel
        assert rel["since"] == 2006

    def test_relate_with_null_data(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        rel = alice.get_or_create_path(("KNOWS", {"since": 2006, "dummy": None}), bob).relationships[0]
        assert rel is not None
        assert isinstance(rel, Relationship)
        assert rel.start_node == alice
        assert rel.type == "KNOWS"
        assert rel.end_node == bob
        assert "since" in rel
        assert rel["since"] == 2006
        assert rel["dummy"] is None

    def test_repeated_relate_with_data(self):
        alice, bob = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"}
        )
        rel1 = alice.get_or_create_path(("KNOWS", {"since": 2006}), bob).relationships[0]
        assert rel1 is not None
        assert isinstance(rel1, Relationship)
        assert rel1.start_node == alice
        assert rel1.type == "KNOWS"
        assert rel1.end_node == bob
        rel2 = alice.get_or_create_path(("KNOWS", {"since": 2006}), bob).relationships[0]
        assert rel1 == rel2
        rel3 = alice.get_or_create_path(("KNOWS", {"since": 2006}), bob).relationships[0]
        assert rel1 == rel3

    # disabled test known to fail due to server issues
    #
    #def test_relate_with_list_data(self):
    #    alice, bob = self.graph.create(
    #        {"name": "Alice"}, {"name": "Bob"}
    #    )
    #    rel, = self.graph.get_or_create_relationships((alice, "LIKES", bob, {"reasons": ["looks", "wealth"]}))
    #    assert rel is not None
    #    assert isinstance(rel, Relationship)
    #    assert rel.start_node == alice
    #    self.assertEqual("LIKES", rel.type)
    #    assert rel.end_node == bob
    #    self.assertTrue("reasons" in rel)
    #    self.assertEqual("looks", rel["reasons"][0])
    #    self.assertEqual("wealth", rel["reasons"][1])

    def test_complex_relate(self):
        alice, bob, carol, dave = self.graph.create(
            {"name": "Alice"}, {"name": "Bob"},
            {"name": "Carol"}, {"name": "Dave"}
        )
        batch = WriteBatch(self.graph)
        batch.get_or_create_path(alice, ("IS~MARRIED~TO", {"since": 1996}), bob)
        #batch.get_or_create((alice, "DISLIKES", carol, {"reasons": ["youth", "beauty"]}))
        batch.get_or_create_path(alice, ("DISLIKES!", {"reason": "youth"}), carol)
        rels1 = batch.submit()
        assert rels1 is not None
        assert len(rels1) == 2
        batch = WriteBatch(self.graph)
        batch.get_or_create_path(bob, ("WORKS WITH", {"since": 2004, "company": "Megacorp"}), carol)
        #batch.get_or_create((alice, "DISLIKES", carol, {"reasons": ["youth", "beauty"]}))
        batch.get_or_create_path(alice, ("DISLIKES!", {"reason": "youth"}), carol)
        batch.get_or_create_path(bob, ("WORKS WITH", {"since": 2009, "company": "Megacorp"}), dave)
        rels2 = batch.submit()
        assert rels2 is not None
        assert len(rels2) == 3
        assert rels1[1] == rels2[1]


def test_rel_cannot_have_multiple_types():
    try:
        _ = Rel("LIKES", "HATES")
    except ValueError:
        assert True
    else:
        assert False


def test_relationship_exists_will_raise_non_404_errors(graph):
    with patch.object(_Resource, "get") as mocked:
        error = GraphError("bad stuff happened")
        error.response = DodgyClientError()
        mocked.side_effect = error
        a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
        try:
            _ = ab.exists
        except GraphError:
            assert True
        else:
            assert False


def test_type_of_bound_rel_is_immutable(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    try:
        ab.rel.type = "LIKES"
    except AttributeError:
        assert True
    else:
        assert False


def test_type_of_unbound_rel_is_mutable():
    ab = Rel("KNOWS")
    ab.type = "LIKES"
    assert ab.type == "LIKES"


def test_type_of_bound_relationship_is_immutable(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    try:
        ab.type = "LIKES"
    except AttributeError:
        assert True
    else:
        assert False


def test_type_of_unbound_relationship_is_mutable():
    ab = Relationship({}, "KNOWS", {})
    ab.type = "LIKES"
    assert ab.type == "LIKES"


def test_changing_type_of_unbound_rel_mirrors_to_pair_rev():
    rel = Rel("KNOWS")
    assert rel.pair is None
    rev = -rel
    assert rel.pair is rev
    assert rev.pair is rel
    assert rel.type == "KNOWS"
    assert rev.type == "KNOWS"
    rel.type = "LIKES"
    assert rel.type == "LIKES"
    assert rev.type == "LIKES"


def test_changing_type_of_unbound_rev_mirrors_to_pair_rel():
    rev = Rev("KNOWS")
    assert rev.pair is None
    rel = -rev
    assert rev.pair is rel
    assert rel.pair is rev
    assert rev.type == "KNOWS"
    assert rel.type == "KNOWS"
    rev.type = "LIKES"
    assert rev.type == "LIKES"
    assert rel.type == "LIKES"


def test_service_root(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    assert ab.service_root == ServiceRoot("http://localhost:7474/")
    ab.rel.unbind()
    assert ab.service_root == ServiceRoot("http://localhost:7474/")
    a.unbind()
    assert ab.service_root == ServiceRoot("http://localhost:7474/")
    b.unbind()
    try:
        _ = ab.service_root
    except BindError:
        assert True
    else:
        assert False


def test_graph(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    assert ab.graph == Graph("http://localhost:7474/db/data/")
    ab.rel.unbind()
    assert ab.graph == Graph("http://localhost:7474/db/data/")
    a.unbind()
    assert ab.graph == Graph("http://localhost:7474/db/data/")
    b.unbind()
    try:
        _ = ab.graph
    except BindError:
        assert True
    else:
        assert False


def test_rel_never_equals_none():
    rel = Rel("KNOWS")
    none = None
    assert rel != none


def test_only_one_relationship_in_a_relationship():
    rel = Relationship({}, "KNOWS", {})
    assert rel.size == 1
