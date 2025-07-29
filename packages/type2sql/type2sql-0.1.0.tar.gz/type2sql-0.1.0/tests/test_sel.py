from textwrap import dedent

from type2sql import gen_select

from .data import ArrayRec


def test_sel():
    expected = dedent("""\
        SELECT ACCT_NM
            , ADDR_LN_TXT
            , ADDR_LN2_TXT
            , ACCT_BAL_AMT
            , LAST_UPD_TS
            , PH1_NUM
            , PH2_NUM
            , PH3_NUM
        FROM FIN.ACCOUNT""")

    actual = gen_select(ArrayRec, "FIN.ACCOUNT")

    assert expected == actual
