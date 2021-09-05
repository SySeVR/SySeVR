/**
   This module contains index lookup functions employed to provide
   start node sets for traversals. All of these lookups support wild
   cards (you will need to escape spaces though).

   For each index lookup function, we define a corresponding Gremlin
   step with the same name which performs the same action as the
   lookup-function but returns only matches occuring in the same
   functions as the nodes piped to it.
*/


/**
   Retrieve nodes from index using a Lucene query.
   
   @param query The lucene query to run
   
*/

Object.metaClass.queryNodeIndex = { query, honorVisibility = true ->
        index = g.getRawGraph().index().forNodes(NODE_INDEX)
	
	try{
	  if(honorVisibility)
	    new Neo4j2VertexIterable(index.query(query), g)._().visible()
	   else
	    new Neo4j2VertexIterable(index.query(query), g)._()
	}catch(ParseException){
	  return []._()
	}
}

/**
   Retrieve nodes with given type and code.
   
   @param type The node type
   @param code The node code
   
*/

Object.metaClass.getNodesWithTypeAndCode = { type, code ->
	query = "$NODE_TYPE:$type AND $NODE_CODE:$code"
	queryNodeIndex(query)
}


/**
   Retrieve nodes with given type
   
   @param type The node type
   
*/

Object.metaClass.getNodesWithType = { type ->
	query = "$NODE_TYPE:$type"
	queryNodeIndex(query)
}

/**
   Retrieve nodes with given type and name.
   
   @param type The node type
   @param name The node name
   
*/

Object.metaClass.getNodesWithTypeAndName = { type, name, honorVisibility = true  ->
	query = "$NODE_TYPE:$type AND $NODE_NAME:$name"
	queryNodeIndex(query, honorVisibility)
}

/**
   Retrieve functions by name.
   
   @param name name of the function
   
*/

Object.metaClass.getFunctionsByName = { name, honorVisibility = true ->
	getNodesWithTypeAndName(TYPE_FUNCTION, name, honorVisibility)
}

Object.metaClass.getFunctionsByParameter = { param ->
	getNodesWithTypeAndCode(TYPE_PARAMETER, param)
	.functions()
}

Object.metaClass.getFunctionsByFilename = { name, honorVisibility = true ->
	query = "$NODE_TYPE:$TYPE_FILE AND $NODE_FILEPATH:$name"
	queryNodeIndex(query, honorVisibility)
	.out('IS_FILE_OF')
	.filter{ it.type == TYPE_FUNCTION }
}

Object.metaClass.getFunctionsByFileAndName = { filename, name, honorVisibility = true ->
	getFunctionsByFilename(filename, honorVisibility)
	.filter{ it.name == name }
}

Object.metaClass.getFilesByName = { filename, honorVisibility = true ->
	query = "$NODE_TYPE:$TYPE_FILE AND $NODE_FILEPATH:$filename"
	queryNodeIndex(query, honorVisibility)
}

/**
   Retrieve functions by name.
   
   @param name name of the function
   
*/

Object.metaClass.getFunctionASTsByName = { name ->
	getNodesWithTypeAndName(TYPE_FUNCTION, name)
	.out(FUNCTION_TO_AST_EDGE)
}

/**
   Retrieve all statements (including conditions)
*/

Object.metaClass.getAllStatements = {
	queryNodeIndex('isCFGNode:True')
}

/**
   Retrieve all conditions
*/

Object.metaClass.getAllConditions = {
	getNodesWithType('Condition')
}

/**
   Retrieve all calls.
   
*/

Object.metaClass.getAllCalls = {
	getNodesWithType(TYPE_CALL)
}

/**
   Retrieve calls by name.
   
   @param callee Name of called function
   
*/

Object.metaClass.getCallsTo = { callee ->
	
  callee = callee.split(' ')[-1].trim()
  callee = callee.replace('*', '')
    
  getNodesWithTypeAndCode(TYPE_CALLEE, callee)
  .parents()
  
}



/**
   Retrieve arguments to functions. Corresponds to the traversal
   'ARG' from the paper. 
   
   @param name Name of called function
   @param i Argument index
   
*/

Object.metaClass.getArguments = { name, i ->
	getCallsTo(name).ithArguments(i)
}

Object.metaClass.getConditions = { funcname, regex, filename = null ->

  if(filename == null)
    getFunctionASTsByName(funcname).match{ it.type == "Condition" && it.code.matches(regex) }
  else
    getFunctionsByFileAndName(filename, funcname).functionToAST()
    .match{ it.type == "Condition" && it.code.matches(regex) } 
}


  /////////////////////////////////////////////////
 //     Corresponding Gremlin Steps             //
/////////////////////////////////////////////////

Gremlin.defineStep('queryNodeIndex', [Vertex,Pipe], { query, c = [] ->
	_()._emitForFunctions({ queryNodeIndex(query) }, c )
})

Gremlin.defineStep('getNodesWithTypeAndCode', [Vertex,Pipe], { type, code, c = [] ->
	_()._emitForFunctions({ getNodesWithTypeAndCode(type, code) }, c )
})

Gremlin.defineStep('getNodesWithTypeAndName', [Vertex,Pipe], { type, name, c = [] ->
	_()._emitForFunctions({ getNodesWithTypeAndName(type, name) }, c )
})

Gremlin.defineStep('getFunctionsByName', [Vertex,Pipe], { name, c = [] ->
	_()._emitForFunctions({ getFunctionsByName(name) }, c )
})

Gremlin.defineStep('getCallsTo', [Vertex,Pipe], { callee, c = [] ->
	_()._emitForFunctions({ getCallsTo(callee) }, c )
})

Gremlin.defineStep('getArguments', [Vertex,Pipe], { name, i, c = [] ->
	_()._emitForFunctions({ getArguments(name, i) }, c )
})




