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


from __future__ import division, unicode_literals

import base64
from io import StringIO
import re
from warnings import warn
import webbrowser

from py2neo import __version__
from py2neo.error import BindError, GraphError, JoinError
from py2neo.packages.httpstream import http, ClientError, ServerError, \
    Resource as _Resource, ResourceTemplate as _ResourceTemplate
from py2neo.packages.httpstream.http import JSONResponse, user_agent
from py2neo.packages.httpstream.numbers import NOT_FOUND
from py2neo.packages.httpstream.packages.urimagic import URI
from py2neo.types import cast_property
from py2neo.util import is_collection, is_integer, round_robin, ustr, version_tuple, \
    raise_from, xstr, ThreadLocalWeakValueDictionary


__all__ = ["Graph", "Node", "Relationship", "Path", "NodePointer", "Rel", "Rev", "Subgraph",
           "ServiceRoot", "PropertySet", "LabelSet", "PropertyContainer",
           "authenticate", "rewrite", "ServerPlugin", "UnmanagedExtension",
           "Service", "Resource", "ResourceTemplate"]


DEFAULT_SCHEME = "http"
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 7474
DEFAULT_HOST_PORT = "{0}:{1}".format(DEFAULT_HOST, DEFAULT_PORT)

PRODUCT = ("py2neo", __version__)

NON_ALPHA_NUM = re.compile("[^0-9A-Za-z_]")
SIMPLE_NAME = re.compile(r"[A-Za-z_][0-9A-Za-z_]*")

http.default_encoding = "UTF-8"

_headers = {
    None: [
        ("User-Agent", user_agent(PRODUCT)),
        ("X-Stream", "true"),
    ],
}

_http_rewrites = {}


def _add_header(key, value, host_port=None):
    """ Add an HTTP header to be sent with all requests if no `host_port`
    is provided or only to those matching the value supplied otherwise.
    """
    if host_port in _headers:
        _headers[host_port].append((key, value))
    else:
        _headers[host_port] = [(key, value)]


def _get_headers(host_port):
    """Fetch all HTTP headers relevant to the `host_port` provided.
    """
    uri_headers = {}
    for n, headers in _headers.items():
        if n is None or n == host_port:
            uri_headers.update(headers)
    return uri_headers


def authenticate(host_port, user_name, password):
    """ Set HTTP basic authentication values for specified `host_port`. The
    code below shows a simple example::

        from py2neo import authenticate, Graph

        # set up authentication parameters
        authenticate("camelot:7474", "arthur", "excalibur")

        # connect to authenticated graph database
        graph = Graph("http://camelot:7474/db/data/")

    Note: a `host_port` can be either a server name or a server name and port
    number but must match exactly that used within the Graph
    URI.

    :arg host_port: the host and optional port requiring authentication
        (e.g. "bigserver", "camelot:7474")
    :arg user_name: the user name to authenticate as
    :arg password: the password
    """
    credentials = (user_name + ":" + password).encode("UTF-8")
    value = "Basic " + base64.b64encode(credentials).decode("ASCII")
    _add_header("Authorization", value, host_port=host_port)


def rewrite(from_scheme_host_port, to_scheme_host_port):
    """ Automatically rewrite all URIs directed to the scheme, host and port
    specified in `from_scheme_host_port` to that specified in
    `to_scheme_host_port`.

    As an example::

        from py2neo import rewrite
        # implicitly convert all URIs beginning with <http://localhost:7474>
        # to instead use <https://dbserver:9999>
        rewrite(("http", "localhost", 7474), ("https", "dbserver", 9999))

    If `to_scheme_host_port` is :py:const:`None` then any rewrite rule for
    `from_scheme_host_port` is removed.

    This facility is primarily intended for use by database servers behind
    proxies which are unaware of their externally visible network address.
    """
    global _http_rewrites
    if to_scheme_host_port is None:
        try:
            del _http_rewrites[from_scheme_host_port]
        except KeyError:
            pass
    else:
        _http_rewrites[from_scheme_host_port] = to_scheme_host_port


class Resource(_Resource):
    """ Base class for all local resources mapped to remote counterparts.
    """

    #: The class of error raised by failure responses from this resource.
    error_class = GraphError

    def __init__(self, uri, metadata=None):
        uri = URI(uri)
        scheme_host_port = (uri.scheme, uri.host, uri.port)
        if scheme_host_port in _http_rewrites:
            scheme_host_port = _http_rewrites[scheme_host_port]
            # This is fine - it's all my code anyway...
            uri._URI__set_scheme(scheme_host_port[0])
            uri._URI__set_authority("{0}:{1}".format(scheme_host_port[1],
                                                     scheme_host_port[2]))
        if uri.user_info:
            authenticate(uri.host_port, *uri.user_info.partition(":")[0::2])
        self._resource = _Resource.__init__(self, uri)
        #self._subresources = {}
        self.__headers = _get_headers(self.__uri__.host_port)
        self.__base = super(Resource, self)
        if metadata is None:
            self.__initial_metadata = None
        else:
            self.__initial_metadata = dict(metadata)
        self.__last_get_response = None

        uri = uri.string
        service_root_uri = uri[:uri.find("/", uri.find("//") + 2)] + "/"
        if service_root_uri == uri:
            self.__service_root = self
        else:
            self.__service_root = ServiceRoot(service_root_uri)
        self.__ref = NotImplemented

    @property
    def graph(self):
        """ The parent graph of this resource.

        :rtype: :class:`.Graph`
        """
        return self.__service_root.graph

    @property
    def headers(self):
        """ The HTTP headers sent with this resource.
        """
        return self.__headers

    @property
    def metadata(self):
        """ Metadata received in the last HTTP response.
        """
        if self.__last_get_response is None:
            if self.__initial_metadata is not None:
                return self.__initial_metadata
            self.get()
        return self.__last_get_response.content

    @property
    def ref(self):
        """ The URI of this resource relative to its graph.

        :rtype: string
        """
        if self.__ref is NotImplemented:
            self_uri = self.uri.string
            graph_uri = self.graph.uri.string
            self.__ref = self_uri[len(graph_uri):]
        return self.__ref

    @property
    def service_root(self):
        """ The root service associated with this resource.

        :return: :class:`.ServiceRoot`
        """
        return self.__service_root

    def get(self, headers=None, redirect_limit=5, **kwargs):
        """ Perform an HTTP GET to this resource.

        :arg headers: Extra headers to pass in the request.
        :arg redirect_limit: Maximum number of times to follow redirects.
        :arg kwargs: Other arguments to pass to the underlying `httpstream` method.
        :rtype: :class:`httpstream.Response`
        :raises: :class:`py2neo.GraphError`
        """
        headers = dict(headers or {})
        headers.update(self.__headers)
        kwargs.update(cache=True)
        try:
            response = self.__base.get(headers=headers, redirect_limit=redirect_limit, **kwargs)
        except (ClientError, ServerError) as error:
            if isinstance(error, JSONResponse):
                content = dict(error.content, request=error.request, response=error)
            else:
                content = {}
            message = content.pop("message", "HTTP GET returned response %s" % error.status_code)
            raise_from(self.error_class(message, **content), error)
        else:
            self.__last_get_response = response
            return response

    def put(self, body=None, headers=None, **kwargs):
        """ Perform an HTTP PUT to this resource.

        :arg body: The payload of this request.
        :arg headers: Extra headers to pass in the request.
        :arg kwargs: Other arguments to pass to the underlying `httpstream` method.
        :rtype: :class:`httpstream.Response`
        :raises: :class:`py2neo.GraphError`
        """
        headers = dict(headers or {})
        headers.update(self.__headers)
        try:
            response = self.__base.put(body, headers, **kwargs)
        except (ClientError, ServerError) as error:
            if isinstance(error, JSONResponse):
                content = dict(error.content, request=error.request, response=error)
            else:
                content = {}
            message = content.pop("message", "HTTP PUT returned response %s" % error.status_code)
            raise_from(self.error_class(message, **content), error)
        else:
            return response

    def post(self, body=None, headers=None, **kwargs):
        """ Perform an HTTP POST to this resource.

        :arg body: The payload of this request.
        :arg headers: Extra headers to pass in the request.
        :arg kwargs: Other arguments to pass to the underlying `httpstream` method.
        :rtype: :class:`httpstream.Response`
        :raises: :class:`py2neo.GraphError`
        """
        headers = dict(headers or {})
        headers.update(self.__headers)
        try:
            response = self.__base.post(body, headers, **kwargs)
        except (ClientError, ServerError) as error:
            if isinstance(error, JSONResponse):
                content = dict(error.content, request=error.request, response=error)
            else:
                content = {}
            message = content.pop("message", "HTTP POST returned response %s" % error.status_code)
            raise_from(self.error_class(message, **content), error)
        else:
            return response

    def delete(self, headers=None, **kwargs):
        """ Perform an HTTP DELETE to this resource.

        :arg headers: Extra headers to pass in the request.
        :arg kwargs: Other arguments to pass to the underlying `httpstream` method.
        :rtype: :class:`httpstream.Response`
        :raises: :class:`py2neo.GraphError`
        """
        headers = dict(headers or {})
        headers.update(self.__headers)
        try:
            response = self.__base.delete(headers, **kwargs)
        except (ClientError, ServerError) as error:
            if isinstance(error, JSONResponse):
                content = dict(error.content, request=error.request, response=error)
            else:
                content = {}
            message = content.pop("message", "HTTP DELETE returned response %s" % error.status_code)
            raise_from(self.error_class(message, **content), error)
        else:
            return response


