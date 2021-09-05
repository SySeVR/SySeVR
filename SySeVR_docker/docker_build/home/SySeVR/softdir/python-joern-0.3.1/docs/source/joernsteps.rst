Start Node Selection
====================

.. default-domain:: joern

.. lookup:: queryNodeIndex(query)

        Retrieves nodes from the database index using a Lucene query.

        :param query: The Lucene query.
        :out*: Arbitrary node

.. lookup:: getNodesWithTypeAndCode(type, code)

        Retrieves nodes with the given type and code. This is
        equivalent to::

	        queryNodeIndex("type:$t AND code:$c")

        .. seealso::

	        - :ref:`queryNodeIndex`

        :param type: The required type.
        :param code: The required code string.
        :out*: All nodes of the given type.

.. lookup:: getNodesWithTypeAndName(type, name)

        Retrieves nodes with the given type and name. This is
        equivalent to::

	        queryNodeIndex("type:$t AND name:$n")

        .. seealso::

	        - :ref:`queryNodeIndex`

        :param type: The required type.
        :param name: The required name
        :out*: All nodes of the given type.

.. lookup:: getFunctionsByName(name)

        Retrieves function nodes with the given name.
        This is equivalent to::

	        getNodesWithTypeAndName('Function', n)

        .. seealso::

        	- :ref:`getNodesWithTypeAndName`

        :param name: The required name of the functions.
        :out Function:

.. lookup:: getFunctionsByFilename(filename)

        Retrieves function nodes with the given filename.

        :param filename: The required filename of the functions.
        :out Function:

.. lookup:: getFunctionsASTsByName(name)

        Retrieves the root node of the abstract syntax tree
        by the name of the function.

        :param name: The function name.
        :out FunctionDef:

.. lookup:: getCallsTo(callee):

        Retrieves function calls by the name of the called function.
        
        :param callee: The name of the called function.
        :out CallExpression:

.. lookup:: getArguments(callee, position)

        Retrieves the i-th argument of a function call by the name of
        the called function and the position of the argument. This is
        equivalent to::

	        getCallsTo(callee).ithArguments(position)

        .. seealso::

        	- :ref:`getCallsTo`
	        - :ref:`ithArguments`

        :param callee: The name of the called function.
        :param position: The position of the required argument.
        :out Argument:

Traversals
==========

Abstract syntax tree traversals
-------------------------------

.. traversal:: astNodes()

        Traverses from a abstract syntax tree (AST) node to all child
        nodes including the node itself.

        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: parents()

        Traverses from a abstract syntax tree (AST) node to its
        parent node.

        .. seealso::

	        - :ref:`children`

        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: children()

        Traverses from a abstract syntax tree (AST) node to all of
        its children nodes.

        .. seealso::

	        - :ref:`parents`
        	- :ref:`ithChildren`

        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: ithChildren(i)

        Traverses from a abstract syntax tree (AST) node to its i-th
        children node.

        .. seealso::

        	- :ref:`children`

        :param i: The child number.
        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: statements()

        Traverses from a abstract syntax tree (AST) node to its
        enclosing statement or predicate node. If the incoming node
        is a statement or predicate node, the node itself is returned.

        .. seealso::

                - :ref:`functionToStatements`

        :in*: Arbitrary AST node.
        :out*: Various AST node.

.. traversal:: functions()

        Traverses from a abstract syntax tree (AST) or symbol node
        to the corresponding function.

        :in*: Arbitrary AST node
        :in Symbol:
        :out Function:

Traversals for assignment expressions
-------------------------------------

.. traversal:: lval

        Traverses from an assignment expression to the left hand side
        of the expression.
        
        .. seealso::

                - :ref:`rval`

        :in AssignmentExpr:
        :out Identifier:
        :out MemberAccess:
        :out PtrMemberAccess:
        :out others:

.. traversal:: rval

        Traverses from an assignment expression to the right hand
        side of the expression.
        
        .. seealso::

                - :ref:`lval`

        :in AssignmentExpr:
        :out*: Various AST nodes.

Traversals for function calls
-----------------------------

.. traversal:: callToArguments()

        Traverses from a function call to its arguments.
        This may return an empty pipe.

        :in CallExpression:
        :out Argument:

.. traversal:: calleeToCall()

        Traverses from a callee node to its corresponding
        function call.

        :in Callee:
        :out CallExpression:

.. traversal:: argToCall()

        Traverses from an argument node to its corresponding
        function call.

        :in Argument:
        :out CallExpression:


