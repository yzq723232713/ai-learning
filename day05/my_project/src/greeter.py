"""一个简单的 Greeter 类"""

class Greeter:
    def __init__(self, app_name: str, app_version: str):
        self.app_name = app_name
        self.app_version = app_version

    def greet(self) -> str:
        return f"你好，我是{self.app_name} v{self.app_version}"
