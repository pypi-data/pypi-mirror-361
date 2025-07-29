#  Copyright (c) 2020 - 2025 DiffusionData Ltd., All Rights Reserved.
#
#  Use is subject to licence terms.
#
#  NOTICE: All information contained herein is, and remains the
#  property of DiffusionData. The intellectual and technical
#  concepts contained herein are proprietary to DiffusionData and
#  may be covered by U.S. and Foreign Patents, patents in process, and
#  are protected by trade secret or copyright law.

""" Various utilities that don't fit into any particular module. """
from __future__ import annotations
import enum
import functools
import itertools
import typing
from collections import defaultdict
from functools import reduce, wraps
from inspect import iscoroutinefunction, ismethod
from itertools import chain
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    List,
    Mapping,
    Type,
    Union,
    TypeVar,
    Generic,
    cast
)

import diffusion.internal.pydantic_compat.v1 as pydantic
import typing_extensions
from diffusion.internal.pydantic_compat.v1 import ValidationError

from diffusion.internal.encoded_data import EncodingType

if typing.TYPE_CHECKING:
    from diffusion.internal.pydantic_compat.v1.decorator import AnyCallableT


def coroutine(fn: Callable) -> Callable:
    """Decorator to convert a regular function to a coroutine function.

    Since asyncio.coroutine is set to be removed in 3.10, this allows
    awaiting a regular function. Not useful as a @-based decorator,
    but very helpful for inline conversions of unknown functions, and
    especially lambdas.
    """
    if iscoroutinecallable(fn):
        return fn

    @wraps(fn)
    async def _wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return _wrapper


def iscoroutinecallable(obj: Callable):
    """Return `True` if the object is a coroutine callable.

    Similar to `inspect.iscoroutinefunction`, except that it also accepts
    objects with coroutine `__call__` methods.
    """
    return iscoroutinefunction(obj) or (
        callable(obj)
        and ismethod(obj.__call__)  # type: ignore
        and iscoroutinefunction(obj.__call__)  # type: ignore
    )


T = TypeVar("T", bound=Type[Any])


def get_all_subclasses(cls: T) -> List[T]:
    """Returns a dict containing all the subclasses of the given class.

    Follows the inheritance tree recursively.
    """
    subclasses = list(cls.__subclasses__())
    if subclasses:
        subclasses.extend(chain.from_iterable(get_all_subclasses(c) for c in subclasses))
    return subclasses


def fnmap(functions: Iterable[Callable[[Any], Any]], *values: Any) -> Union[Any, Iterator[Any]]:
    """Applies a series of single-argument functions to each of the values.

    Returns a single value if one value was given, or an iterator if multiple.
    """
    results = map(lambda val: reduce(lambda v, fn: fn(v), functions, val), values)
    return next(results) if len(values) == 1 else results


def get_fnmap(*functions: Callable[[Any], Any]) -> Callable[..., Any]:
    """ Prepares a single-argument function to apply all the functions. """
    return lambda *values: fnmap(functions, *values)


class CollectionEnum(enum.EnumMeta):
    """Metaclass which allows lookup on enum values.

    The default implementation of `EnumMeta.__contains__` looks
    for instances of the Enum class, which is not very useful.
    With this, it is possible to check whether an Enum class
    contains a certain value.

    Usage:
        >>> class MyEnum(enum.Enum, metaclass=CollectionEnum):
        ...     FOO = "foo"
        ...     BAR = "bar"
        ...
        >>> "foo" in MyEnum
        True
        >>> "blah" in MyEnum
        False
        >>> MyEnum.BAR in MyEnum
        True
    """

    def __contains__(cls, item):  # NOQA: N805
        return isinstance(item, cls) or item in [
            v.value for v in cls.__members__.values()
        ]


def flatten_mapping(values: Iterable) -> Iterable:
    """Extract an iterable of values from an iterable of nested mappings.

    Usage:
        >>> values = ({"a": {"b": "c"}, "d": {"e": "f"}}, {"g": "h"})
        >>> tuple(flatten_mapping(values))
        ('c', 'f', 'h')
    """
    for item in values:
        if isinstance(item, Mapping):
            yield from flatten_mapping(item.values())
        else:
            yield item


