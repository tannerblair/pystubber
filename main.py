from pprint import pprint

import dotnetwrapper.dotnetparser as parser

target_assembly = "C:/Program Files/National Instruments/VeriStand 2021/NationalInstruments.VeriStand.SystemDefinitionAPI.dll"

assem = parser.parse_dotnet(target_assembly)

target = (assem.defined_types[assem.exported_types[0]])

print(target.full_name)