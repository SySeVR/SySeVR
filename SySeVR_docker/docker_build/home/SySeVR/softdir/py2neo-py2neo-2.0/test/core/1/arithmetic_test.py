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


from py2neo import Rel, Rev, Node, Path


def test_can_apply_unary_positive_to_rel():
    before = Rel("KNOWS", since=1999)
    after = +before
    assert isinstance(after, Rel)
    assert after.type == before.type
    assert after.properties == before.properties


def test_can_apply_unary_negative_to_rel():
    before = Rel("KNOWS", since=1999)
    after = -before
    assert isinstance(after, Rev)
    assert after.type == before.type
    assert after.properties == before.properties


def test_can_apply_unary_absolute_to_rel():
    before = Rel("KNOWS", since=1999)
    after = abs(before)
    assert isinstance(after, Rel)
    assert after.type == before.type
    assert after.properties == before.properties


def test_can_apply_unary_positive_to_rev():
    before = Rev("KNOWS", since=1999)
    after = +before
    assert isinstance(after, Rev)
    assert after.type == before.type
    assert after.properties == before.properties


def test_can_apply_unary_negative_to_rev():
    before = Rev("KNOWS", since=1999)
    after = -before
    assert isinstance(after, Rel)
    assert after.type == before.type
    assert after.properties == before.properties


def test_can_apply_unary_absolute_to_rev():
    before = Rev("KNOWS", since=1999)
    after = abs(before)
    assert isinstance(after, Rel)
    assert after.type == before.type
    assert after.properties == before.properties


def test_path_addition():
    alice = Node(name="Alice")
    bob = Node(name="Bob")
    carol = Node(name="Carol")
    assert alice + alice == Path(alice)
    assert alice + "KNOWS" == Path(alice, "KNOWS", None)
    assert alice + "KNOWS" + bob == Path(alice, "KNOWS", bob)
    assert alice + Rev("KNOWS") + bob == Path(alice, Rev("KNOWS"), bob)
    assert ((alice + "KNOWS" + bob) + (bob + "KNOWS" + carol) ==
            Path(alice, "KNOWS", bob, "KNOWS", carol))