class ResourceTemplate(_ResourceTemplate):
    """ A factory class for producing :class:`.Resource` objects dynamically
    based on a template URI.
    """

    #: The class of error raised by failure responses from resources produced by this template.
    error_class = GraphError

    def expand(self, **values):
        """ Produce a resource instance by substituting values into the
        stored template URI.

        :arg values: A set of named values to plug into the template URI.
        :rtype: :class:`.Resource`
        """
        resource = Resource(self.uri_template.expand(**values))
        resource.error_class = self.error_class
        return resource


class Service(object):
    """ Base class for objects that can be optionally bound to a remote resource. This
    class is essentially a container for a :class:`.Resource` instance.
    """

    #: The class of error raised by failure responses from the contained resource.
    error_class = GraphError

    __resource__ = None

    def bind(self, uri, metadata=None):
        """ Associate this «class.lower» with a remote resource.

        :arg uri: The URI identifying the remote resource to which to bind.
        :arg metadata: Dictionary of initial metadata to attach to the contained resource.

        """
        if "{" in uri and "}" in uri:
            if metadata:
                raise ValueError("Initial metadata cannot be passed to a resource template")
            self.__resource__ = ResourceTemplate(uri)
        else:
            self.__resource__ = Resource(uri, metadata)
        self.__resource__.error_class = self.error_class

    @property
    def bound(self):
        """ :const:`True` if this object is bound to a remote resource,
        :const:`False` otherwise.
        """
        return self.__resource__ is not None

    @property
    def graph(self):
        """ The graph associated with the remote resource.

        :rtype: :class:`.Graph`
        """
        return self.service_root.graph

    @property
    def ref(self):
        """ The URI of the remote resource relative to its graph.

        :rtype: string
        """
        return self.resource.ref

    @property
    def resource(self):
        """ The remote resource to which this object is bound.

        :rtype: :class:`.Resource`
        :raises: :class:`py2neo.BindError`
        """
        if self.bound:
            return self.__resource__
        else:
            raise BindError("Local entity is not bound to a remote entity")

    @property
    def service_root(self):
        """ The root service associated with the remote resource.

        :return: :class:`.ServiceRoot`
        """
        return self.resource.service_root

    def unbind(self):
        """ Detach this object from any remote resource.
        """
        self.__resource__ = None

    @property
    def uri(self):
        """ The full URI of the remote resource.
        """
        resource = self.resource
        try:
            return resource.uri
        except AttributeError:
            return resource.uri_template


class ServiceRoot(object):
    """ Wrapper for the base REST resource exposed by a running Neo4j
    server, corresponding to the ``/`` URI.
    """

    #: The URI for a Neo4j service with default configuration.
    DEFAULT_URI = "{0}://{1}/".format(DEFAULT_SCHEME, DEFAULT_HOST_PORT)

    __instances = {}

    __graph = None

    def __new__(cls, uri=None):
        if uri is None:
            uri = cls.DEFAULT_URI
        if not uri.endswith("/"):
            uri += "/"
        try:
            inst = cls.__instances[uri]
        except KeyError:
            inst = super(ServiceRoot, cls).__new__(cls)
            inst.__resource = Resource(uri)
            inst.__graph = None
            cls.__instances[uri] = inst
        return inst

    @property
    def graph(self):
        """ The graph exposed by this service.

        :rtype: :class:`.Graph`
        """
        if self.__graph is None:
            self.__graph = Graph(self.resource.metadata["data"])
        return self.__graph

    @property
    def resource(self):
        """ The contained resource object for this instance.

        :rtype: :class:`py2neo.Resource`
        """
        return self.__resource

    @property
    def uri(self):
        """ The full URI of the contained resource.
        """
        return self.resource.uri


