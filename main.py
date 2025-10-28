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
def getDump() -> tools.GetDumpResponse:
    return tools.getDump()

if __name__ == "__main__":
    mcp.run()
