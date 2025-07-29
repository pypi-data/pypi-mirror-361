# server.py
from mcp.server.fastmcp import FastMCP

from core.html_modifier import HtmlModifierService

# Create an MCP server
mcp = FastMCP("html_modifier")


# 修改html
@mcp.tool()
def modify_html(html: str, modifications) -> str:
    """
    精准修改html

    :param html:html_str
    :param modifications: [{"description": "...","xpath": "...","new_html": "..."}]
    :return: html_str
    """

    return HtmlModifierService.apply_modifications(html, modifications)


def main():
    mcp.run()


if __name__ == "__main__":
    mcp.run()