.. traversal:: ithArguments(i)

        Traverses from a function call to its i-th argument.
        This may return an empty pipe.

        :param i: The argument number.
        :in CallExpression:
        :out Argument:

Traversals for dataflow analysis
--------------------------------
 
.. traversal:: producers(symbols)

.. traversal:: users(symbols)

.. traversal:: sources()

.. traversal:: sinks()

.. traversal:: astSinks()

.. traversal:: astSources()

.. traversal:: unsanitized(sanitizer, src)

.. traversal:: firstElem()

.. traversal:: uPath(sanitizer, src)

Function traversals
-------------------

.. traversal:: functionToAST()

        Traverses from a function node to the root node
        of the corresponding abstract syntax tree (AST).

        :in Function:
        :out FunctionDef:

.. traversal:: functionToASTNodes()
        
        Traverses from a function node to all nodes of the
        corresponding abstract syntax tree.

        This is equivalent to::

               _().functionToAST().astNodes() 

        .. seealso::
                
                - :ref:`functionToAST`
                - :ref:`astNodes`

        :in Function:
        :out*: Arbitrary AST node.

.. traversal:: functionToStatements()

        Traverses from a function node to all statements of
        the function.

        .. seealso::

                - :ref:`statements`

        :in Function:
        :out*: Arbitrary AST node.

.. traversal:: functionToASTNodesOfType(type)

        Traverses from a function node to all abstract syntax
        tree nodes of the given type.

        :param type: The node type.
        :in Function:
        :out*: Nodes of the given **type**

.. traversal:: functionToFile

        Traverses from a function node to the file node of the file,
        which contains the function.

        :in Function:
        :out File:

.. Traversals for information retrieval
.. ------------------------------------

.. .. traversal:: locations()

.. Duplicate
.. .. traversal:: functions()

.. Duplicate
.. .. traversal:: functionToFiles()

Match traversals
----------------

.. note::

        Please note, that tradeoffs in efficientcy are made for
        increased robustness and ease of formulation

.. traversal:: match(predicate)

        Traverses from a abstract syntax tree (AST) node to all child
        nodes matching the given *predicate*. This also includes the
        starting node.

        This is equivalent to::

                _().astNodes().filter(predicate)

        .. seealso::

                - :ref:`astNodes`

        :param predicate: The closure that is used as the filter
                predicate.
        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: matchParents(predicate)

        Traverses from a abstract syntax tree (AST) node to all
        parent nodes stopping at the enclosing statement and emitting
        all nodes matching the given predicate.

        :param predicate: The closure that is used as the filter
                predicate.
        :in*: Arbitrary AST node.
        :out*: Arbitrary AST node.

.. traversal:: arg(function, position)

        Traverses from a abstract syntax tree (AST) node to all child
        nodes emitting all parameters at the given position whose
        functions match the given function name.

        :param function: The name of the function whose parameters
                are of interest.
        :param position: The required position of the parameter.
        :in*: Arbitrary AST node.
        :out Argument:

.. traversal:: param(name)

        Traverses from a abstract syntax tree (AST) node to all child
        nodes emitting all parameters with the given name.

        :param name: The required name of the parameter.  
        :in*: Arbitrary AST node.
        :out Parameter:

Traversals for function parameters
----------------------------------

.. traversal:: paramsToNames()

        Traverses from a function parameter to its identifier node.

        .. seealso::

                - :ref:`paramsToTypes`
                - :ref:`param`

        :in Parameter:
        :out Identifier:

.. traversal:: paramsToTypes()

        Traverses from a function parameter to its type.

        .. seealso::

                - :ref:`paramsToNames`
                - :ref:`param`


        :in Parameter:
        :out ParameterType:

Traversals for symbol graphs
----------------------------

.. traversal:: uses()

        Traverses from a statement to all symbols used by this
        statement.

        .. seealso::

                - :ref:`defines`

        :in Statement:
        :out Symbol:

.. traversal:: defines()

        Traverses from a statement to all symbols defined by this
        statement.

        .. seealso::

                - :ref:`uses`

        :in Statement:
        :out Symbol:

.. traversal:: setBy()

        Traverses from a symbol to all statements that change the value
        of this symbol.

        :in Symbol:
        :outgoing node type: All AST nodes with the property ``isCFGNode = True``.

.. traversal:: definitions()

        Traverses from a statement to all nodes affecting any symbol
        used within this statement.
        
        :in Statement:
        :out IdenifierDeclStmt:
        :out Parameter:
