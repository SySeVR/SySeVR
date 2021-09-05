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

from py2neo import Finished
from py2neo.cypher.error.statement import InvalidSyntax


def test_can_execute_single_statement_transaction(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    assert not tx.finished
    tx.append("CREATE (a) RETURN a")
    results = tx.commit()
    assert repr(results)
    assert len(results) == 1
    for result in results:
        assert len(result) == 1
        for record in result:
            assert record.a
    assert tx.finished


def test_can_execute_transaction_as_with_statement(graph):
    if not graph.supports_cypher_transactions:
        return
    with graph.cypher.begin() as tx:
        assert not tx.finished
        tx.append("CREATE (a) RETURN a")
    assert tx.finished


def test_can_execute_multi_statement_transaction(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    assert not tx.finished
    tx.append("CREATE (a) RETURN a")
    tx.append("CREATE (a) RETURN a")
    tx.append("CREATE (a) RETURN a")
    results = tx.commit()
    assert len(results) == 3
    for result in results:
        assert len(result) == 1
        for record in result:
            assert record.a
    assert tx.finished


def test_can_execute_multi_execute_transaction(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    assert tx._id is None
    for i in range(10):
        assert not tx.finished
        tx.append("CREATE (a) RETURN a")
        tx.append("CREATE (a) RETURN a")
        tx.append("CREATE (a) RETURN a")
        results = tx.process()
        assert tx._id is not None
        assert len(results) == 3
        for result in results:
            assert len(result) == 1
            for record in result:
                assert record.a
    tx.commit()
    assert tx.finished


def test_can_rollback_transaction(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    for i in range(10):
        assert not tx.finished
        tx.append("CREATE (a) RETURN a")
        tx.append("CREATE (a) RETURN a")
        tx.append("CREATE (a) RETURN a")
        results = tx.process()
        assert len(results) == 3
        for result in results:
            assert len(result) == 1
            for record in result:
                assert record.a
    tx.rollback()
    assert tx.finished


def test_can_generate_transaction_error(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    try:
        tx.append("CRAETE (a) RETURN a")
        tx.commit()
    except InvalidSyntax as err:
        assert repr(err)
    else:
        assert False


def test_cannot_append_after_transaction_finished(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    tx.rollback()
    try:
        tx.append("CREATE (a) RETURN a")
    except Finished as error:
        assert error.obj is tx
        assert repr(error) == "CypherTransaction finished"
    else:
        assert False
