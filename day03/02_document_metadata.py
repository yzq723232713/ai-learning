"""
Day 3 检验：用 Pydantic 定义"文档元数据"模型

要求：
1. 类名 DocumentMeta，继承 BaseModel
2. 字段：
   - file_path: str           — 文件路径
   - created_at: datetime     — 创建时间，默认当前时间
   - file_size: int           — 文件大小（字节），必须 >= 0
   - tags: List[str]          — 标签列表，默认空
   - author: Optional[str]    — 作者，可选，默认 None

3. 测试验证：
   - 可以用字典正常创建
   - created_at 不传时自动取当前时间
   - file_size 传负数时报错
   - model_dump() 能正确序列化

测试代码已写好，你的模型让下面全部通过即可。
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# ========================================
# TODO: 在这里写你的 DocumentMeta 类
# ========================================

class DocumentMeta(BaseModel):
    file_path: str
    created_at: datetime = datetime.now()
    file_size: int = Field(ge=0)
    tags: List[str] = []
    author: Optional[str] = None


# ========================================
# 测试代码（不要改下面）
# ========================================
if __name__ == "__main__":
    print("测试1: 正常创建")
    meta1 = DocumentMeta(
        file_path="/data/docs/manual.pdf",
        file_size=102400,
        tags=["手册", "产品"],
        author="张三",
    )
    print(f"  创建成功: {meta1.file_path}, {meta1.file_size}字节")
    
    print("\n测试2: created_at 不传时自动生成")
    meta2 = DocumentMeta(
        file_path="/data/docs/guide.pdf",
        file_size=51200,
    )
    print(f"  自动创建时间: {meta2.created_at}")
    print(f"  时间类型: {type(meta2.created_at).__name__}")  # 应该是 datetime
    
    print("\n测试3: author 不传时默认为 None")
    print(f"  author: {meta2.author}")  # 应该是 None
    
    print("\n测试4: tags 不传时默认为空列表")
    print(f"  tags: {meta2.tags}")  # 应该是 []
    
    print("\n测试5: model_dump() 序列化")
    d = meta1.model_dump()
    print(f"  字典 keys: {list(d.keys())}")
    print(f"  file_path: {d['file_path']}")
    
    print("\n测试6: file_size 不能为负数")
    try:
        meta3 = DocumentMeta(
            file_path="/data/bad.pdf",
            file_size=-100,
        )
        print("  错误: 应该抛出异常但没有!")
    except Exception as e:
        print(f"  正确捕获异常: {type(e).__name__}")
    
    print("\n测试7: 从字典创建（model_validate）")
    data = {
        "file_path": "/data/test.pdf",
        "file_size": 999,
    }
    meta4 = DocumentMeta.model_validate(data)
    print(f"  从字典创建成功: {meta4.file_path}")
    
    print("\n*** 全部通过！***")
