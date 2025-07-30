from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.components.content import Content
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props


class Affix(Element):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TAffixProps],
    ):
        super().__init__("t-affix")

        if content is not None:
            with self:
                Content(content)

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_fixed_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "fixed_change",
            handler,
            extends=extends,
        )
        return self


class TAffixProps(TypedDict, total=False):
    container: str
    default: str
    offset_bottom: float
    offset_top: float
    z_index: float
    on_fixed_change: EventMixin
