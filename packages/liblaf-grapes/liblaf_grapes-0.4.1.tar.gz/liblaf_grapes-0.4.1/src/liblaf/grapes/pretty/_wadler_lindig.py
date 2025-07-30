from typing import Any, TypedDict, Unpack

import attrs
import cytoolz as toolz
import wadler_lindig as wl


class PdocKwargs(TypedDict, total=True):
    """.

    References:
        1. <https://docs.kidger.site/wadler_lindig/api/#wadler_lindig.pdoc>
    """

    indent: int
    hide_defaults: bool
    show_type_module: bool
    show_dataclass_module: bool


@attrs.frozen
class WithRepr:
    string: str = attrs.field()

    def __repr__(self) -> str:
        return self.string


UNINITIALIZED = WithRepr("<uninitialized>")


def pdoc_attrs(self: Any, **kwargs: Unpack[PdocKwargs]) -> wl.AbstractDoc:
    """.

    References:
        1. <https://github.com/patrick-kidger/wadler_lindig/blob/0226340d56f0c18e10cd4d375cf7ea25818359b8/wadler_lindig/_definitions.py#L308-L326>
    """
    cls: type = type(self)
    objs: list[tuple[str, Any]] = []
    for field in attrs.fields(cls):
        field: attrs.Attribute
        if not field.repr:
            continue
        value: Any = getattr(self, field.name, UNINITIALIZED)
        if kwargs["hide_defaults"] and value is field.default:
            continue
        objs.append((field.name, value))
    name_kwargs: PdocKwargs = toolz.assoc(
        kwargs, "show_type_module", kwargs["show_dataclass_module"]
    )  # pyright: ignore[reportAssignmentType]
    return wl.bracketed(
        begin=wl.pdoc(cls, **name_kwargs) + wl.TextDoc("("),
        docs=wl.named_objs(objs, **kwargs),
        sep=wl.comma,
        end=wl.TextDoc(")"),
        indent=kwargs["indent"],
    )


class WadlerLindigMixin:
    def __repr__(self) -> str:
        return wl.pformat(self)

    def __pdoc__(self, **kwargs) -> wl.AbstractDoc:
        return pdoc_attrs(self, **kwargs)
