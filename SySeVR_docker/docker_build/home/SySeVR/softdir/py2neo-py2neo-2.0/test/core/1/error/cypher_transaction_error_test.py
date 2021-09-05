
from py2neo import GraphError
from py2neo.cypher import CypherTransactionError, CypherError
from py2neo.cypher.error import statement, ClientError
from py2neo.packages.httpstream import ClientError as _ClientError, Response as _Response

from .util import assert_new_error


def test_unique_path_not_unique_raises_cypher_transaction_error_in_transaction(graph):
    if not graph.supports_cypher_transactions:
        return
    tx = graph.cypher.begin()
    tx.append("CREATE (a), (b) RETURN a, b")
    results = tx.process()
    result = results[0]
    record = result[0]
    parameters = {"A": record.a._id, "B": record.b._id}
    tx.append("START a=node({A}), b=node({B}) CREATE (a)-[:KNOWS]->(b)", parameters)
    tx.append("START a=node({A}), b=node({B}) CREATE (a)-[:KNOWS]->(b)", parameters)
    tx.append("START a=node({A}), b=node({B}) CREATE UNIQUE (a)-[:KNOWS]->(b)", parameters)
    try:
        tx.commit()
    except CypherTransactionError as error:
        assert_new_error(
            error, (statement.ConstraintViolation, ClientError, CypherTransactionError,
                    CypherError, GraphError), "Neo.ClientError.Statement.ConstraintViolation")
    else:
        assert False


def test_can_hydrate_error_for_all_known_codes():
    codes = [
        "Neo.ClientError.General.ReadOnly",
        "Neo.ClientError.Request.Invalid",
        "Neo.ClientError.Request.InvalidFormat",
        "Neo.ClientError.Schema.ConstraintAlreadyExists",
        "Neo.ClientError.Schema.ConstraintVerificationFailure",
        "Neo.ClientError.Schema.ConstraintViolation",
        "Neo.ClientError.Schema.IllegalTokenName",
        "Neo.ClientError.Schema.IndexAlreadyExists",
        "Neo.ClientError.Schema.IndexBelongsToConstraint",
        "Neo.ClientError.Schema.LabelLimitReached",
        "Neo.ClientError.Schema.NoSuchConstraint",
        "Neo.ClientError.Schema.NoSuchIndex",
        "Neo.ClientError.Statement.ArithmeticError",
        "Neo.ClientError.Statement.ConstraintViolation",
        "Neo.ClientError.Statement.EntityNotFound",
        "Neo.ClientError.Statement.InvalidArguments",
        "Neo.ClientError.Statement.InvalidSemantics",
        "Neo.ClientError.Statement.InvalidSyntax",
        "Neo.ClientError.Statement.InvalidType",
        "Neo.ClientError.Statement.NoSuchLabel",
        "Neo.ClientError.Statement.NoSuchProperty",
        "Neo.ClientError.Statement.ParameterMissing",
        "Neo.ClientError.Transaction.ConcurrentRequest",
        "Neo.ClientError.Transaction.EventHandlerThrewException",
        "Neo.ClientError.Transaction.InvalidType",
        "Neo.ClientError.Transaction.UnknownId",
        "Neo.DatabaseError.General.CorruptSchemaRule",
        "Neo.DatabaseError.General.FailedIndex",
        "Neo.DatabaseError.General.UnknownFailure",
        "Neo.DatabaseError.Schema.ConstraintCreationFailure",
        "Neo.DatabaseError.Schema.ConstraintDropFailure",
        "Neo.DatabaseError.Schema.IndexCreationFailure",
        "Neo.DatabaseError.Schema.IndexDropFailure",
        "Neo.DatabaseError.Schema.NoSuchLabel",
        "Neo.DatabaseError.Schema.NoSuchPropertyKey",
        "Neo.DatabaseError.Schema.NoSuchRelationshipType",
        "Neo.DatabaseError.Schema.NoSuchSchemaRule",
        "Neo.DatabaseError.Statement.ExecutionFailure",
        "Neo.DatabaseError.Transaction.CouldNotBegin",
        "Neo.DatabaseError.Transaction.CouldNotCommit",
        "Neo.DatabaseError.Transaction.CouldNotRollback",
        "Neo.DatabaseError.Transaction.ReleaseLocksFailed",
        "Neo.TransientError.Network.UnknownFailure",
        "Neo.TransientError.Statement.ExternalResourceFailure",
        "Neo.TransientError.Transaction.AcquireLockTimeout",
        "Neo.TransientError.Transaction.DeadlockDetected",
    ]
    for code in codes:
        data = {"code": code, "message": "X"}
        _, classification, category, title = code.split(".")
        error = CypherTransactionError.hydrate(data)
        assert error.code == code
        assert error.message == "X"
        assert error.__class__.__name__ == title
        assert error.__class__.__mro__[1].__name__ == classification
        assert error.__class__.__module__ == "py2neo.cypher.error.%s" % category.lower()
        assert isinstance(error, CypherTransactionError)
        assert isinstance(error, CypherError)
        assert isinstance(error, GraphError)
