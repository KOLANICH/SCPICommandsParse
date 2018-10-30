from .commands import *

basicCommands=CommandGroup("", [
	Command("*IDN", r=True, w=False)
])

root=CommandGroup("", [
	Command("STOP"),
	Command("RUN"),
	Command("SINGle"),
	Command("TFORce"),
	CommandGroup("WAVeform", (
		Command("SOURce", ("channel",)),
		Command("FORMat", ("format",)),
		Command("MODE", ("mode",), r=True),
		Command("STARt", ("pos",), r=True),
		Command("STOP", ("pos",)),
		Command("PREamble", r=True, w=False),
		Command("DATA", r=True, w=False, raw=True),
	)),
	CommandGroup("TIMebase", (
		Command("MAIN:OFFSet", ("offset",), r=True),
		Command("MAIN:SCALe", ("base",), r=True),
	)),
	CommandGroup("ACQuire", (
		Command("MDEPth", ("mdepth",), r=True),
		Command('SRATe?', r=True, w=False),
	)),
	CommandGroup("DISPlay", (
		Command("DATA", ("color", "invert", "format"), raw=True),
	)),
	CommandGroup("TRIGger", (
		Command('STATus', r=True, w=False),
		CommandGroup("STATistic", (
			Command("item?", ("type", "item", "channel"), r=True, w=False),
		)),
	)),
	Command("*IDN", r=True, w=False)
])