class Graph(Service):
    """ The `Graph` class provides a wrapper around the
    `REST API <http://docs.neo4j.org/chunked/stable/rest-api.html>`_ exposed
    by a running Neo4j database server and is identified by the base URI
    of the graph database. If no URI is specified, a default value of
    `http://localhost:7474/db/data/` is assumed; therefore, to connect to a
    local server with default configuration, simply use::

        >>> from py2neo import Graph
        >>> graph = Graph()

    An explicitly specified graph database URI can be passed to the constructor
    as a string::

        >>> other_graph = Graph("http://camelot:1138/db/data/")

    If the database server is behind a proxy that requires HTTP authorisation,
    the relevant criteria can also be specified within the URI::

        >>> secure_graph = Graph("http://arthur:excalibur@camelot:1138/db/data/")

    Once obtained, the `Graph` instance provides direct or indirect access
    to most of the functionality available within py2neo.

    """

    __instances = {}

    __batch = None
    __cypher = None
    __legacy = None
    __schema = None
    __node_labels = None
    __relationship_types = None

    # Auto-sync will be removed in 2.1
    auto_sync_properties = False

    @staticmethod
    def cast(obj):
        """ Cast an general Python object to a graph-specific entity,
        such as a :class:`.Node` or a :class:`.Relationship`.
        """
        if obj is None:
            return None
        elif isinstance(obj, (Node, NodePointer, Path, Rel, Relationship, Rev, Subgraph)):
            return obj
        elif isinstance(obj, dict):
            return Node.cast(obj)
        elif isinstance(obj, tuple):
            return Relationship.cast(obj)
        else:
            raise TypeError(obj)

    def __new__(cls, uri=None):
        if uri is None:
            uri = ServiceRoot().graph.uri.string
        if not uri.endswith("/"):
            uri += "/"
        key = (cls, uri)
        try:
            inst = cls.__instances[key]
        except KeyError:
            inst = super(Graph, cls).__new__(cls)
            inst.bind(uri)
            cls.__instances[key] = inst
        return inst

    def __repr__(self):
        return "<Graph uri=%r>" % self.uri.string

    def __hash__(self):
        return hash(self.uri)

    def __len__(self):
        return self.size

    def __bool__(self):
        return True

    def __nonzero__(self):
        return True

    def __contains__(self, entity):
        return entity.bound and entity.uri.string.startswith(entity.uri.string)

    @property
    def batch(self):
        """ A :class:`py2neo.batch.BatchResource` instance attached to this
        graph. This resource exposes methods for submitting iterable
        collections of :class:`py2neo.batch.Job` objects to the server and
        will often be used indirectly via classes such as
        :class:`py2neo.batch.PullBatch` or :class:`py2neo.batch.PushBatch`.

        :rtype: :class:`py2neo.cypher.BatchResource`

        """
        if self.__batch is None:
            from py2neo.batch import BatchResource
            self.__batch = BatchResource(self.resource.metadata["batch"])
        return self.__batch

    @property
    def cypher(self):
        """ The Cypher execution resource for this graph providing access to
        all Cypher functionality for the underlying database, both simple
        and transactional.

        ::

            >>> from py2neo import Graph
            >>> graph = Graph()
            >>> graph.cypher.execute("CREATE (a:Person {name:{N}})", {"N": "Alice"})

        :rtype: :class:`py2neo.cypher.CypherResource`

        """
        if self.__cypher is None:
            from py2neo.cypher import CypherResource
            metadata = self.resource.metadata
            self.__cypher = CypherResource(metadata["cypher"], metadata.get("transaction"))
        return self.__cypher

    def create(self, *entities):
        """ Create one or more remote nodes, relationships or paths in a
        single transaction. The entity values provided must be either
        existing entity objects (such as nodes or relationships) or values
        that can be cast to them.

        For example, to create a remote node from a local :class:`Node` object::

            from py2neo import Graph, Node
            graph = Graph()
            alice = Node("Person", name="Alice")
            graph.create(alice)

        Then, create a second node and a relationship connecting both nodes::

            german, speaks = graph.create({"name": "German"}, (alice, "SPEAKS", 0))

        This second example shows how :class:`dict` and :class:`tuple` objects
        can also be used to create nodes and relationships respectively. The
        zero value in the relationship tuple references the zeroth item created
        within that transaction, i.e. the "German" node.

        .. note::
            If an object is passed to this method that is already bound to
            a remote entity, that argument will be ignored and nothing will
            be created.

        :arg entities: One or more existing graph entities or values that
                       can be cast to entities.
        :return: A tuple of all entities created (or ignored) of the same
                 length and order as the arguments passed in.
        :rtype: tuple

        .. warning::
            This method will *always* return a tuple, even when creating
            only a single entity. To automatically unpack to a single
            item, append a trailing comma to the variable name on the
            left of the assignment operation.

        """
        from py2neo.cypher.create import CreateStatement
        statement = CreateStatement(self)
        for entity in entities:
            statement.create(entity)
        return statement.execute()

    def create_unique(self, *entities):
        """ Create one or more unique paths or relationships in a single
        transaction. This is similar to :meth:`create` but uses a Cypher
        `CREATE UNIQUE <http://docs.neo4j.org/chunked/stable/query-create-unique.html>`_
        clause to ensure that only relationships that do not already exist are created.
        """
        from py2neo.cypher.create import CreateStatement
        statement = CreateStatement(self)
        for entity in entities:
            statement.create_unique(entity)
        return statement.execute()

    def delete(self, *entities):
        """ Delete one or more nodes, relationships and/or paths.
        """
        from py2neo.cypher.delete import DeleteStatement
        statement = DeleteStatement(self)
        for entity in entities:
            statement.delete(entity)
        return statement.execute()

    def delete_all(self):
        """ Delete all nodes and relationships from the graph.

        .. warning::
            This method will permanently remove **all** nodes and relationships
            from the graph and cannot be undone.
        """
        from py2neo.batch import WriteBatch, CypherJob
        batch = WriteBatch(self)
        batch.append(CypherJob("START r=rel(*) DELETE r"))
        batch.append(CypherJob("START n=node(*) DELETE n"))
        batch.run()

    def find(self, label, property_key=None, property_value=None, limit=None):
        """ Iterate through a set of labelled nodes, optionally filtering
        by property key and value
        """
        if not label:
            raise ValueError("Empty label")
        from py2neo.cypher.lang import cypher_escape
        if property_key is None:
            statement = "MATCH (n:%s) RETURN n,labels(n)" % cypher_escape(label)
            parameters = {}
        else:
            statement = "MATCH (n:%s {%s:{V}}) RETURN n,labels(n)" % (
                cypher_escape(label), cypher_escape(property_key))
            parameters = {"V": property_value}
        if limit:
            statement += " LIMIT %s" % limit
        response = self.cypher.post(statement, parameters)
        for record in response.content["data"]:
            dehydrated = record[0]
            dehydrated.setdefault("metadata", {})["labels"] = record[1]
            yield self.hydrate(dehydrated)
        response.close()

    def find_one(self, label, property_key=None, property_value=None):
        """ Find a single node by label and optional property. This method is
        intended to be used with a unique constraint and does not fail if more
        than one matching node is found.
        """
        for node in self.find(label, property_key, property_value, limit=1):
            return node

    def hydrate(self, data):
        """ Hydrate a dictionary of data to produce a :class:`.Node`,
        :class:`.Relationship` or other graph object instance. The
        data structure and values expected are those produced by the
        `REST API <http://neo4j.com/docs/stable/rest-api.html>`__.

        :arg data: dictionary of data to hydrate
        
        """
        if isinstance(data, dict):
            if "self" in data:
                if "type" in data:
                    return Relationship.hydrate(data)
                else:
                    return Node.hydrate(data)
            elif "nodes" in data and "relationships" in data:
                if "directions" not in data:
                    from py2neo.batch import Job, Target
                    node_uris = data["nodes"]
                    relationship_uris = data["relationships"]
                    jobs = [Job("GET", Target(uri)) for uri in relationship_uris]
                    directions = []
                    for i, result in enumerate(self.batch.submit(jobs)):
                        rel_data = result.content
                        start = rel_data["start"]
                        end = rel_data["end"]
                        if start == node_uris[i] and end == node_uris[i + 1]:
                            directions.append("->")
                        else:
                            directions.append("<-")
                    data["directions"] = directions
                return Path.hydrate(data)
            elif "columns" in data and "data" in data:
                from py2neo.cypher import RecordList
                return RecordList.hydrate(data, self)
            elif "neo4j_version" in data:
                return self
            elif "exception" in data and "stacktrace" in data:
                message = data.pop("message", "The server returned an error")
                raise GraphError(message, **data)
            else:
                warn("Map literals returned over the Neo4j REST interface are ambiguous "
                     "and may be hydrated as graph objects")
                return data
        elif is_collection(data):
            return type(data)(map(self.hydrate, data))
        else:
            return data

    @property
    def legacy(self):
        """ Sub-resource providing access to legacy functionality.

        :rtype: :class:`py2neo.legacy.LegacyResource`
        """
        if self.__legacy is None:
            from py2neo.legacy import LegacyResource
            self.__legacy = LegacyResource(self.uri.string)
        return self.__legacy

    def match(self, start_node=None, rel_type=None, end_node=None, bidirectional=False, limit=None):
        """ Return an iterator for all relationships matching the
        specified criteria.

        For example, to find all of Alice's friends::

            for rel in graph.match(start_node=alice, rel_type="FRIEND"):
                print(rel.end_node.properties["name"])

        :arg start_node: :attr:`~py2neo.Node.bound` start :class:`~py2neo.Node` to match or
                           :const:`None` if any
        :arg rel_type: type of relationships to match or :const:`None` if any
        :arg end_node: :attr:`~py2neo.Node.bound` end :class:`~py2neo.Node` to match or
                         :const:`None` if any
        :arg bidirectional: :const:`True` if reversed relationships should also be included
        :arg limit: maximum number of relationships to match or :const:`None` if no limit
        :return: matching relationships
        :rtype: generator
        """
        if start_node is None and end_node is None:
            query = "START a=node(*)"
            params = {}
        elif end_node is None:
            query = "START a=node({A})"
            start_node = Node.cast(start_node)
            if not start_node.bound:
                raise TypeError("Nodes for relationship match end points must be bound")
            params = {"A": start_node}
        elif start_node is None:
            query = "START b=node({B})"
            end_node = Node.cast(end_node)
            if not end_node.bound:
                raise TypeError("Nodes for relationship match end points must be bound")
            params = {"B": end_node}
        else:
            query = "START a=node({A}),b=node({B})"
            start_node = Node.cast(start_node)
            end_node = Node.cast(end_node)
            if not start_node.bound or not end_node.bound:
                raise TypeError("Nodes for relationship match end points must be bound")
            params = {"A": start_node, "B": end_node}
        if rel_type is None:
            rel_clause = ""
        elif is_collection(rel_type):
            separator = "|:" if self.neo4j_version >= (2, 0, 0) else "|"
            rel_clause = ":" + separator.join("`{0}`".format(_)
                                              for _ in rel_type)
        else:
            rel_clause = ":`{0}`".format(rel_type)
        if bidirectional:
            query += " MATCH (a)-[r" + rel_clause + "]-(b) RETURN r"
        else:
            query += " MATCH (a)-[r" + rel_clause + "]->(b) RETURN r"
        if limit is not None:
            query += " LIMIT {0}".format(int(limit))
        results = self.cypher.stream(query, params)
        try:
            for result in results:
                yield result.r
        finally:
            results.close()

    def match_one(self, start_node=None, rel_type=None, end_node=None, bidirectional=False):
        """ Return a single relationship matching the
        specified criteria. See :meth:`~py2neo.Graph.match` for
        argument details.
        """
        rels = list(self.match(start_node, rel_type, end_node,
                               bidirectional, 1))
        if rels:
            return rels[0]
        else:
            return None

    def merge(self, label, property_key=None, property_value=None, limit=None):
        """ Match or create a node by label and optional property and return
        all matching nodes.
        """
        if not label:
            raise ValueError("Empty label")
        from py2neo.cypher.lang import cypher_escape
        if property_key is None:
            statement = "MERGE (n:%s) RETURN n,labels(n)" % cypher_escape(label)
            parameters = {}
        else:
            statement = "MERGE (n:%s {%s:{V}}) RETURN n,labels(n)" % (
                cypher_escape(label), cypher_escape(property_key))
            parameters = {"V": property_value}
        if limit:
            statement += " LIMIT %s" % limit
        response = self.cypher.post(statement, parameters)
        for record in response.content["data"]:
            dehydrated = record[0]
            dehydrated.setdefault("metadata", {})["labels"] = record[1]
            yield self.hydrate(dehydrated)
        response.close()

    def merge_one(self, label, property_key=None, property_value=None):
        """ Match or create a node by label and optional property and return a
        single matching node. This method is intended to be used with a unique
        constraint and does not fail if more than one matching node is found.
        """
        for node in self.merge(label, property_key, property_value, limit=1):
            return node

    @property
    def neo4j_version(self):
        """ The database software version as a 4-tuple of (``int``, ``int``,
        ``int``, ``str``).
        """
        return version_tuple(self.resource.metadata["neo4j_version"])

    def node(self, id_):
        """ Fetch a node by ID. This method creates an object representing the
        remote node with the ID specified but fetches no data from the server.
        For this reason, there is no guarantee that the entity returned
        actually exists.
        """
        resource = self.resource.resolve("node/%s" % id_)
        uri_string = resource.uri.string
        try:
            return Node.cache[uri_string]
        except KeyError:
            data = {"self": uri_string}
            return Node.cache.setdefault(uri_string, Node.hydrate(data))

    @property
    def node_labels(self):
        """ The set of node labels currently defined within the graph.
        """
        if not self.supports_node_labels:
            raise NotImplementedError("Node labels not available for this Neo4j server version")
        if self.__node_labels is None:
            self.__node_labels = Resource(self.uri.string + "labels")
        return frozenset(self.__node_labels.get().content)

    def open_browser(self):
        """ Open a page in the default system web browser pointing at
        the Neo4j browser application for this graph.
        """
        webbrowser.open(self.service_root.resource.uri.string)

    @property
    def order(self):
        """ The number of nodes in this graph.
        """
        return self.cypher.execute_one("START n=node(*) RETURN count(n)")

    def pull(self, *entities):
        """ Pull data to one or more entities from their remote counterparts.
        """
        if entities:
            from py2neo.batch.pull import PullBatch
            batch = PullBatch(self)
            for entity in entities:
                batch.append(entity)
            batch.pull()

    def push(self, *entities):
        """ Push data from one or more entities to their remote counterparts.
        """
        if entities:
            from py2neo.batch.push import PushBatch
            batch = PushBatch(self)
            for entity in entities:
                batch.append(entity)
            batch.push()

    def relationship(self, id_):
        """ Fetch a relationship by ID.
        """
        resource = self.resource.resolve("relationship/" + str(id_))
        uri_string = resource.uri.string
        try:
            return Relationship.cache[uri_string]
        except KeyError:
            try:
                return Relationship.cache.setdefault(
                    uri_string, Relationship.hydrate(resource.get().content))
            except ClientError:
                raise ValueError("Relationship with ID %s not found" % id_)

    @property
    def relationship_types(self):
        """ The set of relationship types currently defined within the graph.
        """
        if self.__relationship_types is None:
            self.__relationship_types = Resource(self.uri.string + "relationship/types")
        return frozenset(self.__relationship_types.get().content)

    @property
    def schema(self):
        """ The schema resource for this graph.

        :rtype: :class:`SchemaResource <py2neo.schema.SchemaResource>`
        """
        if self.__schema is None:
            from py2neo.schema import SchemaResource
            self.__schema = SchemaResource(self.uri.string + "schema")
        return self.__schema

    @property
    def size(self):
        """ The number of relationships in this graph.
        """
        return self.cypher.execute_one("START r=rel(*) RETURN count(r)")

    @property
    def supports_cypher_transactions(self):
        """ Indicates whether the server supports explicit Cypher transactions.
        """
        return "transaction" in self.resource.metadata

    @property
    def supports_foreach_pipe(self):
        """ Indicates whether the server supports pipe syntax for FOREACH.
        """
        return self.neo4j_version >= (2, 0)

    @property
    def supports_node_labels(self):
        """ Indicates whether the server supports node labels.
        """
        return self.neo4j_version >= (2, 0)

    @property
    def supports_optional_match(self):
        """ Indicates whether the server supports Cypher OPTIONAL MATCH
        clauses.
        """
        return self.neo4j_version >= (2, 0)

    @property
    def supports_schema_indexes(self):
        """ Indicates whether the server supports schema indexes.
        """
        return self.neo4j_version >= (2, 0)


