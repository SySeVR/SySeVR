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

import pytest

from py2neo.core import Node, Relationship, Path
from py2neo.cypher import CypherResource, CypherError, CypherTransactionError


@pytest.fixture
def vanilla_cypher(graph):
    return CypherResource(graph.resource.metadata["cypher"])


def alice_and_bob(graph):
    return graph.create(
        {"name": "Alice", "age": 66},
        {"name": "Bob", "age": 77},
        (0, "KNOWS", 1),
    )


def test_nonsense_query(graph):
    statement = "SELECT z=nude(0) RETURNS x"
    try:
        graph.cypher.execute(statement)
    except CypherTransactionError as error:
        assert error.code == "Neo.ClientError.Statement.InvalidSyntax"
    except CypherError as error:
        assert error.exception == "SyntaxException"
        assert error.fullname in [None, "org.neo4j.cypher.SyntaxException"]
        assert error.statement == statement
        assert error.parameters is None
    else:
        assert False


def test_can_run(graph):
    graph.cypher.run("CREATE (a {name:'Alice'}) RETURN a.name")
    assert True


def test_can_run_through_vanilla_endpoint(vanilla_cypher):
    vanilla_cypher.run("CREATE (a {name:'Alice'}) RETURN a.name")
    assert True


def test_can_execute(graph):
    results = graph.cypher.execute("CREATE (a {name:'Alice'}) RETURN a.name AS name")
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_with_parameter(graph):
    results = graph.cypher.execute("CREATE (a {name:{N}}) RETURN a.name AS name", {"N": "Alice"})
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_with_entity_parameter(graph):
    alice, = graph.create({"name": "Alice"})
    results = graph.cypher.execute("START a=node({N}) RETURN a.name AS name", {"N": alice})
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_through_vanilla_endpoint(vanilla_cypher):
    results = vanilla_cypher.execute("CREATE (a {name:'Alice'}) RETURN a.name AS name")
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_through_vanilla_endpoint_with_parameter(vanilla_cypher):
    results = vanilla_cypher.execute("CREATE (a {name:{N}}) RETURN a.name AS name", {"N": "Alice"})
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_through_vanilla_endpoint_with_entity_parameter(graph, vanilla_cypher):
    alice, = graph.create({"name": "Alice"})
    results = vanilla_cypher.execute("START a=node({N}) RETURN a.name AS name", {"N": alice})
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_execute_one(graph):
    result = graph.cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a.name AS name")
    assert result == "Alice"


def test_can_execute_one_where_none_returned(graph):
    result = graph.cypher.execute_one("START a=node(*) "
                                      "WHERE 2 + 2 = 5 "
                                      "RETURN a.name AS name")
    assert result is None


def test_can_execute_one_through_vanilla_endpoint(vanilla_cypher):
    result = vanilla_cypher.execute_one("CREATE (a {name:'Alice'}) RETURN a.name AS name")
    assert result == "Alice"


def test_can_execute_one_through_vanilla_endpoint_where_none_returned(vanilla_cypher):
    result = vanilla_cypher.execute_one("START a=node(*) "
                                        "WHERE 2 + 2 = 5 "
                                        "RETURN a.name AS name")
    assert result is None


def test_can_stream(graph):
    stream = graph.cypher.stream("CREATE (a {name:'Alice'}) RETURN a.name AS name")
    results = list(stream)
    assert len(results) == 1
    assert results[0].name == "Alice"


def test_can_convert_to_subgraph(graph):
    results = graph.cypher.execute("CREATE (a)-[ab:KNOWS]->(b) RETURN a, ab, b")
    subgraph = results.to_subgraph()
    assert subgraph.order == 2
    assert subgraph.size == 1


class TestCypher(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph

    def test_nonsense_query_with_error_handler(self):
        with pytest.raises(CypherError):
            self.graph.cypher.execute("SELECT z=nude(0) RETURNS x")

    def test_query(self):
        a, b, ab = alice_and_bob(self.graph)
        results = self.graph.cypher.execute((
            "start a=node({0}),b=node({1}) "
            "match a-[ab:KNOWS]->b "
            "return a, b, ab, a.name AS a_name, b.name AS b_name"
        ).format(a._id, b._id))
        assert len(results) == 1
        for record in results:
            assert isinstance(record.a, Node)
            assert isinstance(record.b, Node)
            assert isinstance(record.ab, Relationship)
            assert record.a_name == "Alice"
            assert record.b_name == "Bob"

    def test_query_can_return_path(self):
        a, b, ab = alice_and_bob(self.graph)
        results = self.graph.cypher.execute((
            "start a=node({0}),b=node({1}) "
            "match p=(a-[ab:KNOWS]->b) "
            "return p"
        ).format(a._id, b._id))
        assert len(results) == 1
        for record in results:
            assert isinstance(record.p, Path)
            assert len(record.p.nodes) == 2
            assert record.p.nodes[0] == a
            assert record.p.nodes[1] == b
            assert record.p.relationships[0].type == "KNOWS"

    def test_query_can_return_collection(self):
        node, = self.graph.create({})
        query = "START a=node({N}) RETURN collect(a) AS a_collection"
        params = {"N": node._id}
        results = self.graph.cypher.execute(query, params)
        assert results[0].a_collection == [node]

    def test_param_used_once(self):
        node, = self.graph.create({})
        query = (
            "START a=node({X}) "
            "RETURN a"
        )
        params = {"X": node._id}
        results = self.graph.cypher.execute(query, params)
        record = results[0]
        assert record.a == node

    def test_param_used_twice(self):
        node, = self.graph.create({})
        query = (
            "START a=node({X}), b=node({X}) "
            "RETURN a, b"
        )
        params = {"X": node._id}
        results = self.graph.cypher.execute(query, params)
        record = results[0]
        assert record.a == node
        assert record.b == node

    def test_param_used_thrice(self):
        node, = self.graph.create({})
        query = (
            "START a=node({X}), b=node({X}), c=node({X})"
            "RETURN a, b, c"
        )
        params = {"X": node._id}
        results = self.graph.cypher.execute(query, params)
        record = results[0]
        assert record.a == node
        assert record.b == node
        assert record.b == node

    def test_param_reused_once_after_with_statement(self):
        a, b, ab = alice_and_bob(self.graph)
        query = (
            "START a=node({A}) "
            "MATCH (a)-[:KNOWS]->(b) "
            "WHERE a.age > {min_age} "
            "WITH a "
            "MATCH (a)-[:KNOWS]->(b) "
            "WHERE b.age > {min_age} "
            "RETURN b"
        )
        params = {"A": a._id, "min_age": 50}
        results = self.graph.cypher.execute(query, params)
        record = results[0]
        assert record.b == b

    def test_param_reused_twice_after_with_statement(self):
        a, b, ab = alice_and_bob(self.graph)
        c, bc = self.graph.create(
            {"name": "Carol", "age": 88},
            (b, "KNOWS", 0),
        )
        query = (
            "START a=node({A}) "
            "MATCH (a)-[:KNOWS]->(b) "
            "WHERE a.age > {min_age} "
            "WITH a "
            "MATCH (a)-[:KNOWS]->(b) "
            "WHERE b.age > {min_age} "
            "WITH b "
            "MATCH (b)-[:KNOWS]->(c) "
            "WHERE c.age > {min_age} "
            "RETURN c"
        )
        params = {"A": a._id, "min_age": 50}
        results = self.graph.cypher.execute(query, params)
        record = results[0]
        assert record.c == c
