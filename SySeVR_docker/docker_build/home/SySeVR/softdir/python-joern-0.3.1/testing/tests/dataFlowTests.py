
from PythonJoernTests import PythonJoernTests

class DataFlowTests(PythonJoernTests):
    
    def testSources(self):
        query = """getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .sources().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testProducers(self):
        query = """ getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .producers(['x'])
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testProducersNegative(self):
        query = """ getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .producers([''])
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 0)

    def testCfgPaths(self):
                
        query = """
        
        dstNode = getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo').statements().toList()[0]

        srcNode = getFunctionASTsByName('ddg_simplest_test')
        .getNodesWithTypeAndCode('AssignmentExpr', '*').statements().toList()[0]
        
        cfgPaths('x', { it, s -> [] } , srcNode, dstNode )
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x[0]), 2)

    def testUnsanitized(self):
        query = """
        
        getFunctionASTsByName('ddg_simplest_test')
        .getCallsTo('foo')
        .statements()
        .unsanitized({ it, s -> []})
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testCallTainting(self):
        query = """
        getFunctionASTsByName('test_call_tainting').
        getCallsTo('taint_source').
        sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'y == 0')
        

    def testTwoTaintSources(self):
        query = """
        getFunctionASTsByName('two_taint_sources')
        .getCallsTo('taint_source').
        sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'y == 0')

    def testTwoTaintSources2(self):
        query = """
        getFunctionASTsByName('two_taint_sources')
        .getCallsTo('second_taint_source').
        sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'z == 0')
    
    def testNotATaintSource(self):
        query = """
        getFunctionASTsByName('test_dataFlowFromUntainted')
        .getCallsTo('not_a_taint_source')
        .sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, [])

    def testParamTaintByCall(self):
        
        query = """
        getFunctionASTsByName('testParamTaint')
        .getCallsTo('taint_source')
        .sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, ['EXIT'])
        
    def testParamTaintByAssign(self):
        
        query = """
        getFunctionASTsByName('testParamTaintAssign')
        .match{it.type == 'AssignmentExpr'}
        .sinks().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x, ['EXIT'])
        
