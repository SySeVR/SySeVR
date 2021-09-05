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


class ConcurrentRequest(ClientError):
    """ There were concurrent requests accessing the same transaction,
    which is not allowed.
    """


class EventHandlerThrewException(ClientError):
    """ A transaction event handler threw an exception. The transaction
    will be rolled back.
    """


class InvalidType(ClientError):
    """ The transaction is of the wrong type to service the request.
    For instance, a transaction that has had schema modifications
    performed in it cannot be used to subsequently perform data
    operations, and vice versa.
    """


class UnknownId(ClientError):
    """ The request referred to a transaction that does not exist.
    """


class CouldNotBegin(DatabaseError):
    """ The database was unable to start the transaction.
    """


class CouldNotCommit(DatabaseError):
    """ The database was unable to commit the transaction.
    """


class CouldNotRollback(DatabaseError):
    """ The database was unable to roll back the transaction.
    """


class ReleaseLocksFailed(DatabaseError):
    """ The transaction was unable to release one or more of its locks.
    """


class AcquireLockTimeout(TransientError):
    """ The transaction was unable to acquire a lock, for instance due
    to a timeout or the transaction thread being interrupted.
    """


class DeadlockDetected(TransientError):
    """ This transaction, and at least one more transaction, has
    acquired locks in a way that it will wait indefinitely, and the
    database has aborted it. Retrying this transaction will most likely
    be successful.
    """
