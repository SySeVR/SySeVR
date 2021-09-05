/**
   Elementrary traversals starting at AST nodes.
*/

/** 
    Traverse from root of AST to all nodes it contains
    (including the node itself) This is refered to as 'TNODES' in the
    paper simply because otherwise its definition would not fit in a
    column ;)
*/


Gremlin.defineStep('astNodes', [Vertex, Pipe], {
	_().transform{
	 def x = [] as Set;
	it.children().loop(1){true}{true}
	.store(x).optional(2).transform{x+it}.scatter()
	}.scatter()
})

/**
   Traverse to parent-nodes of AST nodes.
*/

Gremlin.defineStep('parents', [Vertex, Pipe], {
	_().in(AST_EDGE)
})

/**
   Traverse to child-nodes of AST nodes.
*/

Gremlin.defineStep('children', [Vertex, Pipe], {
	_().out(AST_EDGE)
})

/**
   Traverse to i'th children.
   
   @param i The child index
*/

Gremlin.defineStep('ithChildren', [Vertex, Pipe], { i ->
	_().children().filter{ it.childNum == i}
})

Object.metaClass.isStatement = { it ->
  it.isCFGNode == 'True'
}

/**
   Traverse to statements enclosing supplied AST nodes. This may be
   the node itself.
*/

Gremlin.defineStep('statements', [Vertex,Pipe],{
		_().ifThenElse{isStatement(it)}
      		{ it }
      		{ it.in(AST_EDGE).loop(1){it.object.isCFGNode != 'True'} }
});

/**
   Get number of children of an AST node.
*/

Gremlin.defineStep('numChildren', [Vertex, Pipe], {
	_().transform{ numChildren(it)  }
})

Object.metaClass.numChildren = { it ->
	it.out('IS_AST_PARENT').toList().size()
}
