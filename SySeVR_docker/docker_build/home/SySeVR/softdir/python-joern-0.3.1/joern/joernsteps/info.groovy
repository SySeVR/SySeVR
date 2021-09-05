
Gremlin.defineStep('locations', [Vertex,Pipe], {
	_()
	.statements().sideEffect{code = it.code }
	.functions().sideEffect{ name = it.name; }
	.functionToFiles().sideEffect{ filename = it.filepath; }
	.transform{ [code, name, filename] }
})

Gremlin.defineStep('functions', [Vertex,Pipe],{
	_().functionId.idsToNodes()
});

Gremlin.defineStep("functionToFiles", [Vertex,Pipe], {
	_().in(FILE_TO_FUNCTION_EDGE)
})

