from typing import Union, Optional, Annotated

from mcp.server.fastmcp import FastMCP
from pydantic import Field

import tools

mcp = FastMCP("manual-automator")


@mcp.tool(
    name="get_devices_list",
    description=(
            "Retrieve the list of connected Android devices or emulators using ADB. "
            "Each device is represented by its serial number as reported by `adb devices`."
    ),
)
def devicesList() -> tools.DevicesListResponse:
    """Return a list of connected Android devices' serial numbers.

    Behavior:
    - Calls `adbutils.adb.device_list()` under the hood.
    - Returns a list of ADB serial numbers (e.g., 'emulator-5554', 'R9CT200XYZ').
    - If no devices are connected, returns an empty list.
    - If ADB is not accessible, returns an error with `status=False`.

    Use this tool to detect available devices before performing UI actions.
    """
    return tools.getDevices()


@mcp.tool(
    name="connect_device",
    description=(
            "Connect to an Android device via uiautomator2 using an optional ADB serial. "
            "Returns device info on success. Safe to call multiple times."
    ),
    structured_output=True
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
    structured_output=True
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
    structured_output=True
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
            "Retrieve the current Android UI hierarchy via uiautomator2. "
            "Returns a structured list of nodes (views) with detailed attributes. "
            "Optional filters can be applied to narrow down nodes by class, text, or resource ID."
            "As possible, always use filter, they substantially reduce tokens size."
            "Highly recommended to use view_class_name filter; Often, other secondary filters may lead to filtering errors"
    ),
    structured_output=True
)
def getDump(
        request: Annotated[
            tools.GetDumpRequest,
            Field(
                description="Request object defining dump mode and optional node filters.",
                examples=[
                    {"filter": {"view_class_name": "android.widget.Button"}},
                    {"filter": {"view_class_name": "Text"}},
                    {"filter": {"package_name": "com.google.android.apps.youtube.music",
                                "content_description": "Play"}},
                    {"filter": {"view_class_name": "Button", "resource_id": "com.example:id/login_button"}},
                    {"filter": {"view_class_name": "android.widget.TextView", "content_description": "Notifications"}},
                    {"filter": {"content_description": "Settings", "view_class_name": "TextView"}},
                    {"filter": {"text": "5", "view_class_name": "TextView"}},
                    {"filter": {"text": "Вход", "resource_id": "com.example:id/login_button"}},
                    {"filter": {"text": "Search", "resource_id": "com.example:id/search",
                                "view_class_name": "ImageView"}},
                    {"filter": {"hint": "Login", "view_class_name": "EditText"}},
                ],
            ),
        ],
) -> tools.GetDumpResponse:
    """
    Return a structured hierarchy dump of the current UI on the connected Android device.

    Behavior:
    - Uses `device.dump_hierarchy()` via uiautomator2.
    - When filters are provided, applies substring matching for text/content and
      exact/partial matching for resource IDs, classes, and packages.

    Typical uses:
    - Visual UI inspection
    - Automated QA and regression testing
    - Element discovery for interaction scripts
    """
    return tools.getDump(request)


@mcp.tool(
    name="get_app_list",
    description=(
            "Retrieve a list of installed applications on the connected Android device "
            "via uiautomator2 or ADB. Accepts optional filters controlling which apps are included. "
            "If no filter is provided, returns all installed apps."
    ),
    structured_output=True
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
    structured_output=True
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
    structured_output=True
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
    ),
    structured_output=True
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


