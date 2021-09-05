from py2neo import Graph
from py2neo.ext.gremlin import Gremlin
import os

DEFAULT_GRAPHDB_URL = "http://localhost:7474/db/data/"
DEFAULT_STEP_DIR = os.path.dirname(__file__) + '/joernsteps/'

class JoernSteps:

    def __init__(self):
        self._initJoernSteps()
        self.initCommandSent = False

    def setGraphDbURL(self, url):
        """ Sets the graph database URL. By default,
        http://localhost:7474/db/data/ is used."""
        self.graphDbURL = url
    
    def addStepsDir(self, stepsDir):
        """Add an additional directory containing steps to be injected
        into the server"""
        self.stepsDirs.append(stepsDir)
    
    def connectToDatabase(self):
        """ Connects to the database server."""
        self.graphDb = Graph(self.graphDbURL)
        self.gremlin = Gremlin(self.graphDb)

    def runGremlinQuery(self, query):

        """ Runs the specified gremlin query on the database. It is
        assumed that a connection to the database has been
        established. To allow the user-defined steps located in the
        joernsteps directory to be used in the query, these step
        definitions are prepended to the query."""
        
        if not self.initCommandSent:
            self.initCommand = self._createInitCommand()
            self.initCommandSent = True
            finalQuery = self.initCommand
        else:
            finalQuery = ""
        finalQuery += query
        return self.gremlin.execute(finalQuery)
        
    def runCypherQuery(self, cmd):
        """ Runs the specified cypher query on the graph database."""
        return cypher.execute(self.graphDb, cmd)

    def getGraphDbURL(self):
        return self.graphDbURL
    
    """
    Create chunks from a list of ids.
    This method is useful when you want to execute many independent 
    traversals on a large set of start nodes. In that case, you
    can retrieve the set of start node ids first, then use 'chunks'
    to obtain disjoint subsets that can be passed to idListToNodes.
    """
    def chunks(self, idList, chunkSize):
        for i in xrange(0, len(idList), chunkSize):
            yield idList[i:i+chunkSize]

    def _initJoernSteps(self):
        self.graphDbURL = DEFAULT_GRAPHDB_URL
        self.stepsDirs = [DEFAULT_STEP_DIR]

    def _createInitCommand(self):
        
        initCommand = ""

        for stepsDir in self.stepsDirs:
            for (root, dirs, files) in os.walk(stepsDir, followlinks=True):
                files.sort()
                for f in files:
                    filename = os.path.join(root, f)
                    if not filename.endswith('.groovy'): continue
                    initCommand += file(filename).read() + "\n"
        return initCommand
