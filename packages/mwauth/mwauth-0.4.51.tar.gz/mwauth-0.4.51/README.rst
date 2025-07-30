`rst file editor <http://rst.ninjs.org>`_

mwauth

maxwin 团队 的确权管理

auth的使用

>  __init__.py 中创建Auth对象

.. code-block:: python

    from mwauth.kong_auth import KongAuth
    from mwauth.redis_session import RedisSessionInterface
    # 会话存redis
    rds = FlaskRedis(strict=False)
    auth = KongAuth()

    # 创建APP
    app = Flask(__name__)
    # 初始化 app
    rds.init_app(app)
    auth.init_app(app)
    app.session_interface = RedisSessionInterface(app, rds)


>  调用认证代码,代码基于 swagger

.. code-block:: python

    # 检查 员工的浏览权限
    @auth.valid_login
    def employees_id_get(id,jwt = None):
        pass

    # 检查员工的删除
    @auth.valid_login
    @p.check('employee',["delete"])
    def employees_id_delete(id,jwt = None):
        pass

    @auth.valid_login
    def employee_check_auth():
        # 检查是否有看到身份证的权限
        p.check_permission('empolyee','see_ID')


安装方法
``pip install mwauth``

## 构建包命令:
```bash
python -m build
pip install -e .p #  本地安装包
python -m twine upload dist/*
```