class PropertySet(Service, dict):
    """ A dict subclass that equates None with a non-existent key and can be
    bound to a remote *properties* resource.
    """

    def __init__(self, iterable=None, **kwargs):
        Service.__init__(self)
        dict.__init__(self)
        self.update(iterable, **kwargs)

    def __eq__(self, other):
        if not isinstance(other, PropertySet):
            other = PropertySet(other)
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        x = 0
        for key, value in self.items():
            if isinstance(value, list):
                x ^= hash((key, tuple(value)))
            else:
                x ^= hash((key, value))
        return x

    def __getitem__(self, key):
        return dict.get(self, key)

    def __setitem__(self, key, value):
        if value is None:
            try:
                dict.__delitem__(self, key)
            except KeyError:
                pass
        else:
            dict.__setitem__(self, key, cast_property(value))

    def pull(self):
        """ Copy the set of remote properties onto the local set.
        """
        self.resource.get()
        properties = self.resource.metadata
        self.replace(properties or {})

    def push(self):
        """ Copy the set of local properties onto the remote set.
        """
        self.resource.put(self)

    def replace(self, iterable=None, **kwargs):
        self.clear()
        self.update(iterable, **kwargs)

    def setdefault(self, key, default=None):
        if key in self:
            value = self[key]
        elif default is None:
            value = None
        else:
            value = dict.setdefault(self, key, default)
        return value

    def update(self, iterable=None, **kwargs):
        if iterable:
            try:
                for key in iterable.keys():
                    self[key] = iterable[key]
            except (AttributeError, TypeError):
                for key, value in iterable:
                    self[key] = value
        for key in kwargs:
            self[key] = kwargs[key]


class LabelSet(Service, set):
    """ A set subclass that can be bound to a remote *labels* resource.
    """

    def __init__(self, iterable=None):
        Service.__init__(self)
        set.__init__(self)
        if iterable:
            self.update(iterable)

    def __eq__(self, other):
        if not isinstance(other, LabelSet):
            other = LabelSet(other)
        return set.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        value = 0
        for label in self:
            value ^= hash(label)
        return value

    def pull(self):
        """ Copy the set of remote labels onto the local set.
        """
        self.resource.get()
        labels = self.resource.metadata
        self.replace(labels or [])

    def push(self):
        """ Copy the set of local labels onto the remote set.
        """
        self.resource.put(self)

    def replace(self, iterable):
        self.clear()
        self.update(iterable)


class PropertyContainer(Service):
    """ Base class for objects that contain a set of properties,
    i.e. :py:class:`Node` and :py:class:`Relationship`.
    """

    def __init__(self, **properties):
        Service.__init__(self)
        self.__properties = PropertySet(properties)
        # Auto-sync will be removed in 2.1
        self.auto_sync_properties = Graph.auto_sync_properties

    def __eq__(self, other):
        return self.properties == other.properties

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.__properties)

    def __contains__(self, key):
        self.__pull_if_bound()
        return key in self.properties

    def __getitem__(self, key):
        self.__pull_if_bound()
        return self.properties.__getitem__(key)

    def __setitem__(self, key, value):
        self.properties.__setitem__(key, value)
        self.__push_if_bound()

    def __delitem__(self, key):
        self.properties.__delitem__(key)
        self.__push_if_bound()

    def bind(self, uri, metadata=None):
        """ Associate this «class.lower» with a remote resource.

        :arg uri: The URI identifying the remote resource to which to bind.
        :arg metadata: Dictionary of initial metadata to attach to the contained resource.

        """
        Service.bind(self, uri, metadata)
        self.__properties.bind(uri + "/properties")

    @property
    def properties(self):
        """ The set of properties attached to this «class.lower». Properties
        can also be read from and written to any :class:`PropertyContainer`
        by using the index syntax directly.
        """
        return self.__properties

    def pull(self):
        """ Pull data to this «class.lower» from its remote counterpart.
        """
        self.resource.get()
        properties = self.resource.metadata["data"]
        self.__properties.replace(properties or {})

    def push(self):
        """ Push data from this «class.lower» to its remote counterpart.
        """
        self.__properties.push()

    def unbind(self):
        """ Detach this «class.lower» from any remote counterpart.
        """
        Service.unbind(self)
        self.__properties.unbind()

    def __pull_if_bound(self):
        # remove in 2.1
        if self.auto_sync_properties:
            try:
                self.properties.pull()
            except BindError:
                pass

    def __push_if_bound(self):
        # remove in 2.1
        if self.auto_sync_properties:
            try:
                self.properties.push()
            except BindError:
                pass


