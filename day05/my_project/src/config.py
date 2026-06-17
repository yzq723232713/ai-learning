"""加载项目配置，从 .env 文件和系统环境变量读取"""
import os
from dotenv import load_dotenv

# 加载项目根目录的 .env 文件
load_dotenv()

# 读取配置项，提供默认值
APP_NAME = os.getenv("APP_NAME", "未知应用")
APP_VERSION = os.getenv("APP_VERSION", "0.0.0")
