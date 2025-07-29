import jsbeautifier
from lxml import etree, html
from lxml.html import html5parser


class HtmlModifierService:
    @staticmethod
    def apply_modifications(html_content, modifications):
        """
        应用修改点到 HTML 内容
        :param html_content: 原始 HTML 字符串
        :param modifications: 修改点列表
        :return: 修改后的 HTML 字符串
        """
        # 解析 HTML 为 lxml 树
        # tree = html.fromstring(html_content)
        html5parser.html_parser = html5parser.HTMLParser(namespaceHTMLElements=False, debug=True)
        tree = html5parser.fromstring(html_content)

        # 处理每个修改点
        for mod in modifications:
            try:
                # 使用 XPath 定位节点
                nodes = tree.xpath(mod['xpath'])

                if not nodes:
                    print(f"未找到节点: {mod.get('description', '')} (XPath: {mod['xpath']})")
                    continue

                # 解析新 HTML 片段
                new_content = mod['new_html']

                # 处理多个匹配节点
                for node in nodes:
                    # 创建新节点
                    if new_content.strip().startswith('<') and new_content.strip().endswith('>'):
                        if new_content.startswith("<script>"):
                            new_node = html.fragment_fromstring(new_content, create_parent='')
                            node.getparent().replace(node, new_node)
                        else:
                            # 完整的 HTML 元素
                            new_node = html.fragment_fromstring(new_content, create_parent='div')
                            node.getparent().replace(node, new_node)
                    else:
                        # 文本内容
                        node.text = new_content

                    print(f"修改成功: {mod.get('description', '')}")

            except Exception as e:
                print(f"修改失败: {mod.get('description', '')} - {str(e)}")

        for script in tree.xpath('//script'):
            if script.text and script.get('type') in [None, 'script', 'text/javascript']:
                opts = jsbeautifier.default_options()
                opts.indent_size = 4  # 使用4空格缩进更符合Vue代码风格
                opts.brace_style = "expand"  # 强制展开大括号
                opts.preserve_newlines = True  # 保留原始换行
                script.text = jsbeautifier.beautify(script.text, opts)

        # 序列化回 HTML
        result = etree.tostring(tree, encoding='unicode', method='html', pretty_print=True)

        # 还原@click、:active、plain 属性
        result = result.replace('U00040', '@').replace('U0003A', ':').replace('=""', "")
        return result

    @staticmethod
    def apply_line_modifications(html_content, modifications):
        """
        备选方案：基于行号修改
        :param html_content: 原始 HTML 字符串
        :param modifications: 修改点列表（需包含 line_range）
        :return: 修改后的 HTML 字符串
        """
        lines = html_content.split('\n')
        line_changes = []

        for mod in modifications:
            if 'line_range' in mod:
                start, end = mod['line_range']
                new_lines = mod['new_html'].split('\n')
                line_changes.append((start, end, new_lines))

        # 按倒序执行替换避免行号偏移
        line_changes.sort(key=lambda x: x[0], reverse=True)

        for start, end, new_lines in line_changes:
            # 确保行号在有效范围内
            if 1 <= start <= len(lines) and 1 <= end <= len(lines) and start <= end:
                lines[start - 1:end] = new_lines
                print(f"行修改成功: {start}-{end}行")
            else:
                print(f"无效行范围: {start}-{end}")

        return '\n'.join(lines)