class Node(PropertyContainer):
    """ A graph node that may optionally be bound to a remote counterpart
    in a Neo4j database. Nodes may contain a set of named :attr:`~py2neo.Node.properties` and
    may have one or more :attr:`.labels` applied to them::

        >>> from py2neo import Node
        >>> alice = Node("Person", name="Alice")
        >>> banana = Node("Fruit", "Food", colour="yellow", tasty=True)

    All positional arguments passed to the constructor are interpreted
    as labels and all keyword arguments as properties. It is also possible to
    construct Node instances from other data types (such as a dictionary)
    by using the :meth:`.Node.cast` class method::

        >>> bob = Node.cast({"name": "Bob Robertson", "age": 44})

    Labels and properties can be accessed and modified using the
    :attr:`.labels` and :attr:`~py2neo.Node.properties` attributes respectively.
    The former is an instance of :class:`.LabelSet`, which extends the
    built-in :class:`set` class, and the latter is an instance of
    :class:`.PropertySet` which extends :class:`dict`.

        >>> alice.properties["name"]
        'Alice'
        >>> alice.labels
        {'Person'}
        >>> alice.labels.add("Employee")
        >>> alice.properties["employee_no"] = 3456
        >>> alice
        <Node labels={'Employee', 'Person'} properties={'employee_no': 3456, 'name': 'Alice'}>

    One of the core differences between a :class:`.PropertySet` and a standard
    dictionary is in how it handles :const:`None` and missing values. As with actual Neo4j
    properties, missing values and those equal to :const:`None` are equivalent.
    """

    cache = ThreadLocalWeakValueDictionary()

    __id = None

    @staticmethod
    def cast(*args, **kwargs):
        """ Cast the arguments provided to a :class:`.Node` (or
        :class:`.NodePointer`). The following combinations of
        arguments are possible::

            >>> Node.cast(None)
            >>> Node.cast()
            <Node labels=set() properties={}>
            >>> Node.cast("Person")
            <Node labels={'Person'} properties={}>
            >>> Node.cast(name="Alice")
            <Node labels=set() properties={'name': 'Alice'}>
            >>> Node.cast("Person", name="Alice")
            <Node labels={'Person'} properties={'name': 'Alice'}>
            >>> Node.cast(123)
            <NodePointer address=123>
            >>> Node.cast({"name": "Alice"})
            <Node labels=set() properties={'name': 'Alice'}>
            >>> node = Node("Person", name="Alice")
            >>> Node.cast(node)
            <Node labels={'Person'} properties={'name': 'Alice'}>

        """
        if len(args) == 1 and not kwargs:
            from py2neo.batch import Job
            arg = args[0]
            if arg is None:
                return None
            elif isinstance(arg, (Node, NodePointer, Job)):
                return arg
            elif is_integer(arg):
                return NodePointer(arg)

        inst = Node()

        def apply(x):
            if isinstance(x, dict):
                inst.properties.update(x)
            elif is_collection(x):
                for item in x:
                    apply(item)
            else:
                inst.labels.add(ustr(x))

        for arg in args:
            apply(arg)
        inst.properties.update(kwargs)
        return inst

    @classmethod
    def hydrate(cls, data, inst=None):
        """ Hydrate a dictionary of data to produce a :class:`.Node` instance.
        The data structure and values expected are those produced by the
        `REST API <http://neo4j.com/docs/stable/rest-api-nodes.html#rest-api-get-node>`__
        although only the ``self`` value is required.

        :arg data: dictionary of data to hydrate
        :arg inst: an existing :class:`.Node` instance to overwrite with new values

        """
        self = data["self"]
        if inst is None:
            new_inst = cls()
            new_inst.__stale.update({"labels", "properties"})
            inst = cls.cache.setdefault(self, new_inst)
        cls.cache[self] = inst
        inst.bind(self, data)
        if "data" in data:
            inst.__stale.discard("properties")
            properties = data["data"]
            properties.update(inst.properties)
            inst._PropertyContainer__properties.replace(properties)
        if "metadata" in data:
            inst.__stale.discard("labels")
            metadata = data["metadata"]
            labels = set(metadata["labels"])
            labels.update(inst.labels)
            inst.__labels.replace(labels)
        return inst

    @classmethod
    def __joinable(cls, obj):
        from py2neo.batch import Job
        return obj is None or isinstance(obj, (Node, NodePointer, Job))

    @classmethod
    def join(cls, n, m):
        # Attempt to join two nodes together as single node.
        if not cls.__joinable(n) or not cls.__joinable(m):
            raise TypeError("Can only join Node, NodePointer, Job or None")
        if n is None:
            return m
        elif m is None or n is m:
            return n
        elif isinstance(n, NodePointer) or isinstance(m, NodePointer):
            if isinstance(n, NodePointer) and isinstance(m, NodePointer) and n.address == m.address:
                return n
        elif n.bound and m.bound:
            if n.resource == m.resource:
                return n
        raise JoinError("Cannot join nodes {} and {}".format(n, m))

    def __init__(self, *labels, **properties):
        PropertyContainer.__init__(self, **properties)
        self.__labels = LabelSet(labels)
        self.__stale = set()

    def __repr__(self):
        s = [self.__class__.__name__]
        if self.bound:
            s.append("graph=%r" % self.graph.uri.string)
            s.append("ref=%r" % self.ref)
            if "labels" in self.__stale:
                s.append("labels=?")
            else:
                s.append("labels=%r" % set(self.labels))
            if "properties" in self.__stale:
                s.append("properties=?")
            else:
                s.append("properties=%r" % self.properties)
        else:
            s.append("labels=%r" % set(self.labels))
            s.append("properties=%r" % self.properties)
        return "<" + " ".join(s) + ">"

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        from py2neo.cypher import CypherWriter
        string = StringIO()
        writer = CypherWriter(string)
        if self.bound:
            writer.write_node(self, "n" + ustr(self._id))
        else:
            writer.write_node(self)
        return string.getvalue()

    def __eq__(self, other):
        if other is None:
            return False
        other = Node.cast(other)
        if self.bound and other.bound:
            return self.resource == other.resource
        else:
            return (LabelSet.__eq__(self.labels, other.labels) and
                    PropertyContainer.__eq__(self, other))

    def __hash__(self):
        value = super(Node, self).__hash__() ^ hash(self.labels)
        if self.bound:
            value ^= hash(self.resource.uri)
        return value

    def __add__(self, other):
        return Path(self, other)

    @property
    def _id(self):
        """ The internal ID of this node within the database.
        """
        if self.__id is None:
            self.__id = int(self.uri.path.segments[-1])
        return self.__id

    @property
    def ref(self):
        """ The URI of this node relative to its graph.

        :rtype: string
        """
        return "node/%s" % self._id

    def bind(self, uri, metadata=None):
        """ Associate this node with a remote node.

        :arg uri: The URI identifying the remote node to which to bind.
        :arg metadata: Dictionary of initial metadata to attach to the contained resource.

        """
        PropertyContainer.bind(self, uri, metadata)
        if self.graph.supports_node_labels:
            self.__labels.bind(uri + "/labels")
        else:
            from py2neo.legacy.core import LegacyNode
            self.__class__ = LegacyNode
        self.cache[uri] = self

    @property
    def degree(self):
        """ The number of relationships attached to this node.
        """
        statement = "START n=node({n}) MATCH (n)-[r]-() RETURN count(r)"
        return self.graph.cypher.execute_one(statement, {"n": self})

    @property
    def exists(self):
        """ :const:`True` if this node exists in the database,
        :const:`False` otherwise.
        """
        try:
            self.resource.get()
        except GraphError as error:
            if error.__cause__ and error.__cause__.status_code == NOT_FOUND:
                return False
            else:
                raise
        else:
            return True

    @property
    def labels(self):
        """ The set of labels attached to this node.
        """
        if self.bound and "labels" in self.__stale:
            self.refresh()
        return self.__labels

    def match(self, rel_type=None, other_node=None, limit=None):
        """ Return an iterator for all relationships attached to this node
        that match the specified criteria. See :meth:`.Graph.match` for
        argument details.
        """
        return self.graph.match(self, rel_type, other_node, True, limit)

    def match_incoming(self, rel_type=None, start_node=None, limit=None):
        """ Return an iterator for all incoming relationships to this node
        that match the specified criteria. See :meth:`.Graph.match` for
        argument details.
        """
        return self.graph.match(start_node, rel_type, self, False, limit)

    def match_outgoing(self, rel_type=None, end_node=None, limit=None):
        """ Return an iterator for all outgoing relationships from this node
        that match the specified criteria. See :meth:`.Graph.match` for
        argument details.
        """
        return self.graph.match(self, rel_type, end_node, False, limit)

    @property
    def properties(self):
        """ The set of properties attached to this node. Properties
        can also be read from and written to any :class:`Node`
        by using the index syntax directly. This means
        the following statements are equivalent::

            node.properties["name"] = "Alice"
            node["name"] = "Alice"

        """
        if self.bound and "properties" in self.__stale:
            self.refresh()
        return super(Node, self).properties

    def pull(self):
        """ Pull data to this node from its remote counterpart. Consider
        using :meth:`.Graph.pull` instead for batches of nodes.
        """
        super(Node, self).properties.clear()
        self.__labels.clear()
        self.refresh()

    def push(self):
        """ Push data from this node to its remote counterpart. Consider
        using :meth:`.Graph.push` instead for batches of nodes.
        """
        from py2neo.batch.push import PushBatch
        batch = PushBatch(self.graph)
        batch.append(self)
        batch.push()

    def refresh(self):
        # Non-destructive pull.
        query = "START a=node({a}) RETURN a,labels(a)"
        content = self.graph.cypher.post(query, {"a": self._id}).content
        dehydrated, label_metadata = content["data"][0]
        dehydrated.setdefault("metadata", {})["labels"] = label_metadata
        Node.hydrate(dehydrated, self)

    def unbind(self):
        """ Detach this node from any remote counterpart.
        """
        try:
            del self.cache[self.uri]
        except KeyError:
            pass
        PropertyContainer.unbind(self)
        self.__labels.unbind()
        self.__id = None


class NodePointer(object):
    """ Pointer to a :class:`Node` object. This can be used in a batch
    context to point to a node not yet created.
    """

    #: The address or index to which this pointer points.
    address = None

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return "<NodePointer address=%s>" % self.address

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        return "{%s}" % self.address

    def __eq__(self, other):
        return self.address == other.address

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.address)


