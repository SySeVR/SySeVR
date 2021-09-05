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


from mock import patch

from py2neo import Graph


def test_can_create_graph_with_trailing_slash():
    uri = "http://localhost:7474/db/data/"
    graph = Graph(uri)
    assert graph.uri == uri
    index = graph.resource.get().content
    assert "node" in index


def test_can_create_graph_without_trailing_slash():
    uri = "http://localhost:7474/db/data/"
    graph = Graph(uri[:-1])
    assert graph.uri == uri
    index = graph.resource.get().content
    assert "node" in index


def test_same_uri_gives_same_instance():
    uri = "http://localhost:7474/db/data/"
    graph_1 = Graph(uri)
    graph_2 = Graph(uri)
    assert graph_1 is graph_2


def test_graph_len_returns_number_of_rels(graph):
    size = len(graph)
    num_rels = graph.cypher.execute_one("START r=rel(*) RETURN COUNT(r)")
    assert size == num_rels


def test_graph_bool_returns_true(graph):
    assert graph.__bool__()
    assert graph.__nonzero__()


def test_can_hydrate_graph(graph):
    data = graph.resource.get().content
    hydrated = graph.hydrate(data)
    assert hydrated is graph


def test_graph_contains(graph):
    node, = graph.create({})
    assert node in graph


def test_can_hydrate_map(graph):
    data = {
        "foo": "bar"
    }
    hydrated = graph.hydrate(data)
    assert isinstance(hydrated, dict)


def test_supports(graph):
    assert isinstance(graph.supports_foreach_pipe, bool)
    assert isinstance(graph.supports_node_labels, bool)
    assert isinstance(graph.supports_optional_match, bool)
    assert isinstance(graph.supports_schema_indexes, bool)
    assert isinstance(graph.supports_cypher_transactions, bool)


def test_can_open_browser(graph):
    with patch("webbrowser.open") as mocked:
        graph.open_browser()
        assert mocked.called_once_with(graph.service_root.resource.uri.string)
