"""
Day 16：Chunking（文本切分）— RAG 检索质量的命门

为什么切分？
  1. 模型上下文窗口有限（切太大塞不下）
  2. 小块检索精度更高（海量文档中精准找到相关片段）

三种策略今天都手写一遍。
"""
from typing import List
from pydantic import BaseModel


class Chunk(BaseModel):
    """切好的文本块"""
    text: str               # 块内容
    index: int              # 块序号
    char_start: int         # 在原文档中的起始位置
    char_end: int           # 在原文档中的结束位置


# ========================================
# 准备测试文本（模拟一篇长文档）
# ========================================

# 一份模拟的产品手册，约 1500 字
SAMPLE_TEXT = """
智能温控器 X-100 产品手册

第一章 产品概述

智能温控器 X-100 是一款面向家庭和办公场景的智能温度控制设备。
该产品支持Wi-Fi连接，可通过手机APP远程控制室内温度。
产品采用高精度温度传感器，精度可达±0.5°C。外壳采用阻燃材料，
符合国家3C认证标准。设备支持7x24小时持续工作。

第二章 技术参数

工作电压：AC 220V±10%，50Hz。额定功率：3W。温度设定范围：
5°C至35°C。工作环境温度：-10°C至50°C。无线协议：Wi-Fi
802.11 b/g/n，2.4GHz。显示屏：2.4英寸LCD彩色屏幕。传感器
类型：NTC热敏电阻，精度±0.5°C。

第三章 安装指南

3.1 安装前准备

在安装设备之前，请确保墙面平整干燥，周围无强磁场干扰源。
需要准备的工具：十字螺丝刀一把、电钻及6mm钻头、水平尺一把。

3.2 安装步骤

第一步，使用水平尺在墙面标记安装位置，确保水平。第二步，用电钻
在标记位置打孔，深度约35mm。第三步，将膨胀螺栓插入孔中。第四步，
将设备背板对准螺栓固定。第五步，连接电源线：火线接L端子，零线
接N端子，地线接PE端子。注意：接线前务必断开总电源！

3.3 APP连接设置

安装完成后，打开手机蓝牙和Wi-Fi。下载"智能家"APP，注册账号。
点击"添加设备"，选择"温控器X-100"。按照屏幕提示完成设备配对。
配对成功后，即可在APP中设置温度、查看能耗统计、设置定时开关机。

第四章 使用说明

4.1 基本操作

设备正面有3个触摸按键：模式切换键、温度上调键、温度下调键。长按
模式切换键3秒进入设置菜单。短按温度键每次调整0.5°C，长按连续调整。

4.2 智能模式

设备支持三种智能模式：恒温模式（保持设定温度不变）、节能模式
（自动调节以降低能耗）、睡眠模式（夜间自动微调温度，舒适助眠）。

4.3 语音控制

本设备支持接入主流智能音箱，包括小爱同学、天猫精灵。绑定方法：
在智能音箱APP中搜索"智能温控器X-100"，按照提示完成授权。

第五章 常见问题

问题一：设备显示"E01"错误代码。
原因：温度传感器故障。解决方案：断电重启设备，若问题依然存在，
请联系售后服务。

问题二：Wi-Fi连接不稳定。
原因：路由器距离过远或墙体阻挡信号。解决方案：将路由器移至距离
设备5米以内，或增加Wi-Fi信号中继器。

问题三：APP显示设备离线。
原因：设备与路由器断开连接。解决方案：检查路由器是否正常工作，
在设备上长按模式键10秒恢复出厂设置，重新配对。

问题四：设备按键无反应。
原因：触摸面板被水渍或油污覆盖。解决方案：用柔软的干布清洁面板。

第六章 保修条款

本产品自购买之日起享受2年免费保修服务。保修范围包括主机硬件故障。
以下情况不在保修范围：人为损坏、自行拆解、进水、雷击等不可抗力
因素造成的损坏。售后服务热线：400-888-XXXX。

附录A 产品规格速查表

型号：X-100。尺寸：120mm×80mm×25mm。重量：180g。颜色：白色。
包装内容：主机×1、安装螺丝×2、膨胀螺栓×2、说明书×1、保修卡×1。
"""

