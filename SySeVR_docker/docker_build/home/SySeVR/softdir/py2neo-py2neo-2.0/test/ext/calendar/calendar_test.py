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

from py2neo import Node


@pytest.fixture
def calendar(graph):
    from py2neo.ext.calendar import GregorianCalendar
    return GregorianCalendar(graph)


def test_can_create_date(calendar):
    date = calendar.date(2000, 12, 25)
    assert date.year == Node("Year", key="2000", year=2000)
    assert date.month == Node("Month", key="2000-12", year=2000, month=12)
    assert date.day == Node("Day", key="2000-12-25", year=2000, month=12, day=25)


def test_can_create_date_with_short_numbers(calendar):
    date = calendar.date(2000, 1, 2)
    assert date.year == Node("Year", key="2000", year=2000)
    assert date.month == Node("Month", key="2000-01", year=2000, month=1)
    assert date.day == Node("Day", key="2000-01-02", year=2000, month=1, day=2)


def test_can_create_month_year(calendar):
    month_year = calendar.date(2000, 12)
    assert month_year.year == Node("Year", key="2000", year=2000)
    assert month_year.month == Node("Month", key="2000-12", year=2000, month=12)


def test_can_create_year(calendar):
    year = calendar.date(2000)
    assert year.year == Node("Year", key="2000", year=2000)


def test_example_code():
    from py2neo import Graph, Node, Relationship
    from py2neo.ext.calendar import GregorianCalendar

    graph = Graph()
    calendar = GregorianCalendar(graph)

    alice = Node("Person", name="Alice")
    birth = Relationship(alice, "BORN", calendar.date(1800, 1, 1).day)
    death = Relationship(alice, "DIED", calendar.date(1900, 12, 31).day)
    graph.create(alice, birth, death)

    assert birth.end_node["year"] == 1800
    assert birth.end_node["month"] == 1
    assert birth.end_node["day"] == 1

    assert death.end_node["year"] == 1900
    assert death.end_node["month"] == 12
    assert death.end_node["day"] == 31