class Rel(PropertyContainer):
    """ A :class:`.Rel` is similar to a :class:`.Relationship` but does not
    store information about the nodes to which it is attached. This class
    is used internally to bundle relationship type and property details
    for :class:`.Relationship` and :class:`.Path` objects but may also be
    used to denote an explicit forward relationship within a :class:`.Path`.

    .. seealso:: :class:`py2neo.Rev`

    """

    cache = ThreadLocalWeakValueDictionary()
    pair = None
    _pair_class = object

    __id = None

    @staticmethod
    def cast(*args, **kwargs):
        """ Cast the arguments provided to a :class:`.«class»`. The
        following combinations of arguments are possible::

            >>> «class».cast(None)
            >>> «class».cast()
            <«class» type=None properties={}>
            >>> «class».cast("KNOWS")
            <«class» type='KNOWS' properties={}>
            >>> «class».cast("KNOWS", since=1999)
            <«class» type='KNOWS' properties={'since': 1999}>
            >>> «class».cast("KNOWS", {"since": 1999})
            <«class» type='KNOWS' properties={'since': 1999}>
            >>> «class».cast(("KNOWS",))
            <«class» type='KNOWS' properties={}>
            >>> «class».cast(("KNOWS", {"since": 1999}))
            <«class» type='KNOWS' properties={'since': 1999}>
            >>> «class.lower» = «class»("KNOWS", since=1999)
            >>> «class».cast(«class.lower»)
            <«class» type='KNOWS' properties={'since': 1999}>

        """
        if len(args) == 1 and not kwargs:
            from py2neo.batch import Job
            arg = args[0]
            if arg is None:
                return None
            elif isinstance(arg, (Rel, Job)):
                return arg
            elif isinstance(arg, Relationship):
                return arg.rel

        inst = Rel()

        def apply(x):
            if isinstance(x, dict):
                inst.properties.update(x)
            elif is_collection(x):
                for item in x:
                    apply(item)
            else:
                inst.type = ustr(x)

        for arg in args:
            apply(arg)
        inst.properties.update(kwargs)
        return inst

    @classmethod
    def hydrate(cls, data, inst=None):
        """ Hydrate a dictionary of data to produce a :class:`.«class»` instance.
        The data structure and values expected are those produced by the
        `REST API <http://neo4j.com/docs/stable/rest-api-relationships.html#rest-api-get-relationship-by-id>`__
        although only the ``self`` value is required.

        :arg data: dictionary of data to hydrate
        :arg inst: an existing :class:`.«class»` instance to overwrite with new values

        """
        self = data["self"]
        if inst is None:
            new_inst = cls()
            new_inst.__stale.update({"properties"})
            inst = cls.cache.setdefault(self, new_inst)
        cls.cache[self] = inst
        inst.bind(self, data)
        inst.__type = data.get("type")
        pair = inst.pair
        if pair is not None:
            pair._Rel__type = inst.__type
        if "data" in data:
            inst.__stale.discard("properties")
            properties = data["data"]
            properties.update(inst.properties)
            inst._PropertyContainer__properties.replace(properties)
        return inst

    def __init__(self, *type_, **properties):
        if len(type_) > 1:
            raise ValueError("Only one relationship type can be specified")
        PropertyContainer.__init__(self, **properties)
        self.__type = type_[0] if type_ else None
        self.__stale = set()

    def __repr__(self):
        s = [self.__class__.__name__]
        if self.bound:
            s.append("graph=%r" % self.graph.uri.string)
            s.append("ref=%r" % self.ref)
            if self.__type is None:
                s.append("type=?")
            else:
                s.append("type=%r" % self.type)
            if "properties" in self.__stale:
                s.append("properties=?")
            else:
                s.append("properties=%r" % self.properties)
        else:
            s.append("type=%r" % self.type)
            s.append("properties=%r" % self.properties)
        return "<" + " ".join(s) + ">"

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        from py2neo.cypher import CypherWriter
        string = StringIO()
        writer = CypherWriter(string)
        if self.bound:
            writer.write_rel(self, "r" + ustr(self._id))
        else:
            writer.write_rel(self)
        return string.getvalue()

    def __eq__(self, other):
        if other is None:
            return False
        other = Rel.cast(other)
        if self.bound and other.bound:
            return self.resource == other.resource
        else:
            return self.type == other.type and self.properties == other.properties

    def __hash__(self):
        value = super(Rel, self).__hash__() ^ hash(self.type)
        if self.bound:
            value ^= hash(self.resource.uri)
        return value

    def __pos__(self):
        return self

    def __neg__(self):
        if self.pair is None:
            self.pair = self._pair_class()
            self.pair.__resource__ = self.__resource__
            self.pair._PropertyContainer__properties = self._PropertyContainer__properties
            self.pair._Rel__type = self.__type
            self.pair._Rel__stale = self.__stale
            self.pair.pair = self
        return self.pair

    def __abs__(self):
        return self

    @property
    def _id(self):
        """ The internal ID of this relationship within the database.
        """
        if self.__id is None:
            self.__id = int(self.uri.path.segments[-1])
        return self.__id

    @property
    def ref(self):
        """ The URI of this relationship relative to its graph.

        :rtype: string
        """
        return "relationship/%s" % self._id

    def bind(self, uri, metadata=None):
        """ Associate this object with a remote relationship.

        :arg uri: The URI identifying the remote relationship to which to bind.
        :arg metadata: Dictionary of initial metadata to attach to the contained resource.

        """
        PropertyContainer.bind(self, uri, metadata)
        self.cache[uri] = self
        pair = self.pair
        if pair is not None:
            PropertyContainer.bind(pair, uri, metadata)
            # make sure we're using exactly the same resource object
            # (maybe could write a Service.multi_bind classmethod
            pair.__resource__ = self.__resource__
            pair.cache[uri] = pair

    @property
    def exists(self):
        """ :const:`True` if this relationship exists in the database,
        :const:`False` otherwise.
        """
        try:
            self.resource.get()
        except GraphError as error:
            if error.__cause__ and error.__cause__.status_code == NOT_FOUND:
                return False
            else:
                raise
        else:
            return True

    @property
    def properties(self):
        """ The set of properties attached to this relationship. Properties
        can also be read from and written to any :class:`Rel`
        by using the index syntax directly. This means
        the following statements are equivalent::

            rel.properties["since"] = 1999
            rel["since"] = 1999

        """
        if self.bound and "properties" in self.__stale:
            self.refresh()
        return super(Rel, self).properties

    def pull(self):
        """ Pull data to this relationship from its remote counterpart.
        """
        super(Rel, self).properties.clear()
        self.refresh()

    def push(self):
        """ Push data from this relationship to its remote counterpart.
        """
        super(Rel, self).push()

    def refresh(self):
        # Non-destructive pull.
        super(Rel, self).pull()
        pulled_type = self.resource.metadata["type"]
        self.__type = pulled_type
        pair = self.pair
        if pair is not None:
            pair._Rel__type = pulled_type
        self.__stale.clear()

    @property
    def type(self):
        """ The type of this relationship.
        """
        if self.bound and self.__type is None:
            self.pull()
        return self.__type

    @type.setter
    def type(self, name):
        """ Set the type of this relationship (only possible if not bound).
        """
        if self.bound:
            raise AttributeError("The type of a bound Rel is immutable")
        self.__type = name
        pair = self.pair
        if pair is not None:
            pair._Rel__type = name

    def unbind(self):
        """ Detach this relationship from any remote counterpart.
        """
        try:
            del self.cache[self.uri]
        except KeyError:
            pass
        PropertyContainer.unbind(self)
        self.__id = None
        pair = self.pair
        if pair is not None:
            try:
                del pair.cache[pair.uri]
            except KeyError:
                pass
            PropertyContainer.unbind(pair)


class Rev(Rel):
    """ A :class:`.Rev` is identical to a :class:`.Rel` but denotes a
    reversed relationship rather than a forward one. The following
    example shows how to build a :class:`.Path` with one forward and
    one reversed relationship::

        >>> path = Path(Node(name="A"), Rel("TO"), Node(name="B"), Rev("TO"), Node(name="C"))
        >>> for relationship in path.relationships:
        ...     print(relationship)
        ({name:"A"})-[:TO]->({name:"B"})
        ({name:"C"})-[:TO]->({name:"B"})

    .. seealso:: :class:`py2neo.Rel`

    """

    _pair_class = Rel

    def __abs__(self):
        return self.__neg__()

    def __hash__(self):
        return -(super(Rev, self).__hash__())


Rel._pair_class = Rev


