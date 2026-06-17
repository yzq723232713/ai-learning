"""
Day 2 练习：函数与面向对象
对比 C++：Python 的 class 更灵活，没有 private/public 关键字（靠约定）
"""

# ========================================
# Part 1: 函数参数（C++ 没有这么丰富的参数机制）
# ========================================

print("=== Part 1: 函数参数 ===\n")

# 1.1 位置参数（最普通，跟 C++ 一样）
def add(a, b):
    return a + b

print("位置参数:", add(3, 5))            # 8


# 1.2 默认参数（类似 C++ 的默认参数 void func(int a=10)）
def greet(name, greeting="你好"):
    return f"{greeting}, {name}!"

print("默认参数:", greet("张三"))         # 你好, 张三!
print("覆盖默认:", greet("李四", "嗨"))   # 嗨, 李四!


# 1.3 关键字参数（调用时写参数名，可以不按顺序）
def describe(name, age, city):
    return f"{name}, {age}岁, 来自{city}"

print("关键字参数:", describe(city="北京", age=28, name="王五"))


# 1.4 *args — 接收任意多个位置参数（打包成元组）
def sum_all(*args):
    print(f"  收到了 {len(args)} 个参数: {args}")
    return sum(args)

print("*args:", sum_all(1, 2, 3, 4, 5))  # 15


# 1.5 **kwargs — 接收任意多个关键字参数（打包成字典）
def build_config(**kwargs):
    for key, value in kwargs.items():
        print(f"  {key} = {value}")

print("**kwargs:")
build_config(host="localhost", port=8080, debug=True)


# 1.6 组合使用（顺序必须是：位置 → *args → 关键字 → **kwargs）
def full_signature(name, *scores, grade="A", **extra):
    print(f"姓名: {name}")
    print(f"成绩: {scores}")
    print(f"等级: {grade}")
    print(f"其他: {extra}")

print("\n组合参数:")
full_signature("张三", 85, 92, 78, grade="B", city="北京", age=28)


# ========================================
# Part 2: lambda 匿名函数（C++ 的 lambda [](){} 差不多）
# ========================================

print("\n=== Part 2: lambda ===\n")

# 普通函数写法
def square(x):
    return x * x

# lambda 写法：lambda 参数: 返回值
square_lambda = lambda x: x * x

print("普通:", square(5))
print("lambda:", square_lambda(5))

# lambda 真正的用途：当场定义一个短函数传给别的东西
numbers = [1, 5, 3, 8, 2]
# sorted 的 key 参数需要一个函数，lambda 当场给一个
sorted_by_last_digit = sorted(numbers, key=lambda x: x % 10)
print("按个位数排序:", sorted_by_last_digit)

# map + lambda：对每个元素做操作
doubled = list(map(lambda x: x * 2, numbers))
print("每个乘2:", doubled)

# filter + lambda：筛选
big = list(filter(lambda x: x > 3, numbers))
print("大于3的:", big)


# ========================================
# Part 3: class 基础（对比 C++ 的 class）
# ========================================

print("\n=== Part 3: class 基础 ===\n")

class Dog:
    # 类变量（所有实例共享，类似 C++ 的 static）
    species = "犬科"

    # __init__ 是构造函数（类似 C++ 的 Dog::Dog(string name)）
    def __init__(self, name, age):
        # self 类似 C++ 的 this 指针，但必须显式写在参数里
        self.name = name    # 实例变量，不用提前声明类型
        self.age = age

    # 方法（self 必须是第一个参数）
    def bark(self):
        return f"{self.name}说: 汪!"

    def info(self):
        return f"{self.name}, {self.age}岁, {self.species}"

# 创建实例（不需要 new，跟 C++ 的 Dog d("旺财") 类似）
dog1 = Dog("旺财", 3)
dog2 = Dog("来福", 1)

print(dog1.bark())          # 旺财说: 汪!
print(dog2.info())          # 来福, 1岁, 犬科

# 类变量通过类名访问，也可以通过实例访问
print("类变量:", Dog.species)


# ========================================
# Part 4: 继承 + super()（对比 C++ 的 : public BaseClass）
# ========================================

print("\n=== Part 4: 继承 ===\n")

class Animal:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return f"{self.name}发出声音"

# 括号里写父类名（对比 C++ 的 class Cat : public Animal）
class Cat(Animal):
    def __init__(self, name, color):
        # super() 调用父类的 __init__（对比 C++ 的 Animal::Animal(name)）
        super().__init__(name)
        self.color = color

    # 重写父类方法（对比 C++ 的 override）
    def speak(self):
        return f"{self.name}({self.color}色)说: 喵~"

