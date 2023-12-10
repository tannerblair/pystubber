from pathlib import Path

from nationalinstruments.veristand.systemdefinitionapi import SystemDefinition

sysdef = SystemDefinition("Hello", "world", "Python", "1.0", "Controller", "Windows", str(Path(__file__).parent / "test.nivssdf"))
print(sysdef)