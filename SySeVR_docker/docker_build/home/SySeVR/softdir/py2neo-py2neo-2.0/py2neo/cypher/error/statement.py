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


from py2neo.cypher.error.core import ClientError, DatabaseError, TransientError


class ArithmeticError(ClientError):
    """ Invalid use of arithmetic, such as dividing by zero.
    """


class ConstraintViolation(ClientError):
    """ A constraint imposed by the statement is violated by the data
    in the database.
    """


class EntityNotFound(ClientError):
    """ The statement is directly referring to an entity that does not
    exist.
    """


class InvalidArguments(ClientError):
    """ The statement is attempting to perform operations using invalid
    arguments
    """


class InvalidSemantics(ClientError):
    """ The statement is syntactically valid, but expresses something
    that the database cannot do.
    """


class InvalidSyntax(ClientError):
    """ The statement contains invalid or unsupported syntax.
    """


class InvalidType(ClientError):
    """ The statement is attempting to perform operations on values
    with types that are not supported by the operation.
    """


class NoSuchLabel(ClientError):
    """ The statement is referring to a label that does not exist.
    """


class NoSuchProperty(ClientError):
    """ The statement is referring to a property that does not exist.
    """


class ParameterMissing(ClientError):
    """ The statement is referring to a parameter that was not provided
    in the request.
    """


class ExecutionFailure(DatabaseError):
    """ The database was unable to execute the statement.
    """


class ExternalResourceFailure(TransientError):
    """ The external resource is not available
    """
