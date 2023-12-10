from typing import re

import clr
import logging

logger = logging.getLogger(__name__)
from System.Reflection import TypeInfo

class PyType:
    def __init__(self):
        self.imports = set()

    def _from_class(self, value) -> str:
        logger.info(f"PYTYPE CLASS: {value} {value.Attributes}")
        namespace_path = str(value).split('.')
        self.imports.add("typing.override")
        self.imports.add('.'.join(namespace_path))
        return namespace_path[-1]

    def _from_known_type(self, value) -> str:
        return {
            "System.Boolean": "bool",
            "System.Byte": "int",
            "System.SByte": "int",
            "System.Int16": "int",
            "System.UInt16": "int",
            "System.Int32": "int",
            "System.UInt32": "int",
            "System.Int64": "int",
            "System.UInt64": "int",
            "System.IntPtr": "int",
            "System.UIntPtr": "int",
            "System.Char": "int",
            "System.Double": "float",
            "System.Single": "float",
            "System.Void": "None",
            "System.String": "str",
        }.get(str(value), None)

    def _from_array(self, value) -> str:
        logger.info(f"PYTYPE ARRAY: {value} {value.Attributes}")
        self.imports.add("typing.List")
        return f"List[{self.from_type(value.GetElementType())}]"

    def _from_interface(self, value) -> str:
        logger.info(f"PYTYPE INTERFACE: {value} {value.Attributes}")
        return self._from_class(value)

    def _from_enum(self, value) -> str:
        self.imports.add("enum.Enum")
        logger.info(f"PYTYPE ENUM: {value} {value.Attributes}")
        return self._from_class(value)
    #
    # def _from_delegate(self, value) -> str:
    #     logger.info(f"PYTYPE DELEGATE: {value} {value.Attributes}")

    def _from_generic(self, value) -> str:
        logger.info(f"PYTYPE GENERIC: {value} {value.Attributes}")
        py_type = None
        generic_types = {
            "System.Collections.Generic.IEnumerable": ("typing.Iterable", "Iterable"),
            "System.Collections.Generic.List": ("typing.List", "List"),
            "System.Predicate": ("typing.Callable", "Callable"),
            "System.Collections.Generic.Dictionary": ("typing.Dict", "Dict"),
            "System.Collections.Generic.KeyValuePair": ("typing.Tuple", "Tuple"),
            "System.Collections.Generic.IEqualityComparer": ("typing.Callable", "Callable"),
        }

        for dotnet_type, python_type in generic_types.items():
            if str(value).startswith(dotnet_type):
                self.imports.add(python_type[0])
                py_type = python_type[1]

        if not py_type:
            logger.warning(f"UNKNOWN TYPE_INFO: {value}{value.Attributes}")
            return str(value)
        params = []
        for arg in value.GetGenericArguments():
            params.append(self.from_type(arg))

        return f"{py_type}[{','.join(params)}]"

    def _from_value_type(self, value) -> str:
        logger.info(f"PYTYPE VALUETYPE: {value} {value.Attributes}")
        namespace_path = str(value).split('.')
        self.imports.add('.'.join(namespace_path))
        return (namespace_path[-1])

    def parse_parameter_type(self, value):
        if value.ParameterType is not None:
            if value.ParameterType.IsByRef:
                return self.from_type(value.ParameterType.GetElementType())
            else:
                self.from_type(value.ParameterType)
    def from_parameter(self, value) -> str:
        logger.info(f"PYTYPE PARAMETER: {value} {value.Attributes}")
        return_value = f"{str(value.Name)}"
        parameter_type = self.parse_parameter_type(value)
        if value.ParameterType is not None:
            if value.ParameterType.IsByRef:
                return_value += f":{self.from_type(value.ParameterType.GetElementType())}"
            else:
                return_value += f":{self.from_type(value.ParameterType)}"
        if value.HasDefaultValue:
            return_value += f" = {value.RawDefaultValue}"
        return return_value

    def from_parameters(self, parameters) -> str:
        params = []
        for p in parameters:
            params.append(self.from_parameter(p))
        return ', ' + ', '.join(params)

    def from_type(self, value: TypeInfo) -> str:
        lookup = self._from_known_type(value)
        if lookup:
            return lookup
        if value.IsNested:
            return "None"
        if value.IsArray:
            return self._from_array(value)

        if value.IsGenericType:
            return self._from_generic(value)

        if value.IsEnum:
            return self._from_enum(value)

        if value.IsInterface:
            self.imports.add("abc.ABC")
            self.imports.add("abc.abstractmethod")
            return self._from_interface(value)

        if value.IsValueType:
            return self._from_value_type(value)

        if value.IsClass:
            return self._from_class(value)



        # if value.IsDelegate:
        #     return self._from_delegate(value)

        else:
            logger.warning(f"UNKNOWN TYPE_INFO: {value}{value.Attributes}")

def format_name(name):
    if name == "None":
        return "NONE"
    return name
