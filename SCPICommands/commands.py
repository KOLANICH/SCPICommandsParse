__all__=("Command", "CommandGroup", "CommandGroupAdapter")

class CommandProto:
	def __init__(self, name):
		self.name=name

class Command(CommandProto):
	__slots__=("r", "w", "raw", "args")
	def query(self):
		return self.r and self.w
	def __init__(self, name, args=tuple(), w=True, r=False, raw=False):
		super().__init__(name)
		self.r=r
		self.w=w
		self.raw=raw
	
	def __call__(self, path, query, *args):
		txt=":".join(path)+":"+self.name
		if query:
			txt+="?"
		if args:
			txt+=" "+", ".join(( str(arg) for arg in args ))
		return txt

class CommandAdapterProto:
	__slots__=("parent","root")
	def __init__(self, parent):
		self.parent=parent
		if parent:
			while parent.parent:
				parent=parent.parent
		self.root=parent.parent

methodSelector={
	0b00: "write",
	0b01: "write_raw",
	0b10: "query",
	0b11: "query_raw",
}

class CommandAdapter(CommandAdapterProto):
	def __init__(self, parent, command):
		super().__init__(parent)
		self.command=command
	
	def __call__(self, path, *args):
		query=self.command.r and ( (not self.command.w) or (not args and self.command.w) )
		
		txt=self.command(path, query, *args)
		return getattr(self.root.conn, methodSelector[query<<1|self.command.raw])(txt)

class CommandGroup(CommandProto):
	def __init__(self, name, commands):
		super().__init__(name)
		self.commands=commands

import functools

class CommandGroupAdapter(CommandAdapterProto):
	def __init__(self, conn, group, parent=None):
		super().__init__(conn)
		self._group=group
		self._dic={}
		self._parent=parent
		
		for c in group.commands:
			if isinstance(c, Command):
				self._dic[c.name]=CommandAdapter(conn, c)
			elif isinstance(c, CommandGroup):
				self._dic[c.name]=CommandGroupAdapter(conn, c, parent=self)
	
	@property
	@functools.lru_cache(None)
	def _path(self):
		p=[]
		el=self
		while el:
			p.append(el._group.name)
			el=el._parent
		p.reverse()
		return tuple(p)
	
	@functools.lru_cache(None)
	def __getattr__(self, k):
		if k[-1] =="?":
			raise ValueError("Use the stuff without question marks in the end.!")
		if k[0]!="_":
			r=self._dic[k]
			if isinstance(r, CommandAdapter):
				return functools.partial(r, self._path)
			return r
		else:
			return super().__getattr__(k)
	
	def __dir__(self):
		return self._dic.keys()
	
	def __hasattr__(self, k):
		return k in self._dic

class ChannelCommandGroupAdapter(CommandAdapterProto):
	def __init__(self, conn, group, parent=None, chanName="Math"):
		super().__init__(conn, group, parent)
		self.chanName=chanName

class TestConn():
	write=print
	read=print
	write_raw=print
	read_raw=print
	query=print

#tc=TestConn()
#tr=CommandGroupAdapter(tc, root)


def a():
	Command('{0}:DISPlay {1}'.format(channel, int(enable)), r=True)
	Command("{0}:PROBe {1}".format(channel, ratio), r=True)
	Command("{0}:OFFSet {1}".format(channel, volts), r=True)
	Command("{0}:SCALe {1}".format(channel, volts), r=True)
