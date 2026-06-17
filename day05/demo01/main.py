"""入口脚本：从配置读取信息，创建 Greeter，打印欢迎信息"""
import sys
sys.path.insert(0, "E:/learn/day05/my_project/src")

from config import APP_NAME, APP_VERSION
from greeter import Greeter

def main():
    g = Greeter(APP_NAME, APP_VERSION)
    print(g.greet())

if __name__ == "__main__":
    main()
