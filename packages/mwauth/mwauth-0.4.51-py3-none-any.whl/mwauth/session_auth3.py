# encoding=utf8
'''
用于微服务的框架，没有认证的url统一返回401
session 存 redis 中，没有User_Class
'''
from functools import wraps
from flask import  session,  g,  make_response
from mwauth.base_auth import BaseAuth,User

class SessionAuth(BaseAuth):
    """docstring for ClassName"""
    app = None
    def __init__(self, app=None):
        super(SessionAuth, self).__init__()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.auth = self

    def valid_login(self, func):
        @wraps(func)
        def _request_login(*args, **kw):
            user_id = session.get('uid')
            if user_id:
                g.user_name = session.get('uname')
                g.user_id = session.get('uid')
                g.current_user = User(uid=session.get('uid'),uname=session.get('uname'),
                                      systemuser=session.get('systemuser',False),manageuser=session.get('manageuser',False),
                                      manageuserid=session.get('manageuserid'))
                return func(*args, **kw)
            # 没有认证则返回401
            response = make_response()
            response.status_code = 401
            return response
        return _request_login


