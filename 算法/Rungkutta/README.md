# 龙格-库塔法求解微分方程  

> 数值法求解微分方程  

对于微分方程：  
> $$\begin{array}{lll}
y'(x) & = & f(x,y) \\
K_1& = & f(x_n,y_n) \\
y(x_{n+1}) & = & y(x_n)+h*K_1 
\end{array}$$  

$其中，h 是步长、K_1 是y(x) 在x_n 处的斜率。$此为**一阶精度**，减小步长有利于减小迭代的误差。  

$可采用在点x_n 处的斜率K_1，并于x_{n+1} 处的斜率的算术平均值，作为最终斜率K 以减小迭代误差。$能够得到**二阶精度**。如下：    
> $$\begin{array}{lll}
K_1 & = & f(x_n, y_n) \\
K_2 & = & f(x_n+h, y_n+h*K_1) \\
y(x_{n+1}) & = & y(x_n) + \frac{h}{2}
(K_1 + K_2)
\end{array}$$  

$因为无法预知函数未来的斜率，所以只能以当前的斜率预估。$  

以此类推，我们可以得到更高阶的龙格-库塔公式：  
>$$\begin{array}{lll}
K_1 & = & f(x_n, y_n) \\
\\
K_2 & = & f(x_n+\frac{h}{2}, y_n + \frac{h}{2}*K_1) \\
\\
K_3 & = & f(x_n+\frac{h}{2}, y_n + \frac{h}{2}*K_2) \\
\\
K_4 & = & f(x_n+h, y_n + h*K_3) \\ 
\\ 
y(x_{n+1}) & = & y(x_n) + \frac{h*(K_1+2K_2+2K_3+K_4)}{6}      
\end{array}$$  

## Python 代码  
由推导过程可知，`Runge-Kutta` 的函数至少需要4 个参数：$x_n，y(x_n)，h，f(x,y)$。于是可以这样定义：  
```python
import numpy as np
def runge_kutta_4(x_n, y_n, h, f):
    """
    return $y(x_{n+1})$
    """
    k1 = h*f(x_n, y_n)
    k2 = h*f(x_n+0.5*k1, y_n+0.5*k1)
    k3 = h*f(x_n+0.5*k2, y_n+0.5*k2)
    k4 = h*f(x_n+k3, y_n+k3)
    return y_n+(k1+2*k2+2*k3+k4)/6.  

# y' = x
def f(x, y):
    return x


# 初始条件
step = 0.001
tt = np.arange(0, 10, step)  
y = 0  

for t in tt:  
    y = runge_kutta_4(t, y, step, f)
    print(t, y)
```  

## 高阶微分方程求解  
对于高阶微分方程或者多元微分方程，我们可以将它们拆成n 多个一阶微分方程组。每次迭代时，对于每个一阶微分方程使用龙格库塔法进行计算就好了。需要注意的是函数$f(...)$ 可能会需要接收许多参数！  
具体请参考[龙格-库塔法求解单入单出二阶系统状态方程](https://blog.csdn.net/congguitar/article/details/106801306)。  
这里有一个问题：就是求得的状态是否应该在当前循环中生效？实际计算的结果似乎也没差多少。  

### 面向对象的封装  
```python
from copy import deepcopy
import string
import matplotlib.pyplot as plt
import numpy

class State:
    """
    状态变量及其对应的方程，
    如：
    y' = t ==> State("y", 0, lambda t, state: t)
    或也可调用另外一个状态：
    z' = y ==> State("z", 0, lambda t, state: state["y"])
    """
    def __init__(self, name: string, init_value: float, equation) -> None:
        self.name = name
        self.init_value = init_value
        self.equation = equation


class System:
    """
    系统，用于管理状态及状态方程
    """
    def __init__(self, t=0, dt=0):
        self.name = "system"
        self.state = {}
        self.equation = {}
        self.history = []
        self.t = t
        self.dt = dt

    def addState(self, state: State):
        """
        添加状态：要求不要引用未定义的状态变量，时间t 除外
        """
        self.state[state.name] = state.init_value
        self.equation[state.name] = state.equation

    def record(self):
        """
        存储计算结果：待优化
        """
        self.history.append(self.state)

    def RK4(self):
        """
        使用四阶龙格-库塔进行仿真，效果尚可
        中间使用了很多字典暂存变量，可以继续优化
        """
        t, dt = self.t, self.dt
        for t in numpy.arange(0, t, dt):
            self.record()
            next_state = {}
            for state in self.state:
                temp_state = deepcopy(self.state)
                k1 = dt*self.equation[state](t, temp_state)
                for key in temp_state:
                    temp_state[key] += 0.5*k1
                k2 = dt*self.equation[state](t+0.5*k1, temp_state)
                for key in temp_state:
                    temp_state[key] += 0.5*(k2-k1)  
                k3 = dt*self.equation[state](t, temp_state)
                for key in temp_state:
                    temp_state[key] += (k3-k2)
                k4 = dt*self.equation[state](t, temp_state)
                next_state[state] = self.state[state] + (k1+2*k2+2*k3+k4)/6.
            self.state = next_state
        self.record()
```

调用时只需要传入关键参数即可：  
```python
# 首先要import System
sys = System(1, .001)

"""
实例1：
    x1' = t
"""
sys.addState(State("x1", 0, lambda t, state: t))

"""
实例2：
    x1' = x2                (1)
    x2' = -2*x1 - 2*x2 + 1  (2)
"""
# sys.addState(State("x1", 0, lambda t, state: state["x2"]))
# sys.addState(State("x2", 0, lambda t, state: -2 *
#              state["x1"] - 2*state["x2"] + 1))


sys.RK4()
print(sys.history)
```

以上代码亲测可用，但是尚有许多可以优化的地方，例如深拷贝等。也许后面使用矩阵的方法能够得到更优的解决方案。  


## 参考  
1. [龙格-库塔（Rungekutta）法求解常微分方程](https://www.jianshu.com/p/e4aa9a688959)  
2. [龙格-库塔法求解单入单出二阶系统状态方程](https://blog.csdn.net/congguitar/article/details/106801306)