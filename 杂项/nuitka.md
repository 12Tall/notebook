# Nuitka
> Nuitka 相对来说比较好用，但是`0.77` 版本在打包时启用某些模块会有bug，最好升级到`v0.8`  

## CheatSheet  

```bash
pip3 install nuitka  

nuitka {app_name.py} \               # 指定文件名  
    [--output-dir={output_dir}] \    # 结果保存目录  
    [--standalone] \                 # 可独立运行的可执行文件  
    [--one-file] \                   # 打包为一个文件
    [--user-plugin={PATH}] \         # 指定某些三方package 的路径  
    [--nofollow-imports] \           # 禁止编译时递归地编译所有包，对standalone 和onefile 不生效  
    [--follow-import-to=tkinter] \   # 编译时递归地编译某些包，包越多，编译越慢
    [--follow-import-to=matplotlib] \
    [--follow-import-to=numpy] \
    [--plugin-enable=numpy] \        # 在依赖了某些模块编译时需要启用
    [--plugin-enable=tk-inter] \     # 相关依赖项可以用`--plugin-list` 命令查询
    [--plugin-enable=matplotlib] \   # matplotlib 默认会自动启用
    [--windows-uac-admin] \          # 添加UAC
    [--windows-disable-console]      # 禁用控制台窗口 
```

所以如果想要编译可分发的可执行文件，可以使用以下命令  
```bash
nuitka app.py --one-file --plugin-enable=tk-inter --plugin-enable=numpy --windows-uac-admin

# onefile 方式打包的话no follow imports 是不可用的，所以不要过多考虑打包速度的问题了
py -3.8 -m nuitka ./app.py --onefile --output-dir=out --plugin-enable=pywebview --windows-disable-console--include-data-dir=static=static2 --
```  

## pywebview 例子  

### Python 代码  

```python
import webview
import os

# import matplotlib
# matplotlib.use('Agg')   # https://stackoverflow.com/a/51178529/14791867
# 使用agg 渲染器做后端，没有GUI 界面，所以不会显示图像，也就没有很多bug
# 因为agg 是非交互式后端，所以也不用考虑线程安全的问题

import mpld3
from mpld3 import plugins
import numpy as np
import pandas as pd


def draw():
    
    from matplotlib.figure import Figure
    fig = Figure()
    ax = fig.subplots()

    # fig, ax = plt.subplots()  # 该方法会导致异常
    # 在web 服务器中，应尽量避免使用pyplot，取而代之的是直接使用Figure
    ax.grid(True, alpha=0.3)

    N = 50
    df = pd.DataFrame(index=range(N))
    df['x'] = np.random.randn(N)
    df['y'] = np.random.randn(N)
    df['z'] = np.random.randn(N)

    labels = []
    for i in range(N):
        label = df.iloc[[i], :].T
        label.columns = ['Row {0}'.format(i)]
        # .to_html() is unicode; so make leading 'u' go away with str()
        labels.append(str(label.to_html()))

    points = ax.plot(df.x, df.y, 'o', color='b', mec='k', ms=15, mew=1, alpha=.6)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title('HTML tooltips', size=20)

    tooltip = plugins.PointHTMLTooltip(points[0], labels, voffset=10, hoffset=10)
    plugins.connect(fig, tooltip)  # 添加图表组件

    # 定义返回信息的格式
    return {'message': mpld3.fig_to_html(fig,
                                         d3_url="js/d3/d3.v5.min.js",  # 指定本地的js 依赖
                                         mpld3_url="js/mpld3/mpld3.v0.5.8.min.js",  # 需要注意相对路径的问题
                                         )}


def expose(window):  # 在运行时暴露python 接口
    window.expose(draw)  # 向前端暴露接口为`pywebview.api.draw()`

if __name__ == '__main__':
    window = webview.create_window('Title',
                                   # html="<html>strings</html>", # 直接加载html 字符串
                                   # url='https://www.google.com', # 加载远程页面
                                   # 从本地文件夹中加载
                                   os.path.join(os.path.dirname(
                                       __file__), "static/index.html"),
                                   # frameless=True,  # 无边框
                                   # easy_drag=True,  # 允许通过前端class 是
                                   # `.pywebview-drag-region`, 的元素拖动窗口
                                   # # 拖动窗口
                                   # transparent=True, 窗口透明
                                   )
    # window.expose(draw)
    webview.start(expose,window,
    # debug=True, # 如果定义了--windows-disable-console，需要禁用debug，不然程序无法运行
    )

```

### 前端代码  

> 忽略项目文件结构信息  


```html
<!DOCTYPE html>

<html lang="en">

<head>
    <meta charset="UTF-8">
    <title>Title</title>
    <style>
        #response-container {
            padding: 3rem;
            margin: 3rem 5rem;
            font-size: 120%;
            border: 5px dashed #ccc;
        }

        button {
            font-size: 100%;
            padding: 0.5rem;
            margin: 0.3rem;
            text-transform: uppercase;
        }
    </style>

    <!-- 在调试模式下，调整文件相对路径 -->
    <script src="js/jquery-3.6.0.min.js"></script>
</head>

<body>
    <div id="response-container"></div>
    <button onClick="draw()">draw</button><br />

</body>
<script>
    window.addEventListener('pywebviewready', function () {
        $('response-container').html('<i>pywebview</i> is ready')
    })

    function showResponse(response) {
        // innerHTML 默认禁止运行内部的js 
        $('#response-container').html(response.message)
        console.log(response.message)
    }

    function draw() {
        // 调用python 接口，支持传参
        pywebview.api.draw().then(showResponse)
    }
</script>

</html>
```  

### 编译  
```bash
py -3.8 -m nuitka  ./app.py --standalone --onefile --output-dir=out  --plugin-enable=numpy --include-data-dir=static=static --windows-disable-console
```


## 常见问题  

- [x] `pywebview` 库最多支持到python 3.8，且打包时需要启用插件`--plugin-enable=pywebview`  
- [x] `--onefile` 中`--include-data-dir={src_dir}={target_dir}` 需要通过`os.path.join(os.path.dirname(__file__), "target_dir/file_name")` 才能找到文件  
- [x] `matplotlib` 绘图失败。猜测是[线程安全原因](https://stackoverflow.com/a/34769067/14791867)。禁用后端，或者只采用`Figure`绘图即可  
- [ ] 使用`d3.js` 疑似存在内存泄漏的问题，目前不能定位问题出在哪，所幸还不算太严重  




