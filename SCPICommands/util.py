
try:
	try:
		import ujson as json
	except:
		import simple_json as json
except:
	import json

import ruamel.yaml
from io import StringIO

def yaml(o) -> str:
	yamlDumper = ruamel.yaml.YAML(typ="rt")
	yamlDumper.indent(mapping=2, sequence=4, offset=2)
	with StringIO() as s:
		yamlDumper.dump(o, s)
		return s.getvalue()

def countOfBigLetters(t):
	r=0
	for c in t:
		if c in uppercase:
			r+=1
	return r

