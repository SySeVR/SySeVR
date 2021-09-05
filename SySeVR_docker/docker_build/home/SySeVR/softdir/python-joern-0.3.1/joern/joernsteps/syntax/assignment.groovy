
/**
   (Optimized) Match-traversals for assignments
*/

Gremlin.defineStep('lval', [Vertex,Pipe], {
	_().out(AST_EDGE).filter{ it.childNum == "0" }
});

Gremlin.defineStep('rval', [Vertex,Pipe], {
	_().out(AST_EDGE).filter{ it.childNum == "1" }
});