class Path(object):
    """ A sequence of nodes connected by relationships that may
    optionally be bound to remote counterparts in a Neo4j database.

        >>> from py2neo import Node, Path, Rev
        >>> alice, bob, carol = Node(name="Alice"), Node(name="Bob"), Node(name="Carol")
        >>> abc = Path(alice, "KNOWS", bob, Rev("KNOWS"), carol)
        >>> abc
        <Path order=3 size=2>
        >>> abc.nodes
        (<Node labels=set() properties={'name': 'Alice'}>,
         <Node labels=set() properties={'name': 'Bob'}>,
         <Node labels=set() properties={'name': 'Carol'}>)
        >>> abc.rels
        (<Rel type='KNOWS' properties={}>, <Rev type='KNOWS' properties={}>)
        >>> abc.relationships
        (<Relationship type='KNOWS' properties={}>,
         <Relationship type='KNOWS' properties={}>)
        >>> dave, eve = Node(name="Dave"), Node(name="Eve")
        >>> de = Path(dave, "KNOWS", eve)
        >>> de
        <Path order=2 size=1>
        >>> abcde = Path(abc, "KNOWS", de)
        >>> abcde
        <Path order=5 size=4>
        >>> for relationship in abcde.relationships:
        ...     print(relationship)
        ({name:"Alice"})-[:KNOWS]->({name:"Bob"})
        ({name:"Carol"})-[:KNOWS]->({name:"Bob"})
        ({name:"Carol"})-[:KNOWS]->({name:"Dave"})
        ({name:"Dave"})-[:KNOWS]->({name:"Eve"})

    """

    @classmethod
    def hydrate(cls, data, inst=None):
        """ Hydrate a dictionary of data to produce a :class:`.Path` instance.
        The data structure and values expected are those produced by the
        `REST API <http://neo4j.com/docs/stable/rest-api-graph-algos.html#rest-api-find-one-of-the-shortest-paths>`__.

        :arg data: dictionary of data to hydrate
        :arg inst: an existing :class:`.Path` instance to overwrite with new values

        """
        node_uris = data["nodes"]
        relationship_uris = data["relationships"]
        rel_rev = [Rel if direction == "->" else Rev for direction in data["directions"]]
        if inst is None:
            nodes = [Node.hydrate({"self": uri}) for uri in node_uris]
            rels = [rel_rev[i].hydrate({"self": uri}) for i, uri in enumerate(relationship_uris)]
            inst = Path(*round_robin(nodes, rels))
        else:
            for i, node in enumerate(inst.nodes):
                uri = node_uris[i]
                Node.hydrate({"self": uri}, node)
            for i, rel in enumerate(inst.rels):
                uri = relationship_uris[i]
                rel_rev[i].hydrate({"self": uri}, rel)
        inst.__metadata = data
        return inst

    def __init__(self, *entities):
        nodes = []
        rels = []

        def join_path(path, index):
            if len(nodes) == len(rels):
                nodes.extend(path.nodes)
                rels.extend(path.rels)
            else:
                # try joining forward
                try:
                    nodes[-1] = Node.join(nodes[-1], path.start_node)
                except JoinError:
                    # try joining backward
                    try:
                        nodes[-1] = Node.join(nodes[-1], path.end_node)
                    except JoinError:
                        raise JoinError("Path at position %s cannot be joined" % index)
                    else:
                        nodes.extend(path.nodes[-2::-1])
                        rels.extend(-r for r in path.rels[::-1])
                else:
                    nodes.extend(path.nodes[1:])
                    rels.extend(path.rels)

        def join_rel(rel, index):
            if len(nodes) == len(rels):
                raise JoinError("Rel at position %s cannot be joined" % index)
            else:
                rels.append(rel)

        def join_node(node):
            if len(nodes) == len(rels):
                nodes.append(node)
            else:
                nodes[-1] = Node.join(nodes[-1], node)

        for i, entity in enumerate(entities):
            if isinstance(entity, Path):
                join_path(entity, i)
            elif isinstance(entity, Rel):
                join_rel(entity, i)
            elif isinstance(entity, (Node, NodePointer)):
                join_node(entity)
            elif len(nodes) == len(rels):
                join_node(Node.cast(entity))
            else:
                join_rel(Rel.cast(entity), i)
        join_node(None)

        self.__nodes = tuple(nodes)
        self.__rels = tuple(rels)
        self.__relationships = None
        self.__order = len(self.__nodes)
        self.__size = len(self.__rels)
        self.__metadata = None

    def __repr__(self):
        s = [self.__class__.__name__]
        if self.bound:
            s.append("graph=%r" % self.graph.uri.string)
            s.append("start=%r" % self.start_node.ref)
            s.append("end=%r" % self.end_node.ref)
        s.append("order=%r" % self.order)
        s.append("size=%r" % self.size)
        return "<" + " ".join(s) + ">"

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        from py2neo.cypher import CypherWriter
        string = StringIO()
        writer = CypherWriter(string)
        writer.write_path(self)
        return string.getvalue()

    def __eq__(self, other):
        try:
            return self.nodes == other.nodes and self.rels == other.rels
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        value = 0
        for entity in self.rels + self.nodes:
            value ^= hash(entity)
        return value

    def __bool__(self):
        return bool(self.rels)

    def __nonzero__(self):
        return bool(self.rels)

    def __len__(self):
        return self.size

    def __getitem__(self, item):
        try:
            if isinstance(item, slice):
                path = Path()
                p, q = item.start, item.stop
                if q is not None:
                    q += 1
                path.__nodes = self.nodes[p:q]
                path.__rels = self.rels[item]
                return path
            else:
                if item >= 0:
                    start_node = self.nodes[item]
                    end_node = self.nodes[item + 1]
                else:
                    start_node = self.nodes[item - 1]
                    end_node = self.nodes[item]
                return Relationship(start_node, self.rels[item], end_node)
        except IndexError:
            raise IndexError("Path segment index out of range")

    def __iter__(self):
        return iter(self.relationships)

    def __reversed__(self):
        return iter(reversed(self.relationships))

    def __add__(self, other):
        return Path(self, other)

    @property
    def bound(self):
        """ :const:`True` if this path is bound to a remote counterpart,
        :const:`False` otherwise.
        """
        try:
            _ = self.service_root
        except BindError:
            return False
        else:
            return True

    @property
    def end_node(self):
        """ The end node of this «class.lower».

        :return: :class:`.Node`
        """
        return self.__nodes[-1]

    @property
    def exists(self):
        """ :const:`True` if this path exists in the database,
        :const:`False` otherwise.
        """
        return all(entity.exists for entity in self.nodes + self.rels)

    @property
    def graph(self):
        """ The parent graph of this path.

        :rtype: :class:`.Graph`
        """
        return self.service_root.graph

    @property
    def nodes(self):
        """ A tuple of all nodes in this «class.lower».
        """
        return self.__nodes

    @property
    def order(self):
        """ The number of nodes in this «class.lower».
        """
        return self.__order

    def pull(self):
        """ Pull data to all entities in this path from their remote counterparts.
        """
        from py2neo.batch.pull import PullBatch
        batch = PullBatch(self.graph)
        for relationship in self:
            batch.append(relationship)
        batch.pull()

    def push(self):
        """ Push data from all entities in this path to their remote counterparts.
        """
        from py2neo.batch.push import PushBatch
        batch = PushBatch(self.graph)
        for relationship in self:
            batch.append(relationship)
        batch.push()

    @property
    def relationships(self):
        """ A tuple of all relationships in this «class.lower».
        """
        if self.__relationships is None:
            self.__relationships = tuple(
                Relationship(self.nodes[i], rel, self.nodes[i + 1])
                for i, rel in enumerate(self.rels)
            )
        return self.__relationships

    @property
    def rels(self):
        """ A tuple of all rels in this «class.lower».
        """
        return self.__rels

    @property
    def service_root(self):
        """ The root service associated with this path.

        :return: :class:`.ServiceRoot`
        """
        for relationship in self:
            try:
                return relationship.service_root
            except BindError:
                pass
        raise BindError("Local path is not bound to a remote path")

    @property
    def size(self):
        """ The number of relationships in this «class.lower».
        """
        return self.__size

    @property
    def start_node(self):
        """ The start node of this «class.lower».

        :return: :class:`.Node`
        """
        return self.__nodes[0]

    def unbind(self):
        """ Detach all entities in this path
        from any remote counterparts.
        """
        for entity in self.rels + self.nodes:
            try:
                entity.unbind()
            except BindError:
                pass


