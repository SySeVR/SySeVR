Basic Usage
===========

Python-joern currently provides a single class, JoernSteps, that
allows to connect to the database server and run queries. The
following is a simple sample script that employs JoernSteps to
configure the database connection, connect to the server and run a
Gremlin query.

::

	from joern.all import JoernSteps

	j = JoernSteps()

	j.setGraphDbURL('http://localhost:7474/db/data/')

	# j.addStepsDir('Use this to inject utility traversals')

	j.connectToDatabase()

	res =  j.runGremlinQuery('getFunctionsByName("main")')
	# res =  j.runCypherQuery('...')

	for r in res: print r

The sample script employs all methods offered by JoernSteps. We now
discuss each of these methods in detail.

setGraphDbURL(url)
-------------------

**Sets the URL of the graph database server.** The REST API of the
Neo4J Database server is exposed on port 7474 by default. If your
server runs on a different port or server, you can use setGraphDbURL
to specify the alternate URL.

addStepsDir(dirname)
--------------------

**Add a source directory for utility traversals.** By default,
python-joern will inject all utility traversals contained in any of
the source files in joern/joernsteps into the database before running
scripts. Additional traversals specific to your application or
analysis are best placed in a separate directory. python-joern can be
instructed to honor this additional directory using addStepsDir.

connectToDatabase()
-------------------

**Connect to the database.** Call this method once the connection has
been configured to connect to the database server. A connection is
required before queries can be executed.

runGremlinQuery(query)
-----------------------

**Run the specified Gremlin query.** The supplied query is executed
and the result is returned. Depending on the query, the result may
have a different data type, however, it is typically an iterable
containing nodes that match the query.


runCypherQuery(query)
-----------------------

**Run the specified Cypher query.** The supplied query is executed
and the result is returned. Depending on the query, the result may
have a different data type, however, it is typically an iterable
containing nodes that match the query.
