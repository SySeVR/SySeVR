
/**
	Return only visible nodes.
*/

Gremlin.defineStep('visible', [Vertex, Pipe], {
	_().filter{
		if(it.type == 'File')
			(it.hidden != '1')
		else if(it.type == 'Function'){
			l = it.functionToFiles().visible().toList()			
			it.hidden != '1' && l != []	
		}else{
			l = it.functions().visible.toList()
			l != []
		}
	}
});

