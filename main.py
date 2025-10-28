from typing import Union, Optional, Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import tools

mcp = FastMCP("manual-automator")


@mcp.tool(
    name="connect_device",
    description=(
            "Connect to an Android device via uiautomator2 using an optional ADB serial. "
            "Returns device info on success. Safe to call multiple times."
    ),
)
def connectDevice(serial: Annotated[
    str,
    Field(
        description=(
                "ADB serial to target a specific device (e.g., 'emulator-5554'). "
                "Leave empty to auto-pick when only one device is connected."
        ),
        examples=["emulator-5554", ""],
    ),
] = "", ) -> tools.ConnectDeviceResponse:
    """Connect to an Android device using uiautomator2.

       Behavior:
       - If `serial` is provided, attempt to connect to that device.
       - If omitted, connect to the only connected device; fail if multiple are present.

       Requirements:
       - uiautomator2 must be installed and ADB-visible device(s) connected.
       """
    return tools.connect(serial)


@mcp.tool(
    name="open_notifications",
    description=(
            "Open the Android notification shade using uiautomator2. "
            "Equivalent to swiping down from the status bar. "
            "Use this to verify notifications or trigger quick actions."
    ),
)
def openNotifications() -> tools.BaseActionResponse:
    """Open the notification panel on the connected Android device.

    This tool calls `device.open_notification()` via uiautomator2.
    Safe to call multiple times — has no side effects if already open.
    """
    return tools.openNotifications()


@mcp.tool(
    name="open_quick_settings",
    description=(
            "Open the Android quick settings panel (Wi-Fi, Bluetooth, etc.) "
            "via uiautomator2. Useful for toggling or validating system state."
    ),
)
def openQuickSettings() -> tools.BaseActionResponse:
    """Open the quick settings panel on the connected Android device.

    This tool uses `device.open_quick_settings()` under the hood.
    Has no persistent effect — idempotent operation.
    """
    return tools.openQuickSettings()


@mcp.tool(
    name="get_ui_dump",
    description=(
        "Dump the current Android view hierarchy via uiautomator2. "
        "Returns an XML structure of all visible nodes on screen. "
        "When 'compressed' is true, system UI nodes (status bar, nav bar) are excluded."
    )
)
def getDump(
    compressed: Annotated[
        bool,
        Field(
            description=(
                "If true, returns a simplified (compressed) hierarchy excluding "
                "system-level nodes like status bar and navigation bar. "
                "If false, includes all nodes."
            ),
            examples=[True, False],
        ),
    ],
) -> tools.GetDumpResponse:
    """Return an XML dump of the current UI hierarchy on the connected Android device.

    Behavior:
    - Uses `device.dump_hierarchy(compressed=...)` under the hood.
    - When `compressed=True`, omits system UI nodes.
    - When `compressed=False`, returns the full raw hierarchy.

    Use this tool for visual tree inspection, automated QA, or locating view elements.
    """
    return tools.getDump(compressed)

@mcp.tool(
    name="get_app_list",
    description=(
        "Retrieve a list of installed applications on the connected Android device "
        "via uiautomator2 or ADB. Accepts optional filters controlling which apps are included. "
        "If no filter is provided, returns all installed apps."
    )
)
def getAppList(
    apps_filter: Annotated[
        str,
        Field(
            description=(
                "Filter string controlling which apps to include in the list. "
                "May be empty to include all apps. "
                "Supports the same syntax as `adb shell pm list packages`, e.g.: \n"
                "- `-f` — show associated APK file path\n"
                "- `-d` — filter to disabled apps\n"
                "- `-e` — filter to enabled apps\n"
                "- `-s` — filter to system apps\n"
                "- `-3` — filter to third-party(user) apps\n"
                "- `-i` — show installer package name\n"
                "- `-u` — include uninstalled packages\n"
                "- `--user USER_ID` — query for a specific user\n"
                "- `FILTER` — partial string match (e.g. 'com.google.')"
            ),
            examples=["-3", "--user 0 com.google.", ""],
        ),
    ] = "",
) -> tools.GetAppListResponse:
    """Retrieve a list of installed apps on the connected Android device.

    Behavior:
    - If `apps_filter` is empty, returns all installed packages.
    - If a filter is specified, applies it using the same semantics as `adb shell pm list packages`.
    - Output includes package names only.

    Useful for automation scripts, QA validation, or app inventory collection.
    """
    return tools.appList(apps_filter)


