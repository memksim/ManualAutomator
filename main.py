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
def launchApp(package_name: str) -> tools.LaunchAppResponse:
    return tools.launchApp(package_name)

if __name__ == "__main__":
    mcp.run()
