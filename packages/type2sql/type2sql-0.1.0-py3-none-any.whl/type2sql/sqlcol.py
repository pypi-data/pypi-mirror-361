"SQL olumn class"

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SqlCol:
    """SQL column properties

    Attributes:
        name: SQL column name
        sql_type: Full type specification of the column, including it's size if available
        nullable: True if the column can accept NULL values
        default: default value, if available, is reproduced verbatim in the output
    """

    name: str
    sql_type: str
    nullable: bool = True
    default: str | None = None
