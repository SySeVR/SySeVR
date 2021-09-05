Chunking
========

Running the same traversal on a large set of start nodes often leads
to unacceptable performance as all nodes and edges touched by the
traversal are kept in server memory before returning results. For
example, the query::

	getAllStatements().astNodes().id

which retrieves all astNodes that are part of statements, can already
completely exhaust memory. 

If traversals are independent, the query can be chunked to gain high
performance. The following example code shows how this works::

	from joern.all import JoernSteps

	j = JoernSteps()
	j.connectToDatabase()
	
	ids =  j.runGremlinQuery('getAllStatements.id')

	CHUNK_SIZE = 256
	for chunk in j.chunks(ids, CHUNK_SIZE):
	   
	   query = """ idListToNodes(%s).astNodes().id """ % (chunk)
	   
	   for r in j.runGremlinQuery(query): print r

This will execute the query in batches of 256 start nodes each.
