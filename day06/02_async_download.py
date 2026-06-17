"""
Day 6 检验2：异步下载

综合 Day4(异步) + Day5(工程化)

要求：
用 asyncio + aiohttp 同时下载 3 个文件，保存到本地。
打印每个文件的下载耗时和大小。

你的任务：实现 download_all() 函数
"""
import asyncio
import aiohttp
import time
from pathlib import Path


async def download_one(session: aiohttp.ClientSession, url: str, save_dir: str):
    """
    下载单个文件

    参数:
        session: 共享的 aiohttp 连接池（不要在这里创建新的）
        url: 文件 URL
        save_dir: 保存目录

    返回:
        (filename, size_bytes, elapsed_seconds, error)

    提示:
    - 用 url.split("/")[-1] 取文件名
    - 用 resp.content.read() 读二进制内容
    - 用 async with session.get(url) as resp:
    """
    
    start = time.time()
    filename = url.split("/")[-1]

    try:
        async with session.get(url, timeout=30) as resp:
            content = await resp.content.read()
            Path(save_dir, filename).write_bytes(content)
            elapsed = time.time() - start
            size_kb = len(content) / 1024
            return filename, len(content), elapsed, None
    except Exception as e:
        return filename, 0, time.time() - start, str(e)

async def download_all(urls: list, save_dir: str):
    """
    并发下载多个文件

    提示:
    - 只创建一个 ClientSession，所有 download_one 共享
    - 用 asyncio.gather() 并发执行
    - 打印总耗时和每个文件的结果
    """
    print(f"开始下载 {len(urls)} 个文件...\n")
    start = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = [download_one(session, url, save_dir) for url in urls]
        results = await asyncio.gather(*tasks)

    for filename, size, elapsed, error in results:
        if error:
            print(f"❌ {filename}: {error}")
        else:
            print(f"✅ {filename}: {size/1024:.1f} KB, 耗时 {elapsed:.2f}秒")

    print(f"\n全部完成，总耗时: {time.time() - start:.2f}秒")



# ========================================
# 测试
# ========================================
if __name__ == "__main__":
    save_dir = "E:/learn/day06/downloads"
    Path(save_dir).mkdir(exist_ok=True)

    # 3个小文件用于练习
    urls = [
        "https://www.python.org/static/img/python-logo.png",
        "https://www.python.org/static/community_logos/python-powered-h-140x182.png",
        "https://www.python.org/static/img/psf-logo.png",
    ]

    asyncio.run(download_all(urls, save_dir))
