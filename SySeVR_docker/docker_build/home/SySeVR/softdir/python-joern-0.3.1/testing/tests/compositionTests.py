
from PythonJoernTests import *

class CompositionTests(PythonJoernTests):
    
    def testSyntaxOnlyChaining(self):
        
        # functions calling foo AND bar
        
        query = "getCallsTo('foo').getCallsTo('bar')"
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
    
    def testNotComposition(self):
        
        # functions calling foo AND NOT bar
        
        query = "getCallsTo('foo').not{getCallsTo('bar')}"
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 6)
    
    def testPairsComposition(self):
        
       query = """queryNodeIndex('type:AssignmentExpr AND code:"x = bar ( y )"')
       .pairs( _().lval().code, _().rval().code)"""
       x = self.j.runGremlinQuery(query)
       self.assertEquals(x[0][0], "x")
       self.assertEquals(x[0][1], "bar ( y )")
