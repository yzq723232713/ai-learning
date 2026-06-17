"""
Day 4 练习：异步编程
核心理解：同步 = 排队办事；异步 = 同时处理多个事，不等前一个完成
AI 应用每天要调几十次 LLM API，异步是必备技能
"""
import asyncio
import time

# ========================================
# Part 1: 同步 vs 异步 — 直观对比
# ========================================

print("=== Part 1: 同步 vs 异步 ===\n")

# 1.1 模拟一个耗时操作（比如调 API 等待响应）
def sync_task(name, seconds):
    print(f"  [{name}] 开始，等待 {seconds} 秒")
    time.sleep(seconds)           # 同步等待 — 期间什么都干不了
    print(f"  [{name}] 完成")
    return f"{name}的结果"

print("--- 同步执行（一个接一个）---")
start = time.time()
sync_task("任务A", 1)
sync_task("任务B", 1)
sync_task("任务C", 1)
print(f"总耗时: {time.time() - start:.1f}秒\n")   # 大约 3 秒


# 1.2 异步版本
async def async_task(name, seconds):
    print(f"  [{name}] 开始，等待 {seconds} 秒")
    await asyncio.sleep(seconds)  # await = 把控制权交出去，让别人先跑
    print(f"  [{name}] 完成")
    return f"{name}的结果"

async def run_async():
    print("--- 异步执行（同时启动）---")
    start = time.time()
    # asyncio.gather = 同时跑多个协程，等全部完成
    results = await asyncio.gather(
        async_task("任务A", 1),
        async_task("任务B", 1),
        async_task("任务C", 1),
    )
    print(f"总耗时: {time.time() - start:.1f}秒")  # 大约 1 秒！
    print(f"结果: {results}")

asyncio.run(run_async())

# 关键：3个1秒的任务，同步要3秒，异步只要1秒
# 因为三个任务同时在"等"，没有一个在空转


# ========================================
# Part 2: async/await 基础规则
# ========================================

print("\n=== Part 2: async/await 规则 ===\n")

# 规则1：async def 定义一个协程函数，调用它不会立即执行
async def say_hello():
    print("  你好")
    return "hello"

result = say_hello()       # 不执行！返回一个 coroutine 对象
print(f"  没执行，只是创建了: {type(result).__name__}")

# 规则2：必须用 await 或 asyncio.run() 才会执行
print("  用 await 执行:", end=" ")
asyncio.run(say_hello())

# 规则3：await 只能用在 async def 函数里面
async def outer():
    r = await say_hello()  # ✅ 在 async 函数里 await
    print(f"  拿到返回值: {r}")

asyncio.run(outer())

# 规则4：不能用 time.sleep()，要用 asyncio.sleep()
# time.sleep 会阻塞整个线程，async 没意义了
async def bad_example():
    # time.sleep(1)    # ❌ 会阻塞整个事件循环
    await asyncio.sleep(1)  # ✅ 

# 规则5：async 函数里可以调用同步函数，但会阻塞
async def mixed():
    print("  异步开始")
    time.sleep(0.5)          # 同步 sleep，阻塞
    print("  同步sleep完成")
    await asyncio.sleep(0.5) # 异步 sleep，不阻塞
    print("  异步sleep完成")

asyncio.run(mixed())


# ========================================
# Part 3: 常见模式
# ========================================

print("\n=== Part 3: 常见模式 ===\n")

# 模式1：create_task — 创建后台任务（不等它）
# TODO: create_task 创建的任务是"寄生"在主协程的事件循环上的，主协程退出，事件循环关闭，所有未完成的任务原地取消，使用 await task 可以等待所有任务完成
async def fire_and_forget():
    async def background(msg):
        await asyncio.sleep(2)
        print(f"  后台任务完成: {msg}")

    task = asyncio.create_task(background("发邮件"))
    print("  主流程继续，不等后台")
    await asyncio.sleep(1)
    print("  主流程结束")
    await task

asyncio.run(fire_and_forget())

# 模式2：as_completed — 谁先完成先处理谁（流式输出用这个）
# TODO：gather：全部完成后一起给你，按你传进去的顺序排列
# TODO：as_completed：谁先完事先给你，按完成顺序
async def race():
    async def worker(name, delay):
        await asyncio.sleep(delay)
        return f"{name}(耗时{delay}s)"

    print("  三个任务同时开始，谁先完成先处理谁:")
    tasks = [
        worker("慢", 0.3),
        worker("快", 0.1),
        worker("中", 0.2),
    ]
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(f"  -> 完成: {result}")

asyncio.run(race())

# 模式3：带异常处理
async def with_errors():
    async def may_fail(name, fail=False):
        await asyncio.sleep(0.1)
        if fail:
            raise ValueError(f"{name} 失败了")
        return f"{name} 成功"

    print("  处理异常:")
    results = await asyncio.gather(
        may_fail("A"),
        may_fail("B", fail=True),
        may_fail("C"),
        return_exceptions=True,  # 不抛异常，把异常当作返回值
    )
    for r in results:
        if isinstance(r, Exception):
            print(f"  异常: {r}")
        else:
            print(f"  正常: {r}")

asyncio.run(with_errors())


# ========================================
# Part 4: aiohttp — 异步 HTTP 请求
# ========================================

print("\n=== Part 4: aiohttp 异步请求 ===\n")

import aiohttp

async def fetch_url(url):
    """异步获取一个 URL 的内容"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                text = await resp.text()  # await！异步读响应体
                return url, resp.status, len(text)
    except Exception as e:
        return url, None, str(e)

async def demo_fetch():
    print("  发起3个请求（同时，不等任何一个返回）...")
    start = time.time()
    results = await asyncio.gather(
        fetch_url("https://www.baidu.com"),
        fetch_url("https://www.bing.com"),
        fetch_url("https://www.sogou.com"),
    )
    print(f"  全部完成，耗时: {time.time() - start:.2f}秒\n")
    for url, status, info in results:
        if status:
            print(f"  {url}: HTTP {status}, 响应 {info} 字符")
        else:
            print(f"  {url}: 失败 - {info}")

asyncio.run(demo_fetch())


print("\n*** Day 4 基础练习全部完成! ***")
print("下一步：看 02_async_fetch.py 完成检验练习")