def nested_dict():
    """Creates a recursive defaultdict of any depth.

    Usage:
        >>> d = nested_dict()
        >>> d["a"] = 1
        >>> d["b"]["c"] = 2
        >>> d == {"a": 1, "b": {"c": 2}}
        True
    """
    return defaultdict(nested_dict)


def assert_arg_type(obj, tp: type):
    if not isinstance(obj, tp):
        raise TypeError(f"Expected a {tp.__module__}:{tp.__qualname__} but got {obj} "
                        f"of type {type(obj)}")


def decode(item, collapse=False, skip_none=False):
    from diffusion.datatypes import DataType
    if isinstance(item, (list, tuple)):
        result = decode_list_or_tuple(item, collapse, skip_none)
        return result
    from diffusion.internal.serialisers.compound import GenericMapSerialiser
    if isinstance(item, (dict, GenericMapSerialiser)):
        return {decode(k): decode(v) for k, v in item.items()}
    if isinstance(item, (DataType, EncodingType)):
        item = item.value
    return item


def decode_list_or_tuple(item, collapse, skip_none):
    none_stripped = [x for x in item if (not skip_none or x is not None)]
    decoded = [decode(x) for x in none_stripped if
               (not collapse or not (hasattr(x, "__len__") and not len(x)))]
    try:
        result = type(item)(decoded)
    except TypeError:
        result = type(item)(*decoded)
    return result


class BaseConfig(object):
    error_msg_templates = {
        "type_error.arbitrary_type": "instance of {expected_arbitrary_type} expected",
        "type_error.none.not_allowed": "None is an invalid value",
        "value_error.any_str.min_length": "String must be at least of length {limit_value}",
        "type_error.bool": "Boolean required",
        "type_error.str": "Value is not a string",
        "value_error.number.not_ge": (
            "Ensure this value is greater than or equal to {limit_value}"
        ),
        "value_error.number.not_gt": "Ensure this value is greater than {limit_value}",
        "type_error.float": "Value is not a valid float",
        "type_error.integer": "Value is not a valid integer",
        "arbitrary_type": 'instance of {expected_arbitrary_type} expected',
        "type_error.frozenset": "value is not a valid frozenset",
        "type_error.bytes": "value is not of type 'bytes'"
    }
    arbitrary_types_allowed = True
    TC_ERROR = ValidationError
    allow_population_by_field_name = True
    copy_on_model_validation = "shallow"
    frozen = False
    underscore_attrs_are_private = True


def gen_overload_validator(validated_main_func, overloads, validator, **fwd_refs):
    validated_funcs = []
    for overload in overloads:
        validated_func = validator(overload)
        validated_func.model.update_forward_refs(**fwd_refs)  # type: ignore
        validated_funcs.append(validated_func)

    def validated(*args, **kwargs):
        def process(remaining_overloads, *args, **kwargs):
            try:
                return remaining_overloads[0](*args, **kwargs)
            except ValidationError as error:
                if len(remaining_overloads) > 1:
                    try:
                        return process(remaining_overloads[1:], *args, **kwargs)
                    except ValidationError as ex_next:
                        raise ex_next from error
                raise error

        return process(validated_funcs, *args, **kwargs)
    return validated


