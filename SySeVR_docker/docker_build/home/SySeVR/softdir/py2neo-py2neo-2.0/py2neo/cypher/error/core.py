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


from importlib import import_module
import json

from py2neo.error import GraphError


class CypherError(GraphError):

    default_message = "The server returned a Cypher error"
    status_code_map = {}

    statement = None
    parameters = None

    def __init__(self, message, **kwargs):
        GraphError.__init__(self, message, **kwargs)
        if self.request:
            request_body = json.loads(self.request.body)
            self.statement = request_body.get("query")
            self.parameters = request_body.get("params")


class CypherTransactionError(CypherError):
    """ 
    """

    code = None
    message = None

    @classmethod
    def hydrate(cls, data):
        code = data["code"]
        message = data["message"]
        _, classification, category, title = code.split(".")
        error_module = import_module("py2neo.cypher.error." + category.lower())
        error_cls = getattr(error_module, title)
        inst = error_cls(message)
        inst.code = code
        inst.message = message
        return inst


class ClientError(CypherTransactionError):
    """ The Client sent a bad request - changing the request might yield a successful outcome.
    """


class DatabaseError(CypherTransactionError):
    """ The database failed to service the request.
    """


class TransientError(CypherTransactionError):
    """ The database cannot service the request right now, retrying later might yield a successful outcome.
    """
