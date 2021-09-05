
/**
   (Optimized) Match-traversals for Calls.
*/

Gremlin.defineStep('callToArguments', [Vertex, Pipe], {
	 _().children().filter{it.type == TYPE_ARGLIST}
	 .children()
})

Gremlin.defineStep('ithArguments', [Vertex,Pipe], { i -> 
	_().callToArguments()
	.filter{ it.childNum == i }
})


Gremlin.defineStep('argToCall', [Vertex, Pipe], {
	_().in(AST_EDGE).in(AST_EDGE)
})

Gremlin.defineStep('calleeToCall', [Vertex, Pipe], {
	_().in(AST_EDGE)
})

Gremlin.defineStep('callToCallee', [Vertex, Pipe],{
	_().out(AST_EDGE).filter{it.type == 'Callee'}
})

Gremlin.defineStep('callToAssigns', [Vertex, Pipe], {
	_().matchParents{it.type == 'AssignmentExpr'}
})
