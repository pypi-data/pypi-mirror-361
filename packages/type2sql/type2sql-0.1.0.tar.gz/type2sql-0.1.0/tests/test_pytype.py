from type2sql.pytype import PyType, Show

from .data import NestedRec


def test_nested():
    expected: Show = {
        "name": "CUST_NM",
        "primary": {
            "name": "ACCT_NM",
            "street": "ADDR_LN_TXT",
            "street2": "ADDR_LN2_TXT",
            "balance": "ACCT_BAL_AMT",
            "last_updated": "LAST_UPD_TS",
            "phones": ["PH{n}_NUM", "PH{n}_NUM", "PH{n}_NUM"],
        },
        "secondary": {
            "name": "ACCT_NM",
            "street": "ADDR_LN_TXT",
            "street2": "ADDR_LN2_TXT",
            "balance": "ACCT_BAL_AMT",
            "last_updated": "LAST_UPD_TS",
            "phones": ["PH{n}_NUM", "PH{n}_NUM", "PH{n}_NUM"],
        },
    }
    actual = PyType.from_type(NestedRec).show()
    assert actual == expected
