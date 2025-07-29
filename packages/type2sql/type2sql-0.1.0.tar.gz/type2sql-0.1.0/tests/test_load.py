from textwrap import dedent

from type2sql import gen_load

from .data import Customer, NestedRec


def test_nested():
    expected = dedent("""\
        def load(
            cust_nm: str,
            pri_acct_nm: str,
            pri_addr_ln_txt: str,
            pri_addr_ln2_txt: str | None,
            pri_acct_bal_amt: float | None,
            pri_last_upd_ts: datetime,
            pri_ph1_num: str | None,
            pri_ph2_num: str | None,
            pri_ph3_num: str | None,
            sec_acct_nm: str,
            sec_addr_ln_txt: str,
            sec_addr_ln2_txt: str | None,
            sec_acct_bal_amt: float | None,
            sec_last_upd_ts: datetime,
            sec_ph1_num: str | None,
            sec_ph2_num: str | None,
            sec_ph3_num: str | None
        ) -> NestedRec:
            return NestedRec(
                cust_nm,
                ArrayRec(
                    pri_acct_nm,
                    pri_addr_ln_txt,
                    pri_addr_ln2_txt,
                    pri_acct_bal_amt,
                    pri_last_upd_ts,
                    [x for x in [
                        pri_ph1_num,
                        pri_ph2_num,
                        pri_ph3_num
                    ] if x is not None]
                ),
                ArrayRec(
                    sec_acct_nm,
                    sec_addr_ln_txt,
                    sec_addr_ln2_txt,
                    sec_acct_bal_amt,
                    sec_last_upd_ts,
                    [x for x in [
                        sec_ph1_num,
                        sec_ph2_num,
                        sec_ph3_num
                    ] if x is not None]
                )
            )""")

    assert gen_load(NestedRec) == expected


def test_list():
    expected = dedent("""\
        def load(
            cust_nm: str,
            addr1_st1_nm: str | None,
            addr1_st2_nm: str | None,
            addr1_city_nm: str | None,
            addr1_zip_cd: str | None,
            addr2_st1_nm: str | None,
            addr2_st2_nm: str | None,
            addr2_city_nm: str | None,
            addr2_zip_cd: str | None
        ) -> Customer:
            return Customer(
                cust_nm,
                [x for x in [
                    cons_if(Address,
                        addr1_st1_nm,
                        addr1_st2_nm,
                        addr1_city_nm,
                        addr1_zip_cd
                    ),
                    cons_if(Address,
                        addr2_st1_nm,
                        addr2_st2_nm,
                        addr2_city_nm,
                        addr2_zip_cd
                    )
                ] if x is not None]
            )""")

    assert gen_load(Customer) == expected
