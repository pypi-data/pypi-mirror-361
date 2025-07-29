from dataclasses import replace

from type2sql import SqlCol, iter_cols

from .data import NestedRec
from .test_array import expected as array

expected = [SqlCol("CUST_NM", "VARCHAR", False)] + [replace(x, name=f"{pfx}_{x.name}") for pfx in ["PRI", "SEC"] for x in array]


def test_nested():
    assert expected == list(iter_cols(NestedRec))
