
Gremlin.defineStep('In', [Vertex, Pipe], { edgeType, key, vals ->
	
	if(Collection.isAssignableFrom(vals.getClass())){
		filterExpr = { it.getProperty(key) in vals }		
	}else{
		filterExpr = {it.getProperty(key) == vals}
	}

	_().inE(edgeType).filter(filterExpr).outV()
})

Gremlin.defineStep('Out', [Vertex, Pipe], { edgeType, key, vals ->
	
	if(Collection.isAssignableFrom(vals.getClass())){
		filterExpr = { it.getProperty(key) in vals }		
	}else{
		filterExpr = {it.getProperty(key) == vals}
	}

	_().outE(edgeType).filter(filterExpr).inV()
})


/**
   Map node ids to nodes
*/

Gremlin.defineStep('idsToNodes', [Vertex,Pipe], {
	_().transform{ g.v(it) }.scatter()
})

/**
   Map node ids to nodes
*/

Gremlin.defineStep('idsToEdges', [Vertex,Pipe], {
	_().transform{ g.e(it) }.scatter()
})

/**
   Create nodes from a list of node ids
*/

Object.metaClass.idListToNodes = { listOfIds ->
  _().transform{ listOfIds }.scatter().idsToNodes()
}

/**
   Create nodes from a list of node ids
*/

Object.metaClass.idListToEdges = { listOfIds ->
  _().transform{ listOfIds }.scatter().idsToEdges()
}

Gremlin.defineStep('isCheck', [Vertex, Pipe], { symbol ->

   _().astNodes().filter{ it.type in ['EqualityExpression', 'RelationalExpression'] }
   .filter{ it.code.matches(symbol) }
})



Gremlin.defineStep('codeContains', [Vertex, Pipe], { symbol ->
	_().filter{it.code != null}.filter{ it.code.matches(symbol) }
})

/**
 * Traverse to all API symbols from given AST nodes.
 **/

Gremlin.defineStep('apiSyms', [Vertex,Pipe], {
	
	_().match{it.type in ['Callee','IdentifierDeclType', 'Parameter']}.code
})

/**
 * Like 'flatten' but only flatten by one layer.
 * */

Object.metaClass.flattenByOne = { lst ->
	lst.inject([]) {acc, val-> acc.plus(val)}
}

Gremlin.defineStep('_or', [Vertex, Pipe], { Object [] closures ->
	
	_().transform{
		def ret = []
		closures.each{ cl ->
			def x = cl(it).toList()
			ret.addAll(x)
		}
		flattenByOne(ret.unique())
	}.scatter()
})


/**
 For a given list, create a reverse
 index that maps list items to the indices
 they occur at.
*/

Object.metaClass.createReverseIndex = { aList ->
	def reverseIndex = [:]
	aList.eachWithIndex{ item, i ->
		if (!reverseIndex.containsKey(item)){ reverseIndex[item] = [] }
		reverseIndex[item] << i
	}
	reverseIndex
}

Object.metaClass.compareLists = { x, y ->
	if(x == y) return 0
	return 1
}
