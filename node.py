from typing import Iterable, Callable, List, Optional
from xml.etree import ElementTree as ET
import re
import os

from pydantic import Field, BaseModel


class Node(BaseModel):
    """
    Represents a single UI element (node) from the Android view hierarchy
    retrieved via uiautomator2 dump.

    Each node corresponds to one View in the UI tree and includes both
    visual and accessibility-related attributes.
    """

    index: int = Field(
        description="Element index within its parent node.",
        examples=[0],
    )
    text: str = Field(
        description="Visible text content of the element (if any).",
        examples=["OK", ""],
    )
    resource_id: str = Field(
        description="Full Android resource ID (if available).",
        examples=["com.android.systemui:id/mobile_signal", ""],
    )
    view_class_name: str = Field(
        description="Fully qualified Android View class name.",
        examples=["android.widget.ImageView", "android.widget.TextView"],
    )
    package: str = Field(
        description="Package name of the app that owns this element.",
        examples=["com.android.systemui", "com.vk.android"],
    )
    content_desc: str = Field(
        description="Accessibility content description of the element.",
        examples=["Notifications", "Battery status", ""],
    )
    checkable: bool = Field(
        description="True if the element supports the checked/unchecked state.",
        examples=[False],
    )
    checked: bool = Field(
        description="True if the element is currently checked.",
        examples=[False],
    )
    clickable: bool = Field(
        description="True if the element supports click interactions.",
        examples=[True],
    )
    enabled: bool = Field(
        description="True if the element is currently enabled and interactable.",
        examples=[True],
    )
    focusable: bool = Field(
        description="True if the element can gain focus.",
        examples=[False],
    )
    focused: bool = Field(
        description="True if the element currently has focus.",
        examples=[False],
    )
    scrollable: bool = Field(
        description="True if this element can be scrolled.",
        examples=[False],
    )
    long_clickable: bool = Field(
        description="True if the element supports long press interactions.",
        examples=[False],
    )
    password: bool = Field(
        description="True if the element is a password input field.",
        examples=[False],
    )
    selected: bool = Field(
        description="True if the element is currently selected.",
        examples=[False],
    )
    visible_to_user: bool = Field(
        description="True if the element is visible to the user on screen.",
        examples=[True],
    )
    bounds: tuple[tuple[int, int], tuple[int, int]] = Field(
        description="Element bounds in screen coordinates ((x1,y1),(x2,y2)).",
        examples=[[(924, 50), (965, 91)]],
    )
    drawing_order: int = Field(
        description="Drawing order index of the element in the hierarchy.",
        examples=[1],
    )
    hint: str = Field(
        description="Hint text (commonly shown in editable fields).",
        examples=["", "Enter password"],
    )
    display_id: int = Field(
        description="Display ID for multi-display devices.",
        examples=[0],
    )

    @classmethod
    def from_xml(cls, el: ET.Element) -> "Node":
        def as_int(v, default=0):
            try:
                return int(v)
            except (TypeError, ValueError):
                return default

        def as_bool(v, default=False):
            if v is None:
                return default
            return str(v).strip().lower() in {"true", "1", "yes"}

        def parse_bounds(v, default=((0, 0), (0, 0))):
            if not v:
                return default
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", v.strip())
            if not m:
                return default
            x1, y1, x2, y2 = map(int, m.groups())
            return ((x1, y1), (x2, y2))

        a = el.attrib
        return cls(
            index=as_int(a.get("index")),
            text=a.get("text", "") or "",
            resource_id=a.get("resource-id", "") or "",
            view_class_name=a.get("class", "") or "",
            package=a.get("package", "") or "",
            content_desc=a.get("content-desc", "") or "",
            checkable=as_bool(a.get("checkable")),
            checked=as_bool(a.get("checked")),
            clickable=as_bool(a.get("clickable")),
            enabled=as_bool(a.get("enabled")),
            focusable=as_bool(a.get("focusable")),
            focused=as_bool(a.get("focused")),
            scrollable=as_bool(a.get("scrollable")),
            long_clickable=as_bool(a.get("long-clickable")),
            password=as_bool(a.get("password")),
            selected=as_bool(a.get("selected")),
            visible_to_user=as_bool(a.get("visible-to-user")),
            bounds=parse_bounds(a.get("bounds")),
            drawing_order=as_int(a.get("drawing-order")),
            hint=a.get("hint", "") or "",
            display_id=as_int(a.get("display-id")),
        )


class NodesFilter(BaseModel):
    """
    Filters applied to nodes returned by the hierarchy dump.
    If any field is specified, only nodes matching **all non-null filters**
    will be included in the response.
    """

    view_class_name: Optional[str] = Field(
        default=None,
        description="The highest priority filter. If this one is used, the others are not needed. Filter by Android View class name (exact match or substring).",
        examples=["android.widget.Button", "TextView"],
    )
    package_name: Optional[str] = Field(
        default=None,
        description="Optional, rare useful. Filter by package name of the app.",
        examples=["com.google.android.apps.youtube.music"],
    )
    resource_id: Optional[str] = Field(
        default=None,
        description="Use only if you sure that hierarchy have that res id. Always as secondary filter. Filter by full resource ID of the element.",
        examples=["com.example:id/login_button"],
    )
    content_description: Optional[str] = Field(
        default=None,
        description="Use only if you sure that hierarchy have that content_description. Always as secondary filter. Filter by substring in the accessibility content description.",
        examples=["Settings", "Notifications"],
    )
    text: Optional[str] = Field(
        default=None,
        description="Use only if you sure that hierarchy have that text. Always as secondary filter. Filter by substring in the visible text of the element.",
        examples=["Login", "OK", "Search"],
    )
    hint: Optional[str] = Field(
        default=None,
        description="Use only if you sure that hierarchy have that hint. Always as secondary filter. Filter by substring in the hint of the element.",
        examples=["Search", "Password"],
    )


# ---- Парсинг в список ----
def parse_nodes_from_string(xml_text: str) -> List[Node]:
    root = ET.fromstring(xml_text)
    return [Node.from_xml(el) for el in root.iter("node")]


def parse_nodes_from_file(path: str) -> List[Node]:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    tree = ET.parse(path)
    root = tree.getroot()
    return [Node.from_xml(el) for el in root.iter("node")]


def filter_nodes(nodes: Iterable[Node], f: NodesFilter) -> List[Node]:
    preds = []

    if f.view_class_name:
        v = f.view_class_name
        preds.append(lambda n, r=v: r in n.view_class_name)

    if f.package_name:
        v = f.package_name
        preds.append(lambda n, r=v: r in n.package)

    if f.resource_id:
        v = f.resource_id
        preds.append(lambda n, r=v: n.resource_id == r)

    if f.content_description:
        v = f.content_description
        preds.append(lambda n, r=v: r in n.content_desc)

    if f.text:
        v = f.text
        preds.append(lambda n, r=v: r in n.text)

    if f.hint:
        v = f.hint
        preds.append(lambda n, r=v: r in n.hint)

    # 0 фильтров → вернуть всё
    if not preds:
        return list(nodes)

    # 1 фильтр → OR по единственному предикату (деградирует в один чек)
    if len(preds) == 1:
        p = preds[0]
        return [n for n in nodes if p(n)]

    # 2+ фильтров → AND между предикатами
    return [n for n in nodes if all(p(n) for p in preds)]