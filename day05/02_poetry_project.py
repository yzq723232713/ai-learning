"""
Day 5 检验：创建一个 poetry 项目

在 E:\learn\day05\my_project 下创建以下结构：

my_project/
├── pyproject.toml
├── .env
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py          # 用 dotenv 加载配置
│   └── greeter.py         # 一个简单的类
├── tests/
│   ├── __init__.py
│   └── test_greeter.py
└── main.py                # 入口脚本

要求：
1. 用 poetry init（或手动写 pyproject.toml）初始化项目
2. 安装 3 个依赖：pydantic、python-dotenv、pytest
3. config.py: 用 dotenv 读 .env 中的 APP_NAME 和 APP_VERSION
4. greeter.py: 一个 Greeter 类，greet() 返回 "你好，我是{app_name} v{version}"
5. main.py: 从 config 读配置，创建 Greeter，打印欢迎信息
6. test_greeter.py: 写一个 pytest 测试，验证 greet() 返回值正确
7. 用 poetry run python main.py 跑通

提示：每一步的 shell 命令如下
"""

print("""
====== 操作步骤 ======

1. 创建项目结构:
   mkdir E:\learn\day05\my_project
   mkdir E:\learn\day05\my_project\src
   mkdir E:\learn\day05\my_project\tests

2. cd 到项目目录:
   cd E:\learn\day05\my_project

3. 初始化 poetry 项目:
   poetry init --no-interaction --name my_project --description "Day5练习" --python "^3.11"

4. 添加依赖:
   poetry add pydantic python-dotenv
   poetry add --group dev pytest

5. 创建各文件（内容见下面的 TODO 区）

6. 运行:
   poetry run python main.py

7. 运行测试:
   poetry run pytest
""")
