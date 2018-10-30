from networkx import *
from .util import yaml

class Token:
	__slots__=("name", "prefix")
	def __init__(self, name="", prefix=":"):
		self.name=name
		self.prefix=prefix
	
	def __hash__(self):
		return hash((self.name, self.prefix))
	
	def __repr__(self):
		return self.prefix+self.name
	
	def __eq__(self, other):
		return (self.name, self.prefix)==(other.name, other.prefix)

class VirtualToken(Token):
	def __hash__(self):
		return id(self)
	
	def __repr__(self):
		return "~"+self.name+"("+hex(id(self))+")~"

class LeafNode(Token):
	__slots__=("r", "w", "args", "raw")
	def __init__(self, name="", args=tuple(), w=True, r=False, raw=False):
		super().__init__(name)
		self.r=r
		self.w=w
		self.raw=raw
		self.args=args
	
	def toDict(self):
		return {k:getattr(self, k) for k in __class__.__slots__}
	
	def __hash__(self):
		return id(self)
	
	def __repr__(self):
		return "("+", ".join(self.args)+") "+repr({"r":self.r, "w":self.w, "raw": self.raw})
	
	def update(self, dict):
		
		
		(pfx, cmdName, optionality)=ress["path"][-1]
		
		res={
			"r":ress["query"],
			"w":bool(ress["args"] or not ress["query"]),
			"args": ress["args"]
		}
		
		if cmdName in gr:
			updatee=gr[cmdName]
			updatee["r"]|=res["r"]
			updatee["w"]|=res["w"]
			assert(bool(updatee["args"]) != bool(res["args"])), cmdName + " " + repr(updatee["args"]) + " " + repr(res["args"])
			if not updatee["args"]:
				updatee["args"]=res["args"]
			del(res["r"])
			del(res["w"])
			del(res["args"])
			gr[cmdName].update(res)
		else:
			gr[cmdName]=res
		
		
		#pprint(gr)

class _PathInGraph:
	def __hash__(self):
		return hash(tuple(self))
	
	def __eq__(self, other):
		return tuple(self)==tuple(other)
	
	def __repr__(self):
		return self.__class__.__name__+"<"+str(self)+">"
	
	def __str__(self):
		return "".join((el.prefix+el.name for el in self[1:]))
	
	@property
	def name(self):
		return self.path[-1]

class TuplePathInGraph(_PathInGraph, tuple):
	pass

class ListPathInGraph(_PathInGraph, list):
	pass


class TokensGraph():
	def __init__(self):
		self.graph=DiGraph()
		self.root=VirtualToken("r")
		self.rootId=TuplePathInGraph((self.root,))
		self.poss={self.rootId:(-1,0)}
		self.visiblePaths={}
	
	def importPath(self, tokenz, **kwargs):
		g=self.graph
		leaf=LeafNode(**kwargs)
		
		prevId=self.rootId
		optionalityStack=[]
		nameStack=ListPathInGraph(self.rootId)
		visibleStack=ListPathInGraph(self.rootId)
		prevOptionality=0
		virtualTokensCounter=0
		for i, (prefix, name, optionality) in enumerate(tokenz):
			if name is None:
				idTup=VirtualToken(prevId[-1].name.lower()+"_"+str(virtualTokensCounter))
			else:
				idTup=Token(name, prefix)
				visibleStack.append(idTup)
			
			if visibleStack in self.visiblePaths:
				if len(nameStack) > len(self.visiblePaths[visibleStack]):
					self.visiblePaths[visibleStack]=nameStack
				else:
					nameStack=self.visiblePaths[visibleStack]
				continue
			else:
				nameStack.append(idTup)
				self.visiblePaths[visibleStack]=nameStack
			
			id=TuplePathInGraph(nameStack)
			
			if name is None:
				self.poss[id]=(i, optionality+0.1)
				virtualTokensCounter+=1
			else:
				self.poss[id]=(i, optionality)
			
			#print("has visibleStack", visibleStack, hash(visibleStack), self.graph.has_node(visibleStack))
			#print("has nameStack", nameStack, hash(nameStack), self.graph.has_node(nameStack))
			
			if self.graph.has_node(id):
				continue
			
			if prevOptionality < optionality:
				optionalityStack.append(prevId)
			elif prevOptionality > optionality:
				#print(optionalityStack)
				for el in optionalityStack:
					#print(el, "->", id)
					g.add_edge(el, id)
				del(optionalityStack[optionality:])
			g.add_edge(prevId, id)
			
			prevId=id
			prevOptionality=optionality
		
		nameStack.append(leaf)
		id=TuplePathInGraph(nameStack)
		g.add_edge(prevId, id)
		
		for optId in optionalityStack:
			g.add_edge(optId, id)
		
		self.poss[id]=(len(tokenz), 0)
		return leaf


	def optimize(self):
		doing=True
		while doing:
			doing=False
			for n in self.graph.node:
				if isinstance(n, VirtualToken) and n is not self.root:
					e=self.graph.edges(n)
					#print(n, e)
					if len(e) == 1:
						self.graph=networkx.contracted_nodes(self.graph, *reversed(next(iter(e))), self_loops=False)
						doing=True
						break
		return self.graph
	
	

