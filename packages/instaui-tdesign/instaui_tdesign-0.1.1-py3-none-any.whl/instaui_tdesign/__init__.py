"""
Easy to use TDesign UI components for InstaUI.

Examples:
.. code-block:: python
    from instaui import ui
    import instaui_tdesign as td

    td.use()

    @ui.page("/")
    def index_page():
        td.input(placeholder="input")
"""

__all__ = [
    "use",
    "affix",
    "alert",
    "anchor",
    "auto_complete",
    "back_top",
    "badge",
    "breadcrumb",
    "breadcrumb_item",
    "button",
    "card",
    "cascader",
    "checkbox",
    "color_picker",
    "color_picker_panel",
    "date_picker",
    "date_picker_panel",
    "date_range_picker",
    "date_range_picker_panel",
    "divider",
    "dropdown",
    "form",
    "form_item",
    "input_adornment",
    "input_number",
    "input",
    "link",
    "select",
    "space",
    "steps",
    "step_item",
    "sticky_tool",
    "sticky_item",
    "switch",
    "tabs",
    "tab_panel",
    "tag_input",
    "menu",
    "menu_group",
    "menu_item",
    "sub_menu",
    "head_menu",
    "pagination",
    "radio",
    "radio_group",
    "typography_paragraph",
    "typography_text",
    "typography_title",
    "row",
    "col",
    "layout",
    "header",
    "aside",
    "content",
    "footer",
]


from .setup import use
from .components.affix import Affix as affix
from .components.alert import Alert as alert
from .components.anchor import Anchor as anchor
from .components.auto_complete import AutoComplete as auto_complete
from .components.back_top import BackTop as back_top
from .components.badge import Badge as badge
from .components.breadcrumb import (
    Breadcrumb as breadcrumb,
    BreadcrumbItem as breadcrumb_item,
)
from .components.button import Button as button
from .components.card import Card as card
from .components.cascader import Cascader as cascader
from .components.checkbox import Checkbox as checkbox
from .components.color_picker import (
    ColorPicker as color_picker,
    ColorPickerPanel as color_picker_panel,
)
from .components.date_picker import (
    DatePicker as date_picker,
    DatePickerPanel as date_picker_panel,
    DateRangePicker as date_range_picker,
    DateRangePickerPanel as date_range_picker_panel,
)
from .components.divider import Divider as divider
from .components.dropdown import Dropdown as dropdown
from .components.form import Form as form, FormItem as form_item
from .components.input_adornment import InputAdornment as input_adornment
from .components.input_number import InputNumber as input_number
from .components.input import Input as input
from .components.grid import Row as row, Col as col
from .components.link import Link as link
from .components.select import Select as select
from .components.space import Space as space
from .components.steps import Steps as steps, StepItem as step_item
from .components.sticky_tool import StickyTool as sticky_tool, StickyItem as sticky_item
from .components.switch import Switch as switch
from .components.tabs import Tabs as tabs, TabPanel as tab_panel
from .components.tag_input import TagInput as tag_input
from .components.menu import (
    Menu as menu,
    SubMenu as sub_menu,
    MenuItem as menu_item,
    MenuGroup as menu_group,
    HeadMenu as head_menu,
)
from .components.pagination import Pagination as pagination
from .components.radio import Radio as radio, RadioGroup as radio_group
from .components.typography import (
    TypographyText as typography_text,
    TypographyTitle as typography_title,
    TypographyParagraph as typography_paragraph,
)
from .components.layout import (
    Layout as layout,
    Header as header,
    Aside as aside,
    Content as content,
    Footer as footer,
)
