import pathlib

from System.Reflection import Assembly
from System.IO import FileNotFoundException
from jinja2 import Environment, PackageLoader, select_autoescape
import logging

logger = logging.getLogger(__name__)

from dotnetwrapper.pytype import PyType, format_name


class PyWriter:
    pytype = PyType()

    def get_utils(self):
        return {
            "enumerate": enumerate,
            "pytype": self.pytype.from_type,
            "pyparam": self.pytype.from_parameter,
            "pyparams": self.pytype.from_parameters,
            "pyname": format_name,
            "pywrite": self.write_typeinfo,
            "type": type,
        }

    env = Environment(
        loader=PackageLoader("dotnetwrapper"),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )

    def write_typeinfo(self, type_def):
        if type_def is None:
            logger.warning(f"WRITE TYPE IS NONE")
            return "None"
        if str(type_def.MemberType) == "Property":
            return self.write_property(type_def)
        if str(type_def.MemberType) == "TypeInfo":
            return self.write_type(type_def)
        if str(type_def.MemberType) == "NestedType":
            return self.write_nested_type(type_def)

        if str(type_def.MemberType) == "Method":
            return self.write_method(type_def)
        if str(type_def.MemberType) == "Constructor":
            return self.write_constructor(type_def)
        logger.warning(f"WRITE TYPE UNKNOWN: {type_def} {type_def.Attributes}")

    def write_enum(self, enum_info):
        logger.info(f"WRITE ENUM: {enum_info} {enum_info.Attributes}")
        return self.env.get_template("enum.j2").render(enum=enum_info, **self.get_utils())

    def write_class(self, class_info):
        logger.info(f"WRITE CLASS: {class_info} {class_info.Attributes}")
        return self.env.get_template("class.j2").render(class_info=class_info, **self.get_utils())

    def write_interface(self, interface):
        logger.info(f"WRITE INTERFACE: {interface}{interface.Attributes}")
        return self.env.get_template("interface.j2").render(interface=interface, **self.get_utils())

    def write_value_type(self, value):
        logger.info(f"WRITE VALUE TYPE: {value} {value.Attributes}")
        return self.env.get_template("class.j2").render(class_info=value, **self.get_utils())

    def write_array(self, array):
        logger.info(f"WRITE ARRAY: {array} {array.Attributes}")
        return self.env.get_template("array.j2").render(array=array, **self.get_utils())

    def write_delegate(self, delegate):
        logger.info(f"WRITE DELEGATE: {delegate} {delegate.Attributes}")
        return self.env.get_template("delegate.j2").render(delegate=delegate, **self.get_utils())

    def write_generic(self, generic):
        logger.info(f"WRITE GENERIC: {generic} {generic.Attributes}")
        return self.env.get_template("generic.j2").render(generic=generic, **self.get_utils())

    def write_type(self, type_info):
        if type_info.Name == "SLSC":
            logger.warning(f"NESTED TYPE_INFO: {type_info}{type_info.Attributes}")
        if type_info.IsArray:
            return self.write_array(type_info)

        if type_info.IsEnum:
            return self.write_enum(type_info)

        if type_info.IsValueType:
            return self.write_value_type(type_info)

        if type_info.IsClass:
            return self.write_class(type_info)

        if type_info.IsInterface:
            return self.write_interface(type_info)

        if type_info.IsDelegate:
            return self.write_delegate(type_info)

        if type_info.IsGeneric:
            return self.write_generic(type_info)

        logger.warning(f"UNKNOWN TYPE_INFO: {type_info}{type_info.Attributes}")

    def write_property(self, prop):
        logger.info(f"WRITE PROPERTY: {prop} {prop.Attributes}")
        return self.env.get_template("property.j2").render(property=prop, **self.get_utils())

    def write_method(self, method):
        logger.info(f"WRITE METHOD: {method} {method.Attributes}")
        if not method.IsPublic:
            return ""

        attr = method.GetCustomAttributes(False)
        for a in attr:
            if str(a) == "System.ObsoleteAttribute":
                logger.info(f"SKIPPING OBSOLETE METHOD: {method} {method.Attributes}")
                return ""
        method_name = method.Name
        if method.DeclaringType.Name != method.Name:
            logger.info(f"SKIPPING OVERRIDE METHOD: {method} {method.Attributes}")

        if method.IsSpecialName:
            if method_name.startswith("get_") or method_name.startswith("set_"):
                method_name = method_name[4:]
                logger.info(f"WRITE GETTER: {method} {method.Attributes}")
        return_types = [self.pytype.from_type(method.ReturnType)]
        for p in method.GetParameters():
            if p.IsOut or p.ParameterType.IsByRef:
                return_types.append(self.pytype.parse_parameter_type(p))

        if len(return_types) == 1:
            return_type = return_types[0]
        else:
            return_type = f"Tuple[{', '.join(return_types)}]"
        return self.env.get_template("method.j2").render(method=method, method_name=method_name,
                                                         params=self.pytype.from_parameters(method.GetParameters()),
                                                         returns=return_type, **self.get_utils())

    def write_nested_type(self, nested):
        logger.info(f"WRITE NESTED: {nested} {nested.Attributes}")
        return self.env.get_template("nested.j2").render(nested=nested, **self.get_utils())

    def write_assembly(self, assembly: Assembly):
        lib_name = pathlib.Path(assembly.Location).stem

        exported_types = []
        try:
            [exported_types.append(exported_type) for exported_type in assembly.GetExportedTypes()]
        except FileNotFoundException:
            logger.warning(f"Load Error:  {assembly}")
        body = ""
        for exported_type in exported_types:
            body += self.write_typeinfo(exported_type)

        # import_list = [i for i in self.pytype.imports if not i.startswith(lib_name)]
        # import_list = sorted(import_list)
        # imports = []
        # for i in import_list:
        #     imports.append(f"from {'.'.join(i.split('.')[:-1])} import {i.split('.')[-1]}")
        # body = "\n\r".join(imports) + "\n\r" * 3 + body
        return body

    def write_constructor(self, constructor):
        logger.info(f"WRITE CSTOR: {constructor} {constructor.Attributes}")
        return self.env.get_template("constructor.j2").render(constructor=constructor, **self.get_utils())
