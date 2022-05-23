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


# app.register_blueprint(bp)  # 注册蓝图  

app.run(host='0.0.0.0', debug=True)
# debug=True 开启调试模式，服务会热启动
# host/port 监听选项

# 也可以通过全局的session 和cookie 判断用户状态，这里不写了
```  

## 项目化  
> 随着项目的增大，一般我们需要将业务逻辑从`app.py` 分离出来，使项目结构更加清晰明了。  

### 关于Python 包
- 每一个包含`*.py` 文件的子文件加都可以被认为是一个包  
- 可以在`__init__.py` 中定义在包被导入时的行为，例如可以统一子模块的的导出  
- `import` 与其说是导入，不如说是`using` 使用，因为`import` 不会重复导入包  


### 路由与蓝图
> 一般我们会将路由单独写作一个子模块，或者随业务划分到子模块。这里以第一种情况为例  

在`app.py` 中注册路由很简单，直接用`app.route()` 装饰器就好了。但是如果要从子模块中注册路由，就需要将`app` 提前传入到子模块，这个在逻辑上会非常绕，于是Flask 提供了蓝图的功能，可以让我们的代码逻辑显得更清晰一些。  

```python
'''
app.py  
在`app.py` 文件中注册蓝图    
'''
from flask import Flask
from bp import bp  # 子模块放在/bp/ 目录下

# ...
app.register_blueprint(bp)  # 注册蓝图
# ...
app.run()


'''
bp/__init__.py  
可以在`bp/__init__.py` 统一将更子级的蓝图统一为一个整体，然后再导出  
'''
from bp.sub import sub
from flask import Blueprint

bp = Blueprint('bp', __name__, url_prefix='/bp')
# 蓝图名称：bp。在子模块中如果要使用url_for 需要指定name！ 
# 导入位置：__name__  
# 路由前缀：`/bp`

bp.register_blueprint(sub)


'''
bp/sub.py  
可以在`bp/sub.py` 定义真正的路由代码  
'''
from flask import Blueprint, current_app, url_for

sub = Blueprint('sub', __name__, url_prefix='/sub')

@sub.route('/')
def sub_index():
    current_app.logger.error("error from /bp/sub/sub_index")  # 通过current_app 就可以在蓝图中使用logger 了
    return url_for('bp.sub.sub_index')  # 注意这里使用url_for 的方式
    # 上级蓝图name.次级蓝图name.方法名
```


### 关于元编程  
可以把`metaclass` 类比为`class` 类型的父类。普通的对象在创建时会自动执行父类的构造函数，而`class` 在被创建（包括被`import`）时，会自动调用`metaclass` 的构造方法。所以在`SQLAlchemy` 中需要在`createtables()` 之前要`import` 我们的`Model` 子类。

### 数据库操作  
> 使用`SQLAlchemy` 作为ORM  

```python
'''
app.py  
在`app.py` 文件中初始化数据库    
'''
from db import init_db, user
from flask import Flask
from bp import bp  # 子模块放在/bp/ 目录下

init_db()

# ...
@app.route("/")  # 
def index():
    u = user.User('admin1', 'admin1@localhost')
    u.add_to_db()
    return "done"
# ...
app.run()

'''
db/__init__.py  
可以在`db/__init__.py` 定义真正的路由代码  
'''
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///test.db')  # 数据库连接
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
# scoped_session 相当于一个线程有效期内单例全局变量吧
#  为每个应用线程 保持着一个不同的对象.
Base = declarative_base()                    # 元类相关
Base.query = db_session.query_property()

def init_db():
    # 在这里导入定义模型所需要的所有模块，这样它们就会正确的注册在
    # 元数据上。否则你就必须在调用 init_db() 之前导入它们。
    import db.user  # 可以在子模块中通过__all__=["var","function"] 限制导出
    Base.metadata.create_all(bind=engine)


'''
db/user.py  
可以在`db/user.py` 定义真正的路由代码  
'''
from sqlalchemy import Column, Integer, String
from db import Base, db_session

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<User {self.name!r}>'
        
    def add_to_db(self):
        db_session.add(self)
        db_session.commit()
```

以上！