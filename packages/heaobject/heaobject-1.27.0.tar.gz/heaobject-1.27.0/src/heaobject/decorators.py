from .util import type_name_to_type, type_to_type_name
from .attribute import HEAAttribute
from dataclasses import dataclass, field
from typing import Callable, TypeVar, ParamSpec

@dataclass(frozen=True)
class AttributeMetadata:
    """
    Class to hold metadata for attributes, such as read-only status.
    """
    read_only: bool = field(default=False, metadata={'description': 'If True, the attribute is read-only.'})
    requires_sharer: bool = field(default=False, metadata={'description': 'If True, the attribute requires SHARER permissions to edit.'})


_attr_metadata: dict[object, AttributeMetadata] = {}

P = ParamSpec('P')
RT = TypeVar('RT')

def attribute_metadata(read_only = False, requires_sharer = False) -> Callable[[Callable[P, RT]], Callable[P, RT]]:
    """
    Decorator to mark an HEAObject attribute as read-only or writable. It supports properties, and it also supports
    descriptors that subclass heaobject.attribute.HEAAttribute. It is unnecessary to use this decorator to mark an
    attribute as read-only if the attribute is already defined as read-only (property with a None fset or HEAAttribute
    with no __set__ method). However, decorating such an attribute with read_only set to False will raise an error.

    :param read_only: If True, the attribute is read-only. Defaults to False.
    :param requires_sharer: If True, the attribute requires SHARER permissions to edit. Defaults to False.
    """
    def decorator(func: Callable[P, RT]) -> Callable[P, RT]:
        if isinstance(func, property):
            fget = func.fget
            assert fget is not None, "Property must have a getter"
            if read_only and not _is_property_readonly(func):
                raise ValueError(f"Cannot set read_only=True on a property with a setter: {fget.__name__}")
            # If the function is a property getter, we set the metadata on the getter
            type_name = type_to_type_name(fget).rsplit('.', 1)[0]
            _attr_metadata[(type_name, fget.__qualname__)] = AttributeMetadata(read_only=read_only,
                                                                               requires_sharer=requires_sharer)
        elif isinstance(func, HEAAttribute):
            # If the function is an HEAAttribute, we set the metadata on the attribute
            if read_only and not _is_hea_attribute_readonly(func):
                raise ValueError(f"Cannot set read_only=True on a read-only HEAAttribute: {func._public_name}")
            cls = func._owner
            _attr_metadata[(type_to_type_name(cls), f'{cls.__qualname__}.{func._public_name}')] = AttributeMetadata(read_only=read_only,
                                                                                                                    requires_sharer=requires_sharer)
        return func
    return decorator


def get_attribute_metadata(attr) -> AttributeMetadata:
    """
    Retrieve metadata for a given attribute.

    :param attr: The attribute.

    :return : Metadata object.
    """
    if fget := getattr(attr, 'fget', None):
        # If the function is a property getter, we set the metadata on the getter
        type_ = type_name_to_type(f'{fget.__module__}.{fget.__qualname__}'.rsplit('.', 1)[0])
        for cls in type_.__mro__:
            if result := _attr_metadata.get((type_to_type_name(cls), f'{cls.__qualname__}.{fget.__name__}')):
                return result
        else:
            return _new_attribute_metadata(type_, fget.__name__, attr.fset is None)
    elif isinstance(attr, HEAAttribute):
        for cls in attr._owner.__mro__:
            if result := _attr_metadata.get((type_to_type_name(cls), f'{cls.__qualname__}.{attr._public_name}')):
                return result
        else:
            return _new_attribute_metadata(attr._owner, attr._public_name, not hasattr(attr, '__set__'))
    raise ValueError(f"Attribute {attr} does not have metadata")


def _new_attribute_metadata(cls: type, attr: str, read_only: bool) -> AttributeMetadata:
    """
    Create a new AttributeMetadata instance for the given class.

    :param cls: The class for which to create metadata.
    :return: A new AttributeMetadata instance.
    """
    result = AttributeMetadata(read_only=read_only)
    _attr_metadata[(type_to_type_name(cls), f'{cls.__qualname__}.{attr}')] = result
    return result


def _is_property_readonly(prop: property) -> bool:
    """
    Return whether a property is read-only.

    :param prop: The property to check.

    :return: True if the property is read-only, False otherwise.
    """
    return prop.fset is None

def _is_hea_attribute_readonly(attr: HEAAttribute) -> bool:
    """
    Return whether an HEAAttribute is read-only.

    :param attr: The HEAAttribute to check.

    :return: True if the HEAAttribute is read-only, False otherwise.
    """
    return not hasattr(attr, '__set__')