print(f"测试文档长度: {len(SAMPLE_TEXT)} 字符\n")


# ========================================
# 策略1: 固定长度切分（最简单）
# ========================================

print("=== 策略1: 固定长度切分 ===\n")

def chunk_by_fixed_size(text: str, chunk_size: int = 200, overlap: int = 30) -> List[Chunk]:
    """
    每 chunk_size 字切一块，相邻块重叠 overlap 字。
    重叠的作用：防止关键信息刚好在边界上被切开。
    """
    chunks = []
    start = 0
    index = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunks.append(Chunk(
            text=chunk_text,
            index=index,
            char_start=start,
            char_end=end,
        ))
        index += 1
        next_start = end - overlap
        if next_start <= start:     # 防止死循环：最后一块太小，不重叠了
            break
        start = next_start

    return chunks


fixed_chunks = chunk_by_fixed_size(SAMPLE_TEXT)
print(f"块数: {len(fixed_chunks)}")
print(f"平均块大小: {sum(len(c.text) for c in fixed_chunks) / len(fixed_chunks):.0f} 字符")
print(f"重叠量: 30 字符\n")

# 展示前3块
for c in fixed_chunks[:3]:
    preview = c.text[:80].replace("\n", " ")
    print(f"  块{c.index}: [{c.char_start}-{c.char_end}] \"{preview}...\"")
print()

# 展示重叠：看块0的结尾和块1的开头
print("重叠验证（块0的末尾 vs 块1的开头）:")
print(f"  块0结尾: ...{fixed_chunks[0].text[-50:]}")
print(f"  块1开头: {fixed_chunks[1].text[:50]}...")


# ========================================
# 策略2: 按分隔符切分（语义优先）
# ========================================

print("\n\n=== 策略2: 按分隔符切分 ===\n")

def chunk_by_separator(text: str, separator: str = "\n\n", max_chunk_size: int = 500) -> List[Chunk]:
    """
    先按自然段落（\\n\\n）切分。
    如果某段太长，再降级用句子（。）切分。
    如果还是太长，再降级用固定长度切分。
    """
    # 第1级：按段落切
    paragraphs = text.split(separator)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    chunks = []
    index = 0
    pos = 0  # 跟踪在原文本中的位置

    for para in paragraphs:
        if len(para) <= max_chunk_size:
            # 段落够短，直接作为一个块
            start_pos = text.index(para, pos) if para in text[pos:] else pos
            chunks.append(Chunk(
                text=para,
                index=index,
                char_start=start_pos,
                char_end=start_pos + len(para),
            ))
            index += 1
            pos = start_pos + len(para)
        else:
            # 段落太长，降级按句子切
            sentences = para.replace("。", "。\n").split("\n")
            sentences = [s.strip() for s in sentences if s.strip()]

            for sent in sentences:
                if len(sent) <= max_chunk_size:
                    start_pos = text.index(sent, pos) if sent in text[pos:] else pos
                    chunks.append(Chunk(
                        text=sent,
                        index=index,
                        char_start=start_pos,
                        char_end=start_pos + len(sent),
                    ))
                    index += 1
                    pos = start_pos + len(sent)
                else:
                    # 单句还太长，硬切（罕见情况）
                    for i in range(0, len(sent), max_chunk_size):
                        sub = sent[i:i + max_chunk_size]
                        chunks.append(Chunk(
                            text=sub,
                            index=index,
                            char_start=0,  # 粗略
                            char_end=0,
                        ))
                        index += 1

    return chunks


sep_chunks = chunk_by_separator(SAMPLE_TEXT)
print(f"块数: {len(sep_chunks)}")
print(f"平均块大小: {sum(len(c.text) for c in sep_chunks) / len(sep_chunks):.0f} 字符")
print(f"最大块: {max(len(c.text) for c in sep_chunks)} 字符，最小块: {min(len(c.text) for c in sep_chunks)} 字符\n")

