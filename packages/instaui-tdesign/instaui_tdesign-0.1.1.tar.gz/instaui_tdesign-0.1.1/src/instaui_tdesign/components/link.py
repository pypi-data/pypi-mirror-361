from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props


class Link(Element):
    def __init__(
        self,
        *,
        href: typing.Optional[str] = None,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TLinkProps],
    ):
        super().__init__("t-link")
        self.props({"content": content, "href": href})

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_click(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "click",
            handler,
            extends=extends,
        )
        return self


class TLinkProps(TypedDict, total=False):
    disabled: bool
    download: typing.Union[bool, str]
    hover: typing.Literal["color", "underline"]
    prefix_icon: str
    size: typing.Literal["small", "medium", "large"]
    suffix_icon: str
    target: str
    theme: typing.Literal["default", "primary", "danger", "warning", "success"]
    underline: bool
    on_click: EventMixin
