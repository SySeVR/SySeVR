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

from uuid import uuid4

from py2neo import Node


def test_can_merge_on_label_only(graph):
    if not graph.supports_node_labels:
        return
    label = uuid4().hex
    merged = list(graph.merge(label))
    assert len(merged) == 1
    assert isinstance(merged[0], Node)
    assert merged[0].labels == {label}


def test_can_merge_on_label_and_property(graph):
    if not graph.supports_node_labels:
        return
    label = uuid4().hex
    merged = list(graph.merge(label, "foo", "bar"))
    assert len(merged) == 1
    assert isinstance(merged[0], Node)
    assert merged[0].labels == {label}
    assert merged[0].properties == {"foo": "bar"}


def test_cannot_merge_empty_label(graph):
    if not graph.supports_node_labels:
        return
    try:
        _ = list(graph.merge(""))
    except ValueError:
        assert True
    else:
        assert False


def test_can_merge_one_on_label_and_property(graph):
    if not graph.supports_node_labels:
        return
    label = uuid4().hex
    try:
        merged = graph.merge_one(label, "foo", "bar")
        assert isinstance(merged, Node)
        assert merged.labels == {label}
        assert merged.properties == {"foo": "bar"}
    finally:
        graph.delete(merged)

