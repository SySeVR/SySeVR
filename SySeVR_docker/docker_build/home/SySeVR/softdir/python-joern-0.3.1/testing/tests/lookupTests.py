
from PythonJoernTests import *

class IndexLookupTests(PythonJoernTests):
    
    def testGetNodesWithTypeAndCode(self):

        query = 'getNodesWithTypeAndCode("Callee", "bar")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testGetNodesWithTypeAndName(self):

        query = 'getNodesWithTypeAndName("Function", "foo")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
        
    def testGetFunctionsByName(self):
        
        query = 'getFunctionsByName("foo")'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testGetCallsTo(self):
        
        query = 'getCallsTo("bar")'
        x = self.j.runGremlinQuery(query)
        self.assertTrue(len(x) == 1)

    def testGetArguments(self):
        
        query = 'getArguments("bar", "0").code'
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'y')
