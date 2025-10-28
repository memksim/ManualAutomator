from dataclasses import dataclass
from pydantic import Field
from typing import Any, Union, Optional
import uiautomator2 as u2
from device import set_device, get_device


@dataclass(frozen=True)
class BaseActionResponse:
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


@dataclass(frozen=True)
class ConnectDeviceResponse:
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


@dataclass(frozen=True)
class GetDumpResponse:
    """Response containing the UI hierarchy dump."""
    status: bool = Field(
        description="True if hierarchy dump was retrieved successfully.",
        examples=[True, False],
    )
    error: str = Field(
        default="",
        description="Error message if dump failed; empty string when successful.",
        examples=["device not connected", ""],
    )
    hierarchy: str = Field(
        description=(
            "Serialized XML string representing the current view hierarchy "
            "as returned by uiautomator2. "
            "Empty if dump failed."
        ),
        examples=[
            "<?xml version='1.0' encoding='UTF-8' standalone='yes' ?><hierarchy rotation=\"0\"><node index=\"0\" ... /></hierarchy>",
            "",
        ],
    )


def getDump(compressed: bool) -> GetDumpResponse:
    try:
        xml = get_device().dump_hierarchy(compressed=compressed)
        return GetDumpResponse(
            status=True,
            error="",
            hierarchy=xml,
        )
    except Exception as e:
        return GetDumpResponse(
            status=False,
            error=str(e),
            hierarchy="",
        )


@dataclass(frozen=True)
class GetAppListResponse:
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
