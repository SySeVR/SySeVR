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
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from py2neo.core import ServerPlugin


class FakePlugin(ServerPlugin):

    def __init__(self, graph):
        super(FakePlugin, self).__init__(graph, "FakePlugin")


class NaughtyPlugin(ServerPlugin):

    def __init__(self, graph):
        super(NaughtyPlugin, self).__init__(graph, "NaughtyPlugin")


@pytest.fixture
def fake_plugin_discovery(graph):
    metadata = graph.resource.metadata
    metadata["extensions"]["FakePlugin"] = {}
    graph.bind(graph.uri, metadata)


@pytest.mark.usefixtures("fake_plugin_discovery")
def test_can_init_server_plugin(graph):
    plugin = FakePlugin(graph)
    assert plugin.resources == {}


def test_cannot_init_non_existent_server_plugin(graph):
    try:
        _ = NaughtyPlugin(graph)
    except LookupError:
        assert True
    else:
        assert False
