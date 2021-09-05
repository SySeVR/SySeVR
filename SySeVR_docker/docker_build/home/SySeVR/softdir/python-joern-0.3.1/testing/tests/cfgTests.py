from PythonJoernTests import *

class CFGTests(PythonJoernTests):

    def _numberCFGNodes(self, function):
        query = """getFunctionsByName('%s')
        .functionToStatements()""" % function
        return self.j.runGremlinQuery(query)

    def _numberCFGEdges(self, function):
        query = """getFunctionsByName('%s')
        .functionToStatements().outE('FLOWS_TO')""" % function
        return self.j.runGremlinQuery(query)

    def _CFGConditionEdgeLabels(self, function):
        query = """getFunctionsByName('%s')
        .functionsToASTNodesOfType('Condition')
        .outE('FLOWS_TO').flowLabel""" % function
        return self.j.runGremlinQuery(query)

    def _CFGInfiniteNodeEdgeLabels(self, function):
        query = """getFunctionsByName('%s')
        .functionsToASTNodesOfType('InfiniteForNode')
        .outE('FLOWS_TO').flowLabel""" % function
        return self.j.runGremlinQuery(query)

    

    def testSwitch1(self):
        self.assertEquals(len(self._numberCFGNodes('switch_test1')), 9)
        self.assertEquals(len(self._numberCFGEdges('switch_test1')), 11)
        labels = self._CFGConditionEdgeLabels('switch_test1')
        self.assertIn('case 1', labels)
        self.assertIn('case 2', labels)
        self.assertIn('case 3', labels)
        self.assertEqual(len(labels), 4)

    def testSwitch2(self):
        self.assertEquals(len(self._numberCFGNodes('switch_test2')), 10)
        self.assertEquals(len(self._numberCFGEdges('switch_test2')), 12)
        labels = self._CFGConditionEdgeLabels('switch_test2')
        self.assertIn('case 1', labels)
        self.assertIn('case 2', labels)
        self.assertIn('case 3', labels)
        self.assertEqual(len(labels), 4)

    def testSwitch3(self):
        self.assertEquals(len(self._numberCFGNodes('switch_test3')), 9)
        self.assertEquals(len(self._numberCFGEdges('switch_test3')), 10)
        labels = self._CFGConditionEdgeLabels('switch_test3')
        self.assertIn('case 1', labels)
        self.assertIn('case 2', labels)
        self.assertIn('default', labels)
        self.assertEqual(len(labels), 3)

    def testSwitch4(self):
        self.assertEquals(len(self._numberCFGNodes('switch_test4')), 9)
        self.assertEquals(len(self._numberCFGEdges('switch_test4')), 11)
        labels = self._CFGConditionEdgeLabels('switch_test4')
        self.assertIn("case '1'", labels)
        self.assertIn("case '2'", labels)
        self.assertIn("case '3'", labels)
        self.assertEqual(len(labels), 4)

    def testGoto(self):
        self.assertEquals(len(self._numberCFGNodes('goto_test')), 5)
        self.assertEquals(len(self._numberCFGEdges('goto_test')), 5)
        labels = self._CFGConditionEdgeLabels('goto_test')
        self.assertIn('True', labels)
        self.assertIn('False', labels)
        self.assertEqual(len(labels), 2)

    def testSimpleFor(self):
        self.assertEquals(len(self._numberCFGNodes('simple_for_test')), 7)
        self.assertEquals(len(self._numberCFGEdges('simple_for_test')), 7)
        labels = self._CFGConditionEdgeLabels('simple_for_test')
        self.assertIn('True', labels)
        self.assertIn('False', labels)
        self.assertEqual(len(labels), 2)

    def testInfiniteFor(self):
        self.assertEquals(len(self._numberCFGNodes('infinite_for_test')), 4)
        self.assertEquals(len(self._numberCFGEdges('infinite_for_test')), 4)
        labels = self._CFGInfiniteNodeEdgeLabels('infinite_for_test')
        self.assertIn('True', labels)
        self.assertIn('False', labels)
        self.assertEqual(len(labels), 2)

    def testFor1(self):
        self.assertEquals(len(self._numberCFGNodes('for_test1')), 4)
        self.assertEquals(len(self._numberCFGEdges('for_test1')), 4)
        labels = self._CFGConditionEdgeLabels('for_test1')
        self.assertIn('True', labels)
        self.assertIn('False', labels)
        self.assertEqual(len(labels), 2)

    def testFor2(self):
        self.assertEquals(len(self._numberCFGNodes('for_test2')), 5)
        self.assertEquals(len(self._numberCFGEdges('for_test2')), 5)
        labels = self._CFGConditionEdgeLabels('for_test2')
        self.assertIn('True', labels)
        self.assertIn('False', labels)
        self.assertEqual(len(labels), 2)
    
    def testComplexCFG(self):
        self.assertEquals(len(self._numberCFGNodes('complex_test')), 29)
        self.assertEquals(len(self._numberCFGEdges('complex_test')), 36)