cat = Cat("咪咪", "白")
print(cat.speak())          # 咪咪(白色)说: 喵~

# 判断类型
print("是Cat?", isinstance(cat, Cat))        # True
print("是Animal?", isinstance(cat, Animal))  # True（继承关系成立）


# ========================================
# Part 5: 魔术方法（Python 特色，C++ 没有直接对应）
# ========================================

print("\n=== Part 5: 魔术方法 ===\n")

class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    # __str__：给人看的（print 时调用），类似 C++ 重载 <<
    def __str__(self):
        return f"《{self.title}》作者:{self.author}"

    # __repr__：给开发者看的（调试用，命令行直接敲变量名时调用）
    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', pages={self.pages})"

    # __call__：让实例可以像函数一样被调用
    def __call__(self, times):
        return f"把《{self.title}》读了{times}遍"

    # __len__：支持 len(book)
    def __len__(self):
        return self.pages

    # __eq__：支持 == 比较
    def __eq__(self, other):
        return self.title == other.title and self.author == other.author


book1 = Book("三体", "刘慈欣", 300)
book2 = Book("三体", "刘慈欣", 300)

print("str:", str(book1))       # 《三体》作者:刘慈欣
print("print:", book1)          # print 自动调用 __str__
print("repr:", repr(book1))     # Book(title='三体', ...)

print("call:", book1(3))        # 把《三体》读了3遍
print("len:", len(book1))       # 300
print("相等?", book1 == book2)  # True（调用了 __eq__）


# ========================================
# Part 6: @property（getter/setter 的 Python 写法）
# ========================================

# 个人理解： 
# 与直接访问和赋值的不同：
#   1、能加校验逻辑，自动使用方法里的校验
#   2、能算出来不用存，可以访问没有赋值的属性(值从其他属性得来)
#   3、能事后改内部实现

print("\n=== Part 6: @property ===\n")

class Circle:
    def __init__(self, radius):
        self._radius = radius   # _ 前缀约定为"私有"，实际还是能访问

    # @property：把方法变成属性一样访问（getter）
    @property
    def radius(self):
        print("  获取半径")
        return self._radius

    # @xxx.setter：setter
    @radius.setter
    def radius(self, value):
        if value <= 0:
            raise ValueError("半径必须大于0")
        print(f"  设置半径: {value}")
        self._radius = value

    # 计算属性（只读，只有 getter）
    @property
    def area(self):
        return 3.14159 * self._radius ** 2

c = Circle(5)
print("半径:", c.radius)    # 像访问属性一样，实际调用了方法
print("面积:", c.area)      # 19.6349...

c.radius = 10               # 像赋值一样，实际调用了 setter
print("新面积:", c.area)

# c.area = 100  # 报错！area 没有 setter，只读


# ========================================
# Part 7: with 上下文管理器（C++ 的 RAII + 析构函数）
# ========================================

print("\n=== Part 7: with 上下文管理器 ===\n")

# with 保证资源一定会被释放（类似 C++ 的 ifstream 在析构时自动 close）
# open 就是一个上下文管理器

print("写文件...")
with open("E:/learn/day02/test.txt", "w", encoding="utf-8") as f:
    f.write("Hello from Day 2!\n")
    f.write("第二行内容\n")
# 离开 with 块，文件自动关闭（即使中间抛异常也会关）

print("读文件...")
with open("E:/learn/day02/test.txt", "r", encoding="utf-8") as f:
    content = f.read()
    print(f"文件内容:\n{content}")

# 自己写一个上下文管理器（实现 __enter__ 和 __exit__）
class Timer:
    """一个简单的计时器，用来演示上下文管理器"""
    import time

    def __enter__(self):
        self.start = self.time.time()
        print(f"  开始计时...")
        return self   # return 的值会赋给 as 后面的变量

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = self.time.time() - self.start
        print(f"  计时结束，耗时: {elapsed:.3f}秒")
        # 返回 False（默认）表示有异常就往外抛
        # 返回 True 表示吞掉异常
        return False

print("\n使用自定义计时器:")
with Timer() as t:
    print(f"  开始时间：{t.start}")
    total = sum(range(10000000))  # 一千万次求和
    print(f"  求和结果: {total}")


print("\n*** Day 2 基础练习全部完成! ***")
print("下一步：看 02_document_class.py 完成检验练习")
