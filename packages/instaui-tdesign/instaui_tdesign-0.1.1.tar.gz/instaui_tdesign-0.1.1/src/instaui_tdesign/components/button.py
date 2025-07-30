from __future__ import annotations
import typing
from instaui.components.element import Element
from instaui.components.content import Content
from instaui.event.event_mixin import EventMixin
from typing_extensions import TypedDict, Unpack

from ._utils import handle_props, handle_event_from_props


class TButtonProps(TypedDict, total=False):
    block: bool
    disabled: bool
    form: str
    ghost: bool
    href: str
    icon: str
    loading: bool
    shape: typing.Literal["rectangle", "square", "round", "circle"]
    loading_props: typing.Dict
    size: typing.Literal["small", "medium", "large"]
    suffix: str
    tag: typing.Literal["button", "a", "div"]
    theme: typing.Literal["default", "primary", "danger", "warning", "success"]
    type: typing.Literal["submit", "reset", "button"]
    variant: typing.Literal["base", "outline", "dashed", "text"]
    on_click: EventMixin


class Button(Element):
    def __init__(
        self,
        content: typing.Optional[str] = None,
        **kwargs: Unpack[TButtonProps],
    ):
        """Create a button element.

        Args:
            content (Optional[TMaybeRef[str]], optional): _description_. Defaults to None.
        """

        super().__init__("t-button")

        if content is not None:
            with self:
                Content(content)

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
