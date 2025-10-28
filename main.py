from typing import Union, Optional

from mcp.server.fastmcp import FastMCP

import tools

mcp = FastMCP("Demo")


@mcp.tool()
def connect(serial: str) -> tools.ToolResponse:
    return tools.connect(serial)


@mcp.tool()
def openNotifications() -> tools.OpenNotificationsResponse:
    return tools.openNotifications()

@mcp.tool()
def getDump(compressed: bool) -> tools.GetDumpResponse:
    return tools.getDump(compressed)

@mcp.tool()
def getAppList(apps_filter: str) -> tools.GetAppListResponse:
    """
    :param apps_filter: [-f] [-d] [-e] [-s] [-3] [-i] [-u] [--user USER_ID] [FILTER]
    """
    return tools.appList(apps_filter)

@mcp.tool()
def launchApp(package_name: str) -> tools.BaseActionResponse:
    return tools.launchApp(package_name)

@mcp.tool()
def click(x: Union[float, int], y: Union[float, int]) -> tools.BaseActionResponse:
    return tools.click(x, y)

@mcp.tool()
def swipe(fx, fy, tx, ty, duration: Optional[float] = None, steps: Optional[int] = None) -> tools.BaseActionResponse:
    return tools.swipe(fx, fy, tx, ty, duration, steps)

if __name__ == "__main__":
    mcp.run()
