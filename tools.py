from dataclasses import dataclass
from typing import Any
import uiautomator2 as u2
from device import set_device, get_device


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


def getDump() -> GetDumpResponse:
    try:
        xml = get_device().dump_hierarchy()
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