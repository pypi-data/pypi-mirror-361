"Python classes to represent scalar, list and object types"

import datetime as dt
from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Iterable, Self, get_type_hints

from .sqlcol import SqlCol
from .type_info import TypeInfo

type Show = str | list[Show] | dict[str, Show]

BASIC_TYPES: dict[type, str] = {
    bool: "BOOLEAN",
    str: "VARCHAR",
    dt.datetime: "TIMESTAMP",
    dt.date: "DATE",
    dt.time: "TIME",
    int: "INTEGER",
    float: "DECIMAL",
    Decimal: "DECIMAL",
}


@dataclass(frozen=True, slots=True)
class PyType:
    """Base class that describes an attribute of a Python class"""

    def iter_cols(self) -> Iterable[SqlCol]: ...

    def show(self) -> Show:
        raise RuntimeError(f"Invalid PyType instance {self.__class__.__name__}")

    @staticmethod
    def from_type[T](t: type[T]) -> "PyType":
        def go(attr_name: str, ti: TypeInfo) -> "PyType":
            if ti.is_list:
                return PyList(go(attr_name, replace(ti, is_list=False)), ti.meta.occurs)

            if ti.base_type in BASIC_TYPES:
                return PyScalar(
                    py_name=attr_name,
                    py_type=ti.base_type,
                    value=SqlCol(
                        name=ti.meta.name or attr_name,
                        sql_type=BASIC_TYPES[ti.base_type] + ti.meta.size_str,
                        nullable=ti.is_optional,
                        default=ti.meta.default,
                    ),
                )

            return PyObj(
                ti.base_type,
                {
                    n: go(n, TypeInfo.make(t))
                    for n, t in get_type_hints(ti.base_type, include_extras=True).items()
                    if not TypeInfo.make(t).meta.skip
                },
                ti.meta.name or "{sub}",
            )

        return go(t.__name__, TypeInfo.make(t))


@dataclass(frozen=True, slots=True)
class PyScalar(PyType):
    """Type that describes properties of a scalar attribute

    A scalar attribute has one of the supported built-in type and is neihter a list or another class

    Attributes:
        py_name: name of the Python attribute
        py_type: Python type of the attribute
        value: derived SQL column type
    """

    py_name: str
    py_type: type
    value: SqlCol

    def show(self) -> Show:
        return f"{self.value.name}"

    def with_name(self, name: str) -> Self:
        """Returns a copy of self with value.name updated with the suppled new name value

        Args:
            name: new name value

        Returns:
            A new instance of Self
        """
        return replace(self, value=replace(replace(self.value, name=name)))


@dataclass(frozen=True, slots=True)
class PyList(PyType):
    """Type that describes properties of an attribute that is a list of another type

    list can have a base class that is either scalar of another supported Python class

    Attributes:
        value: the base class
        occurs: number of instances to create for the converted SQL type
    """

    value: PyType
    occurs: int

    def show(self) -> Show:
        return [self.value.show()] * self.occurs


@dataclass(frozen=True, slots=True)
class PyObj(PyType):
    """Type that describes a Python object (an instance of a supported class)

    Attributes:
        py_type: type of the Python class
        value: dictionary consisting of class attributes and their Python types
        occurs: number of instances to create for the converted SQL type
        sub: a string pattern that contains `{sub}` to derive unique SQL column names
    """

    py_type: type
    value: dict[str, PyType]
    sub: str

    def show(self) -> Show:
        return {k: v.show() for k, v in self.value.items()}
