from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props, try_setup_vmodel


class Cascader(Element):
    def __init__(
        self,
        value: typing.Optional[typing.Union[int, str]] = None,
        **kwargs: Unpack[TCascaderProps],
    ):
        super().__init__("t-cascader")

        try_setup_vmodel(self, value)

        self.props(handle_props(kwargs))  # type: ignore
        handle_event_from_props(self, kwargs)  # type: ignore

    def on_blur(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "blur",
            handler,
            extends=extends,
        )
        return self

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

    def on_focus(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "focus",
            handler,
            extends=extends,
        )
        return self

    def on_popup_visible_change(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "popup_visible_change",
            handler,
            extends=extends,
        )
        return self

    def on_remove(
        self,
        handler: EventMixin,
        *,
        extends: typing.Optional[typing.List] = None,
    ):
        self.on(
            "remove",
            handler,
            extends=extends,
        )
        return self


class TCascaderProps(TypedDict, total=False):
    autofocus: bool
    borderless: bool
    check_props: typing.Dict
    check_strictly: bool
    clearable: bool
    collapsed_items: str
    disabled: bool
    empty: str
    filter: str
    filterable: bool
    input_props: typing.Dict
    keys: typing.Dict
    label: str
    lazy: bool
    load: str
    loading: bool
    loading_text: str
    max: float
    min_collapsed_num: float
    multiple: bool
    option: str
    options: typing.List
    panel_bottom_content: str
    panel_top_content: str
    placeholder: str
    popup_props: typing.Dict
    popup_visible: bool
    default_popup_visible: bool
    prefix_icon: str
    readonly: bool
    reserve_keyword: bool
    select_input_props: typing.Dict
    show_all_levels: bool
    size: typing.Literal["large", "medium", "small"]
    status: typing.Literal["default", "success", "warning", "error"]
    suffix: str
    suffix_icon: str
    tag_input_props: typing.Dict
    tag_props: typing.Dict
    tips: str
    trigger: typing.Literal["click", "hover"]
    default_value: typing.Union[int, str]
    value_display: str
    value_mode: typing.Literal["onlyLeaf", "parentFirst", "all"]
    value_type: typing.Literal["single", "full"]
    on_blur: EventMixin
    on_change: EventMixin
    on_focus: EventMixin
    on_popup_visible_change: EventMixin
    on_remove: EventMixin
