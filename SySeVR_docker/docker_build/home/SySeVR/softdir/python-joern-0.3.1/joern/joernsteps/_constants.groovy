
NODE_INDEX = 'nodeIndex'

// Node Keys

NODE_TYPE = 'type'
NODE_NAME = 'name'
NODE_CODE = 'code'
NODE_FILEPATH = 'filepath'

// Node Values

TYPE_CALL = 'CallExpression'
TYPE_CALLEE = 'Callee'
TYPE_FUNCTION = 'Function'
TYPE_ARGLIST = 'ArgumentList'
TYPE_ASSIGNMENT = 'AssignmentExpr'

TYPE_IDENTIFIER_DECL_STMT = 'IdentifierDeclStatement'
TYPE_PARAMETER = 'Parameter'

TYPE_FILE = 'File'

// Edge types

AST_EDGE = 'IS_AST_PARENT'
CFG_EDGE = 'FLOWS_TO'

USES_EDGE = 'USE'
DEFINES_EDGE = 'DEF'
DATA_FLOW_EDGE = 'REACHES'

FUNCTION_TO_AST_EDGE = 'IS_FUNCTION_OF_AST'

FILE_TO_FUNCTION_EDGE = 'IS_FILE_OF'

// Edge keys

DATA_FLOW_SYMBOL = 'var'