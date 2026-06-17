"""
Day 4 检验：用 asyncio.gather 同时请求 3 个 URL，打印响应长度

要求：
1. 定义 async def fetch_url(url) 函数
   - 用 aiohttp.ClientSession 发 GET 请求
   - 返回 (url, 响应长度(字符数), HTTP状态码)
   - 请求失败时返回 (url, 0, 错误信息)

2. 定义 async def main() 函数
   - 用 asyncio.gather 同时请求3个URL
   - 打印每个URL的结果

3. 用 asyncio.run(main()) 启动

测试 URL（选3个你喜欢的，比如）：
- https://www.baidu.com
- https://www.bilibili.com
- https://www.zhihu.com
"""

import asyncio
import aiohttp
import time

# ========================================
# TODO: 在这里写你的代码
# ========================================

async def main():
    async with aiohttp.ClientSession() as session:
        async def fetch_url(url):
            try:
                async with session.get(url, timeout=10) as resp:
                    text = await resp.text()
                    return url, len(text), 200
            except Exception as e:
                return url, None, 404
        
        results = await asyncio.gather(
            fetch_url("https://www.baidu.com"),
            fetch_url("https://www.bing.com"),
            fetch_url("https://www.sogou.com"),
            fetch_url("https://this-does-not-exist-xyz.com")
        )

    for url, textlen, status in results:
        if status == 200:
            print(url, textlen, status)
        else:
            print(url, status)
    

if __name__ == "__main__":
    asyncio.run(main())
