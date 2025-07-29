from textwrap import dedent

from type2sql import gen_ddl

from .data import Customer


def test_ddl():
    expected = dedent("""\
        CREATE TABLE FIN.CUSTOMER (
            CUST_NM        VARCHAR(60) NOT NULL,
            ADDR1_ST1_NM   VARCHAR(60),
            ADDR1_ST2_NM   VARCHAR(60),
            ADDR1_CITY_NM  VARCHAR(30),
            ADDR1_ZIP_CD   VARCHAR(9),
            ADDR2_ST1_NM   VARCHAR(60),
            ADDR2_ST2_NM   VARCHAR(60),
            ADDR2_CITY_NM  VARCHAR(30),
            ADDR2_ZIP_CD   VARCHAR(9)
        )""")

    actual = gen_ddl(Customer, "FIN.CUSTOMER")
    assert expected == actual
