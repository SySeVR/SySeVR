
/**
   (Optimized) match-traversals for functions.
*/

Gremlin.defineStep("functionToAST", [Vertex,Pipe], {
	_().out(FUNCTION_TO_AST_EDGE)
})

Gremlin.defineStep("functionToASTNodes", [Vertex,Pipe], {
	_().functionToAST().astNodes()
})

Gremlin.defineStep("functionToStatements", [Vertex,Pipe],{
	_().transform{ queryNodeIndex('isCFGNode:True AND functionId:' + it.id) }
	 .scatter()
})

Gremlin.defineStep("functionsToASTNodesOfType", [Vertex,Pipe],{ type ->
	_().transform{ queryNodeIndex('functionId:' + it.id + " AND $NODE_TYPE:$type") }
	 .scatter()
})

Gremlin.defineStep('functionToFile', [Vertex, Pipe], {
	_().in(FILE_TO_FUNCTION_EDGE)
})

/**
 * For a function node, get callers using `name` property.
 **/

Gremlin.defineStep('functionToCallers', [Vertex,Pipe], {
	_().transform{
		getCallsTo(it.name)
	}.scatter()
})