def validate_member_arguments_configured(
    config: "typing.Union[typing.Type[BaseConfig]]" = BaseConfig,
    deferred: typing.Optional[typing.Union[typing.Callable[[], typing.Dict]]] = None,
    check_overloads=False,
    **fwd_refs,
) -> typing.Callable[["AnyCallableT"], "AnyCallableT"]:
    """
    Decorator to validate member function arguments.
    Automatically updates forward refs for class members
    that reference the type of 'self' e.g. Builders...

    Args:
        check_overloads: whether to check overloads
        config: the Pydantic BaseConfig to use
        deferred: callable returning dict of forward references to be passed
            to the validation model the first time the wrapped function is called
        **fwd_refs: any additional forward refs
    Returns:
        The decorated function with argument validation
    """

    def transformer(func: "AnyCallableT") -> "AnyCallableT":
        """
        Wraps the function with parameter validation.

        Args:
            func: the original function

        Returns:
            the wrapped, validated function
        """
        validator = pydantic.validate_arguments(config=config)
        validated_main_func = validator(func)

        try:
            validated_main_func.model.update_forward_refs(**fwd_refs)  # type: ignore
        except NameError:
            pass

        if check_overloads:
            overloads: typing.List[Callable[..., object]] = []
            try:
                # noinspection PyUnresolvedReferences
                overloads.extend(typing_extensions.get_overloads(func))
            except AttributeError:
                pass
            try:
                # noinspection PyUnresolvedReferences
                overloads.extend(
                    typing_extensions.get_overloads(func)
                )
            except AttributeError:
                pass
        else:
            overloads = []

        if overloads:
            result = gen_overload_validator(
                validated_main_func, overloads, validator, **fwd_refs
            )
        else:
            result = validated_main_func

        def first_time(self, *args, **kwargs):
            nonlocal wrapped
            nonlocal deferred
            if deferred:
                deferred_run = deferred()
            else:
                deferred_run = {}
            updated = {type(self).__name__: type(self)}
            updated.update(deferred_run)
            validated_main_func.model.update_forward_refs(
                **updated
            )
            wrapped = result
            return result(self, *args, **kwargs)

        wrapped = first_time

        if config.TC_ERROR == ValidationError:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return wrapped(*args, **kwargs)

        else:

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    return wrapped(*args, **kwargs)
                except ValidationError as ex:
                    raise config.TC_ERROR from ex

        return cast("AnyCallableT", wrapper)

    return transformer


validate_member_arguments = validate_member_arguments_configured()


ModelImpl = TypeVar("ModelImpl")


Self = typing.TypeVar("Self")


class BuilderBase(Generic[ModelImpl]):
    tp: Type[ModelImpl]
    _target: ModelImpl

    # noinspection PyTypeChecker
    @classmethod
    @functools.lru_cache(maxsize=None)
    def __class_getitem__(cls, tp: Type[ModelImpl]) -> "BuilderBase[ModelImpl]":
        dct = {"tp": tp, **cls.__dict__}
        return cast(
            "BuilderBase[ModelImpl]",
            type(f"{tp.__name__}BuilderBase", cls.__bases__, dct),
        )

    def __init__(self, *args, **kwargs):
        """
        Generic builder.

        Builds an object of type `ModelImpl`.

        Args:
            *args: positional arguments to pass into `ModelImpl`
                constructor on initialisation/reset
            **kwargs: keyword arguments to pass into `ModeLimpl`
                constructor on initialisation/reset
        """
        self._args = args
        self._kwargs = kwargs
        self.reset()

    V = TypeVar("V", bound="BuilderBase")

    def reset(self: V) -> V:
        """
        Reset the builder.

        Returns:
            this builder
        """
        self._target = self.tp(*self._args, **self._kwargs)
        return self

    def _create(self: V, **kwargs) -> ModelImpl:
        """
        Create a new `ModelImpl` using the values
        currently know to this builder.

        Args:
            **kwargs: overriden arguments

        Returns:
            a new `ModelImpl` with all of the current settings of
            the builder, overriden as specified
        """
        dct = self._target.dict()
        dct.update(**kwargs)
        return self.tp(**dct)


_KT = typing.TypeVar("_KT")
_VT_co = typing.TypeVar("_VT_co", covariant=True)
_T_co = typing.TypeVar("_T_co", covariant=True)


def get_base_type_parameters(tl_annotation) -> typing.Set[typing.Type]:
    hints = typing_extensions.get_origin(tl_annotation)
    if hints == typing.Union:
        elements = typing_extensions.get_args(tl_annotation)
        return set(itertools.chain.from_iterable(get_base_type_parameters(x) for x in elements))
    else:
        return {tl_annotation}
