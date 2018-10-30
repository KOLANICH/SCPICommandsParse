import parglare
from pathlib import Path
curDir=Path(__file__).parent

addrGrammar = parglare.Grammar.from_file(str(curDir/"addr.pg"))
argsGrammar = parglare.Grammar.from_file(str(curDir/"args.pg"))
grammar = parglare.Grammar.from_file(str(curDir/"vx11command.pg"))
#parser = parglare.Parser(grammar, ws=False)
parser = parglare.GLRParser(grammar, ws=False)

addrParser = parglare.GLRParser(addrGrammar, ws=False)
argsParser = parglare.GLRParser(argsGrammar, ws=False)

def selfTest():
	for parser, lines in selftests:
		for l in lines:
			print(parser.parse(l))

selftests=(
	(addrParser,
		(
			":DISPlay:TEXT[:SET]",
			":DISPlay:TEXT[:SET]",
		)
	),
	(argsParser,
		(
			"<string>",
			"<string>[,<x>]",
			"<string>[,<x>[,<y>]]",
			"<file1>,<file2>",
		)
	),
	(parser,
		(
			":DISPlay:TEXT[:SET] <string>",
			":DISPlay:TEXT[:SET] <string>[,<x>]",
			":DISPlay:TEXT[:SET] <string>[,<x>[,<y>]]",
			":MMEMory:MOVE <file1>,<file2>"
		)
	),
)
#g=networkx.Graph()
selfTest()

def alternative2iter(alt):
	if isinstance(alt, grammar.classes["args.alternative"]):
		yield from alternative2iter(alt.first)
		yield from alternative2iter(alt.last)
	else:
		yield alt

def parse(line:str):
	res=parser.parse(line)
	path=[]
	assert(len(res) == 1)
	res=res[0]
	cmdName=res.addr.cmdName
	#print(cmdName.__class__)
	#print(cmdName)
	
	special=False
	
	def addrReducer(token, optionality=0):
		if isinstance(token ,list):
			for token in token:
				#print("token: ", token, dir(token))
				addrReducer(token, optionality)
		else:
			if isinstance(token ,grammar.classes["addr.addrToken"]):
				path.append((token.prefix, token.name.name, optionality))
			elif isinstance(token ,grammar.classes["addr.special"]):
				path.append((token.prefix, token.name.name, optionality))
				special=True
			elif isinstance(token, grammar.classes["addr.optionalAddr"]):
				addrReducer(token.optionalPath, optionality+1)
				path.append((None, None, optionality))
			else:
				#print(token)
				raise Exception()
	
	addrReducer(cmdName)
	
	args=res.args
	if args:
		#print(type(args))
		args=args.args
		if isinstance(args, grammar.classes["args.optionalArgs"]):
			argsAreOptional=True
			args=args.args
		
		argz=[]
		
		if args.first:
			def argsReducer(a):
				#print("argsReducer", a)
				if hasattr(a, "args"):
					return argsReducer(a.args)
				
				if isinstance(a, list):
					argz=[]
					for b in a:
						argz.extend(argsReducer(b))
					return argz
				elif hasattr(a, "arg"):
					return argsReducer(a.arg)
				else:
					#print("argsReducer else", a)
					return [a]
			
			argz.extend(argsReducer(args.first))
			if args.rest:
				argz.extend(argsReducer(args.rest))
		args=argz
	
	argNames=[]
	if args:
		for a in args:
			while isinstance(a, grammar.classes["args.argInCurlyBraces"]):
				a=a.arg
			if isinstance(a, grammar.classes["args.alternative"]):
				for b in alternative2iter(a):
					if isinstance(b, grammar.classes["args.basic.argument"]):
						argNames.append(b.name)
						break
			else:
				argNames.append(a.name)
	
	#args=[a.name for a in args]
	#print({"path":path, "query":res.addr.queryMarker, "args": argNames})
	return {"path":path, "query":res.addr.queryMarker, "args": argNames, "fullCmd":res}
