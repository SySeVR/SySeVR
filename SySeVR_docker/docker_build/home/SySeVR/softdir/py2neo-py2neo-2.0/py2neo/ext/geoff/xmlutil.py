#!/usr/bin/env python
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

import json
import re
from xml.etree import ElementTree

from py2neo.cypher import cypher_repr
from py2neo.util import xstr


SIMPLE_NAME = re.compile(r"^[A-Za-z_][0-9A-Za-z_]*$")


def jsonify(obj, ensure_ascii=True):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True, ensure_ascii=ensure_ascii)


def cyphify(obj, ensure_ascii=True):
    return cypher_repr(obj)


def _convert_xml(src, prefixes=None, verb=None, method=jsonify,
                 ensure_ascii=True, separator="\n"):
    """ Convert data from XML source to Cypher or Geoff.
    """
    TAG_PATTERN = re.compile(r"^(\{(.*)\})?(.*)$")
    if prefixes:
        prefixes = dict((b, a) for a, b in prefixes.items())
    nodes, rels, buffer, node_ids = [], [], [], []

    def local(tag):
        groups = TAG_PATTERN.match(tag).groups()
        if prefixes and groups[1] and groups[1] in prefixes:
            return prefixes[groups[1]] + "_" + groups[2]
        else:
            return groups[2]

    def node_no(node):
        if node not in nodes:
            n = len(nodes) + 1
            nodes.append(node)
            node_id = node.attrib.get("id")
            if node_id and (not ensure_ascii or SIMPLE_NAME.match(node_id)):
                node_ids.append(node_id)
            else:
                node_ids.append("node_{0}".format(n))
        return nodes.index(node)

    def walk(parent, child):
        if parent is not None:
            rels.append((node_no(parent), local(child.tag), node_no(child),
                         dict((key, value)
                              for key, value in child.attrib.items()
                              if key != "id")
            ))
        for grandchild in child:
            if len(grandchild) > 0:
                walk(child, grandchild)

    def typed(value):
        try:
            return int(value)
        except ValueError:
            try:
                return float(value)
            except ValueError:
                return value

    walk(None, ElementTree.fromstring(xstr(src)))
    for i, node in enumerate(nodes):
        properties = {}
        for child in node:
            is_leaf = len(child) == 0
            if child.text:
                inner_value = typed(child.text.strip())
            else:
                inner_value = None
            if is_leaf:
                if inner_value is not None:
                    properties[local(child.tag)] = inner_value
                for key, value in child.attrib.items():
                    if key != "id":
                        properties[local(child.tag) + " " + local(key)] = typed(value)
        if properties:
            buffer.append("({0} {1})".format(node_ids[i], method(properties, ensure_ascii=ensure_ascii)))
        else:
            buffer.append("({0})".format(node_ids[i]))
    for rel in rels:
        properties = rel[3]
        if properties:
            buffer.append("({0})-[:{1} {3}]->({2})".format(
                node_ids[rel[0]],
                rel[1] if SIMPLE_NAME.match(rel[1]) else method(rel[1], ensure_ascii=ensure_ascii),
                node_ids[rel[2]],
                method(properties, ensure_ascii=ensure_ascii),
            ))
        else:
            buffer.append("({0})-[:{1}]->({2})".format(
                node_ids[rel[0]],
                rel[1] if SIMPLE_NAME.match(rel[1]) else method(rel[1], ensure_ascii=ensure_ascii),
                node_ids[rel[2]],
            ))
    if verb:
        return verb + "\n" + separator.join(buffer)
    else:
        return separator.join(buffer)


def xml_to_geoff(src, prefixes=None):
    return _convert_xml(src, prefixes=prefixes, ensure_ascii=False)


def xml_to_cypher(src, prefixes=None):
    return _convert_xml(src, prefixes=prefixes, verb="CREATE", method=cyphify,
                        ensure_ascii=True, separator=",\n")
