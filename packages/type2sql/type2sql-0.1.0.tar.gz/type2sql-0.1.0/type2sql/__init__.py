from typing import Any

from .gen import gen_ddl, gen_load, gen_select, iter_cols
from .meta import Meta
from .pytype import PyList, PyObj, PyScalar, PyType
from .sqlcol import SqlCol
from .type_info import TypeInfo

__version__ = "0.1.0"


def cons_if[T](cls: type[T], *args: Any) -> T | None:
    """Construct an object if at least one parameter is not None or if it's a list, it's not empty

    Args:
        cls: A Python type that to be constructed

    Returns:
        An instance of cls or None
    """
    return None if all(x is None or (isinstance(x, list) and not x) for x in args) else cls(*args)


__all__ = [
    "Meta",
    "SqlCol",
    "PyList",
    "PyObj",
    "PyScalar",
    "PyType",
    "iter_cols",
    "TypeInfo",
    "gen_ddl",
    "gen_load",
    "gen_select",
    "cons_if",
]
