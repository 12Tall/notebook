# Flask 学习  

## Cheat Sheet  
记录最简单的使用方法  

```python
from flask import Flask, render_template, render_template_string, url_for, request, redirect
from markupsafe import escape
# 用于字符串转义，保证前端安全

app = Flask(__name__)
# 用于定位资源文件，一般用`__name__`就行了
# 但是如果是从`python -m project.app`，就需要设置硬编码
# app = Flask('yourapplication')
# app = Flask(__name__.split('.')[0])
# 最后一种是最安全的了


@app.route('/', methods=['GET'])  # 默认参数，只允许GET 请求
@app.route('/<string:name>/')  # 转换器:变量名
# 定义路由时以斜线结尾，浏览器访问`/name` 时会自动补全为`/name/`
# 反之则不然
def index(name='world'):
    app.logger.debug('记录日志')
    if request.method == 'POST':  # 判断请求方法，注意request 是全局导入的
        # 参考：https://dormousehole.readthedocs.io/en/latest/quickstart.html#id14

        return "hello %s! %s" % (escape(name), url_for('index', name='12tall'))
        # url_for 用于根据函数名生成链接，传入的参数依次为函数名、url 参数
        # 在模板渲染时很有用
        # url_for('static', filename='style.css')  # 用于返回静态文件

    else:
        print(request.form)  # 获取请求体参数

        if name == '12tall':  # 重定向
            return redirect(url_for('index', name='12tall ^^'))
            # 当然也可以返回字典对象，会被自动转化为json  

        # return render_template('jinja2_template_file', data=data)
        return render_template_string('hello {{name}}~', name=name)


app.run(host='0.0.0.0', debug=True)
# debug=True 开启调试模式，服务会热启动
# host/port 监听选项

# 也可以通过全局的session 和cookie 判断用户状态，这里不写了
```  

## 高级应用  

- [ ] 大型项目文件拆分  
- [ ] 数据库  
- [ ] 路由和蓝图  
- [ ] 如何在路由处理函数中使用logger  