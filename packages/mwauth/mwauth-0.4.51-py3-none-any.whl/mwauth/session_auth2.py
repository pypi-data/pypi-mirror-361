# encoding=utf8
'''
用于微服务的框架，没有认证的url统一返回401
'''
import json
from functools import wraps
from flask import request, session,  g,  make_response
from mwauth.base_auth import BaseAuth

class SessionAuth(BaseAuth):
    """docstring for ClassName"""
    app = None
    db = None
    user_class = None

    def __init__(self, app=None):
        super(SessionAuth, self).__init__()
        #if not self.home_url:
            # 用于登录用户进入登录页面跳转链接问题
         #   self.home_url = "/"
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
                # 如果没有manageuser key，则补充到session中，确保管理者权限设定页面有效
                if not session.get('manageuser') and hasattr(self.user_class,'manageuser'):
                    userObj = self.user_class.FindUser(session.get('uname'))
                    session.update(userObj.to_json())
                else:
                    userObj = self.user_class()
                user_dict = userObj.to_json()
                for key in user_dict:
                    setattr(userObj, key, session.get(key))
                g.current_user = userObj
                return func(*args, **kw)
            # 没有认证则返回401
            response = make_response()
            response.status_code = 401
            return response
        return _request_login


