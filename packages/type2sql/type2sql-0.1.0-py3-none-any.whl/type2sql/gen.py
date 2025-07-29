"generators to generate SQL statements and Python code"

from dataclasses import replace
from textwrap import dedent
from typing import Iterable, Iterator

from .pytype import PyList, PyObj, PyScalar, PyType
from .sqlcol import SqlCol


def gen_ddl[T](cls: type[T], table: str | None = None) -> str:
    """generate SQL CREATE TABLE statement for the flattened Python object

    Args:
        cls: A Python type that to be constructed
        table: Optional, if not given, class name is used as table name

    Returns:
        SQL DDL statement
    """
    cols = list(iter_cols(cls))
    max_width = max(len(c.name) for c in cols)

    def sql_def(c: SqlCol) -> str:
        n = "" if c.nullable else " NOT NULL"
        d = "" if c.default is None else f" DEFAULT {c.default}"
        return f"    {c.name:{max_width}}  {c.sql_type}{n}{d}"

    return f"CREATE TABLE {table or cls.__name__} (\n{',\n'.join(sql_def(c) for c in cols)}\n)"


def gen_select[T](cls: type[T], table: str | None = None) -> str:
    """generate SQL SELECT statement for the flattened Python object

    Args:
        cls: A Python type that to be constructed
        table: Optional, if not given, class name is used as table name

    Returns:
        SQL SELECT statement
    """
    return f"SELECT {'\n    , '.join(c.name for c in iter_cols(cls))}\nFROM {table or cls.__name__}"


def gen_load[T](cls: type[T], fn_name: str = "load") -> str:
    """generate a Python function to instantiate Python object from it's constituent flattened inputs
       - function named will be load()
       - the arguments are expected to be in the order they are defined in Python type when flattened
       - generated code doesn't include any needed import statements (e.g. date, time etc)
       - generated code may make use of a special function named `cons_if` to coonditionally construct
         instance of types when used in list.
         - `cons_of` function is available as a top-level function of this package

    Args:
        cls: A Python type
        fn_name: name of the function generated; default is "load"

    Returns:
        Python function code as string
    """
    xs = list(flatten_with_marks(cls))

    def param(x: PyScalar) -> str:
        return f"{x.value.name.lower()}: {x.py_type.__name__}{' | None' if x.value.nullable else ''}"

    def go(xs: Iterator[PyScalar | str], check_nulls: bool = False) -> Iterable[str]:
        for x in xs:
            if isinstance(x, PyScalar):
                yield x.value.name.lower()
            elif x == "list":
                yield dedent(f"""\
                    [x for x in [
                        {indent(",\n".join(go(xs, True)), 6)}
                    ] if x is not None]""")
            elif x == ")":
                return
            else:
                cons = f"cons_if({x}," if check_nulls else f"{x}("
                yield dedent(f"""\
                    {cons}
                        {indent(",\n".join(go(xs, check_nulls)), 6)}
                    )""")

    fn = dedent(f"""\
        def {fn_name}(
            {indent(",\n    ".join(param(x) for x in xs if isinstance(x, PyScalar)), 2)}
        ) -> {cls.__name__}:
            return {indent("".join(go(iter(xs))), 3)}""")

    return fn


def flatten_with_marks[T](cls: type[T]) -> Iterable[PyScalar | str]:
    """similar to flatten() except adds start and end markers for PyList and PyObj instances
       - start marker values are "list" for PyList and name of the Python type for PyObj
       - end marker value is ")" for both PyList and uPyObj

    Args:
        cls: A Python type that can return type hints, usuallay a dataclass or a NamedTuple instaces

    Returns:
        Iterable of PyScalar instances or marker (str) values
    """

    def sub_var(var: str, **subs: str | int) -> str:
        for k, v in subs.items():
            var = var.replace(f"{{{k}}}", str(v))
        return var

    def go(po: PyType, force_null: bool = False) -> Iterable[PyScalar | str]:
        if isinstance(po, PyScalar):
            yield replace(po, value=replace(po.value, nullable=True)) if force_null else po
        elif isinstance(po, PyList):
            yield "list"
            yield from (
                y.with_name(sub_var(y.value.name, n=x + 1)) if isinstance(y, PyScalar) else y
                for x in range(po.occurs)
                for y in go(po.value, force_null=True)
            )
            yield ")"
        elif isinstance(po, PyObj):
            yield po.py_type.__name__
            yield from (
                y.with_name(sub_var(po.sub, sub=y.value.name)) if isinstance(y, PyScalar) else y
                for x in po.value.values()
                for y in go(x, force_null)
            )
            yield ")"

    return go(PyType.from_type(cls))


def flatten[T](cls: type[T]) -> Iterable[PyScalar]:
    """flatten nested (PyObj) and list (PyList) instances of PyType and return PyScalar values with resolved names

    Args:
        cls: A Python type that can return type hints, usuallay a dataclass or a NamedTuple instaces

    Returns:
        Iterable of PyScalar instances
    """
    yield from (x for x in flatten_with_marks(cls) if isinstance(x, PyScalar))


def iter_cols[T](cls: type[T]) -> Iterable[SqlCol]:
    """iterate over a Python type flattening nested and list types with SqlCol instances

    Args:
        cls: A Python type that can return type hints, usuallay a dataclass or a NamedTuple instaces

    Returns:
        Iterable of SqlCol instances
    """
    yield from (po.value for po in flatten(cls))


def indent(x: str, by: int = 1, init: bool = False):
    prefix = "\n" + "    " * by
    return (prefix if init else "") + prefix.join(x.splitlines())
