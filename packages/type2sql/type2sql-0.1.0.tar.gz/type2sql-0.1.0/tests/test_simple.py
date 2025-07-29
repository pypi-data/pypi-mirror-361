from type2sql import SqlCol, iter_cols

from .data import SimpleRec


def test_simple():
    # fmt: off
    expected = [
        SqlCol("ACCT_NM",      "VARCHAR",       False),
        SqlCol("ADDR_LN_TXT",  "VARCHAR(50)",   False),
        SqlCol("ADDR_LN2_TXT", "VARCHAR(50)",   True),
        SqlCol("ACCT_BAL_AMT", "DECIMAL(14,2)", True),
        SqlCol("LAST_UPD_TS",  "TIMESTAMP",     False, "CURRENT_TIMESTAMP"),
    ]
    # fmt: on

    assert expected == list(iter_cols(SimpleRec))
