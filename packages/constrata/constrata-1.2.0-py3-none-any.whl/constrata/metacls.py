from __future__ import annotations

__all__ = ["BinaryStructMeta"]

import abc
import typing as tp
from dataclasses import dataclass

from .fields import *


@tp.dataclass_transform(
    kw_only_default=True,  # IDEs struggle with false positives for field defaults without this
    field_specifiers=(
        binary,
        binary_string,
        binary_array,
        binary_pad,
    ),
)
class BinaryStructMeta(abc.ABCMeta):
    """Base metaclass for `BinaryStruct` that automatically applies `dataclass(slots=True, kw_only=True)` decorator.

    This saves users from having to apply that decorator every time `BinaryStruct` is subclassed.

    May be subclassed to hijack certain constructor overloads.
    """

    # Required to ensure we wrap with `dataclass` exactly once.
    __WRAPPED_TYPE_IDS: set[int] = set()

    __PRIMED_BASE_ID: int = 0

    def __new__(mcs, name, bases, namespace, **kwargs):

        cls = super().__new__(mcs, name, bases, namespace)

        if mcs.__PRIMED_BASE_ID > 0:
            # This must be a `dataclass` recursive call.
            mcs.__WRAPPED_TYPE_IDS.add(mcs.__PRIMED_BASE_ID)
            mcs.__PRIMED_BASE_ID = 0
            return cls  # true `dataclass`

        if not hasattr(cls, "__qualname__"):
            raise TypeError(f"Unprimed wrapped dataclass encountered by {mcs.__name__}.")

        mcs.__PRIMED_BASE_ID = id(cls)

        # TRICK: We copy '__classcell__' from `namespace`, if it exists, while we construct the new class. This
        # is necessary because `dataclass` has no choice but to construct a new class that uses `__slots__`, which
        # will break classes that use the zero-argument form of `super()` (they rely on the 'magical context' of
        # the classcell to get the correct class). This trick works because `dataclasses._add_slots()` uses the class
        # `__dict__`.

        del_classcell = False
        if "__classcell__" in namespace:
            cls.__classcell__ = namespace["__classcell__"]
            del_classcell = True

        # noinspection PyArgumentList
        datacls = dataclass(cls, slots=True, kw_only=True)

        if mcs.__PRIMED_BASE_ID > 0:
            raise ValueError("Dataclass was not wrapped successfully with `dataclass`.")

        if del_classcell:
            del cls.__classcell__

        return datacls
