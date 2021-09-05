
Gremlin.defineStep('paramsToNames', [Vertex,Pipe], {
	_().children().filter{ it.type != 'ParameterType'}
})

Gremlin.defineStep('paramsToTypes', [Vertex,Pipe], {
	_().children().filter{ it.type == 'ParameterType'}
})
