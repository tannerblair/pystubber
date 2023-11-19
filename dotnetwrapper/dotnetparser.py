from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple


@dataclass
class Assembly:
    custom_attributes: Dict[str, CustomAttributeData]
    defined_types: Dict[str, TypeInfo]
    exported_types: List[str]
    name: str
    full_name: str
    is_dynamic: bool
    location: str
    manifest_module: ModuleInfo
    modules: Dict[Tuple[str, str], ModuleInfo]
    referenced_assemblies: List[str]
    manifest_resource_names: List[str]

    @staticmethod
    def from_dotnet(ref):
        custom_attributes = {}
        for attr in ref.CustomAttributes:
            custom_attributes[str(attr)] = CustomAttributeData.from_dotnet(attr)

        defined_types = {}
        for dotnet_type in ref.DefinedTypes:
            defined_types[str(dotnet_type)] = TypeInfo.from_dotnet(dotnet_type)

        modules = {}

        for m in ref.Modules:
            modules[(m.Name, m.ModuleVersionId)] = ModuleInfo.from_dotnet(m)
        return Assembly(
            custom_attributes=custom_attributes,
            defined_types=defined_types,
            exported_types=[str(o) for o in ref.ExportedTypes],
            name=str(ref.GetName()),
            full_name=str(ref.FullName),
            is_dynamic=bool(ref.IsDynamic),
            location=str(ref.Location),
            manifest_module=ModuleInfo.from_dotnet(ref.ManifestModule),
            modules=modules,
            referenced_assemblies=[str(o) for o in ref.GetReferencedAssemblies()],
            manifest_resource_names=[str(s) for s in ref.GetManifestResourceNames()],
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class ConstructorInfo:
    name: str
    attributes: List[str]
    calling_convention: List[str]
    contains_generic_parameters: bool
    custom_attributes: List[CustomAttributeData]
    declaring_type: str
    is_abstract: bool
    is_assembly: bool
    is_family: bool
    is_constructor: bool
    is_family_and_assembly: bool
    is_family_or_assembly: bool
    is_final: bool
    is_generic_method: bool
    is_generic_method_definition: bool
    is_hide_by_sig: bool
    is_private: bool
    is_public: bool
    is_static: bool
    is_virtual: bool
    member_type: str
    module: str
    method_implementation_flags: List[str]
    is_special_name: bool
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        return ConstructorInfo(
            name=ref.Name,
            attributes=str(ref.Attributes).split(","),
            calling_convention=str(ref.CallingConvention).split(","),
            contains_generic_parameters=bool(ref.ContainsGenericParameters),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declaring_type=str(ref.DeclaringType),
            is_abstract=bool(ref.IsAbstract),
            is_assembly=bool(ref.IsAssembly),
            is_constructor=bool(ref.IsConstructor),
            is_family=bool(ref.IsFamily),
            is_family_and_assembly=bool(ref.IsFamilyAndAssembly),
            is_family_or_assembly=bool(ref.IsFamilyOrAssembly),
            is_final=bool(ref.IsFinal),
            is_generic_method=bool(ref.IsGenericMethod),
            is_generic_method_definition=bool(ref.IsGenericMethodDefinition),
            is_hide_by_sig=bool(ref.IsHideBySig),
            is_private=bool(ref.IsPrivate),
            is_public=bool(ref.IsPublic),
            is_static=bool(ref.IsStatic),
            is_virtual=bool(ref.IsVirtual),
            member_type=str(ref.MemberType),
            module=str(ref.Module),
            method_implementation_flags=str(ref.MethodImplementationFlags).split(","),
            is_special_name=bool(ref.IsSpecialName),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class CustomAttributeData:
    attribute_type: str
    constructor: ConstructorInfo
    constructor_arguments: List[CustomAttributeTypedArgument]
    named_arguments: Dict[str, CustomAttributeNamedArgument]

    @staticmethod
    def from_dotnet(ref):
        named_arguments = {}
        for a in ref.NamedArguments:
            named_arguments[a.MemberName] = CustomAttributeNamedArgument.from_dotnet(a)

        return CustomAttributeData(
            attribute_type=ref.AttributeType.Name,
            constructor=ConstructorInfo.from_dotnet(ref.Constructor),
            constructor_arguments=[
                CustomAttributeTypedArgument.from_dotnet(o)
                for o in ref.ConstructorArguments
            ],
            named_arguments=named_arguments,
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class CustomAttributeNamedArgument:
    is_field: bool
    member_info: MemberInfo
    member_name: str
    typed_value: CustomAttributeTypedArgument

    @staticmethod
    def from_dotnet(ref):
        return CustomAttributeNamedArgument(
            is_field=bool(ref.IsField),
            member_info=MemberInfo.from_dotnet(ref.MemberInfo),
            member_name=str(ref.MemberName),
            typed_value=CustomAttributeTypedArgument.from_dotnet(ref.TypedValue),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class CustomAttributeTypedArgument:
    argument_type: str
    value: str

    @staticmethod
    def from_dotnet(ref):
        return CustomAttributeTypedArgument(
            argument_type=str(ref.ArgumentType), value=str(ref.Value)
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class EventInfo:
    name: str
    attributes: List[str]
    custom_attributes: List[CustomAttributeData]
    add_method: MethodInfo
    remove_method: MethodInfo
    raise_method: MethodInfo
    declaring_type: str
    event_handler_type: str
    is_multicast: bool
    is_special_name: bool
    member_type: List[str]
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        add_method = None
        if ref.AddMethod:
            add_method = MethodInfo.from_dotnet(ref.AddMethod)

        remove_method = None
        if ref.RemoveMethod:
            remove_method = MethodInfo.from_dotnet(ref.RemoveMethod)

        raise_method = None
        if ref.RaiseMethod:
            raise_method = MethodInfo.from_dotnet(ref.RaiseMethod)

        return EventInfo(
            name=ref.Name,
            attributes=str(ref.Attributes).split(","),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            add_method=add_method,
            remove_method=remove_method,
            raise_method=raise_method,
            declaring_type=str(ref.DeclaringType),
            event_handler_type=str(ref.EventHandlerType),
            is_multicast=bool(ref.IsMulticast),
            is_special_name=bool(ref.IsSpecialName),
            member_type=str(ref.Attributes).split(","),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class FieldInfo:
    name: str
    attributes: List[str]
    custom_attributes: List[CustomAttributeData]
    declaring_type: str
    field_type: str
    is_assembly: bool
    is_family: bool
    is_family_and_assembly: bool
    is_family_or_assembly: bool
    is_init_only: bool
    is_literal: bool
    is_pinvoke_impl: bool
    is_private: bool
    is_public: bool
    is_static: bool
    member_type: str
    module: str
    is_special_name: bool
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        return FieldInfo(
            name=ref.Name,
            attributes=str(ref.Attributes).split(","),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declaring_type=str(ref.DeclaringType),
            field_type=str(ref.FieldType),
            is_assembly=bool(ref.IsAssembly),
            is_family=bool(ref.IsFamily),
            is_family_and_assembly=bool(ref.IsFamilyAndAssembly),
            is_family_or_assembly=bool(ref.IsFamilyOrAssembly),
            is_init_only=bool(ref.IsInitOnly),
            is_literal=bool(ref.IsLiteral),
            is_pinvoke_impl=bool(ref.IsPinvokeImpl),
            is_private=bool(ref.IsPrivate),
            is_public=bool(ref.IsPublic),
            is_static=bool(ref.IsStatic),
            member_type=str(ref.MemberType),
            module=str(ref.Module),
            is_special_name=bool(ref.IsSpecialName),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class MemberInfo:
    name: str
    custom_attributes: List[CustomAttributeData]
    declaring_type: str
    member_type: str
    module: str
    is_special_name: bool
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        return MemberInfo(
            name=ref.Name,
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declaring_type=str(ref.DeclaringType),
            member_type=str(ref.MemberType),
            module=str(ref.Module),
            is_special_name=bool(ref.IsSpecialName),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class MethodInfo:
    name: str
    attributes: List[str]
    calling_convention: List[str]
    contains_generic_parameters: bool
    custom_attributes: List[CustomAttributeData]
    declaring_type: str
    is_abstract: bool
    is_assembly: bool
    is_family: bool
    is_constructor: bool
    is_family_and_assembly: bool
    is_family_or_assembly: bool
    is_final: bool
    is_generic_method: bool
    is_generic_method_definition: bool
    is_hide_by_sig: bool
    is_private: bool
    is_public: bool
    is_static: bool
    is_virtual: bool
    member_type: str
    module: str
    method_implementation_flags: List[str]
    return_parameter: ParameterInfo
    return_type: str
    return_type_custom_attributes: List[CustomAttributeData]
    is_special_name: bool
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        return MethodInfo(
            name=ref.Name,
            attributes=str(ref.Attributes).split(","),
            calling_convention=str(ref.CallingConvention).split(","),
            contains_generic_parameters=bool(ref.ContainsGenericParameters),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declaring_type=str(ref.DeclaringType),
            is_abstract=bool(ref.IsAbstract),
            is_assembly=bool(ref.IsAssembly),
            is_constructor=bool(ref.IsConstructor),
            is_family=bool(ref.IsFamily),
            is_family_and_assembly=bool(ref.IsFamilyAndAssembly),
            is_family_or_assembly=bool(ref.IsFamilyOrAssembly),
            is_final=bool(ref.IsFinal),
            is_generic_method=bool(ref.IsGenericMethod),
            is_generic_method_definition=bool(ref.IsGenericMethodDefinition),
            is_hide_by_sig=bool(ref.IsHideBySig),
            is_private=bool(ref.IsPrivate),
            is_public=bool(ref.IsPublic),
            is_static=bool(ref.IsStatic),
            is_virtual=bool(ref.IsVirtual),
            member_type=str(ref.MemberType),
            module=str(ref.Module),
            method_implementation_flags=str(ref.MethodImplementationFlags).split(","),
            return_parameter=ParameterInfo.from_dotnet(ref.ReturnParameter),
            return_type=str(ref.ReturnType),
            return_type_custom_attributes=[
                CustomAttributeData.from_dotnet(o)
                for o in ref.ReturnTypeCustomAttributes.GetCustomAttributes(True)
            ],
            is_special_name=bool(ref.IsSpecialName),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class ModuleInfo:
    assembly: str
    custom_attributes: List[CustomAttributeData]
    version_id: str
    name: str
    scope_name: str

    @staticmethod
    def from_dotnet(ref):
        return ModuleInfo(
            assembly=str(ref.Assembly),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            version_id=str(ref.ModuleVersionId),
            name=str(ref.Name),
            scope_name=str(ref.ScopeName),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class ParameterInfo:
    attributes: List[str]
    custom_attributes: List[CustomAttributeData]
    default_value: str
    has_default_value: bool
    is_input: bool
    is_locale_identifier: bool
    is_optional: bool
    is_output: bool
    is_return_value: bool
    member: str
    name: str
    parameter_type: str
    position: int
    raw_default_value: str

    @staticmethod
    def from_dotnet(ref):
        return ParameterInfo(
            name=ref.Name,
            attributes=str(ref.Attributes).split(","),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            default_value=str(ref.DefaultValue),
            has_default_value=bool(ref.HasDefaultValue),
            is_input=bool(ref.IsIn),
            is_locale_identifier=bool(ref.IsLcid),
            is_optional=bool(ref.IsOptional),
            is_output=bool(ref.IsOut),
            is_return_value=bool(ref.IsRetval),
            member=str(ref.Member),
            parameter_type=str(ref.ParameterType),
            position=int(ref.Position),
            raw_default_value=str(ref.RawDefaultValue),
        )


@dataclass
class PropertyInfo:
    name: str
    can_read: bool
    can_write: bool
    custom_attributes: List[CustomAttributeData]
    declaring_type: str
    get_method: MethodInfo
    set_method: MethodInfo
    member_type: str
    property_type: str
    module: str
    is_special_name: bool
    reflected_type: str

    @staticmethod
    def from_dotnet(ref):
        get_method = None
        if ref.GetMethod:
            get_method = MethodInfo.from_dotnet(ref.GetMethod)

        set_method = None
        if ref.SetMethod:
            set_method = MethodInfo.from_dotnet(ref.SetMethod)

        return PropertyInfo(
            name=ref.Name,
            can_read=bool(ref.CanRead),
            can_write=bool(ref.CanWrite),
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declaring_type=str(ref.DeclaringType),
            get_method=get_method,
            set_method=set_method,
            member_type=str(ref.MemberType),
            property_type=str(ref.PropertyType),
            module=str(ref.Module),
            is_special_name=bool(ref.IsSpecialName),
            reflected_type=str(ref.ReflectedType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})


@dataclass
class TypeInfo:
    assembly_qualified_name: str
    attributes: List[str]
    base_type: str
    contains_generic_parameters: bool
    custom_attributes: List[CustomAttributeData]
    declared_constructors: List[ConstructorInfo]
    declared_events: Dict[str, EventInfo]
    declared_fields: Dict[str, FieldInfo]
    declared_members: Dict[str, MemberInfo]
    declared_methods: Dict[str, MethodInfo]
    declared_nested_types: List[str]
    declared_properties: Dict[str, PropertyInfo]
    full_name: str
    generic_parameter_attributes: Optional[List[str]]
    generic_parameter_position: Optional[int]
    generic_type_arguments: List[str]
    generic_type_parameters: List[str]
    guid: str
    has_element_type: bool
    implemented_interfaces: List[str]
    is_abstract: bool
    is_ansi_class: bool
    is_array: bool
    is_autoclass: bool
    is_autolayout: bool
    is_by_ref: bool
    is_class: bool
    is_com_object: bool
    is_constructed_generic_type: bool
    is_contextful: bool
    is_enum: bool
    is_explicit_layout: bool
    is_generic_parameter: bool
    is_generic_type: bool
    is_generic_type_definition: bool
    is_import: bool
    is_interface: bool
    is_layout_sequential: bool
    is_marshall_by_ref: bool
    is_nested: bool
    is_nested_assembly: bool
    is_nested_fam_and_assem: bool
    is_nested_family: bool
    is_nested_fam_or_assem: bool
    is_nested_private: bool
    is_nested_public: bool
    is_not_public: bool
    is_pointer: bool
    is_primitive: bool
    is_public: bool
    is_sealed: bool
    is_special_name: bool
    is_unicode_class: bool
    is_value_type: bool
    is_visible: bool
    member_type: List[str]
    metadata_token: int
    module: str
    name: str
    namespace: str
    reflected_type: str
    type_initializer: ConstructorInfo
    underlying_system_type: str

    @staticmethod
    def from_dotnet(ref):
        generic_parameter_attributes = None
        generic_parameter_position = None

        if ref.IsGenericParameter:
            generic_parameter_attributes = str(ref.GenericParameterAttributes).split(
                ","
            )
            generic_parameter_position = int(ref.GenericParameterPosition)

        type_initializer = None
        if ref.TypeInitializer:
            type_initializer = ConstructorInfo.from_dotnet(ref.TypeInitializer)

        declared_events = {}
        for event in ref.DeclaredEvents:
            declared_events[event.Name] = EventInfo.from_dotnet(event)

        declared_fields = {}
        for field in ref.DeclaredFields:
            declared_fields[field.Name] = FieldInfo.from_dotnet(field)

        declared_members = {}
        for member in ref.DeclaredMembers:
            declared_members[member.Name] = MemberInfo.from_dotnet(member)

        declared_methods = {}
        for method in ref.DeclaredMethods:
            declared_methods[method.Name] = MethodInfo.from_dotnet(method)

        declared_properties = {}
        for property in ref.DeclaredProperties:
            declared_properties[property.Name] = PropertyInfo.from_dotnet(property)

        return TypeInfo(
            assembly_qualified_name=str(ref.AssemblyQualifiedName),
            attributes=str(ref.Attributes).split(","),
            base_type=str(ref.BaseType),
            contains_generic_parameters=ref.ContainsGenericParameters,
            custom_attributes=[
                CustomAttributeData.from_dotnet(o) for o in ref.CustomAttributes
            ],
            declared_constructors=[
                ConstructorInfo.from_dotnet(o) for o in ref.DeclaredConstructors
            ],
            declared_events=declared_events,
            declared_fields=declared_fields,
            declared_members=declared_members,
            declared_methods=declared_methods,
            declared_nested_types=[str(o) for o in ref.DeclaredNestedTypes],
            declared_properties=declared_properties,
            full_name=ref.FullName,
            generic_parameter_attributes=generic_parameter_attributes,
            generic_parameter_position=generic_parameter_position,
            generic_type_arguments=[str(o) for o in ref.GenericTypeArguments],
            generic_type_parameters=[str(o) for o in ref.GenericTypeParameters],
            guid=str(ref.GUID),
            has_element_type=bool(ref.HasElementType),
            implemented_interfaces=[str(o) for o in ref.ImplementedInterfaces],
            is_abstract=ref.IsAbstract,
            is_ansi_class=ref.IsAnsiClass,
            is_array=ref.IsArray,
            is_autoclass=ref.IsAutoClass,
            is_autolayout=ref.IsAutoLayout,
            is_by_ref=ref.IsByRef,
            is_class=ref.IsClass,
            is_com_object=ref.IsCOMObject,
            is_constructed_generic_type=ref.IsConstructedGenericType,
            is_contextful=ref.IsContextful,
            is_enum=ref.IsEnum,
            is_explicit_layout=ref.IsExplicitLayout,
            is_generic_parameter=ref.IsGenericParameter,
            is_generic_type=ref.IsGenericType,
            is_generic_type_definition=ref.IsGenericTypeDefinition,
            is_import=ref.IsImport,
            is_interface=ref.IsInterface,
            is_layout_sequential=ref.IsLayoutSequential,
            is_marshall_by_ref=ref.IsMarshalByRef,
            is_nested=ref.IsNested,
            is_nested_assembly=ref.IsNestedAssembly,
            is_nested_fam_and_assem=ref.IsNestedFamANDAssem,
            is_nested_family=ref.IsNestedFamily,
            is_nested_fam_or_assem=ref.IsNestedFamORAssem,
            is_nested_private=ref.IsNestedPrivate,
            is_nested_public=ref.IsNestedPublic,
            is_not_public=ref.IsNotPublic,
            is_pointer=ref.IsPointer,
            is_primitive=ref.IsPrimitive,
            is_public=ref.IsPublic,
            is_sealed=ref.IsSealed,
            is_special_name=ref.IsSpecialName,
            is_unicode_class=ref.IsUnicodeClass,
            is_value_type=ref.IsValueType,
            is_visible=ref.IsVisible,
            member_type=str(ref.MemberType).split(","),
            metadata_token=ref.MetadataToken,
            module=str(ref.Module),
            name=ref.Name,
            namespace=ref.Namespace,
            reflected_type=str(ref.ReflectedType),
            type_initializer=type_initializer,
            underlying_system_type=str(ref.UnderlyingSystemType),
        )

    def __str__(self):
        return str({k: str(v) for k, v in asdict(self).items()})
