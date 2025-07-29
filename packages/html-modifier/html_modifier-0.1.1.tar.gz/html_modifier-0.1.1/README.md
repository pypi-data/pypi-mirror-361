# MCP HTML修改

## 功能说明

针对大模型生成的长HTML代码时存在语法错误，提供精准修改能力。

## 示例

```json
"<div class=\"container\">原始HTML内容</div>"
```

```json
[
  {
    "description": "替换容器类名",
    "xpath": "//div[@class='container']",
    "new_html": "<section class=\"main-content\" :active>新内容</section>"
  }
]
```

## 参数说明

### 函数名 `modify_html`

| 参数名             | 类型     | 父级            | 说明          |
|-----------------|--------|---------------|-------------|
| `html`          | string |               | 原始HTML模板字符串 |
| `modifications` | array  |               | 修改任务列表      |
| `description`   | string | modifications | 修改描述（调试用）   |
| `xpath`         | string | modifications | XML路径定位符    |
| `new_html`      | string | modifications | 替换后的HTML片段  |

## 注意事项

1. 确保XPath表达式符合XML规范
2. Vue模板语法只是简单字符串替换
3. 设置环境变量`DANGEROUSLY_OMIT_AUTH=True`