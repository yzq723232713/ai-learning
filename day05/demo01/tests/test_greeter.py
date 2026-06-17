"""测试 Greeter 类"""
import sys
sys.path.insert(0, "E:/learn/day05/my_project/src")

from greeter import Greeter


def test_greet():
    g = Greeter("测试应用", "1.0")
    assert g.greet() == "你好，我是测试应用 v1.0"


def test_greet_with_real_config():
    """用真实配置测试"""
    from config import APP_NAME, APP_VERSION
    g = Greeter(APP_NAME, APP_VERSION)
    result = g.greet()
    assert APP_NAME in result
    assert APP_VERSION in result
