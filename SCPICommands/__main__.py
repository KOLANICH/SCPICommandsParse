import RichConsole

style={
	"success": RichConsole.groups.Fore.lightgreenEx,
	"fail": RichConsole.groups.Fore.lightredEx,
}

from pathlib import Path

from .vx11CommandParse import parse
from .commands import *
from .devices import *

from . import graphToObjectHierarchy


curDir=Path(__file__).parent
testsDataDir=Path(".")/"testData"

from string import ascii_uppercase as uppercase
uppercase=frozenset(uppercase)

from .util import *
from .graph import *

def preprocessFile(f:Path):
	lines=list(f.read_text().splitlines())
	succesfulLines=[]
	failedLines=[]
	certainlySuccesfulLines=[]

	for line in sorted(set(lines)):
		try:
			res=parse(line)
			if res['query'] or res['args']:
				certainlySuccesfulLines.append(line)
			else:
				if len(res["path"]) == 1 and countOfBigLetters(res[0].name)<2:
					failedLines.append(line)
				else:
					succesfulLines.append(line)
			print(style["success"](line), " -> ", res)
		except:
			failedLines.append(line)
			print(style["fail"](line))

	with f.open("wt", encoding="utf-8") as fd:
		fd.write("\n".join(failedLines))
		fd.write("\n\n")
		fd.write("\n".join(succesfulLines))
		fd.write("\n\n")
		fd.write("\n".join(certainlySuccesfulLines))



from plumbum import cli


class CLI(cli.Application):
	pass

class FilesProcessor(cli.Application):
	def main(self, *files):
		if not files:
			files=(".",)
		newFiles=[]
		for fileOrDir in files:
			fileOrDir=Path(fileOrDir)
			
			if fileOrDir.is_dir():
				newFiles.extend(testsDataDir.glob("**/*.txt"))
			else:
				newFiles.append(fileOrDir)
		self.files=newFiles

@CLI.subcommand("preprocess")
class PreprocessCLI(FilesProcessor):
	def main(self, *files):
		super().main(*files)
		for f in self.files:
			preprocessFile(f)



from pprint import pprint


@CLI.subcommand("makeModel")
class MakeModelCLI(FilesProcessor):
	def main(self, *files):
		super().main(*files)
		for f in self.files:
			lines=list(f.read_text().splitlines())
			certainlySuccesfulRess=[]
			
			for line in sorted(set(lines)):
				if line:
					#try:
					res=parse(line)
					if res['query'] or res['args']:
						certainlySuccesfulRess.append(res)
					else:
						certainlySuccesfulRess.append(res)
						pass
					print(style["success"](line), " -> ", res)
					#except:
					#	pass
			
			#print(certainlySuccesfulRess)
			tg=TokensGraph()
			
			for ress in certainlySuccesfulRess[:10]:
				print(ress)
				#tg=TokensGraph()
				tg.importPath(ress["path"], **({
					"r":ress["query"],
					"w":bool(ress["args"] or not ress["query"]),
					"args": ress["args"]
				}))
			
				tg.optimize()
			
				oRoot, leavesMap=graphToObjectHierarchy(tg)
				print(yaml(oRoot))
				
			"""
			iter(leavesMap.values())oLeaf.update()
			"""
			
			#print("oRoot", oRoot)
			print(yaml(oRoot))
			
			#print(json.dumps(root, indent="\t"))
			

if __name__=="__main__":
	CLI.run()