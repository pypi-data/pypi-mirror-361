from type2sql import SqlCol, iter_cols

from .data import SkipRec
from .test_nested import expected as nested

expected = nested + [SqlCol("LINKS_IND", "BOOLEAN", False)]


def test_nested():
    assert expected == list(iter_cols(SkipRec))
