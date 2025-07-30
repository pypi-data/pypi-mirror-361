from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props


class Breadcrumb(Element):
    def __init__(
        self,
        **kwargs: Unpack[TBreadcrumbProps],
    ):
        super().__init__("t-breadcrumb")

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore


class BreadcrumbItem(Element):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TBreadcrumbItemProps],
    ):
        super().__init__("t-breadcrumb-item")
        self.props({"content": content})
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


class TBreadcrumbProps(TypedDict, total=False):
    ellipsis: str
    items_after_collapse: float
    items_before_collapse: float
    max_item_width: str
    max_items: float
    options: typing.List
    separator: str
    theme: typing.Literal["light"]


class TBreadcrumbItemProps(TypedDict, total=False):
    disabled: bool
    href: str
    icon: str
    max_width: str
    replace: bool
    router: typing.Dict
    target: typing.Literal["_blank", "_self", "_parent", "_top"]
    to: typing.Literal["Route"]
    on_click: EventMixin
