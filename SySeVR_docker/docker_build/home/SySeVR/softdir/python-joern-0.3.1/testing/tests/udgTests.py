
from PythonJoernTests import *

class UDGTests(PythonJoernTests):

    def testSimpleDecl(self):
        query = """getFunctionASTsByName('udg_test_simple_decl')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().filter{it.code == 'x'}
        .code
        """        
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testDeclWithAssign(self):
        query = """getFunctionASTsByName('udg_test_decl_with_assign')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().filter{it.code == 'x'}
        .code
        """        
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testParamDecl(self):
        query = """getFunctionASTsByName('udg_test_param_decl')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().filter{it.code == 'x'}
        .code
        """        
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testUntaintedParamUse(self):
        
        query = """getFunctionASTsByName('udg_test_use_untainted_call')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().filter{it.code == 'x'}
        .code
        """
        
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 0)

        query = """getFunctionASTsByName('udg_test_use_untainted_call')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses().filter{it.code == 'x'}
        .code
        """
        
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    def testStructFieldUse(self):
        
        query = """getFunctionASTsByName('udg_test_struct_field_use')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses()
        .code
        """
        
        x = self.j.runGremlinQuery(query)
        self.assertTrue('x . y' in x)
        self.assertTrue('x' in x)

    def testArrUse(self):
        
        query = """getFunctionASTsByName('arrUse')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses()
        .code
        """
        
        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('arr' in x)
        self.assertTrue('i' in x)


    def testComplexArg(self):
        
        query = """getFunctionASTsByName('complexInArgs')
        .astNodes().filter{ it.type == 'Argument'}
        .uses().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 3)

    def testStatementContainingCall(self):
        
        query = """getFunctionASTsByName('complexInArgs')
        .astNodes().filter{ it.type == 'Argument'}
        .statements()
        .uses().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 5)
        

    def testComplexAssign(self):
        
        query = """getFunctionASTsByName('complexAssign')
        .astNodes().filter{ it.type == 'AssignmentExpr'}
        .defines().code
        """
        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('* pLtv' in x)
        self.assertTrue('pLtv -> u' in x)
        self.assertTrue('pLtv -> u . u16' in x)

    def testConditionalExpr(self):
        
        query = """getFunctionASTsByName('conditional_expr')
        .astNodes()
        .filter{ it.type == 'Condition'}
        .uses()
        .code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(len(x), 1)

    
    def testDefEdgeFromTaintedArg(self):
        
        query = """getFunctionASTsByName('test_call_tainting')
        .astNodes()
        .filter{ it.type == 'Argument' && it.code == '& y'}
        .defines().code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'y')

    def testPlusEquals(self):
        query = """
        getFunctionASTsByName('plusEqualsUse')
        .astNodes()
        .filter{ it.type == 'ExpressionStatement'}
        .out('DEF').code
        """

        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'x')

    def testPlusEqualsExpr(self):
        query = """
        getFunctionASTsByName('plusEqualsUse')
        .astNodes()
        .filter{ it.type == 'AssignmentExpr'}
        .out('DEF').code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'x')

    def testPlusEqualsExprUse(self):
        query = """
        getFunctionASTsByName('plusEqualsUse')
        .astNodes()
        .filter{ it.type == 'AssignmentExpr'}
        .out('USE').code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'x')

    def testPlusPlusDef(self):
        query = """
        getFunctionASTsByName('plusplus')
        .astNodes()
        .filter{ it.type == 'ExpressionStatement'}
        .out('DEF').code
        """
    
    def testPlusPlusDefExpr(self):
        query = """
        getFunctionASTsByName('plusplus')
        .astNodes()
        .filter{ it.type == 'IncDecOp'}
        .out('DEF').code
        """

        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'a') 

    def testPlusPlusUseExpr(self):
        query = """
        getFunctionASTsByName('plusplus')
        .astNodes()
        .filter{ it.type == 'IncDecOp'}
        .out('USE').code
        """
        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'a') 

    def testAssignToArrayField(self):
        query = """
        getFunctionASTsByName('udg_test_assign_to_array_field')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().code
        """
         
        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('* arr' in x)

    def testAssignToExprDef(self):
        query = """
        getFunctionASTsByName('udg_test_assign_to_expression')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines()
        .code
        """
         
        x = self.j.runGremlinQuery(query)
        self.assertTrue('* ( a + b )' in x)
        self.assertTrue('* a' in x)
        self.assertTrue('* b' in x)
    
    def testAssignToExprUse(self):
        query = """
        getFunctionASTsByName('udg_test_assign_to_expression')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses()
        .code
        """
         
        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('a' in x)
        self.assertTrue('b' in x)
        

    def testArrDefDef(self):
        
        query = """
        getFunctionASTsByName('test_buf_def')
        .astNodes().filter{it.isCFGNode == 'True'}
        .defines().code
        """

        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('* buf' in x)
        self.assertTrue('* i' in x)

    def testArrDefUse(self):

        query = """
        getFunctionASTsByName('test_buf_def')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses().code
        """

        x = self.j.runGremlinQuery(query)
        
        self.assertTrue('buf' in x)
        self.assertTrue('i' in x)

    def testNonDerefUnary(self):

        query = """
        getFunctionASTsByName('nonDerefUnary')
        .astNodes().filter{it.isCFGNode == 'True'}
        .uses().code
        """

        x = self.j.runGremlinQuery(query)
        self.assertEquals(x[0], 'a')
