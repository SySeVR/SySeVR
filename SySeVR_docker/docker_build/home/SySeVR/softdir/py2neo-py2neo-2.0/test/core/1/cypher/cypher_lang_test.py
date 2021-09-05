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


from io import StringIO

from py2neo.core import Node, Relationship, Rel, Rev, Path
from py2neo.cypher.lang import CypherWriter, cypher_repr


def test_can_write_simple_identifier():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write_identifier("foo")
    written = string.getvalue()
    assert written == "foo"


def test_can_write_identifier_with_odd_chars():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write_identifier("foo bar")
    written = string.getvalue()
    assert written == "`foo bar`"


def test_can_write_identifier_containing_back_ticks():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write_identifier("foo `bar`")
    written = string.getvalue()
    assert written == "`foo ``bar```"


def test_cannot_write_empty_identifier():
    string = StringIO()
    writer = CypherWriter(string)
    try:
        writer.write_identifier("")
    except ValueError:
        assert True
    else:
        assert False


def test_cannot_write_none_identifier():
    string = StringIO()
    writer = CypherWriter(string)
    try:
        writer.write_identifier(None)
    except ValueError:
        assert True
    else:
        assert False


def test_can_write_simple_node():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Node())
    written = string.getvalue()
    assert written == "()"


def test_can_write_node_with_labels():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Node("Dark Brown", "Chicken"))
    written = string.getvalue()
    assert written == '(:Chicken:`Dark Brown`)'


def test_can_write_node_with_properties():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Node(name="Gertrude", age=3))
    written = string.getvalue()
    assert written == '({age:3,name:"Gertrude"})'


def test_can_write_node_with_labels_and_properties():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Node("Dark Brown", "Chicken", name="Gertrude", age=3))
    written = string.getvalue()
    assert written == '(:Chicken:`Dark Brown` {age:3,name:"Gertrude"})'


def test_can_write_simple_relationship():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Relationship({}, "KNOWS", {}))
    written = string.getvalue()
    assert written == "()-[:KNOWS]->()"


def test_can_write_relationship_with_properties():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Relationship(
        {"name": "Fred"}, ("LIVES WITH", {"place": "Bedrock"}), {"name": "Wilma"}))
    written = string.getvalue()
    assert written == '({name:"Fred"})-[:`LIVES WITH` {place:"Bedrock"}]->({name:"Wilma"})'


def test_can_write_simple_rel():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Rel("KNOWS"))
    written = string.getvalue()
    assert written == "-[:KNOWS]->"


def test_can_write_simple_rev():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Rev("KNOWS"))
    written = string.getvalue()
    assert written == "<-[:KNOWS]-"


def test_can_write_simple_path():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(Path({}, "LOVES", {}, Rev("HATES"), {}, "KNOWS", {}))
    written = string.getvalue()
    assert written == "()-[:LOVES]->()<-[:HATES]-()-[:KNOWS]->()"


def test_can_write_array():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write([1, 1, 2, 3, 5, 8, 13])
    written = string.getvalue()
    assert written == "[1,1,2,3,5,8,13]"


def test_can_write_mapping():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write({"one": "eins", "two": "zwei", "three": "drei"})
    written = string.getvalue()
    assert written == '{one:"eins",three:"drei",two:"zwei"}'


def test_writing_none_writes_nothing():
    string = StringIO()
    writer = CypherWriter(string)
    writer.write(None)
    written = string.getvalue()
    assert written == ""


def test_can_write_with_wrapper_function():
    written = cypher_repr(Path({}, "LOVES", {}, Rev("HATES"), {}, "KNOWS", {}))
    assert written == "()-[:LOVES]->()<-[:HATES]-()-[:KNOWS]->()"
