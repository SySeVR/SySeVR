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


from py2neo import Node, Rel, Path, Relationship


def raises(error_, func_, *args, **kwargs):
    try:
        func_(*args, **kwargs)
    except error_:
        return True
    else:
        return False


def test_minimal_node_hydrate():
    dehydrated = {
        "self": "http://localhost:7474/db/data/node/0",
    }
    hydrated = Node.hydrate(dehydrated)
    assert isinstance(hydrated, Node)
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_node_hydrate_with_properties():
    dehydrated = {
        "self": "http://localhost:7474/db/data/node/0",
        "data": {
            "name": "Alice",
            "age": 33,
        },
    }
    hydrated = Node.hydrate(dehydrated)
    assert isinstance(hydrated, Node)
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_full_node_hydrate_without_labels():
    dehydrated = {
        "extensions": {
        },
        "paged_traverse": "http://localhost:7474/db/data/node/0/paged/traverse/{returnType}{?pageSize,leaseTime}",
        "labels": "http://localhost:7474/db/data/node/0/labels",
        "outgoing_relationships": "http://localhost:7474/db/data/node/0/relationships/out",
        "traverse": "http://localhost:7474/db/data/node/0/traverse/{returnType}",
        "all_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/all/{-list|&|types}",
        "property": "http://localhost:7474/db/data/node/0/properties/{key}",
        "all_relationships": "http://localhost:7474/db/data/node/0/relationships/all",
        "self": "http://localhost:7474/db/data/node/0",
        "outgoing_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/out/{-list|&|types}",
        "properties": "http://localhost:7474/db/data/node/0/properties",
        "incoming_relationships": "http://localhost:7474/db/data/node/0/relationships/in",
        "incoming_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/in/{-list|&|types}",
        "create_relationship": "http://localhost:7474/db/data/node/0/relationships",
        "data": {
            "name": "Alice",
            "age": 33,
        },
    }
    hydrated = Node.hydrate(dehydrated)
    assert isinstance(hydrated, Node)
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_full_node_hydrate_with_labels():
    dehydrated = {
        "extensions": {
        },
        "paged_traverse": "http://localhost:7474/db/data/node/0/paged/traverse/{returnType}{?pageSize,leaseTime}",
        "labels": "http://localhost:7474/db/data/node/0/labels",
        "outgoing_relationships": "http://localhost:7474/db/data/node/0/relationships/out",
        "traverse": "http://localhost:7474/db/data/node/0/traverse/{returnType}",
        "all_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/all/{-list|&|types}",
        "property": "http://localhost:7474/db/data/node/0/properties/{key}",
        "all_relationships": "http://localhost:7474/db/data/node/0/relationships/all",
        "self": "http://localhost:7474/db/data/node/0",
        "outgoing_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/out/{-list|&|types}",
        "properties": "http://localhost:7474/db/data/node/0/properties",
        "incoming_relationships": "http://localhost:7474/db/data/node/0/relationships/in",
        "incoming_typed_relationships": "http://localhost:7474/db/data/node/0/relationships/in/{-list|&|types}",
        "create_relationship": "http://localhost:7474/db/data/node/0/relationships",
        "data": {
            "name": "Alice",
            "age": 33,
        },
        "metadata": {
            "labels": ["Person", "Employee"],
        },
    }
    hydrated = Node.hydrate(dehydrated)
    assert isinstance(hydrated, Node)
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.labels == set(dehydrated["metadata"]["labels"])
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_minimal_rel_hydrate():
    dehydrated = {
        "self": "http://localhost:7474/db/data/relationship/11",
    }
    hydrated = Rel.hydrate(dehydrated)
    assert isinstance(hydrated, Rel)
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_rel_hydrate_with_type():
    dehydrated = {
        "self": "http://localhost:7474/db/data/relationship/11",
        "type": "KNOWS",
    }
    hydrated = Rel.hydrate(dehydrated)
    assert isinstance(hydrated, Rel)
    assert hydrated.type == dehydrated["type"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_rel_hydrate_with_properties():
    dehydrated = {
        "self": "http://localhost:7474/db/data/relationship/11",
        "data": {
            "since": 1999,
        },
    }
    hydrated = Rel.hydrate(dehydrated)
    assert isinstance(hydrated, Rel)
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_rel_hydrate_with_type_and_properties():
    dehydrated = {
        "self": "http://localhost:7474/db/data/relationship/11",
        "type": "KNOWS",
        "data": {
            "since": 1999,
        },
    }
    hydrated = Rel.hydrate(dehydrated)
    assert isinstance(hydrated, Rel)
    assert hydrated.type == dehydrated["type"]
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_full_rel_hydrate():
    dehydrated = {
        "extensions": {
        },
        "start": "http://localhost:7474/db/data/node/23",
        "property": "http://localhost:7474/db/data/relationship/11/properties/{key}",
        "self": "http://localhost:7474/db/data/relationship/11",
        "properties": "http://localhost:7474/db/data/relationship/11/properties",
        "type": "KNOWS",
        "end": "http://localhost:7474/db/data/node/22",
        "data": {
            "since": 1999,
        },
    }
    hydrated = Rel.hydrate(dehydrated)
    assert isinstance(hydrated, Rel)
    assert hydrated.type == dehydrated["type"]
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]


def test_full_relationship_hydrate():
    dehydrated = {
        "extensions": {
        },
        "start": "http://localhost:7474/db/data/node/23",
        "property": "http://localhost:7474/db/data/relationship/11/properties/{key}",
        "self": "http://localhost:7474/db/data/relationship/11",
        "properties": "http://localhost:7474/db/data/relationship/11/properties",
        "type": "KNOWS",
        "end": "http://localhost:7474/db/data/node/22",
        "data": {
            "since": 1999,
        },
    }
    hydrated = Relationship.hydrate(dehydrated)
    assert isinstance(hydrated, Relationship)
    assert hydrated.type == dehydrated["type"]
    assert hydrated.properties == dehydrated["data"]
    assert hydrated.bound
    assert hydrated.resource.uri == dehydrated["self"]
