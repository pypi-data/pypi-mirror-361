"utility types"

from dataclasses import dataclass


@dataclass
class Meta:
    """Metadata to augment SQL types when they are derived from corresponding Python types

    Notes:
    - Instances of this class are meant to used with `typing.Annotated`.
    - Base Python types are mapped to equivalent SQL types with Annotations providing additional information
    - Providing an Annotated type allows mapping them to more precise SQL types. For example, while Python strings
      are not limited to specfic length, SQL strings commonly are. Similarly, SQL numeric types are more fine grained
    - All attributes are optional. When no attributes are specified, it's equivalent to not supplying any annotated information

    Attributes:
        name: SQL column name, if omitted Python attribute name is used
        size: size of the SQL column. It can be either a pair of numbers specified as a tuple or a single number
        occurs: relevant when converting python attributes that are defiend as `list`. A list is flattened to created as
                many instances as specified by this parameter. Note that name must be specified and must include `{n}' to give
                unique names to flattened column names
        skip: if specified, this attribute is skipped when any SQL statements are generated.
        default: default value for the generated SQL column. This must be specified as text even for non-text columns.
    """

    name: str | None = None
    size: int | tuple[int, int] | None = None
    occurs: int = 1
    skip: bool = False
    default: str | None = None

    @property
    def size_str(self) -> str:
        return "" if self.size is None else f"({self.size})" if isinstance(self.size, int) else f"({self.size[0]},{self.size[1]})"
