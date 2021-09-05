from PythonJoernTests import *

class ParsingTests(PythonJoernTests):
    
    def testNewOperator1(self):
        
        query = """getFunctionASTsByName('new_operator_test')
        .astNodes().filter{ it.isCFGNode == 'True'}.code"""
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 3)
        
