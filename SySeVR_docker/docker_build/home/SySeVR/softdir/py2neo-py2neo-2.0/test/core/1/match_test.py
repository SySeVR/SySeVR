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


from uuid import uuid4

import pytest

from py2neo import neo4j, Node


class TestMatch(object):

    @pytest.fixture(autouse=True)
    def setup(self, graph):
        self.graph = graph
        stuff = self.graph.create(
            {"name": "Alice"},
            {"name": "Bob"},
            {"name": "Carol"},
            (0, "LOVES", 1),
            (1, "LOVES", 0),
            (0, "KNOWS", 1),
            (1, "KNOWS", 0),
            (1, "KNOWS", 2),
            (2, "KNOWS", 1),
        )
        self.alice, self.bob, self.carol = stuff[0:3]

    #def test_can_match_all(self):
    #    rels = list(self.graph.match())
    #    assert len(rels) == 6

    def test_can_match_start_node(self):
        rels = list(self.graph.match(start_node=self.alice))
        assert len(rels) == 2
        assert "KNOWS" in [rel.type for rel in rels]
        assert "LOVES" in [rel.type for rel in rels]
        assert self.bob in [rel.end_node for rel in rels]

    #def test_can_match_type_only(self):
    #    rels = list(self.graph.match(rel_type="LOVES"))
    #    assert len(rels) == 2
    #    assert self.alice in [rel.start_node for rel in rels]
    #    assert self.bob in [rel.start_node for rel in rels]
    #    assert self.alice in [rel.end_node for rel in rels]
    #    assert self.bob in [rel.end_node for rel in rels]

    def test_can_match_start_node_and_type(self):
        rels = list(self.graph.match(start_node=self.alice, rel_type="KNOWS"))
        assert len(rels) == 1
        assert self.bob in [rel.end_node for rel in rels]

    def test_can_match_start_node_and_end_node(self):
        rels = list(self.graph.match(start_node=self.alice, end_node=self.bob))
        assert len(rels) == 2
        assert "KNOWS" in [rel.type for rel in rels]
        assert "LOVES" in [rel.type for rel in rels]

    def test_can_match_type_and_end_node(self):
        rels = list(self.graph.match(rel_type="KNOWS", end_node=self.bob))
        assert len(rels) == 2
        assert self.alice in [rel.start_node for rel in rels]
        assert self.carol in [rel.start_node for rel in rels]

    def test_can_bidi_match_start_node(self):
        rels = list(self.graph.match(start_node=self.bob, bidirectional=True))
        assert len(rels) == 6
        assert "KNOWS" in [rel.type for rel in rels]
        assert "LOVES" in [rel.type for rel in rels]
        assert self.alice in [rel.start_node for rel in rels]
        assert self.bob in [rel.start_node for rel in rels]
        assert self.carol in [rel.start_node for rel in rels]
        assert self.alice in [rel.end_node for rel in rels]
        assert self.bob in [rel.end_node for rel in rels]
        assert self.carol in [rel.end_node for rel in rels]

    def test_can_bidi_match_start_node_and_type(self):
        rels = list(self.graph.match(start_node=self.bob, rel_type="KNOWS", bidirectional=True))
        assert len(rels) == 4
        assert self.alice in [rel.start_node for rel in rels]
        assert self.bob in [rel.start_node for rel in rels]
        assert self.carol in [rel.start_node for rel in rels]
        assert self.alice in [rel.end_node for rel in rels]
        assert self.bob in [rel.end_node for rel in rels]
        assert self.carol in [rel.end_node for rel in rels]

    def test_can_bidi_match_start_node_and_end_node(self):
        rels = list(self.graph.match(start_node=self.alice, end_node=self.bob, bidirectional=True))
        assert len(rels) == 4
        assert "KNOWS" in [rel.type for rel in rels]
        assert "LOVES" in [rel.type for rel in rels]
        assert self.alice in [rel.start_node for rel in rels]
        assert self.bob in [rel.start_node for rel in rels]
        assert self.alice in [rel.end_node for rel in rels]
        assert self.bob in [rel.end_node for rel in rels]

    def test_can_bidi_match_type_and_end_node(self):
        rels = list(self.graph.match(rel_type="KNOWS", end_node=self.bob, bidirectional=True))
        assert len(rels) == 4
        assert self.alice in [rel.start_node for rel in rels]
        assert self.carol in [rel.start_node for rel in rels]
        assert self.alice in [rel.start_node for rel in rels]
        assert self.bob in [rel.start_node for rel in rels]
        assert self.carol in [rel.start_node for rel in rels]
        assert self.alice in [rel.end_node for rel in rels]
        assert self.bob in [rel.end_node for rel in rels]
        assert self.carol in [rel.end_node for rel in rels]

    def test_can_match_with_limit(self):
        rels = list(self.graph.match(limit=3))
        assert len(rels) == 3

    def test_can_match_one_when_some_exist(self):
        rel = self.graph.match_one()
        assert isinstance(rel, neo4j.Relationship)

    def test_can_match_one_when_none_exist(self):
        rel = self.graph.match_one(rel_type=uuid4())
        assert rel is None

    def test_can_match_none(self):
        rels = list(self.graph.match(rel_type="ZXZXZXZXZXZXZXZXZ", limit=1))
        assert len(rels) == 0

    #def test_can_match_multiple_types(self):
    #    rels = list(self.graph.match(rel_type=("LOVES", "KNOWS")))
    #    assert len(rels) == 6

    def test_can_match_start_node_and_multiple_types(self):
        rels = list(self.graph.match(start_node=self.alice, rel_type=("LOVES", "KNOWS")))
        assert len(rels) == 2

    def test_relationship_start_node_must_be_bound(self):
        try:
            list(self.graph.match(start_node=Node()))
        except TypeError:
            assert True
        else:
            assert False

    def test_relationship_end_node_must_be_bound(self):
        try:
            list(self.graph.match(end_node=Node()))
        except TypeError:
            assert True
        else:
            assert False

    def test_relationship_start_and_end_node_must_be_bound(self):
        try:
            list(self.graph.match(start_node=Node(), end_node=Node()))
        except TypeError:
            assert True
        else:
            assert False
