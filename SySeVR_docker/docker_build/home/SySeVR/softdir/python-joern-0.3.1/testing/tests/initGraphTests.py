
from PythonJoernTests import *

class InitGraphTests(PythonJoernTests):
    
    def testCreate1(self):
        query = """
        
        callSiteId = getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        
        initGraph = createInitGraph(callSiteId)
        initGraph.graphlets.size()

        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, 3)
    
    def testCreate2(self):
        
        query = """
        
        callSiteId = getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        
        initGraph = createInitGraph(callSiteId)
        initGraph.graphlets.size()

        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, 3)

    def testDecompress1(self):
        
        query = """
        
        callSiteId = getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        
        initGraph = createInitGraph(callSiteId)
        invocs = decompressInitGraph(initGraph)
        [ g.v(invocs.defStmtsPerArg[0][0][0]).code, g.v(invocs.defStmtsPerArg[0][1][0]).code]
        """
        x = self.j.runGremlinQuery(query)
        self.assertTrue(x[0].find('sourceA') != -1)
        self.assertTrue(x[1].find('sourceB') != -1)
        
    def testDecompress2(self):
        
        query = """
        
        callSiteId = getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        
        initGraph = createInitGraph(callSiteId)
        invocs = decompressInitGraph(initGraph)
        [ g.v(invocs.defStmtsPerArg[0][0][0]).code, g.v(invocs.defStmtsPerArg[0][1][0]).code]
        """
        x = self.j.runGremlinQuery(query)
        self.assertTrue(x[0].find('sourceA') == -1)
        self.assertTrue(x[1].find('sourceB') != -1)

    def testCanBeTainted1(self):
        
        query = """

        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        callSiteId = getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        initGraph = createInitGraph(callSiteId)
        canBeTainted(initGraph, argDescrs)
        
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, True)

    def testCanBeTainted2(self):
        
        query = """
        
        callSiteId = getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        initGraph = createInitGraph(callSiteId)
        canBeTainted(initGraph, [{ it.code.contains('sourceX')}, { it.code.contains('sourceB')} ] )
        
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, False)

    def testIsTainted1(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        callSiteId = getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        initGraph = createInitGraph(callSiteId)
        invocs = decompressInitGraph(initGraph)
        invocs.collect{ isTainted(it, argDescrs) }

        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], True)

    def testIsTainted2(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        callSiteId = getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .id.toList()[0];
        initGraph = createInitGraph(callSiteId)
        invocs = decompressInitGraph(initGraph)
        invocs.collect{ isTainted(it, argDescrs) }

        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], False)

    
    def testTaintedArgs1(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        
        getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .taintedArgs(argDescrs)
        
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 2)

    
    def testTaintedArgs2(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        
        getFunctionASTsByName("two_arg_sink_caller")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .taintedArgs(argDescrs)
        
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 0)

    def testUnchecked1(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        sanitizerDescrs = [ null, { it,s -> it.code.contains(s) }]
        
        getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .taintedArgs(argDescrs)
        .unchecked(sanitizerDescrs)
                
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testUnchecked2(self):
        
        query = """
        
        argDescrs = [{ it.code.contains('sourceA')}, { it.code.contains('sourceB')} ]
        sanitizerDescrs = [ { it,s -> false }, { it,s -> false } ]
        
        getFunctionASTsByName("two_arg_sink_caller_p")
        .match{ it.type == "CallExpression" && it.code.startsWith('asink') }
        .taintedArgs(argDescrs)
        .unchecked(sanitizerDescrs)
        
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 2)
