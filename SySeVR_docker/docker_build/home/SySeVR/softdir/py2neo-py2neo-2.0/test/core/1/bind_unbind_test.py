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

from py2neo.core import Resource, Node, Rel, Rev, Relationship, Service, Path
from py2neo.error import BindError


def test_can_create_bindable_with_initial_uri():
    uri = "http://localhost:7474/db/data/node/1"
    bindable = Service()
    bindable.bind(uri)
    assert bindable.bound
    assert bindable.uri == uri


def test_can_create_bindable_with_initial_uri_and_metadata():
    uri = "http://localhost:7474/db/data/node/1"
    metadata = {"foo": "bar"}
    bindable = Service()
    bindable.bind(uri, metadata)
    assert bindable.bound
    assert bindable.uri == uri
    assert bindable.resource.metadata == metadata


def test_can_create_bindable_with_initial_uri_template():
    uri = "http://localhost:7474/db/data/node/{node_id}"
    bindable = Service()
    bindable.bind(uri)
    assert bindable.bound
    assert bindable.uri == uri


def test_cannot_create_bindable_with_initial_uri_template_and_metadata():
    uri = "http://localhost:7474/db/data/node/{node_id}"
    metadata = {"foo": "bar"}
    service = Service()
    try:
        service.bind(uri, metadata)
    except ValueError:
        assert True
    else:
        assert False


def test_default_state_for_node_is_unbound():
    node = Node()
    assert not node.bound
    with pytest.raises(BindError):
        _ = node.resource


def test_bound_path_is_bound(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    graph.create(path)
    assert path.bound


def test_unbound_path_is_not_bound():
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    assert not path.bound


def test_can_bind_node_to_resource():
    uri = "http://localhost:7474/db/data/node/1"
    node = Node()
    node.bind(uri)
    assert node.bound
    assert isinstance(node.resource, Resource)
    assert node.resource.uri == uri
    node.unbind()
    assert not node.bound
    with pytest.raises(BindError):
        _ = node.resource


def test_can_bind_rel_to_resource():
    uri = "http://localhost:7474/db/relationship/1"
    rel = Rel()
    rel.bind(uri)
    assert rel.bound
    assert isinstance(rel.resource, Resource)
    assert rel.resource.uri == uri
    rel.unbind()
    assert not rel.bound
    with pytest.raises(BindError):
        _ = rel.resource


def test_can_bind_rev_to_resource():
    uri = "http://localhost:7474/db/relationship/1"
    rel = Rev()
    rel.bind(uri)
    assert rel.bound
    assert isinstance(rel.resource, Resource)
    assert rel.resource.uri == uri
    rel.unbind()
    assert not rel.bound
    with pytest.raises(BindError):
        _ = rel.resource


def test_can_bind_relationship_to_resource():
    uri = "http://localhost:7474/db/relationship/1"
    metadata = {
        "start": "http://localhost:7474/db/node/1",
        "end": "http://localhost:7474/db/node/2",
    }
    relationship = Relationship({}, "", {})
    # Pass in metadata to avoid callback to server
    relationship.bind(uri, metadata=metadata)
    assert relationship.bound
    assert isinstance(relationship.resource, Resource)
    assert relationship.resource.uri == uri
    relationship.unbind()
    assert not relationship.bound
    with pytest.raises(BindError):
        _ = relationship.resource


def test_can_unbind_node_if_not_cached(graph):
    node, = graph.create({})
    Node.cache.clear()
    node.unbind()
    assert not node.bound


def test_can_unbind_rel_if_not_cached(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    Rel.cache.clear()
    ab.rel.unbind()
    assert not ab.bound


def test_can_unbind_relationship_if_not_cached(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    Relationship.cache.clear()
    ab.unbind()
    assert not ab.bound


def test_can_unbind_relationship_with_already_unbound_nodes(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    a.unbind()
    b.unbind()
    assert not a.bound
    assert not b.bound
    ab.unbind()
    assert not ab.bound


def test_can_unbind_bound_path(graph):
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    graph.create(path)
    path.unbind()
    assert not path.bound


def test_can_unbind_unbound_path_without_error():
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    dave = Node(name="Dave")
    path = Path(alice, "LOVES", bob, Rev("HATES"), carol, "KNOWS", dave)
    path.unbind()
    assert not path.bound


def test_unbinding_rel_also_unbinds_rev(graph):
    a, b, ab = graph.create({}, {}, (0, "KNOWS", 1))
    rel = ab.rel
    assert rel.pair is None
    rev = -rel
    assert rel.pair is rev
    assert rev.pair is rel
    assert rel.bound
    assert rev.bound
    assert rel.resource is rev.resource
    rel.unbind()
    assert not rel.bound
    assert not rev.bound


def test_unbinding_rev_also_unbinds_rel(graph):
    a, b, ab = graph.create({}, {}, (0, Rev("KNOWS"), 1))
    rev = ab.rel
    #assert rev.pair is None
    rel = -rev
    assert rev.pair is rel
    assert rel.pair is rev
    assert rev.bound
    assert rel.bound
    assert rev.resource is rel.resource
    rev.unbind()
    assert not rev.bound
    assert not rel.bound
