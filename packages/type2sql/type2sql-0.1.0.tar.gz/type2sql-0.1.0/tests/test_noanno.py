from type2sql import SqlCol, iter_cols

from .data import NoAnno


def test_noanno():
    # fmt: off
    expected = [
        SqlCol(name='X',   sql_type='VARCHAR', nullable=False),
        SqlCol(name='b',   sql_type='VARCHAR', nullable=True),
        SqlCol(name='C_1', sql_type='INTEGER', nullable=True),
        SqlCol(name='C_2', sql_type='INTEGER', nullable=True),
        SqlCol(name='d',   sql_type='VARCHAR', nullable=False)
    ]
    # fmt: on

    assert expected == list(iter_cols(NoAnno))
