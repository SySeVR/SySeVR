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


from py2neo.cypher.error.core import ClientError, DatabaseError


class ReadOnly(ClientError):
    """ This is a read only database, writing or modifying the database
    is not allowed.
    """


class CorruptSchemaRule(DatabaseError):
    """ A malformed schema rule was encountered. Please contact your
    support representative.
    """


class FailedIndex(DatabaseError):
    """ The request (directly or indirectly) referred to an index that
    is in a failed state. The index needs to be dropped and recreated
    manually.
    """


class UnknownFailure(DatabaseError):
    """ An unknown failure occurred.
    """
