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


from py2neo import rewrite, Resource


def test_can_rewrite_uri():
    rewrite(("https", "localtoast", 4747), ("http", "localhost", 7474))
    assert Resource("https://localtoast:4747/").uri == "http://localhost:7474/"


def test_can_remove_rewrite_uri():
    rewrite(("https", "localtoast", 4747), ("http", "localhost", 7474))
    rewrite(("https", "localtoast", 4747), None)
    assert Resource("https://localtoast:4747/").uri == "https://localtoast:4747/"


def test_can_remove_unknown_rewrite_uri():
    rewrite(("https", "localnonsense", 4747), None)
