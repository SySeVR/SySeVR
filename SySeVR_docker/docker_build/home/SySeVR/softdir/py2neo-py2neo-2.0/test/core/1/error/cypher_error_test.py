

from py2neo.cypher import CypherError, CypherTransactionError
from py2neo.error import GraphError
from py2neo.packages.httpstream import ClientError as _ClientError, Response as _Response

from .util import assert_error, get_non_existent_node_id


def test_invalid_syntax_raises_cypher_error(graph):
    cypher = graph.cypher
    try:
        cypher.execute("X")
    except CypherTransactionError as error:
        assert error.code == "Neo.ClientError.Statement.InvalidSyntax"
    except CypherError as error:
        assert_error(
            error, (CypherError, GraphError), "org.neo4j.cypher.SyntaxException",
            (_ClientError, _Response), 400)
    else:
        assert False


def test_entity_not_found_raises_cypher_error(graph):
    node_id = get_non_existent_node_id(graph)
    cypher = graph.cypher
    try:
        cypher.execute("START n=node({N}) RETURN n", {"N": node_id})
    except CypherTransactionError as error:
        assert error.code == "Neo.ClientError.Statement.EntityNotFound"
    except CypherError as error:
        if graph.neo4j_version >= (1, 9):
            fullname = "org.neo4j.cypher.EntityNotFoundException"
        else:
            fullname = "org.neo4j.cypher.BadInputException"
        assert_error(
            error, (CypherError, GraphError), fullname,
            (_ClientError, _Response), 400)
    else:
        assert False


def test_unique_path_not_unique_raises_cypher_error(graph):
    cypher = graph.cypher
    results = cypher.execute("CREATE (a), (b) RETURN a, b")
    parameters = {"A": results[0].a, "B": results[0].b}
    cypher.execute("START a=node({A}), b=node({B}) CREATE (a)-[:KNOWS]->(b)", parameters)
    cypher.execute("START a=node({A}), b=node({B}) CREATE (a)-[:KNOWS]->(b)", parameters)
    try:
        cypher.execute("START a=node({A}), b=node({B}) CREATE UNIQUE (a)-[:KNOWS]->(b)", parameters)
    except CypherTransactionError as error:
        assert error.code == "Neo.ClientError.Statement.ConstraintViolation"
    except CypherError as error:
        assert_error(
            error, (CypherError, GraphError), "org.neo4j.cypher.UniquePathNotUniqueException",
            (_ClientError, _Response), 400)
    else:
        assert False
