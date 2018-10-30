from .util import *

from .commands import *
from .devices import *
from .graph import *

def graphToObjectHierarchy(graph, yaml=True):
	o=networkx.convert.to_dict_of_dicts(graph.graph)
	o1={}
	virtualTable={}
	leavesMap={}
	print("o", o)
	
	for nId in o:
		n=nId[-1]
		if not isinstance(n, LeafNode):
			r=type(o[nId])({"$virt":{}})
			anchorName=str(n)
		else:
			r=n.toDict()
		
		if yaml:
			#print(n)
			if not isinstance(n, LeafNode):
				r=ruamel.yaml.comments.CommentedMap(r)
				r.yaml_set_anchor(str(nId))
		
		if isinstance(n, (VirtualToken, LeafNode)):
			virtualTable[nId]=r
		else:
			o1[nId]=r

	print("o1", o1)
	for nId in o:
		n=nId[-1]
		if isinstance(n, (VirtualToken, LeafNode)):
			r=virtualTable[nId]
		else:
			r=o1[nId]

		for vId in o[nId]:
			v=vId[-1]
			if isinstance(v, VirtualToken):
				r["$virt"][id(virtualTable[vId])]=virtualTable[vId]
			elif isinstance(v, LeafNode):
				r["$leaf"]=virtualTable[vId]
				leavesMap[v.name]=r["$leaf"]
			else:
				r[v.name]=o1[vId]
				if v.prefix!=":":
					r[v.name]["$prefix"]=v.prefix
		
		if "$virt" in r:
			if not r["$virt"]:
				del(r["$virt"])
			else:
				print(r["$virt"])
				r["$virt"]=list(r["$virt"].values())
		
	return virtualTable[(graph.root,)], leavesMap

