#encoding=utf8

import json
from functools import wraps
from flask import request,  g, \
    Blueprint
from mwauth.base_auth import BaseAuth
from werkzeug.wrappers import Response
from redis import Redis

# key的过期时间，默认为7天
expire_time  = 7*24*60*60


auth = Blueprint("auth", __name__)

def not_authenticated():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})

class BasicAuth(BaseAuth):
    """docstring for ClassName"""
    app = None
    user_class = None
    redis = None
    def __init__(self,app=None,redis=None):
        super(BasicAuth, self).__init__()
        if app is not None:
            self.init_app(app,redis)

    def get_rds_key(self):
        return 'session:%s'%request.headers.environ['HTTP_AUTHORIZATION']

    def get_user_cache(self):
        userinfo = self.redis.get(self.get_rds_key())
        if userinfo is not None:
            try:
                userinfo = json.loads(userinfo.decode())
                user = self.user_class()
                for k, v in userinfo.items():
                    setattr(user, k, v)
            except:#如果userinfo的格式错误，不能创建物件就成资料库中载入资料
                self.redis.delete(self.get_rds_key())
                return None
            return user
        return None

    def check_auth(self,username, password):
        """This function is called to check if a username /
        password combination is valid.
        """
        user = self.get_user_cache()
        if user is not None:
            g.current_user = user
            # 重置key的有效期为2天
            self.redis.expire(self.get_rds_key(),expire_time)
            return True
        # 请指定user_class类
        assert self.user_class != None
        try:
            user = self.user_class.FindUser(username)
        except Exception as e:
            self.app.logger.error('FindUser error:'+str(e))
            user = None
        if user and user.check(password):
            g.current_user = user
            self.redis.setex(self.get_rds_key(),json.dumps(user.to_json()),expire_time)
            return True
        return False

    def init_app(self, app,redis):
        self.app = app
        app.auth = self
        assert redis != None
        self.redis =redis
        assert self.redis.provider_class == Redis,"请使用提示格式创建rds:rds = FlaskRedis(app,strict=False)"
        self.app.register_blueprint(auth)

    def valid_login(self, func):
        @wraps(func)
        def _request_login(*args, **kwargs):
            auth = request.authorization
            if not auth or not self.check_auth(auth.username, auth.password):
                return not_authenticated()
            return func(*args, **kwargs)
        return _request_login