class Relationship(Path):
    """ A graph relationship that may optionally be bound to a remote counterpart
    in a Neo4j database. Relationships require a type name and may contain a set
    of named :attr:`~py2neo.Node.properties`.

    .. seealso::
       :class:`py2neo.Rel`
       :class:`py2neo.Rev`

    """

    cache = ThreadLocalWeakValueDictionary()

    __id = None

    @staticmethod
    def cast(*args, **kwargs):
        """ Cast the arguments provided to a :class:`.Relationship`. The
        following combinations of arguments are possible::

            >>> Relationship.cast(Node(), "KNOWS", Node())
            <Relationship type='KNOWS' properties={}>
            >>> Relationship.cast((Node(), "KNOWS", Node()))
            <Relationship type='KNOWS' properties={}>
            >>> Relationship.cast(Node(), "KNOWS", Node(), since=1999)
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast(Node(), "KNOWS", Node(), {"since": 1999})
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast((Node(), "KNOWS", Node(), {"since": 1999}))
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast(Node(), ("KNOWS", {"since": 1999}), Node())
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast((Node(), ("KNOWS", {"since": 1999}), Node()))
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast(Node(), Rel("KNOWS", since=1999), Node())
            <Relationship type='KNOWS' properties={'since': 1999}>
            >>> Relationship.cast((Node(), Rel("KNOWS", since=1999), Node()))
            <Relationship type='KNOWS' properties={'since': 1999}>

        """
        if len(args) == 1 and not kwargs:
            arg = args[0]
            if isinstance(arg, Relationship):
                return arg
            elif isinstance(arg, tuple):
                if len(arg) == 3:
                    return Relationship(*arg)
                elif len(arg) == 4:
                    return Relationship(arg[0], arg[1], arg[2], **arg[3])
                else:
                    raise TypeError("Cannot cast relationship from {0}".format(arg))
            else:
                raise TypeError("Cannot cast relationship from {0}".format(arg))
        elif len(args) == 3:
            rel = Relationship(*args)
            rel.properties.update(kwargs)
            return rel
        elif len(args) == 4:
            props = args[3]
            props.update(kwargs)
            return Relationship(*args[0:3], **props)
        else:
            raise TypeError("Cannot cast relationship from {0}".format((args, kwargs)))

    @classmethod
    def hydrate(cls, data, inst=None):
        """ Hydrate a dictionary of data to produce a :class:`.Relationship` instance.
        The data structure and values expected are those produced by the
        `REST API <http://neo4j.com/docs/stable/rest-api-relationships.html#rest-api-get-relationship-by-id>`__.

        :arg data: dictionary of data to hydrate
        :arg inst: an existing :class:`.Relationship` instance to overwrite with new values

        """
        self = data["self"]
        if inst is None:
            inst = cls.cache.setdefault(self, cls(Node.hydrate({"self": data["start"]}),
                                                  Rel.hydrate(data),
                                                  Node.hydrate({"self": data["end"]})))
        else:
            Node.hydrate({"self": data["start"]}, inst.start_node)
            Node.hydrate({"self": data["end"]}, inst.end_node)
            Rel.hydrate(data, inst.rel)
        cls.cache[self] = inst
        return inst

    def __init__(self, start_node, rel, end_node, **properties):
        cast_rel = Rel.cast(rel)
        cast_rel._PropertyContainer__properties.update(properties)
        if isinstance(cast_rel, Rev):  # always forwards
            Path.__init__(self, end_node, -cast_rel, start_node)
        else:
            Path.__init__(self, start_node, cast_rel, end_node)

    def __repr__(self):
        s = [self.__class__.__name__]
        if self.bound:
            s.append("graph=%r" % self.graph.uri.string)
            s.append("ref=%r" % self.ref)
            s.append("start=%r" % self.start_node.ref)
            s.append("end=%r" % self.end_node.ref)
            if self.rel._Rel__type is None:
                s.append("type=?")
            else:
                s.append("type=%r" % self.type)
            if "properties" in self.rel._Rel__stale:
                s.append("properties=?")
            else:
                s.append("properties=%r" % self.properties)
        else:
            s.append("type=%r" % self.type)
            s.append("properties=%r" % self.properties)
        return "<" + " ".join(s) + ">"

    def __str__(self):
        return xstr(self.__unicode__())

    def __unicode__(self):
        from py2neo.cypher import CypherWriter
        string = StringIO()
        writer = CypherWriter(string)
        if self.bound:
            writer.write_relationship(self, "r" + ustr(self._id))
        else:
            writer.write_relationship(self)
        return string.getvalue()

    def __len__(self):
        return 1

    def __contains__(self, key):
        return self.rel.__contains__(key)

    def __getitem__(self, key):
        return self.rel.__getitem__(key)

    def __setitem__(self, key, value):
        self.rel.__setitem__(key, value)

    def __delitem__(self, key):
        self.rel.__delitem__(key)

    @property
    def _id(self):
        """ The internal ID of this relationship within the database.
        """
        if self.__id is None:
            self.__id = self.rel._id
        return self.__id

    def bind(self, uri, metadata=None):
        """ Associate this relationship with a remote relationship. The start and
        end nodes will also be associated with their corresponding remote nodes.

        :arg uri: The URI identifying the remote relationship to which to bind.
        :arg metadata: Dictionary of initial metadata to attach to the contained resource.

        """
        self.rel.bind(uri, metadata)
        self.cache[uri] = self
        for i, key, node in [(0, "start", self.start_node), (-1, "end", self.end_node)]:
            uri = self.resource.metadata[key]
            if isinstance(node, Node):
                node.bind(uri)
            else:
                nodes = list(self._Path__nodes)
                node = Node.cache.setdefault(uri, Node())
                if not node.bound:
                    node.bind(uri)
                nodes[i] = node
                self._Path__nodes = tuple(nodes)

    @property
    def bound(self):
        """ :const:`True` if this relationship is bound to a remote counterpart,
        :const:`False` otherwise.
        """
        return self.rel.bound

    @property
    def exists(self):
        """ :const:`True` if this relationship exists in the database,
        :const:`False` otherwise.
        """
        return self.rel.exists

    @property
    def graph(self):
        """ The parent graph of this relationship.

        :rtype: :class:`.Graph`
        """
        return self.service_root.graph

    @property
    def properties(self):
        """ The set of properties attached to this relationship. Properties
        can also be read from and written to any :class:`Relationship`
        by using the index syntax directly. This means
        the following statements are equivalent::

            relationship.properties["since"] = 1999
            relationship["since"] = 1999

        """
        return self.rel.properties

    def pull(self):
        """ Pull data to this relationship from its remote counterpart.
        """
        self.rel.pull()

    def push(self):
        """ Push data from this relationship to its remote counterpart.
        """
        self.rel.push()

    @property
    def ref(self):
        """ The URI of this relationship relative to its graph.

        :rtype: string
        """
        return self.rel.ref

    @property
    def rel(self):
        """ The :class:`.Rel` object within this relationship.
        """
        return self.rels[0]

    @property
    def resource(self):
        """ The resource object wrapped by this relationship, if
        bound.
        """
        return self.rel.resource

    @property
    def service_root(self):
        """ The root service associated with this relationship.

        :return: :class:`.ServiceRoot`
        """
        try:
            return self.rel.service_root
        except BindError:
            try:
                return self.start_node.service_root
            except BindError:
                return self.end_node.service_root

    @property
    def size(self):
        """ The number of relationships in this relationship. This property
        always equals 1 for a :class:`.Relationship` and is inherited from
        the more general parent class, :class:`.Path`.
        """
        return super(Relationship, self).size

    @property
    def type(self):
        """ The type of this relationship.
        """
        return self.rel.type

    @type.setter
    def type(self, name):
        """ Set the type of this relationship (only possible if not bound).
        """
        if self.rel.bound:
            raise AttributeError("The type of a bound Relationship is immutable")
        self.rel.type = name

    def unbind(self):
        """ Detach this relationship and its start and end
        nodes from any remote counterparts.
        """
        try:
            del self.cache[self.uri]
        except KeyError:
            pass
        self.rel.unbind()
        for node in [self.start_node, self.end_node]:
            if isinstance(node, Node):
                try:
                    node.unbind()
                except BindError:
                    pass
        self.__id = None

    @property
    def uri(self):
        """ The URI of this relationship, if bound.
        """
        return self.rel.uri


class Subgraph(object):
    """ A collection of :class:`Node` and :class:`Relationship` objects.
    """

    def __init__(self, *entities):
        self.__nodes = set()
        self.__relationships = set()
        for entity in entities:
            entity = Graph.cast(entity)
            if isinstance(entity, Node):
                self.__nodes.add(entity)
            elif isinstance(entity, Relationship):
                self.__nodes.add(entity.start_node)
                self.__nodes.add(entity.end_node)
                self.__relationships.add(entity)
            else:
                for node in entity.nodes:
                    self.__nodes.add(node)
                for relationship in entity.relationships:
                    self.__relationships.add(relationship)

    def __repr__(self):
        return "<Subgraph order=%s size=%s>" % (self.order, self.size)

    def __eq__(self, other):
        try:
            return self.nodes == other.nodes and self.relationships == other.relationships
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        value = 0
        for entity in self.__nodes | self.__relationships:
            value ^= hash(entity)
        return value

    def __bool__(self):
        return bool(self.__relationships)

    def __nonzero__(self):
        return bool(self.__relationships)

    def __len__(self):
        return self.size

    def __iter__(self):
        return iter(self.__relationships)

    def __contains__(self, item):
        if isinstance(item, Node):
            return item in self.__nodes
        elif isinstance(item, Path):
            for relationship in item:
                if relationship not in self.__relationships:
                    return False
            return True
        else:
            return False

    @property
    def bound(self):
        """ :const:`True` if all entities in this subgraph are bound to remote counterparts,
        :const:`False` otherwise.
        """
        try:
            _ = self.service_root
        except BindError:
            return False
        else:
            return True

    @property
    def exists(self):
        """ :const:`True` if this subgraph exists in the database,
        :const:`False` otherwise.
        """
        return all(entity.exists for entity in self.__nodes | self.__relationships)

    @property
    def graph(self):
        """ The parent graph of this subgraph.

        :rtype: :class:`.Graph`
        """
        return self.service_root.graph

    @property
    def nodes(self):
        """ The set of all nodes in this subgraph.
        """
        return frozenset(self.__nodes)

    @property
    def order(self):
        """ The number of nodes in this subgraph.
        """
        return len(self.__nodes)

    @property
    def relationships(self):
        """ The set of all relationships in this subgraph.
        """
        return frozenset(self.__relationships)

    @property
    def service_root(self):
        """ The root service associated with this subgraph.

        :return: :class:`.ServiceRoot`
        """
        for relationship in self:
            try:
                return relationship.service_root
            except BindError:
                pass
        raise BindError("Local path is not bound to a remote path")

    @property
    def size(self):
        """ The number of relationships in this subgraph.
        """
        return len(self.__relationships)

    def unbind(self):
        """ Detach all entities in this subgraph
        from any remote counterparts.
        """
        for entity in self.__nodes | self.__relationships:
            try:
                entity.unbind()
            except BindError:
                pass


class ServerPlugin(object):
    """ Base class for server plugins.
    """

    def __init__(self, graph, name):
        self.graph = graph
        self.name = name
        extensions = self.graph.resource.metadata["extensions"]
        try:
            self.resources = {key: Resource(value) for key, value in extensions[self.name].items()}
        except KeyError:
            raise LookupError("No plugin named %r found on graph <%s>" % (self.name, graph.uri))


class UnmanagedExtension(object):
    """ Base class for unmanaged extensions.
    """

    def __init__(self, graph, path):
        self.graph = graph
        self.resource = Resource(graph.service_root.uri.resolve(path))
        try:
            self.resource.get()
        except GraphError:
            raise NotImplementedError("No extension found at path %r on "
                                      "graph <%s>" % (path, graph.uri))


from py2neo.deprecated import *
