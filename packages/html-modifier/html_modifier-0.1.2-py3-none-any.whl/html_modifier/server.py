# server.py
from mcp.server.fastmcp import FastMCP

from html_modifier.html_modifier_service import HtmlModifierService

# Create an MCP server
mcp = FastMCP("html-modifier")


# 存储html
@mcp.tool()
def save_html(html: str, key: str) -> str:
    """
    存储html，并返回一个key，这样需要输出html或者调用mcp时，只需要用这个key，而不需要大费周章地输出或者传递整个html

    :param html:html_str
    :param key:用于查找html的key
    :return:返回一个能查询到html的key
    """

    return HtmlModifierService.save_html(html, key)


# 导出html到文件
@mcp.tool()
def export_html_to_file(key: str, path: str) -> bool:
    """
    将key对应的html内容导出到文件
    :param key: key
    :param path: 目标文件路径
    :return: 成功返回 True，失败返回 False
    """
    return HtmlModifierService.export_html(key, path)


# 修改html
@mcp.tool()
def modify_html(html: str, modifications) -> str:
    """
    精准修改html，需要传递html，以及一个json数组，更费力

    :param html:html_str
    :param modifications: [{"description": "...","xpath": "...","new_html": "..."}]
    :return: html_str
    """

    return HtmlModifierService.apply_modifications(html, modifications)


# 通过key修改html
@mcp.tool()
def modify_html_by_key(key: str, modifications) -> str:
    """
    精准修改html，但是只需要传递之前存储html时的key，以及一个json数组，更省力

    :param key: 之前存储html返回的key
    :param modifications: [{"description": "...","xpath": "...","new_html": "..."}]
    :return: 提示修改成功或失败，不会返回html
    """

    return HtmlModifierService.apply_modifications_by_key(key, modifications)


def run():
    mcp.run(transport='stdio')


if __name__ == '__main__':
    run()
