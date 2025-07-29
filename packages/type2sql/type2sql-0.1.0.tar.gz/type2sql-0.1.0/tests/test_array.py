from type2sql import SqlCol, iter_cols

from .data import ArrayRec, Customer

# fmt: off
expected = [
    SqlCol("ACCT_NM",      "VARCHAR",       False),
    SqlCol("ADDR_LN_TXT",  "VARCHAR(50)",   False),
    SqlCol("ADDR_LN2_TXT", "VARCHAR(50)",   True),
    SqlCol("ACCT_BAL_AMT", "DECIMAL(14,2)", True),
    SqlCol("LAST_UPD_TS",  "TIMESTAMP",     False, "CURRENT_TIMESTAMP"),
    SqlCol("PH1_NUM",      "VARCHAR",       True),
    SqlCol("PH2_NUM",      "VARCHAR",       True),
    SqlCol("PH3_NUM",      "VARCHAR",       True),
]
# fmt: on


def test_simple():
    assert expected == list(iter_cols(ArrayRec))


def test_class():
    # fmt: off
    expected = [
        SqlCol("CUST_NM",       "VARCHAR(60)", False),
        SqlCol("ADDR1_ST1_NM",  "VARCHAR(60)", True),
        SqlCol("ADDR1_ST2_NM",  "VARCHAR(60)", True),
        SqlCol("ADDR1_CITY_NM", "VARCHAR(30)", True),
        SqlCol("ADDR1_ZIP_CD",  "VARCHAR(9)",  True),
        SqlCol("ADDR2_ST1_NM",  "VARCHAR(60)", True),
        SqlCol("ADDR2_ST2_NM",  "VARCHAR(60)", True),
        SqlCol("ADDR2_CITY_NM", "VARCHAR(30)", True),
        SqlCol("ADDR2_ZIP_CD",  "VARCHAR(9)",  True),
    ]
    # fmt: on

    assert expected == list(iter_cols(Customer))
