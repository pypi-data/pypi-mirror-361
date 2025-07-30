from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack, Required

from ._utils import handle_props, handle_event_from_props


class Dropdown(Element):
    def __init__(
        self,
        options: typing.List[DropdownOptionItem],
        **kwargs: Unpack[TDropdownProps],
    ):
        super().__init__("t-dropdown")
        self.props({"options": options})

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


class DropdownItem(Element):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TDropdownItemProps],
    ):
        super().__init__("t-dropdown-item")
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


class DropdownOptionItem(TypedDict, total=False):
    active: bool
    content: Required[str]
    disabled: bool
    divider: bool
    prefix_icon: str
    theme: typing.Literal["default", "success", "warning", "error"]
    value: Required[int]
    childred: typing.Optional[typing.List[DropdownOptionItem]]


class TDropdownProps(TypedDict, total=False):
    direction: typing.Literal["left", "right"]
    disabled: bool
    hide_after_item_click: bool
    max_column_width: typing.Union[float, str]
    max_height: float
    min_column_width: typing.Union[float, str]
    panel_bottom_content: str
    panel_top_content: str
    placement: typing.Literal[
        "top",
        "left",
        "right",
        "bottom",
        "top-left",
        "top-right",
        "bottom-left",
        "bottom-right",
        "left-top",
        "left-bottom",
        "right-top",
        "right-bottom",
    ]
    popup_props: typing.Dict
    trigger: typing.Literal["hover", "click", "focus", "context-menu"]
    on_click: EventMixin


class TDropdownItemProps(TypedDict, total=False):
    active: bool
    disabled: bool
    divider: bool
    prefix_icon: str
    theme: typing.Literal["default", "success", "warning", "error"]
    value: int
    on_click: EventMixin
