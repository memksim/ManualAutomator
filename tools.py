from dataclasses import dataclass
from typing import Any, Union, Optional
import uiautomator2 as u2
from device import set_device, get_device

@dataclass(frozen=True)
class BaseActionResponse:
    status: bool
    error: str

@dataclass(frozen=True)
class ToolResponse:
    status: bool
    info: dict[str, Any]
    error: str


def connect(serial: str) -> ToolResponse:
    try:
        d = u2.connect(serial) if len(serial) > 0 else u2.connect()
        i = d.info
        set_device(d)
        return ToolResponse(
            status=True,
            info=i,
            error="",
        )
    except Exception as e:
        return ToolResponse(
            status=False,
            info={},
            error=str(e),
        )


@dataclass(frozen=True)
class OpenNotificationsResponse:
    status: bool
    error: str


def openNotifications() -> OpenNotificationsResponse:
    try:
        get_device().open_notification()
        return OpenNotificationsResponse(
            status=True,
            error="",
        )
    except Exception as e:
        return OpenNotificationsResponse(
            status=False,
            error=str(e),
        )


@dataclass(frozen=True)
class GetDumpResponse:
    status: bool
    error: str
    hierarchy: str


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
    status: bool
    error: str
    apps: list[str]


def appList(apps_filter: str) -> GetAppListResponse:
    try:
        apps = get_device().app_list(apps_filter)
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