@mcp.tool(
    name="press_key",
    description=(
            "Simulate a hardware key press on the connected Android device using uiautomator2. "
            "The key can be specified by name (e.g., 'home', 'back') or numeric key code. "
            "Useful for navigating the system or testing key events."
    ),
)
def pressKey(
        key: Annotated[
            str,
            Field(
                description=(
                        "Name or key code of the Android hardware button to press. "
                        "Supported key names include:\n"
                        "- `home`\n"
                        "- `back`\n"
                        "- `left`\n"
                        "- `right`\n"
                        "- `up`\n"
                        "- `down`\n"
                        "- `center`\n"
                        "- `menu`\n"
                        "- `search`\n"
                        "- `enter`\n"
                        "- `delete` (or `del`)\n"
                        "- `recent` (recent apps)\n"
                        "- `volume_up`\n"
                        "- `volume_down`\n"
                        "- `volume_mute`\n"
                        "- `camera`\n"
                        "- `power`\n"
                        "Alternatively, you can pass a numeric key code such as '26' for Power."
                ),
                examples=["home", "back", "power", "26"],
            ),
        ],
) -> tools.BaseActionResponse:
    """Press a hardware key on the connected Android device.

    Behavior:
    - Calls `device.press(key)` via uiautomator2.
    - Accepts both string key names and integer key codes.
    - Returns a success flag and error message if the operation fails.

    Typical use-cases:
    - Navigating back to the home screen (`home`).
    - Dismissing dialogs (`back`).
    - Adjusting volume (`volume_up`, `volume_down`).
    """
    return tools.pressKey(key)


@mcp.tool(
    name="stop_app",
    description=(
            "Force-stop a running Android application using uiautomator2. "
            "The app is identified by its package name. "
            "This tool simulates pressing the Home button first, then stops the app process via ADB."
    ),
)
def stopApp(
        pkg: Annotated[
            str,
            Field(
                description=(
                        "Full package name of the Android application to stop. "
                        "Example: 'com.google.android.youtube' or 'ru.yandex'. "
                        "Must not be empty; app must be installed and currently running."
                ),
                min_length=1,
                examples=[
                    "com.google.android.youtube",
                    "com.ru.yandex",
                    "com.duolingo",
                ],
            ),
        ],
) -> tools.BaseActionResponse:
    """Force-stop an Android application on the connected device.

    Behavior:
    - First simulates pressing the 'home' key to minimize the current app.
    - Then calls `device.app_stop(package_name)` to stop the app process completely.
    - Returns `status=True` on success, or `status=False` with an error message if stopping fails.

    Typical use-cases:
    - Closing apps after automation tests.
    - Resetting app state before the next scenario.
    - Ensuring a clean environment for UI tests.
    """
    return tools.closeApp(pkg)


@mcp.tool(
    name="input_text",
    description=(
        "Enter text into a specific input field on the connected Android device "
        "by locating it through its resource ID (XPath selector). "
        "Uses uiautomator2's XPath engine to find the element and set its text value."
    )
)
def inputText(
    res_id: Annotated[
        str,
        Field(
            description=(
                "XPath or resource ID selector of the target input field. "
                "Typically in the form `//*[@resource-id='com.example:id/username']` "
                "or `com.example:id/username`. Must uniquely identify the editable element."
            ),
            examples=[
                "//*[@resource-id='com.example:id/search_bar']",
                "com.vk.android:id/message_input",
            ],
        ),
    ],
    text: Annotated[
        str,
        Field(
            description=(
                "Text string to input into the target field. "
                "Supports Unicode characters. Existing text will be replaced."
            ),
            examples=["Hello world", "test_user123", "Поиск"],
        ),
    ],
) -> tools.BaseActionResponse:
    """Set text inside an input field on the connected Android device.

    Behavior:
    - Uses `device.xpath(res_id).set_text(text)` internally.
    - If multiple elements match the selector, the first one is used.
    - Replaces existing content in the field.
    - Returns a success flag and optional error message.

    Typical use-cases:
    - Filling login forms, search bars, or message inputs.
    - Automating form entry in test scenarios.
    """
    return tools.inputText(res_id, text)


@mcp.tool(
    name="hide_keyboard",
    description=(
        "Hide the on-screen (soft) keyboard on the connected Android device. "
        "Useful after typing text into input fields to restore full screen visibility."
    )
)
def hideKeyboard() -> tools.BaseActionResponse:
    """Hide the Android on-screen keyboard if it is currently visible.

    Behavior:
    - Calls `device.hide_keyboard()` internally via uiautomator2.
    - If the keyboard is already hidden, the operation succeeds silently.
    - Returns a success flag and an error message if the action fails.

    Typical use-cases:
    - Restoring screen visibility after text input.
    - Ensuring UI elements are not covered by the soft keyboard during automation.
    """
    return tools.hideKeyboard()

if __name__ == "__main__":
    mcp.run(transport="stdio")