for c in sep_chunks[:5]:
    preview = c.text[:80].replace("\n", " ")
    print(f"  块{c.index}: {len(c.text)}字 \"{preview}...\"")


# ========================================
# 策略3: 递归切分（实际工程最常用）
# ========================================

print("\n\n=== 策略3: 递归切分 ===\n")

def chunk_recursive_simple(text: str, chunk_size: int = 300, separators: List[str] = None) -> List[Chunk]:
    """
    递归切分的简化实现，展示核心思路：
    依次尝试各种分隔符，切出来的片段尽量不超 chunk_size。
    """
    if separators is None:
        separators = ["\n\n", "\n", "。", " "]

    # 第1步：优先按段落切
    chunks = _split_by_seps(text, separators, chunk_size)

    # 第2步：检查超长块，硬切
    result = []
    idx = 0
    for chunk_text in chunks:
        if len(chunk_text) <= chunk_size:
            result.append(Chunk(text=chunk_text, index=idx, char_start=0, char_end=0))
            idx += 1
        else:
            # 超长块硬切
            for i in range(0, len(chunk_text), chunk_size):
                result.append(Chunk(
                    text=chunk_text[i:i + chunk_size],
                    index=idx,
                    char_start=0, char_end=0,
                ))
                idx += 1
    return result


def _split_by_seps(text: str, separators: List[str], max_size: int) -> List[str]:
    """逐个试分隔符，一旦某个分隔符能切出不过长的片段就停"""
    if not separators:
        return [text]

    sep = separators[0]
    if sep not in text:
        return _split_by_seps(text, separators[1:], max_size)

    pieces = text.split(sep)
    pieces = [p for p in pieces if p.strip()]

    # 检查是否所有片段都不超过限制
    if all(len(p) <= max_size for p in pieces):
        return pieces

    # 有太长的片段，继续用下一个分隔符
    result = []
    for p in pieces:
        if len(p) <= max_size:
            result.append(p)
        else:
            result.extend(_split_by_seps(p, separators[1:], max_size))
    return result


rec_chunks = chunk_recursive_simple(SAMPLE_TEXT, chunk_size=300)
print(f"块数: {len(rec_chunks)}")
print(f"平均块大小: {sum(len(c.text) for c in rec_chunks) / max(len(rec_chunks), 1):.0f} 字符\n")

for c in rec_chunks:
    preview = c.text[:80].replace("\n", " ")
    print(f"  块{c.index}: {len(c.text)}字 \"{preview}...\"")


# ========================================
# 三种策略对比
# ========================================

print("\n\n=== 三种策略对比 ===\n")

print(f"{'策略':<16s} {'块数':<6s} {'平均大小':<10s} {'语义完整性':<12s} {'复杂度'}")
print("-" * 60)
print(f"{'固定长度':<16s} {len(fixed_chunks):<6d} {sum(len(c.text) for c in fixed_chunks)/len(fixed_chunks):<10.0f} {'差（会截断）':<12s} {'低'}")
print(f"{'按分隔符':<16s} {len(sep_chunks):<6d} {sum(len(c.text) for c in sep_chunks)/len(sep_chunks):<10.0f} {'好':<12s} {'中'}")
print(f"{'递归切分':<16s} {len(rec_chunks):<6d} {sum(len(c.text) for c in rec_chunks)/max(len(rec_chunks),1):<10.0f} {'好':<12s} {'中'}")

print("\n实际工程中：")
print("  - 一般文档用「递归切分」（LangChain默认方案）")
print("  - 表格/CSV 用「按分隔符」（按行切）")
print("  - 代码用「按分隔符 + 固定长度」（按函数/类切，超长函数硬截）")


print("\n\n*** Day 16 基础练习全部完成! ***")
print("\n关键结论：")
print("  1. Chunking 策略直接影响检索质量——切太碎没上下文，切太大不精准")
print("  2. Overlap 防止关键信息被切断（30-50字常用）")
print("  3. 递归切分是最实用的方案：先按段落→句子→逗号→硬切")
print("  4. Chunk 保留 index/char_start/char_end，后续可追溯回原文")
