Neo4j 2.1.5
=======================================

Welcome to Neo4j release 2.1.5, a high-performance graph database.
This is the community distribution of Neo4j, including everything you need to
start building applications that can model, persist and explore graph-like data.

In the box
----------

Neo4j runs as a server application, exposing a Web-based management
interface and RESTful endpoints for data access.

Here in the installation directory, you'll find:

* bin - scripts and other executables
* conf - server configuration
* data - database, log, and other variable files
* lib - core libraries
* plugins - user extensions
* system - super-secret server stuff

Make it go
----------

For full instructions, see http://neo4j.com/docs/2.1.5/deployment/

To get started with Neo4j, let's start the server and take a
look at the web interface ...

1. Open a console and navigate to the install directory.
2. Start the server:
   * Windows: use bin\Neo4j.bat
   * Linux/Mac: use ./bin/neo4j console
3. In a browser, open http://localhost:7474/
4. From any REST client or browser, open http://localhost:7474/db/data
   in order to get a REST starting point, e.g.
   curl -v http://localhost:7474/db/data
5. Shutdown the server by typing Ctrl-C in the console.

Learn more
----------

* Neo4j Home: http://neo4j.com/
* Getting Started: http://neo4j.com/docs/2.1.5/introduction/
* The Neo4j Manual: http://neo4j.com/docs/2.1.5/

License(s)
----------
Various licenses apply. Please refer to the LICENSE and NOTICE files for more
detailed information.

