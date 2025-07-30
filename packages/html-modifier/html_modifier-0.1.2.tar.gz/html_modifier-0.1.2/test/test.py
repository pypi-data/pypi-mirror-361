# test
from src.html_modifier.html_modifier_service import HtmlModifierService

result = HtmlModifierService.apply_modifications(
    "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>企业级管理后台 - 项目构建</title><link rel=\"stylesheet\" href=\"https://unpkg.com/element-ui/lib/theme-chalk/index.css\"><script src=\"https://cdn.jsdelivr.net/npm/vue@2.6.14/dist/vue.js\"></script><script src=\"https://unpkg.com/element-ui/lib/index.js\"></script><div class=\"container\">原始HTML内容</div></body></html>",

    [
        {
            "description": "替换容器类名",
            "xpath": "//div[@class='container']",
            "new_html": "<section class=\"main-content\" @click=\"modifyContent\" :active>新内容</section>"
        }
    ]
)

# 使用 with 语句自动管理文件资源
with open("./test_page.html", "w", encoding="utf-8") as file:
    # 将字符串写入文件
    file.write(result)

print("已保存test_page.html")

print()

print(result)
