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


try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from py2neo import Resource, GraphError
from py2neo.packages.httpstream import ClientError as _ClientError, ServerError as _ServerError, \
    Resource as _Resource, Response as _Response


class DodgyServerError(_ServerError):

    status_code = 599


def test_can_handle_json_error_from_get():
    resource = Resource("http://localhost:7474/db/data/node/spam")
    try:
        resource.get()
    except GraphError as error:
        cause = error.__cause__
        assert isinstance(cause, _ClientError)
        assert isinstance(cause, _Response)
        assert cause.status_code == 404
    else:
        assert False


def test_can_handle_json_error_from_put(graph):
    node, = graph.create({})
    try:
        node.properties.resource.put(["foo"])
    except GraphError as error:
        cause = error.__cause__
        assert isinstance(cause, _ClientError)
        assert isinstance(cause, _Response)
        assert cause.status_code == 400
    else:
        assert False


def test_can_handle_json_error_from_post():
    new_node_resource = Resource("http://localhost:7474/db/data/node")
    try:
        new_node_resource.post(["foo"])
    except GraphError as error:
        cause = error.__cause__
        assert isinstance(cause, _ClientError)
        assert isinstance(cause, _Response)
        assert cause.status_code == 400
    else:
        assert False


def test_can_handle_json_error_from_delete(graph):
    node, = graph.create({})
    non_existent_property = Resource(node.properties.resource.uri.string + "/foo")
    try:
        non_existent_property.delete()
    except GraphError as error:
        cause = error.__cause__
        assert isinstance(cause, _ClientError)
        assert isinstance(cause, _Response)
        assert cause.status_code == 404
    else:
        assert False


def test_can_handle_other_error_from_get():
    with patch.object(_Resource, "get") as mocked:
        mocked.side_effect = DodgyServerError
        resource = Resource("http://localhost:7474/db/data/node/spam")
        try:
            resource.get()
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyServerError)
        else:
            assert False


def test_can_handle_other_error_from_put():
    with patch.object(_Resource, "put") as mocked:
        mocked.side_effect = DodgyServerError
        resource = Resource("http://localhost:7474/db/data/node/spam")
        try:
            resource.put()
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyServerError)
        else:
            assert False


def test_can_handle_other_error_from_post():
    with patch.object(_Resource, "post") as mocked:
        mocked.side_effect = DodgyServerError
        resource = Resource("http://localhost:7474/db/data/node/spam")
        try:
            resource.post()
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyServerError)
        else:
            assert False


def test_can_handle_other_error_from_delete():
    with patch.object(_Resource, "delete") as mocked:
        mocked.side_effect = DodgyServerError
        resource = Resource("http://localhost:7474/db/data/node/spam")
        try:
            resource.delete()
        except GraphError as error:
            assert isinstance(error.__cause__, DodgyServerError)
        else:
            assert False
