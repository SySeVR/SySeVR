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


import sys

from py2neo.cypher.core import RecordProducer


def test_record_field_access(graph):
    statement = "CREATE (a {name:'Alice',age:33}) RETURN a,a.name as name,a.age as age"
    for record in graph.cypher.stream(statement):
        alice = record.a
        assert record.name == alice.properties["name"]
        assert record.age == alice.properties["age"]
        assert record[1] == alice.properties["name"]
        assert record[2] == alice.properties["age"]
        assert record["name"] == alice.properties["name"]
        assert record["age"] == alice.properties["age"]
        try:
            _ = record[object()]
        except LookupError:
            assert True
        else:
            assert False


def test_record_representation(graph):
    statement = "CREATE (a {name:'Alice',age:33}) RETURN a,a.name,a.age"
    for record in graph.cypher.stream(statement):
        assert repr(record)


def test_producer_representation():
    producer = RecordProducer(["apple", "banana", "carrot"])
    assert repr(producer)


def test_producer_length():
    producer = RecordProducer(["apple", "banana", "carrot"])
    assert len(producer) == 3


def test_record_equality(graph):
    if graph.neo4j_version < (2,):
        return
    statement = "MERGE (a {name:'Superfly',age:55}) RETURN a,a.name,a.age"
    results = graph.cypher.execute(statement)
    r1 = results[0]
    results = graph.cypher.execute(statement)
    r2 = results[0]
    assert r1 == r2


def test_record_inequality(graph):
    statement = "CREATE (a {name:'Alice',age:33}) RETURN a,a.name,a.age"
    results = graph.cypher.execute(statement)
    r1 = results[0]
    statement = "CREATE (a {name:'Bob',age:44}) RETURN a,a.name,a.age"
    results = graph.cypher.execute(statement)
    r2 = results[0]
    assert r1 != r2
