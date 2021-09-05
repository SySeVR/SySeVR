

Gremlin.defineStep('iUnsanitized', [Vertex,Pipe], { sanitizer, src = { [1]._() }, N_LOOPS = 4 ->
	
  // Note, that the special value [1] is returned by
  // source descriptions to indicate that the user
  // does not care what the source looks like.
		  
  _().transform{
	  
	  nodes = getNodesToSrc(it, src, N_LOOPS)
	  finalNodes = nodes.findAll{ it[1] == true}.collect{ it[0] }.unique()
	  nodes = nodes.collect{ it[0] }.unique()
	  srcChecker = { node -> if(node.id in nodes) [10] else [] }
	  
	  it.as('x').iUnsanitizedExpand(sanitizer, srcChecker).dedup()
	  // loop if either no node matched the source-description or we simply don't have a source description
	  .loop('x'){ it.loops <= N_LOOPS && (src(it.object).toList() == [] || src(it.object).toList() == [1] ) }
	  // output nodes if they match the source description or we don't have one.
	  // and only if they are final nodes.
	  {src(it.object).toList() != [] && (it.object.id in finalNodes) }
	  
  }.scatter()
})

Gremlin.defineStep('iUnsanitizedExpand', [Vertex,Pipe], { sanitizer, srcChecker ->
	
	_().transform{
		if(it.type == 'Parameter')
			it.expandParameters().toList()
		else{
			def l = [];
			tainters = it.match{it.type == 'CallExpression'}.argTainters().toList()
			l.addAll(tainters)
			l.addAll(it.unsanitized(sanitizer, srcChecker).toList())
			l
		}
	}.scatter()
	
})


/**
  (Called by iUnsanitized)
  Starting from a sink-node 'it' and for a given
  source-description 'sourceDescription', find all
  source nodes that match the source description
  even across the boundaries of functions.
  Elements in the returned list are pairs of the form
  [id, isFinalNode] where 'id' is the node's id and
  isFinalNode indicates whether no further expansion
  of this node was performed.
**/

Object.metaClass.getNodesToSrc = { it, sourceDescription, N_LOOPS ->
  
  _getNodesToSrc(it, sourceDescription, 0, N_LOOPS).unique()
}

Object.metaClass._getNodesToSrc = { it, src, depth, N_LOOPS ->
  

  if(src(it).toList() != [1] && src(it).toList() != []){
	// found src
	 return [ [it.id,true] ]
  }
	  
  if(depth == N_LOOPS){
	  if(src(it).toList() == [1])
		  return [ [it.id,true] ]
	  else
		  return []
  }
  
  def children = it._().taintedArgExpand()
   // .expandParameters().allProducers()
  .toList()
  
  def x = children.collect{ child ->
	  _getNodesToSrc(child, src, depth + 1, N_LOOPS)
  }
  .inject([]) {acc, val-> acc.plus(val)}	// flatten by one layer
  .unique()
  
  if(x == [])
	  return [[it.id, true]]
  else
	  return x.plus([[it.id, false]])
}

/**
 * Version of iUnsanitized that returns paths.
 * */

Gremlin.defineStep('iUnsanitizedPaths', [Vertex,Pipe], { sanitizer, src = { [1]._() }, N_LOOPS = 4 ->
		  
  _().transform{
	  
	  nodes = getNodesToSrc(it, src, N_LOOPS)
	  finalNodes = nodes.findAll{ it[1] == true}.collect{ it[0] }.unique()
	  nodes = nodes.collect{ it[0] }.unique()
	  srcChecker = { node -> if(node.id in nodes) [10] else [] }
	  
	  it.sideEffect{ d = [:]; rootNode = null; }
	  .as('x').expandParameters()
	  .unsanitizedPaths(sanitizer, srcChecker).dedup()
	  .transform{
		  def path = it.toList()
		  if(!rootNode && path.size() != 0) rootNode = path[-1]
		  d[path[-1]] = (d[path[-1]] ?: []).plus([path]);
			path[0]
	  }
	  .loop('x'){ it.loops <= N_LOOPS && (src(it.object).toList() == [] || src(it.object).toList() == [1] ) }
	  {src(it.object).toList() != [] && (it.object.id in finalNodes) }
	  .transform{
		  dict2List(d, rootNode)
	  }
	  
  } //.scatter()
})

Object.metaClass.dict2List = { d, node ->
	if(!d[node])
		return [[node, []]]
	
	def retval = [[node, d[node]]]
	d[node].each{
		retval.add(dict2List(d, it[0]))
	}
	retval
}

