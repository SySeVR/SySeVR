from PythonJoernTests import *

class InterprocTests(PythonJoernTests):
    
    def testTaintedArgs(self):
        query = """
        getFunctionASTsByName("interproc_arg_tainter_test")
        .match{ it.type == "CallExpression" && it.code.startsWith('interproc') }
        .taintedArguments()
        .code

        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
    
    def testArgTainters(self):
        query = """
        getFunctionASTsByName("interproc_arg_tainter_test")
        .match{ it.type == "CallExpression" && it.code.startsWith('interproc')}
        .argTainters()
        .code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], '* x = source12 ( )')
    
    def testTaintedArg(self):
        query = """
        getFunctionASTsByName("interproc_arg_tainter_test")
        .match{ it.type == "CallExpression" && it.code.startsWith('sink12')}
        .taintedArg('0', { it -> if(it.code.matches('.*source12.*')) [1] else [] } )
        .code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)
    
    def testGetNodesToSrc(self):
        
        query = """
        getFunctionASTsByName("interproc_arg_tainter_test")
        .match{ it.type == "CallExpression" && it.code.startsWith('sink12')}
        .statements()
        .transform{ it -> getNodesToSrc(it, { it2 -> if(it2.code.matches('.*source12.*')) [20] else [] }  , 4) }
        .scatter().transform{ g.v(it[0]).code }
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[1], 'interproc_callee ( & x )')

    def testIUnsanitized(self):
        
        query = """
        getFunctionASTsByName("interproc_arg_tainter_test")
        .match{ it.type == "CallExpression" && it.code.startsWith('sink12')}
        .statements()
        .iUnsanitized(NO_RESTRICTION, { it2 -> if(it2.code.matches('.*source12.*')) [20] else [] } )
        .code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], '* x = source12 ( )')
