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

### 高阶微分方程求解  
对于高阶微分方程或者多元微分方程，我们可以将它们拆成n 多个一阶微分方程组。每次迭代时，对于每个一阶微分方程使用龙格库塔法进行计算就好了。需要注意的是函数$f(...)$ 可能会需要接收许多参数！  
具体请参考[龙格-库塔法求解单入单出二阶系统状态方程](https://blog.csdn.net/congguitar/article/details/106801306)



## 参考  
1. [龙格-库塔（Rungekutta）法求解常微分方程](https://www.jianshu.com/p/e4aa9a688959)  
2. [龙格-库塔法求解单入单出二阶系统状态方程](https://blog.csdn.net/congguitar/article/details/106801306)