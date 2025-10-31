import adbutils
from pydantic import Field, BaseModel
from typing import Any, Union, Optional
import uiautomator2 as u2
from device import set_device, get_device
from node import parse_nodes_from_string, filter_nodes, Node, NodesFilter


class BaseActionResponse(BaseModel):
    """Response containing info about action performed """
    status: bool = Field(
        description="True if action performed successfully.",
        examples=[True, False],
    )
    error: str = Field(
        default="",
        description=(
            "Error message when performing fails;"
            "Leaving empty string on success."),
        examples=["device '<serial>' not found", ""],
    )


class ConnectDeviceResponse(BaseModel):
    """Response containing info about connecting device"""
    status: bool = Field(
        description="True if connection to the Android device succeeded.",
        examples=[True, False],
    )
    info: dict[str, Any] = Field(
        description="Device info returned from uiautomator2 (d.info).",
        examples=[
            {"serial": "123xxx", "sdk": 36, "brand": "google", "model": "Pixel 6", "arch": "arm64-v8a", "version": 16}],
    )
    error: str = Field(
        default="",
        description=(
            "Error message when connection fails;"
            "Leaving empty string on success."),
        examples=["Can't find any android device/emulator", ""],
    )


class DevicesListResponse(BaseModel):
    """Response containing the list of connected Android devices."""

    status: bool = Field(
        description="True if device list was retrieved successfully.",
        examples=[True, False],
    )
    error: str = Field(
        default="",
        description="Error message if listing failed; empty string when successful.",
        examples=["ADB not found", ""],
    )
    devices_serial_list: list[str] = Field(
        description="List of ADB serial numbers for all connected Android devices or emulators.",
        examples=[
            ["emulator-5554", "R9CT200XYZ"],
            [],
        ],
    )


def getDevices() -> DevicesListResponse:
    try:
        devices = adbutils.adb.device_list()
        serials = []
        for device in devices:
            serials.append(device.serial)
        return DevicesListResponse(
            status=True,
            error="",
            devices_serial_list=serials,
        )
    except Exception as e:
        return DevicesListResponse(
            status=False,
            error=str(e),
            devices_serial_list=[],
        )


def connect(serial: str) -> ConnectDeviceResponse:
    try:
        d = u2.connect(serial) if len(serial) > 0 else u2.connect()
        i = d.device_info
        set_device(d)
        return ConnectDeviceResponse(
            status=True,
            info=i,
            error="",
        )
    except Exception as e:
        return ConnectDeviceResponse(
            status=False,
            info={},
            error=str(e),
        )


def openNotifications() -> BaseActionResponse:
    try:
        get_device().open_notification()
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def openQuickSettings() -> BaseActionResponse:
    try:
        get_device().open_quick_settings()
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


class GetDumpResponse(BaseModel):
    """
    Response containing the UI hierarchy dump after applying optional filters.
    """

    status: bool = Field(
        description="True if hierarchy dump was retrieved successfully.",
        examples=[True, False],
    )
    error: str = Field(
        default="",
        description="Error message if dump failed; empty string when successful.",
        examples=["device not connected", ""],
    )
    hierarchy: list[Node] = Field(
        description=(
            "List of UI nodes currently visible on the device screen, "
            "each represented as a `Node` object. "
            "If filters are provided, only matching nodes are included."
        ),
        examples=[
            [
                {
                    "index": 0,
                    "text": "OK",
                    "resource_id": "com.example:id/ok_button",
                    "class_name": "android.widget.Button",
                    "package": "com.example",
                    "clickable": True,
                    "enabled": True,
                    "visible_to_user": True,
                    "bounds": [[100, 200], [300, 260]],
                },
                {}
            ]
        ],
    )


class GetDumpRequest(BaseModel):
    """
    Request for retrieving the current Android UI hierarchy dump.
    """
    filter: Optional[NodesFilter] = Field(
        default=None,
        description="Optional filters for selecting nodes from the dump result.",
        examples=[
            {"class_name": "Button"},
            {"text": "OK"},
            {"packageName": "com.vk.android", "contentDescription": "Search"},
        ],
    )


def getDump(request: GetDumpRequest) -> GetDumpResponse:
    try:
        xml = get_device().dump_hierarchy(compressed=False)
        nodes = parse_nodes_from_string(xml)

        if request.filter is None:
            return GetDumpResponse(
                status=True,
                error="",
                hierarchy=nodes
            )

        filtered = filter_nodes(nodes, request.filter)

        # If filtering returns empty, considering filtering only by view_class_name.
        if len(filtered) == 0 and request.filter.view_class_name is not None:
            filtered = filter_nodes(nodes, NodesFilter(
                view_class_name=request.filter.view_class_name,
            ))

        if len(filtered) == 0:
            return GetDumpResponse(
                status=True,
                error="",
                hierarchy=nodes
            )
        else:
            return GetDumpResponse(
                status=True,
                error="",
                hierarchy=filtered,
            )
    except Exception as e:
        return GetDumpResponse(
            status=False,
            error=str(e),
            hierarchy=list(),
        )


class GetAppListResponse(BaseModel):
    """Response containing the list of installed Android apps."""
    status: bool = Field(
        description="True if app list was retrieved successfully.",
        examples=[True, False],
    )
    error: str = Field(
        default="",
        description="Error message if retrieval failed; empty string on success.",
        examples=["device not connected", ""],
    )
    apps: list[str] = Field(
        description=(
            "List of package names matching the provided filter. "
            "Empty if retrieval failed."
        ),
        examples=[
            [{"com.google.android.keep", "com.duolingo", "com.google.android.apps.youtube.music"}, {}]
        ],
    )


def appList(apps_filter: str) -> GetAppListResponse:
    try:
        apps = get_device().app_list(apps_filter) if len(apps_filter) > 0 else get_device().app_list()
        return GetAppListResponse(
            status=True,
            error="",
            apps=apps,
        )
    except Exception as e:
        return GetAppListResponse(
            status=False,
            error=str(e),
            apps=[],
        )


def launchApp(pkg: str) -> BaseActionResponse:
    try:
        info = get_device().app_info(package_name=pkg)
        if not info:
            return BaseActionResponse(
                status=False,
                error="Cannot launch app '{}'.".format(pkg),
            )
        get_device().app_start(package_name=pkg)
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def pressKey(key: str) -> BaseActionResponse:
    try:
        get_device().press(key)
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def closeApp(pkg: str) -> BaseActionResponse:
    try:
        get_device().press("home")
        get_device().app_stop(pkg)
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def click(x: Union[float, int], y: Union[float, int]) -> BaseActionResponse:
    try:
        get_device().click(x, y)
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def swipe(fx, fy, tx, ty, duration: Optional[float] = None, steps: Optional[int] = None) -> BaseActionResponse:
    try:
        get_device().swipe(fx, fy, tx, ty, duration, steps)
        return BaseActionResponse(
            status=True,
            error=""
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def inputText(res_id, text: str) -> BaseActionResponse:
    try:
        get_device().xpath(res_id).set_text(text)
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )


def hideKeyboard():
    try:
        get_device().hide_keyboard()
        return BaseActionResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return BaseActionResponse(
            status=False,
            error=str(e),
        )