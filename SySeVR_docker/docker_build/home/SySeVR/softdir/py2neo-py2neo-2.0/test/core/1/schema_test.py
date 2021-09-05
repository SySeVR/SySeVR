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

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch
from uuid import uuid4

import pytest

from py2neo import neo4j, GraphError, Node
from py2neo.packages.httpstream import ClientError, Resource as _Resource


class NotFoundError(ClientError):
    status_code = 404


class DodgyClientError(ClientError):
    status_code = 499


def get_clean_database():
    # Constraints have to be removed before the indexed property keys can be removed.
    graph = neo4j.Graph()
    if graph.supports_node_labels:
        for label in graph.node_labels:
            for key in graph.schema.get_uniqueness_constraints(label):
                graph.schema.drop_uniqueness_constraint(label, key)
            for key in graph.schema.get_indexes(label):
                graph.schema.drop_index(label, key)
    return graph


def test_schema_not_supported(graph):
    with patch("py2neo.Graph.supports_schema_indexes") as mocked:
        mocked.__get__ = Mock(return_value=False)
        try:
            _ = graph.schema
        except NotImplementedError:
            assert True
        else:
            assert False


def test_schema_index():
    graph = get_clean_database()
    if not graph.supports_node_labels:
        return
    label_1 = uuid4().hex
    label_2 = uuid4().hex
    munich, = graph.create({'name': "München", 'key': "09162000"})
    munich.labels.replace({label_1, label_2})
    graph.schema.create_index(label_1, "name")
    graph.schema.create_index(label_1, "key")
    graph.schema.create_index(label_2, "name")
    graph.schema.create_index(label_2, "key")
    found_borough_via_name = graph.find(label_1, "name", "München")
    found_borough_via_key = graph.find(label_1, "key", "09162000")
    found_county_via_name = graph.find(label_2, "name", "München")
    found_county_via_key = graph.find(label_2, "key", "09162000")
    assert list(found_borough_via_name) == list(found_borough_via_key)
    assert list(found_county_via_name) == list(found_county_via_key)
    assert list(found_borough_via_name) == list(found_county_via_name)
    keys = graph.schema.get_indexes(label_1)
    assert "name" in keys
    assert "key" in keys
    graph.schema.drop_index(label_1, "name")
    graph.schema.drop_index(label_1, "key")
    graph.schema.drop_index(label_2, "name")
    graph.schema.drop_index(label_2, "key")
    with pytest.raises(GraphError):
        graph.schema.drop_index(label_2, "key")
    graph.delete(munich)


def test_unique_constraint():
    graph = get_clean_database()
    if not graph.supports_node_labels:
        return
    label_1 = uuid4().hex
    borough, = graph.create(Node(label_1, name="Taufkirchen"))
    graph.schema.create_uniqueness_constraint(label_1, "name")
    constraints = graph.schema.get_uniqueness_constraints(label_1)
    assert "name" in constraints
    with pytest.raises(GraphError):
        graph.create(Node(label_1, name="Taufkirchen"))
    graph.delete(borough)


def test_labels_constraints():
    graph_db = get_clean_database()
    if not graph_db.supports_node_labels:
        return
    label_1 = uuid4().hex
    a, b = graph_db.create(Node(label_1, name="Alice"), Node(label_1, name="Alice"))
    with pytest.raises(GraphError):
        graph_db.schema.create_uniqueness_constraint(label_1, "name")
    b.labels.remove(label_1)
    b.push()
    graph_db.schema.create_uniqueness_constraint(label_1, "name")
    a.labels.remove(label_1)
    a.push()
    b.labels.add(label_1)
    b.push()
    try:
        graph_db.schema.drop_index(label_1, "name")
    except GraphError as error:
        # this is probably a server bug
        assert error.__cause__.status_code // 100 == 5
    else:
        assert False
    b.labels.remove(label_1)
    b.push()
    graph_db.schema.drop_uniqueness_constraint(label_1, "name")
    with pytest.raises(GraphError):
        graph_db.schema.drop_uniqueness_constraint(label_1, "name")
    graph_db.delete(a, b)


def test_drop_index_handles_404_errors_correctly(graph):
    if not graph.supports_node_labels:
        return
    with patch.object(_Resource, "delete") as mocked:
        mocked.side_effect = NotFoundError
        try:
            graph.schema.drop_index("Person", "name")
        except GraphError:
            assert True
        else:
            assert False


def test_drop_index_handles_non_404_errors_correctly(graph):
    if not graph.supports_node_labels:
        return
    with patch.object(_Resource, "delete") as mocked:
        mocked.side_effect = DodgyClientError
        try:
            graph.schema.drop_index("Person", "name")
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyClientError)
        else:
            assert False


def test_drop_unique_constraint_handles_404_errors_correctly(graph):
    if not graph.supports_node_labels:
        return
    with patch.object(_Resource, "delete") as mocked:
        mocked.side_effect = NotFoundError
        try:
            graph.schema.drop_uniqueness_constraint("Person", "name")
        except GraphError:
            assert True
        else:
            assert False


def test_drop_unique_constraint_handles_non_404_errors_correctly(graph):
    if not graph.supports_node_labels:
        return
    with patch.object(_Resource, "delete") as mocked:
        mocked.side_effect = DodgyClientError
        try:
            graph.schema.drop_uniqueness_constraint("Person", "name")
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyClientError)
        else:
            assert False
