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

from py2neo.neo4j import PropertySet, PropertyContainer


class TestPropertySet(object):

    def test_none_is_not_stored(self):
        # when
        p = PropertySet(name=None)
        # then
        assert "name" not in p

    def test_missing_property_is_none(self):
        # when
        p = PropertySet()
        # then
        assert p["name"] is None

    def test_setting_to_none_deletes(self):
        # given
        p = PropertySet(name="Alice")
        # when
        p["name"] = None
        # then
        assert "name" not in p

    def test_deleting_sets_to_none(self):
        # given
        p = PropertySet(name="Alice")
        # when
        del p["name"]
        # then
        assert p["name"] == None

    def test_setdefault_on_existing_returns_existing(self):
        # given
        p = PropertySet(name="Alice")
        # when
        value = p.setdefault("name", "Bob")
        # then
        assert value == "Alice"

    def test_setdefault_on_missing_returns_default(self):
        # given
        p = PropertySet()
        # when
        value = p.setdefault("name", "Bob")
        # then
        assert value == "Bob"

    def test_setdefault_on_missing_with_no_default_returns_none(self):
        # given
        p = PropertySet()
        # when
        value = p.setdefault("name")
        # then
        assert value is None

    def test_setdefault_on_missing_with_no_default_does_not_add_key(self):
        # given
        p = PropertySet()
        # when
        p.setdefault("name")
        # then
        assert "name" not in p

    def test_update_with_dict(self):
        # given
        p = PropertySet()
        # when
        p.update({"name": "Alice"})
        # then
        assert p["name"] == "Alice"

    def test_update_with_key_value_list(self):
        # given
        p = PropertySet()
        # when
        p.update([("name", "Alice")])
        # then
        assert p["name"] == "Alice"

    def test_property_set_hash_match(self):
        # given
        p = PropertySet(name="Alice", age="33", colours=["red", "green", "blue"])
        q = PropertySet(name="Alice", age="33", colours=["red", "green", "blue"])
        # then
        assert hash(p) == hash(q)


class TestPropertyContainer(object):

    def test_none_is_not_stored(self):
        # when
        p = PropertyContainer(name=None)
        # then
        assert "name" not in p

    def test_missing_property_is_none(self):
        # when
        p = PropertyContainer()
        # then
        assert p["name"] is None

    def test_setting_to_none_deletes(self):
        # given
        p = PropertyContainer(name="Alice")
        # when
        p["name"] = None
        # then
        assert "name" not in p

    def test_deleting_sets_to_none(self):
        # given
        p = PropertyContainer(name="Alice")
        # when
        del p["name"]
        # then
        assert p["name"] == None
