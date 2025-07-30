from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props


class Alert(Element):
    def __init__(
        self,
        message: typing.Optional[str] = None,
        **kwargs: Unpack[TAlertProps],
    ):
        super().__init__("t-alert")

        self.props({"message": message})
        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_close(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "close",
            handler,
            extends=extends,
        )
        return self

    def on_closed(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "closed",
            handler,
            extends=extends,
        )
        return self


class TAlertProps(TypedDict, total=False):
    close: typing.Literal["boolean"]
    close_btn: typing.Literal["boolean"]
    default: str
    icon: str
    max_line: float
    operation: str
    theme: typing.Literal["success", "info", "warning", "error"]
    title: str
    on_close: EventMixin
    on_closed: EventMixin
