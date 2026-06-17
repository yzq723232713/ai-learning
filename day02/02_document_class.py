"""
Day 2 检验：用类封装一个"文档对象"

要求：
1. 类名 Document
2. 属性：title（标题）、content（正文）、tags（标签列表）、created_at（创建时间）
3. 方法：
   - add_tag(tag)：添加一个标签，重复的标签不添加
   - remove_tag(tag)：移除一个标签
   - summary(n)：返回正文的前 n 个字符 + "..."
   - __str__：返回 "标题: xxx | 标签: xxx, xxx"
   - __len__：返回正文长度

测试用例写在下面，你的代码让这些测试全部通过即可。
"""

# ========================================
# TODO: 在这里写你的 Document 类
# ========================================
from datetime import datetime
# from datetime import datetime 已经帮你写好了

class Document:
    def __init__(self, title, content, tags=None):
        self.title = title
        self.content = content
        self.tags = tags if tags is not None else []
        self.created_at = datetime.now()

    def add_tag(self, tag):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag):
        if tag in self.tags:
            self.tags.remove(tag)

    def summary(self, n=20):
        if len(self.content) <= n:
            return self.content
        return self.content[:n] + "..."
    
    @property
    def title(self):
        print("获取标题")
        return self._title
    
    @title.setter
    def title(self, value):
        if len(value) > 10:
            raise ValueError("标题长度不能大于10")
        print("设置标题为：", value)
        self._title = value 
        
    def __str__(self):
        tags_str = ", ".join(self.tags)
        return f"标题：{self._title} | 标签：{tags_str}"
    
    def __len__(self):
        return len(self.content)


# ========================================
# 测试代码（不要改下面）
# ========================================
if __name__ == "__main__":
    # 创建文档
    doc = Document(
        title="Python学习笔记",
        content="Python是一种解释型语言。语法简洁，适合快速开发。拥有丰富的第三方库。",
        tags=["编程", "Python"]
    )
    
    # 测试 __str__
    print(doc)  # 应该输出: 标题: Python学习笔记 | 标签: 编程, Python
    
    # 测试 add_tag
    doc.add_tag("学习")
    doc.add_tag("Python")  # 重复的，不添加
    print(f"标签: {doc.tags}")  # 应该是 ['编程', 'Python', '学习']
    
    # 测试 remove_tag
    doc.remove_tag("编程")
    print(f"删除后: {doc.tags}")  # 应该是 ['Python', '学习']
    
    # 测试 summary
    print(f"摘要: {doc.summary(10)}")  # 应该是 "Python是一种解释型语..."
    
    # 测试 __len__
    print(f"正文长度: {len(doc)}")  # 应该是30（取决于你的正文）
    
    # 测试 created_at
    print(f"创建时间: {doc.created_at}")

    # 测试 @property
    print(f"标题为：{doc.title}")
    
    print("\n全部通过说明你掌握了 Day 2 的核心内容!")