@mcp.tool(
    name="launch_app",
    description=(
        "Launch an installed Android application by its package name "
        "using uiautomator2. Fails if the package is not found or cannot be started."
    ),
)
def launchApp(
    package_name: Annotated[
        str,
        Field(
            description=(
                "Full package name of the Android app to launch. "
                "Must not be empty. Example: 'com.google.android.apps.youtube.music'."
            ),
            min_length=1,
            examples=[
                "com.google.android.apps.youtube.music",
                "com.vk.android",
                "com.android.settings",
            ],
        ),
    ],
) -> tools.BaseActionResponse:
    """Launch an application on the connected Android device.

    This tool wraps `device.app_start(package_name=...)` via uiautomator2.

    Behavior:
    - Checks if the app is installed using `device.app_info()`.
    - Returns an error if not found or failed to start.
    - Otherwise, launches the app in the foreground.

    Use this for functional testing or automation of app startup flows.
    """
    return tools.launchApp(package_name)


@mcp.tool(
    name="click",
    description=(
        "Perform a tap gesture at the specified screen coordinates using uiautomator2. "
        "Useful for precise element interaction when accessibility selectors are unavailable."
    ),
)
def click(
    x: Annotated[
        Union[float, int],
        Field(
            description="X coordinate of the tap on screen in pixels.",
            examples=[120, 640.5],
        ),
    ],
    y: Annotated[
        Union[float, int],
        Field(
            description="Y coordinate of the tap on screen in pixels.",
            examples=[480, 1280.2],
        ),
    ],
) -> tools.BaseActionResponse:
    """Simulate a single tap gesture at the specified screen coordinates.

    Behavior:
    - Equivalent to `device.click(x, y)` in uiautomator2.
    - Coordinates are in absolute screen pixels.
    - Returns success or failure status.

    Use this when element-based selectors are unavailable.
    """
    return tools.click(x, y)


@mcp.tool(
    name="swipe",
    description=(
        "Perform a swipe gesture on the connected Android device "
        "from one coordinate to another using uiautomator2. "
        "Either 'duration' or 'steps' can control swipe speed, but not both."
    )
)
def swipe(
    fx: Annotated[
        int,
        Field(
            description="Start X coordinate (in screen pixels).",
            examples=[100, 640.5],
        ),
    ],
    fy: Annotated[
        int,
        Field(
            description="Start Y coordinate (in screen pixels).",
            examples=[800, 550.1],
        ),
    ],
    tx: Annotated[
        int,
        Field(
            description="End X coordinate (in screen pixels).",
            examples=[100, 99.7],
        ),
    ],
    ty: Annotated[
        int,
        Field(
            description="End Y coordinate (in screen pixels).",
            examples=[200, 100.8],
        ),
    ],
    duration: Annotated[
        Optional[float],
        Field(
            default=None,
            description=(
                "Swipe duration in seconds. "
                "Defines total gesture time. "
                "Cannot be used together with 'steps'. "
                "If both are provided, 'duration' will be ignored and a warning issued."
            ),
            examples=[0.3, None],
        ),
    ] = None,
    steps: Annotated[
        Optional[int],
        Field(
            default=None,
            description=(
                "Number of move steps sent to the system. "
                "Use this to control swipe speed instead of 'duration'. "
                "Cannot be set together with 'duration'. "
                "Recommended when you need deterministic behavior."
            ),
            examples=[10, 20, None],
        ),
    ] = None,
) -> tools.BaseActionResponse:
    """Swipe gesture from (fx, fy) to (tx, ty) on the connected Android device.

    Behavior:
    - Executes `device.swipe(fx, fy, tx, ty, steps=...)` internally.
    - If both `duration` and `steps` are provided, `duration` is ignored and a warning is raised.
    - If `duration` is provided, steps are computed as `duration * 200`.
    - If neither is provided, uses a default constant (e.g., `SCROLL_STEPS`).

    Typical use-cases:
    - Scrolling screens
    - Simulating drag gestures
    """
    return tools.swipe(fx, fy, tx, ty, duration, steps)

if __name__ == "__main__":
    mcp.run(transport="stdio")
