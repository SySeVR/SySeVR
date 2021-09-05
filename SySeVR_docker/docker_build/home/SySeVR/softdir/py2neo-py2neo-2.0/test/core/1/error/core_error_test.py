

from py2neo import Resource
from py2neo.error import GraphError
from py2neo.packages.httpstream import ClientError as _ClientError, Response as _Response

from .util import assert_error, get_non_existent_node_id, get_attached_node_id


def test_can_handle_400():
    resource = Resource("http://localhost:7474/db/data/cypher")
    try:
        resource.post()
    except GraphError as error:
        assert_error(
            error, (GraphError,), "org.neo4j.server.rest.repr.BadInputException",
            (_ClientError, _Response), 400)
    else:
        assert False


def test_can_handle_404(graph):
    node_id = get_non_existent_node_id(graph)
    resource = Resource("http://localhost:7474/db/data/node/%s" % node_id)
    try:
        resource.get()
    except GraphError as error:
        assert_error(
            error, (GraphError,), "org.neo4j.server.rest.web.NodeNotFoundException",
            (_ClientError, _Response), 404)
    else:
        assert False


def test_can_handle_409(graph):
    node_id = get_attached_node_id(graph)
    resource = Resource("http://localhost:7474/db/data/node/%s" % node_id)
    try:
        resource.delete()
    except GraphError as error:
        assert_error(
            error, (GraphError,), "org.neo4j.server.rest.web.OperationFailureException",
            (_ClientError, _Response), 409)
    else:
        assert False
