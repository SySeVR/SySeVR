
/**
   For an AST node, traverse to the exit-node
   of the function
*/

Gremlin.defineStep('toExitNode', [Vertex,Pipe], {
	_().transform{ queryNodeIndex('functionId:' + it.functionId + " AND type:CFGExitNode ") }
	.scatter()
})
