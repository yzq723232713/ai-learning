"""
Day 1 练习：Python 基础语法复习
对比 C++：Python 不需要声明类型、不需要分号、不需要编译
"""

# ========================================
# Part 1: print, 变量, 基本类型
# ========================================

# 打印（不需要 #include <iostream>，不需要 std::cout）
print("Hello, AI开发!")

# 变量（不用写 int/float/string，直接赋值）
name = "张三"          # 字符串，对应 C++ 的 std::string
age = 28               # 整数，对应 int
height = 175.5         # 浮点数，对应 double
is_learning = True     # 布尔值，注意大写 True/False

print(f"我叫{name}，{age}岁，身高{height}cm，正在学习: {is_learning}")

# type() 查看变量类型
print(type(name), type(age), type(height), type(is_learning))


# ========================================
# Part 2: 条件判断 if/elif/else
# ========================================

score = 85

if score >= 90:
    print("优秀")
elif score >= 80:
    print("良好")
elif score >= 60:
    print("及格")
else:
    print("不及格")

# Python 没有 switch-case，用 if-elif 代替


# ========================================
# Part 3: 循环 for/while
# ========================================

# for 循环（Python 的 for 跟 C++ 的 range-for 类似）
print("\n--- for 循环 ---")
for i in range(5):        # range(5) 产生 0,1,2,3,4
    print(f"第{i}次循环")

# 遍历列表（类似 C++ 的 for(auto& item : vec)）
fruits = ["苹果", "香蕉", "橘子"]
for fruit in fruits:
    print(f"我喜欢吃{fruit}")

# while 循环
print("\n--- while 循环 ---")
count = 3
while count > 0:
    print(f"倒计时: {count}")
    count -= 1           # Python 没有 count--


# ========================================
# Part 4: 列表、字典、元组、集合
# ========================================

# --- 列表 list --- （对应 C++ 的 std::vector，但可以混装不同类型）
print("\n=== 列表 ===")
my_list = [1, 2, 3, "hello", 5.5]   # 可以混类型
print("原始:", my_list)

# 增删改查
my_list.append("新元素")             # 尾部追加，类似 push_back
print("append后:", my_list)

my_list.insert(1, "插入到索引1")     # 指定位置插入
print("insert后:", my_list)

my_list.remove("hello")             # 按值删除
print("remove后:", my_list)

popped = my_list.pop()              # 弹出尾部，类似 pop_back
print(f"pop出的元素: {popped}")
print("pop后:", my_list)

print(f"索引0的元素: {my_list[0]}")  # 访问
print(f"最后一个: {my_list[-1]}")    # 负数索引从尾部开始
print(f"切片: {my_list[1:3]}")       # [1:3] 取索引1到2（不含3）

# --- 字典 dict --- （对应 C++ 的 std::unordered_map）
print("\n=== 字典 ===")
person = {
    "name": "张三",
    "age": 28,
    "skills": ["Python", "C++", "SQL"]
}
print("原始字典:", person)

print(f"姓名: {person['name']}")     # 访问
person["city"] = "北京"              # 添加新键值对
print("添加city后:", person)

print(f"所有键: {list(person.keys())}")
print(f"所有值: {list(person.values())}")

# 安全访问（键不存在时不报错）
print(person.get("salary", "未填写"))

# --- 元组 tuple --- （不可变的列表，类似 C++ 的 const vector）
print("\n=== 元组 ===")
point = (3, 4)
print(f"坐标: x={point[0]}, y={point[1]}")
# point[0] = 5  # 错误！元组不能修改

# --- 集合 set --- （无序、不重复，类似 C++ 的 std::unordered_set）
print("\n=== 集合 ===")
numbers = {1, 2, 3, 3, 2, 1}   # 重复的自动去重
print(f"集合（自动去重）: {numbers}")

a = {1, 2, 3, 4}
b = {3, 4, 5, 6}
print(f"交集: {a & b}")
print(f"并集: {a | b}")
print(f"差集: {a - b}")


# ========================================
# Part 5: 列表推导式（Python 特色，C++ 没有直接对应）
# ========================================
print("\n=== 列表推导式 ===")

# 基本用法：[表达式 for 变量 in 可迭代对象 if 条件]
squares = [x**2 for x in range(10)]
print(f"0-9的平方: {squares}")

# 带条件筛选
evens = [x*2 for x in range(10) if x % 2 == 0]
print(f"0-9中偶数的2倍: {evens}")

# 字典推导式
word_lengths = {word: len(word) for word in ["go", "python", "rust"]}
print(f"单词长度: {word_lengths}")

# 对比：不用推导式的写法
old_way = []
for x in range(10):
    if x % 2 == 0:
        old_way.append(x * 2)
print(f"传统写法结果相同: {old_way}")


# ========================================
# Part 6: 函数定义
# ========================================
print("\n=== 函数 ===")

def greet(name, greeting="你好"):
    """向用户打招呼（这是 docstring）"""
    return f"{greeting}, {name}!"

print(greet("张三"))
print(greet("李四", "早上好"))


print("\n*** Day 1 基础练习全部完成! ***")
print("下一步：看 02_cpp_to_python.py 翻译练习")
