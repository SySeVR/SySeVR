

from py2neo import Node


def assert_error(error, classes, fullname, cause_classes, status_code=None):
    for cls in classes:
        assert isinstance(error, cls)
    name = fullname.rpartition(".")[-1]
    assert error.__class__.__name__ == name
    assert error.exception == name
    assert error.fullname in [None, fullname]
    assert error.stacktrace
    cause = error.__cause__
    for cls in cause_classes:
        assert isinstance(cause, cls)
    if status_code:
        assert cause.status_code == status_code


def assert_new_error(error, classes, code):
    for cls in classes:
        assert isinstance(error, cls)
    name = code.rpartition(".")[-1]
    assert error.__class__.__name__ == name
    assert error.code == code
    assert error.message


def get_non_existent_node_id(graph):
    node = Node()
    graph.create(node)
    node_id = node._id
    graph.delete(node)
    return node_id


def get_attached_node_id(graph):
    node = Node()
    graph.create(node, {}, (0, "KNOWS", 1))
    return node._id
