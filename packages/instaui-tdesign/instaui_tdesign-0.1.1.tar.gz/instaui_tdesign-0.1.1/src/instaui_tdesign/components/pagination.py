from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Pagination(Element):
    def __init__(
        self,
        current: typing.Optional[int] = None,
        *,
        current_value: typing.Optional[bool] = None,
        **kwargs: Unpack[TPaginationProps],
    ):
        super().__init__("t-pagination")

        try_setup_vmodel(self, current)

        self.props(handle_props(kwargs, model_value=current_value))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self

    def on_current_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "current_change",
            handler,
            extends=extends,
        )
        return self

    def on_page_size_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "page_size_change",
            handler,
            extends=extends,
        )
        return self


class PaginationMini(Element):
    def __init__(
        self,
        current: typing.Optional[int] = None,
        *,
        current_value: typing.Optional[bool] = None,
        **kwargs: Unpack[TPaginationMiniProps],
    ):
        super().__init__("t-pagination-mini")

        try_setup_vmodel(self, current)

        self.props(handle_props(kwargs, model_value=current_value))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "change",
            handler,
            extends=extends,
        )
        return self


class TPaginationProps(TypedDict, total=False):
    default_current: int
    disabled: bool
    folded_max_page_btn: int
    max_page_btn: int
    page_ellipsis_mode: typing.Literal["mid", "both-ends"]
    page_size: int
    default_page_size: int
    page_size_options: typing.List
    select_props: typing.Dict
    show_first_and_last_page_btn: bool
    show_jumper: bool
    show_page_number: bool
    show_page_size: bool
    show_previous_and_next_btn: bool
    size: typing.Literal["small", "medium"]
    theme: typing.Literal["default", "simple"]
    total: int
    total_content: typing.Union[bool, str]
    on_change: EventMixin
    on_current_change: EventMixin
    on_page_size_change: EventMixin


class TPaginationMiniProps(TypedDict, total=False):
    disabled: typing.Union[bool, typing.Dict]
    layout: typing.Literal["horizontal", "vertical"]
    show_current: bool
    size: typing.Literal["small", "medium", "large"]
    tips: typing.Dict
    variant: typing.Literal["text", "outline"]
    on_change: EventMixin
