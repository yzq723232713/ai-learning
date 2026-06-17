"""
Day 1 检验：把下面这段 C++ 逻辑用 Python 重写
下面的 C++ 代码是一段信号处理中常见的逻辑：滑动窗口求均值
你在上位机开发中应该见过类似的东西

#include <vector>
#include <iostream>
using namespace std;

int main() {
    // 原始信号数据
    vector<double> signal = {1.2, 2.5, 3.1, 4.8, 5.0, 6.2, 7.1, 8.4, 9.0, 10.3};
    int window_size = 3;
    vector<double> smoothed;

    // 滑动窗口求均值（去噪）
    for (int i = 0; i <= signal.size() - window_size; i++) {
        double sum = 0;
        for (int j = 0; j < window_size; j++) {
            sum += signal[i + j];
        }
        smoothed.push_back(sum / window_size);
    }

    // 输出结果
    cout << "原始信号: ";
    for (double v : signal) cout << v << " ";
    cout << endl;

    cout << "平滑后: ";
    for (double v : smoothed) cout << v << " ";
    cout << endl;

    // 找出平滑后大于5的值
    cout << "大于5的值: ";
    for (double v : smoothed) {
        if (v > 5) {
            cout << v << " ";
        }
    }
    cout << endl;

    return 0;
}
"""

# ========================================
# 你的 Python 版本写在这里
# ========================================

# TODO: 用 Python 重写上面的 C++ 程序
# 提示：
#   vector → list
#   cout << v << " " → print(v, end=" ")
#   push_back → append
#   滑动窗口可以继续用两层 for，但 Python 有更简洁的写法（切片 + sum）

signal = [1.2, 2.5, 3.1, 4.8, 5.0, 6.2, 7.1, 8.4, 9.0, 10.3]
window_size = 3
smoothed = []

for i in range(len(signal) - window_size + 1):
    window = signal[i : i + window_size]
    smoothed.append(sum(window) / window_size)

print(f"原始信号：{signal}")
print(f"平滑后：{smoothed}")
print("平滑后大于5的值：", *(x for x in smoothed if x > 5))
