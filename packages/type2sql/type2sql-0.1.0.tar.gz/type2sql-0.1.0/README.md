# type2sql

Code generator for Python classes to flattened relational SQL Table types

For generating SQL code, attributes are *flattened*, that is nested classes, and lists are generated as single SQL columns. A reverse process happens when generating Python code, that is, Python object can be instantiated from flattened SQL columns.

## Annotation

Instances of **type2sql.Meta** class can be used to annotate Python types. Meta class supports the following, all optional, attributes:

- **name**: SQL column name, when omitted, Python attribute name is used
- **size**: the size of the SQL column. It can be either a pair of numbers specified as a tuple or a single number
- **occurs**: relevant when converting python attributes that are defined as `list`. A list is flattened to create as many instances as specified by this parameter. Note that the name must be specified and must include `{n}` to give unique names to flattened column names
- **skip**: if specified, this attribute is skipped when any SQL statements are generated. Other specifications, if specified, are ignored
- **default**: default value for the generated SQL column.

## Supported Python types

Supported Python types:

Python Type         | SQL Type    | Notes
--------------------|-------------|------------------------------------------------------------------
`str`               | `VARCHAR`   |
`int`               | `INTEGER`   |
`float`             | `DECIMAL`   |
`Decimal`           | `DECIMAL`   |
`bool`              | `BOOLEAN`   |
`datetime.date`     | `DATE`      |
`datetime.time`     | `TIME`      |
`datetime.datetime` | `TIMESTAMP` |
`T`                 | <flattened> | any Python class with all of its attributes having one of the supported type
`list[T]`           | <flattened> | where T is one of the supported type
`T \| None`         | Same as `T` | generated SQL Column will allow `NULL` values

## Usage

Install `type2sql` as a dependency in other Python applications or modules that contain target classes for code generation. Use the following functions to generate the required code.

- `gen_select(<class>[, <table>])` generates `SELECT` SQL statement
- `gen_ddl(<class>[, <table>])` generates `CREATE TABLE` SQL statement
- `gen_load(<class>[, <fn>])` generates a Python function to instantiate Python type that accepts flattened values as parameters

## Example

```python
@dataclass
class Address:
     street1: Annotated[str,        Meta(name="ST1_NM",  size=60)]
     street2: Annotated[str | None, Meta(name="ST2_NM",  size=60)]
     city:    Annotated[str,        Meta(name="CITY_NM", size=30)]
     zip:     Annotated[str,        Meta(name="ZIP_CD",  size=9)]


@dataclass
class Customer:
     name: Annotated[str,           Meta(name="CUST_NM", size=60)]
     addr: Annotated[list[Address], Meta(name="ADDR{n}_{sub}", occurs=2)]


print(gen_ddl(Customer, "FIN.CUSTOMER"))
```

The above script will print:

```sql
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
)
```

More examples can be found in the test suite under `tests/` folder.
