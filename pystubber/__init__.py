from dataclasses import dataclass
from typing import Optional, List

import clr
clr.AddReference('System')
clr.AddReference('System.Collections')
clr.AddReference('System.Reflection')
clr.AddReference('System.IO')

import System
from System.Collections import Generic
from System.Reflection import Assembly
from System.IO import DirectoryInfo, Directory, Path, File
from System import AppDomain, Enum, Convert, Type


@dataclass
class BuildConfig:
    prefix: str = ""
    postfix: str = ""
    dest_path_is_root: bool = False


class StubBuilder:
    def __init__(self):
        self._search_paths: List = []
        self._target_assembly_path = None

    def build_assembly_stubs(
            self,
            target_assembly_path: str,
            dest_path: Optional[str] = None,
            search_paths: List[str] = None,
            cfgs: Optional[BuildConfig] = None
    ):
        self._target_assembly_path = target_assembly_path
        # prepare configs
        if not cfgs:
            cfgs = BuildConfig()

        # prepace resolver
        AppDomain.CurrentDomain.AssemblyResolve += self._assembly_resolve

        # pick a dll and load
        assembly_to_stub = Assembly.LoadFrom(target_assembly_path)
        self._search_paths.append(target_assembly_path)
        if search_paths:
            self._search_paths += search_paths

        # extract types
        types_to_stub = assembly_to_stub.GetExportedTypes()
        root_namespace = types_to_stub[0].Namespace.split('.')[0]

        #prepare output directory
        if cfgs.dest_path_is_root and Directory.Exists(dest_path):
            stubs_directory = DirectoryInfo(dest_path)
        else:
            extended_root_namespace = cfgs.prefix + root_namespace + cfgs.postfix
            if dest_path is None or not Directory.Exists(dest_path):
                stubs_directory = Directory.CreateDirectory(f'../{extended_root_namespace}')
            else:
                stubs_directory = Directory.CreateDirectory(Path.Combine(dest_path, extended_root_namespace))

        # build type db
        stub_dictionary = {}
        for stub_type in types_to_stub:
            if stub_type.Namespace not in stub_dictionary:
                stub_dictionary[stub_type.Namespace] = []
            stub_dictionary[stub_type.Namespace].append(stub_type)

        namespaces = stub_dictionary.keys()

        # generate stubs for each type
        for stub_list in stub_dictionary.values():
            self._write_stub_list(stubs_directory, namespaces, stub_list)


        # update the setup.py version with the matching version of the assembly
        parent_directory = stubs_directory.Parent
        setup_py = Path.Combine(parent_directory.FullName, "setup.py")
        if File.Exists(setup_py):
            contents = File.ReadAllLines(setup_py)
            for idx in range(len(contents)):
                line = contents[idx].Trim()
                if line.StartsWith("version="):
                    version = assembly_to_stub.GetName().Version
                    contents[idx] = "version=" + version
            File.WriteAllLines(setup_py, contents)
        return stubs_directory.FullName

    def _assembly_resolve(self, sender, args):
        assembly_to_resolve = args.Name.split(',')[0] + ".dll"
        for search_path in self._search_paths:
            assembly_path = Path.Combine(search_path, assembly_to_resolve)
            if File.Exists(assembly_path):
                return Assembly.LoadFrom(assembly_path)

    def _write_stub_list(self, root_directory, all_namespaces, stub_types):
        # TODO Fix this later -- stub_types.sort()
        ns = stub_types[0].Namespace.split('.')
        path = root_directory.FullName
        for idx in range(len(ns)):
            path = Path.Combine(path, ns[idx])

        if not Directory.Exists(path):
            Directory.CreateDirectory(path)

        init_path = Path.Combine(path, "__init__.py")
        path = Path.Combine(path, "__init__.pyi")

        init_text = f"""
import clr
clr.AddReference('{self._target_assembly_path}')

from {stub_types[0].Namespace} import *
                """
        File.WriteAllText(init_path, init_text)

        sb = ""
        all_child_namespaces = self._get_child_namespaces(stub_types[0].Namespace, all_namespaces)
        if all_child_namespaces:
            sb += "__all__ = [\n"
            for idx in range(len(all_child_namespaces)):
                if idx > 0:
                    sb += ','
                sb += f"{all_child_namespaces[idx]}"
            sb += "]\n"

        sb += "from typing import Tuple, Set, Iterable, List, overload\n"

        for stub_type in stub_types:
            #TODO obsolete = stub_type.GetCustomAttribute(type(System.ObsoleteAttribute))
            sb += "\n\n"

            if stub_type.IsGenericType:
                continue

            if stub_type.IsEnum:
                sb += f"class {stub_type.Name}:\n"
                names = Enum.GetNames(stub_type)
                values = Enum.GetValues(stub_type)

                for idx in range(len(names)):
                    name = names[idx]
                    if name == "None":
                        name = "#None"
                    val = Convert.ChangeType(values[idx], Type.GetTypeCode(stub_type))
                    sb += f"\t{name} = {val}\n"
                continue

            if stub_type.BaseType:
                if stub_type.BaseType.FullName.startswith(ns[0]) and not "+" in stub_type.BaseType.FullName and not \
                        "`" in stub_type.BaseType.FullName:
                    sb += f"class {stub_type.Name}({stub_type.BaseType.Name}):\n"
                else:
                    sb += f"class {stub_type.Name}:\n"
            class_start = sb

            constructors = stub_type.GetConstructors()
            #TODO Array.Sort(constructors, MethodCompare);

            for constructor in constructors:
                if len(constructors) > 1:
                    sb += "\t@overload\n"
                sb += "\tdef __init__(self"
                parameters = constructor.GetParameters()
                for idx in range(len(parameters)):
                    if idx == 0:
                        sb += ", "
                    sb += f"{self._safe_python_name(parameters[idx].Name)}: " \
                          f"{self._to_python_type(parameters[idx].ParameterType)}"
                    if idx < len(parameters) - 1:
                        sb += ", "
                sb += "): ...\n"

            methods = stub_type.GetMethods()
            # TODO Array.Sort(methods, MethodCompare);
            method_names = {}
            for method in methods:
                # TODO check if obsolete
                if method.Name in method_names:
                    method_names[method.Name] += 1
                else:
                    method_names[method.Name] = 1

            for method in methods:
                # TODO check if obsolete
                if method.DeclaringType != stub_type:
                    continue
                parameters = method.GetParameters()
                out_param_count = 0
                ref_param_count = 0
                for parameter in parameters:
                    if parameter.IsOut:
                        out_param_count += 1
                    elif (parameter.ParameterType.IsByRef):
                        ref_param_count += 1

                if method.IsSpecialName and method.Name.startswith("get_") or method.Name.startswith("set_"):
                    prop_name = method.Name[4:]
                    if method.Name.startswith("get_"):
                        sb += "\t@property\n"
                    else:
                        sb += f"\t@{prop_name}.setter\n"
                    sb += f"\tdef {prop_name}("
                else:
                    if method.IsStatic:
                        sb += "\t@staticmethod\n"
                    if method_names[method.Name] > 1:
                        sb += "\t@overload\n"
                    sb += f"\tdef {method.Name}("

                add_comma = False
                if not method.IsStatic:
                    sb += "self"
                    add_comma = True
                for idx in range(len(parameters)):
                    if parameters[idx].IsOut:
                        continue

                    if add_comma:
                        sb += ", "
                    sb += f"{self._safe_python_name(parameters[idx].Name)}: " \
                          f"{self._to_python_type(parameters[idx].ParameterType)}"
                    add_comma = True
                sb += ")"

                types = []
                if method.ReturnType is None:
                    if not out_param_count and not ref_param_count:
                        types.append("None")
                else:
                    types.append(self._to_python_type(method.ReturnType))
                for p in parameters:

                    if p.IsOut or p.ParameterType.IsByRef:
                        types.append(self._to_python_type(p.ParameterType))
                sb += " -> "
                if not out_param_count and not ref_param_count:
                    sb += types[0]
                else:
                    sb += "Tuple["
                    for idx in range(len(types)):
                        if idx > 0:
                            sb += ", "
                        sb += types[idx]
                    sb += "]"
                sb += ":...\n"
            if len(sb) == len(class_start):
                sb += "\tpass"
        File.WriteAllText(path, sb)

    def _safe_python_name(self, s: str):
        if s == "from":
            return "from_"
        return s

    def _to_python_type(self, s: str or System.Type):
        if not isinstance(s, str):
            s = s.Name
        if s.endswith("&"):
            s = s[0: -1]
        if s.endswith("`1") or s.endswith("`2"):
            s = s[0: -2]
        if s.endswith("[]"):
            partial = self._to_python_type(s[0:-2])
            return f"List[{partial}]"
        if s.endswith("[,]"):
            partial = self._to_python_type(s[0:-3])
            return f"List[{partial}]"
        if s.endswith("*"):
            return s[0:-1]
        if s == "System.String" or "String":
            return "str"
        if s == "System.Double" or "Double":
            return "float"
        if s == "System.Boolean" or "Boolean":
            return "bool"
        if s == "System.Int32" or "Int32":
            return "int"
        return s

    def _get_child_namespaces(self, parent_namespace, all_namespaces: List[str]):
        child_namespaces = []
        for ns in all_namespaces:
            if ns.startswith(parent_namespace + "."):
                child_namespace = ns[0:len(parent_namespace) + 1]
                if '.' not in child_namespace:
                    child_namespaces.append(child_namespace)
        child_namespaces.sort()
        return child_namespaces


if __name__ == '__main__':
    StubBuilder().build_assembly_stubs("C:/Program Files/National Instruments/VeriStand 2020/NationalInstruments.VeriStand.SystemDefinitionAPI.dll")


