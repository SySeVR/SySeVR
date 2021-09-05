
/**
 * For a given call-expression, determine whether it's `argNum`'th
 * argument is tainted by a statement matching the source description.
 * */

Gremlin.defineStep('taintedArg', [Vertex, Pipe], { argNum, src = { [1]._() }, N_LOOPS = 4 ->
	_().filter{
		argIsTainted(it, argNum, src, N_LOOPS)
	}
})

Object.metaClass.argIsTainted = { node, argNum, src, N_LOOPS = 2 ->
	
	node.ithArguments(argNum)
	.as('y').taintedArgExpand()
	// .expandParameters().allProducers()
	.dedup()
	.loop('y'){ it.loops <= N_LOOPS && (src(it.object).toList() == [] || src(it.object).toList() == [1] ) }
	{true}
	// {  src(it.object).toList() == [10] }
	.filter{ src(it).toList() != [] }
	.toList() != []
}

Gremlin.defineStep('taintedArgExpand', [Vertex, Pipe], {
	_().transform{
				
		if(it.type == 'Parameter')
			it.expandParameters().toList()
		else{
			def l = [];
			tainters = it.match{it.type == 'CallExpression'}.argTainters().toList()
			l.addAll(tainters)
			l.addAll(it.allProducers().toList())
			l
		}
			
	}.scatter()
	
})


/**
 * For a given node, obtain producers for
 * all symbols it uses.
 **/

Gremlin.defineStep('allProducers', [Vertex, Pipe], {
	_().transform{
		it.producers(it.uses().code.toList())
	}.scatter()
})
