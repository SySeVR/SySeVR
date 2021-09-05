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


from collections import OrderedDict
import logging

from py2neo import Service, Resource, Node, Rel, Relationship, Subgraph, Path, Finished
from py2neo.cypher.error.core import CypherError, CypherTransactionError
from py2neo.packages.jsonstream import assembled
from py2neo.packages.tart.tables import TextTable
from py2neo.util import is_integer, is_string, xstr


__all__ = ["CypherResource", "CypherTransaction", "RecordListList", "RecordList", "RecordStream",
           "Record", "RecordProducer"]


log = logging.getLogger("py2neo.cypher")


class CypherResource(Service):
    """ Service wrapper for all Cypher functionality, providing access
    to transactions (if available) as well as single statement execution
    and streaming. If the server supports Cypher transactions, these
    will be used for single statement execution; if not, the vanilla
    Cypher endpoint will be used.

    This class will usually be instantiated via a :class:`py2neo.Graph`
    object and will be made available through the
    :attr:`py2neo.Graph.cypher` attribute. Therefore, for single
    statement execution, simply use the :func:`execute` method::

        from py2neo import Graph
        graph = Graph()
        results = graph.cypher.execute("MATCH (n:Person) RETURN n")

    """

    error_class = CypherError

    __instances = {}

    def __new__(cls, uri, transaction_uri=None):
        key = (uri, transaction_uri)
        try:
            inst = cls.__instances[key]
        except KeyError:
            inst = super(CypherResource, cls).__new__(cls)
            inst.bind(uri)
            inst.transaction_uri = transaction_uri
            cls.__instances[key] = inst
        return inst

    def post(self, statement, parameters=None):
        """ Post a Cypher statement to this resource, optionally with
        parameters.

        :param statement: A Cypher statement to execute.
        :param parameters: A dictionary of parameters.
        :rtype: :class:`httpstream.Response`
        """
        payload = {"query": statement}
        if parameters:
            payload["params"] = {}
            for key, value in parameters.items():
                if isinstance(value, (Node, Rel, Relationship)):
                    value = value._id
                payload["params"][key] = value
        log.info("execute %r %r", payload["query"], payload.get("params", {}))
        return self.resource.post(payload)

    def run(self, statement, parameters=None):
        """ Execute a single Cypher statement, ignoring any return value.

        :param statement: A Cypher statement to execute.
        :param parameters: A dictionary of parameters.
        """
        if self.transaction_uri:
            tx = CypherTransaction(self.transaction_uri)
            tx.append(statement, parameters)
            tx.commit()
        else:
            self.post(statement, parameters).close()

    def execute(self, statement, parameters=None):
        """ Execute a single Cypher statement.

        :param statement: A Cypher statement to execute.
        :param parameters: A dictionary of parameters.
        :rtype: :class:`py2neo.cypher.RecordList`
        """
        if self.transaction_uri:
            tx = CypherTransaction(self.transaction_uri)
            tx.append(statement, parameters)
            results = tx.commit()
            return results[0]
        else:
            response = self.post(statement, parameters)
            try:
                return self.graph.hydrate(response.content)
            finally:
                response.close()

    def execute_one(self, statement, parameters=None):
        """ Execute a single Cypher statement and return the value from
        the first column of the first record returned.

        :param statement: A Cypher statement to execute.
        :param parameters: A dictionary of parameters.
        :return: Single return value or :const:`None`.
        """
        if self.transaction_uri:
            tx = CypherTransaction(self.transaction_uri)
            tx.append(statement, parameters)
            results = tx.commit()
            try:
                return results[0][0][0]
            except IndexError:
                return None
        else:
            response = self.post(statement, parameters)
            results = self.graph.hydrate(response.content)
            try:
                return results[0][0]
            except IndexError:
                return None
            finally:
                response.close()

    def stream(self, statement, parameters=None):
        """ Execute the query and return a result iterator.

        :param statement: A Cypher statement to execute.
        :param parameters: A dictionary of parameters.
        :rtype: :class:`py2neo.cypher.RecordStream`
        """
        return RecordStream(self.graph, self.post(statement, parameters))

    def begin(self):
        """ Begin a new transaction.

        :rtype: :class:`py2neo.cypher.CypherTransaction`
        """
        if self.transaction_uri:
            return CypherTransaction(self.transaction_uri)
        else:
            raise NotImplementedError("Transaction support not available from this "
                                      "Neo4j server version")


