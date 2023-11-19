from __future__ import annotations
from pprint import pprint

import clr

import dotnetwrapper.dotnetparser as parser

clr.AddReference("System.Reflection")

import System.Reflection

target_assembly = "C:/Program Files/National Instruments/VeriStand 2021/NationalInstruments.VeriStand.SystemDefinitionAPI.dll"

assembly_to_stub = System.Reflection.Assembly.LoadFrom(target_assembly)

asm = parser.Assembly.from_dotnet(assembly_to_stub)

pprint(asm.exported_types)
