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

from py2neo.core import UnmanagedExtension


class FakeExtension(UnmanagedExtension):

    def __init__(self, graph):
        super(FakeExtension, self).__init__(graph, "/fake/")


class NaughtyExtension(UnmanagedExtension):

    def __init__(self, graph):
        super(NaughtyExtension, self).__init__(graph, "/naughty/")


@pytest.yield_fixture
def fake_resource_get():
    with patch("py2neo.core.Resource.get") as mocked:
        yield mocked


@pytest.mark.usefixtures("fake_resource_get")
def test_can_init_unmanaged_extension(graph):
    plugin = FakeExtension(graph)
    assert plugin.resource.uri == "http://localhost:7474/fake/"


def test_cannot_init_non_existent_server_plugin(graph):
    try:
        _ = NaughtyExtension(graph)
    except NotImplementedError:
        assert True
    else:
        assert False