class CypherTransaction(object):
    """ A transaction is a transient resource that allows multiple Cypher
    statements to be executed within a single server transaction.
    """

    error_class = CypherTransactionError

    def __init__(self, uri):
        log.info("begin")
        self.statements = []
        self.__begin = Resource(uri)
        self.__begin_commit = Resource(uri + "/commit")
        self.__execute = None
        self.__commit = None
        self.__finished = False
        self.graph = self.__begin.graph

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.commit()

    def __assert_unfinished(self):
        if self.__finished:
            raise Finished(self)

    @property
    def _id(self):
        """ The internal server ID of this transaction, if available.
        """
        if self.__execute is None:
            return None
        else:
            return int(self.__execute.uri.path.segments[-1])

    @property
    def finished(self):
        """ Indicates whether or not this transaction has been completed or is
        still open.

        :return: :py:const:`True` if this transaction has finished,
                 :py:const:`False` otherwise
        """
        return self.__finished

    def append(self, statement, parameters=None):
        """ Add a statement to the current queue of statements to be
        executed.

        :param statement: the statement to append
        :param parameters: a dictionary of execution parameters
        """
        self.__assert_unfinished()
        p = {}
        if parameters:
            for key, value in parameters.items():
                if isinstance(value, (Node, Rel, Relationship)):
                    value = value._id
                p[key] = value
        # OrderedDict is used here to avoid statement/parameters ordering bug
        log.info("append %r %r", statement, p)
        self.statements.append(OrderedDict([
            ("statement", statement),
            ("parameters", p),
            ("resultDataContents", ["REST"]),
        ]))

    def post(self, resource):
        self.__assert_unfinished()
        rs = resource.post({"statements": self.statements})
        location = rs.location
        if location:
            self.__execute = Resource(location)
        j = rs.content
        rs.close()
        self.statements = []
        if "commit" in j:
            self.__commit = Resource(j["commit"])
        if "errors" in j:
            errors = j["errors"]
            if len(errors) >= 1:
                error = errors[0]
                raise self.error_class.hydrate(error)
        out = RecordListList()
        for result in j["results"]:
            columns = result["columns"]
            producer = RecordProducer(columns)
            out.append(RecordList(columns, [producer.produce(self.graph.hydrate(r["rest"]))
                                            for r in result["data"]]))
        return out

    def process(self):
        """ Send all pending statements to the server for execution, leaving
        the transaction open for further statements. Along with
        :meth:`append <.CypherTransaction.append>`, this method can be used to
        batch up a number of individual statements into a single HTTP request::

            from py2neo import Graph

            graph = Graph()
            statement = "MERGE (n:Person {name:{N}}) RETURN n"

            tx = graph.cypher.begin()

            def add_names(*names):
                for name in names:
                    tx.append(statement, {"N": name})
                tx.process()

            add_names("Homer", "Marge", "Bart", "Lisa", "Maggie")
            add_names("Peter", "Lois", "Chris", "Meg", "Stewie")

            tx.commit()

        :return: list of results from pending statements
        """
        log.info("process")
        return self.post(self.__execute or self.__begin)

    def commit(self):
        """ Send all pending statements to the server for execution and commit
        the transaction.

        :return: list of results from pending statements
        """
        log.info("commit")
        try:
            return self.post(self.__commit or self.__begin_commit)
        finally:
            self.__finished = True

    def rollback(self):
        """ Rollback the current transaction.
        """
        self.__assert_unfinished()
        log.info("rollback")
        try:
            if self.__execute:
                self.__execute.delete()
        finally:
            self.__finished = True


class RecordListList(list):
    """ Container for multiple RecordList instances that presents a more
    consistent representation.
    """

    def __repr__(self):
        out = []
        for i in self:
            out.append(repr(i))
        return "\n".join(out)


