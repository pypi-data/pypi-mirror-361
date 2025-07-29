from dataclasses import dataclass
from types import UnionType
from typing import Annotated, Self, Union, get_args, get_origin

from .meta import Meta


@dataclass
class TypeInfo:
    """An internal class used for extracting various pieces of information from type of Python classe attribute

    Attributes:
        base_type: base type after removing `None` and `list` types
        is_list: indicates if the specified type had `list` specification
        is_optional: indicates if the specified type had `Optional` or `| None` specification
        meta: Annotation information, if none was specified, an empty, default instance is attached
    """

    base_type: type
    is_list: bool
    is_optional: bool
    meta: Meta

    @classmethod
    def make(cls: type[Self], atype: Annotated[type, ...]) -> Self:
        tp, *hints = get_args(atype) if get_origin(atype) == Annotated else (atype,)

        if origin := get_origin(tp):
            is_list = issubclass(origin, list)
            is_optional = (origin is Union or origin is UnionType) and get_args(tp)[1] is type(None)
        else:
            is_list = is_optional = False

        return cls(
            base_type=get_args(tp)[0] if is_list or is_optional else tp,
            is_list=is_list,
            is_optional=is_optional,
            meta=next((h for h in hints if isinstance(h, Meta)), Meta()),
        )