class RecordList(object):
    """ A list of records returned from the execution of a Cypher statement.
    """

    @classmethod
    def hydrate(cls, data, graph):
        columns = data["columns"]
        rows = data["data"]
        producer = RecordProducer(columns)
        return cls(columns, [producer.produce(graph.hydrate(row)) for row in rows])

    def __init__(self, columns, records):
        log.info("result %r %r", columns, len(records))
        self.columns = columns
        self.records = records

    def __repr__(self):
        out = ""
        if self.columns:
            table = TextTable([None] + self.columns, border=True)
            for i, record in enumerate(self.records):
                table.append([i + 1] + list(record))
            out = repr(table)
        return out

    def __len__(self):
        return len(self.records)

    def __getitem__(self, item):
        return self.records[item]

    def __iter__(self):
        return iter(self.records)

    def to_subgraph(self):
        """ Convert a RecordList into a Subgraph.
        """
        entities = []
        for record in self.records:
            for value in record:
                if isinstance(value, (Node, Path)):
                    entities.append(value)
        return Subgraph(*entities)


class RecordStream(object):
    """ An accessor for a sequence of records yielded by a streamed Cypher statement.

    ::

        for record in graph.cypher.stream("START n=node(*) RETURN n LIMIT 10")
            print record[0]

    Each record returned is cast into a :py:class:`namedtuple` with names
    derived from the resulting column names.

    .. note ::
        Results are available as returned from the server and are decoded
        incrementally. This means that there is no need to wait for the
        entire response to be received before processing can occur.
    """

    def __init__(self, graph, response):
        self.graph = graph
        self.__response = response
        self.__response_item = self.__response_iterator()
        self.columns = next(self.__response_item)
        log.info("stream %r", self.columns)

    def __response_iterator(self):
        producer = None
        columns = []
        record_data = None
        for key, value in self.__response:
            key_len = len(key)
            if key_len > 0:
                section = key[0]
                if section == "columns":
                    if key_len > 1:
                        columns.append(value)
                elif section == "data":
                    if key_len == 1:
                        producer = RecordProducer(columns)
                        yield tuple(columns)
                    elif key_len == 2:
                        if record_data is not None:
                            yield producer.produce(self.graph.hydrate(assembled(record_data)))
                        record_data = []
                    else:
                        record_data.append((key[2:], value))
        if record_data is not None:
            yield producer.produce(self.graph.hydrate(assembled(record_data)))
        self.close()

    def __iter__(self):
        return self

    def __next__(self):
        return next(self.__response_item)

    def next(self):
        return self.__next__()

    def close(self):
        """ Close results and free resources.
        """
        self.__response.close()


class Record(object):
    """ A simple object containing values from a single row of a Cypher
    result. Each value can be retrieved by column position or name,
    supplied as either an index key or an attribute name.

    Consider the record below::

           | person                     | name
        ---+----------------------------+-------
         1 | (n1:Person {name:"Alice"}) | Alice

    If this record is named ``r``, the following expressions
    are equivalent and will return the value ``'Alice'``::

        r[1]
        r["name"]
        r.name

    """

    __producer__ = None

    def __init__(self, values):
        columns = self.__producer__.columns
        for i, column in enumerate(columns):
            setattr(self, column, values[i])

    def __repr__(self):
        out = ""
        columns = self.__producer__.columns
        if columns:
            table = TextTable(columns, border=True)
            table.append([getattr(self, column) for column in columns])
            out = repr(table)
        return out

    def __eq__(self, other):
        return vars(self) == vars(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __len__(self):
        return self.__producer__.__len__()

    def __getitem__(self, item):
        if is_string(item):
            return getattr(self, item)
        elif is_integer(item):
            return getattr(self, self.__producer__.columns[item])
        else:
            raise LookupError(item)


class RecordProducer(object):

    def __init__(self, columns):
        self.__columns = tuple(column for column in columns if not column.startswith("_"))
        self.__len = len(self.__columns)
        dct = dict.fromkeys(self.__columns)
        dct["__producer__"] = self
        self.__type = type(xstr("Record"), (Record,), dct)

    def __repr__(self):
        return "RecordProducer(columns=%r)" % (self.__columns,)

    def __len__(self):
        return self.__len

    @property
    def columns(self):
        return self.__columns

    def produce(self, values):
        """ Produce a record from a set of values.
        """
        return self.__type(values)
