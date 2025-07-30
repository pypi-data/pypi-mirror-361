#encoding=utf8
import json
from datetime import timedelta
from uuid import uuid4
from flask_redis import FlaskRedis
from flask import request,session
from redis import Redis
from werkzeug.datastructures import CallbackDict
from flask.sessions import SessionInterface, SessionMixin

class RedisSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None, new=False):
        def on_update(self):
            self.modified = True
            self.new = False
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.new = new
        self.modified = False
        self.seend_cookie = True
        # 某些临时session的过期时间会比较短或长
        self.temp_expiration_time = 0

class RedisSessionInterface(SessionInterface):
    session_class = RedisSession
    def __get_sid(self,sid):
        if self.prefix:
            return self.prefix +':'+sid
        else:
            return sid

    def __init__(self, app, redis, prefix='session'):
        # if redis is None:
        #     redis = FlaskRedis(strict=False)
        assert redis is not None,'redis 必须要指定'
        self.redis = redis
        # assert self.redis.provider_class == Redis,"请使用提示格式创建rds:rds = FlaskRedis(app,strict=False)"
        self.prefix = prefix
        if app:
            self.init_app(app)

    def init_app(self,app):
        app.session_interface = self
        # self.redis.init_app(app)
        app.session_cookie_name='sessionid'

    def generate_sid(self):
        return str(uuid4())

    def get_redis_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        if session.temp_expiration_time>0:
            return timedelta(seconds=session.temp_expiration_time)
        return timedelta(days=2)

    def get_session(self,sid):
        if not sid:
            sid = self.generate_sid()
            return self.session_class(sid=sid, new=True)
        val = self.redis.get(self.__get_sid(sid))
        if val is not None:
            data = json._default_decoder.decode(val.decode())
            return self.session_class(data, sid=sid)
        return self.session_class(sid=sid, new=True)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        return self.get_session(sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            # 如果是新创建的session，还没有写入redis时，不用做delete redis的动作，以提升性能
            if not session.new:
                self.redis.delete(self.__get_sid(session.sid))
            if session.modified:
                response.delete_cookie(app.session_cookie_name,
                                       domain=domain)
            return
        redis_exp = self.get_redis_expiration_time(app, session)
        cookie_exp = self.get_expiration_time(app, session)
        val = json._default_encoder.encode((dict(session)))

        try:
            self.redis.setex(self.__get_sid(session.sid),
                             int(redis_exp.total_seconds()),
                             val
                             )
        except Exception as e:
            # assert self.redis.provider_class == Redis,"请使用提示格式创建rds:rds = FlaskRedis(app,strict=False)"
            self.redis.setex(self.__get_sid(session.sid),val,
                                 int(redis_exp.total_seconds())
                                 )
        # 有某些认证只需要记录session，不需要送给前端
        # 默认每次都送保持，在使用时，保证cookie不过期
        if session.seend_cookie:
            response.set_cookie(app.session_cookie_name,
                                session.sid,
                                expires=cookie_exp,
                                httponly=True,
                                domain=domain)
            # 改为在login中指定，以后每次sendcookie时，不能覆盖掉前端设定的locale
            # response.set_cookie('locale', get_lang(session.get('locale')),
            #                     expires=cookie_exp,
            #                     # 需要让前端修改
            #                     httponly=False,
            #                     domain=domain
            #                     )
            # 确保下次正常时需要
            session.seend_cookie = False
            session.temp_expiration_time = 0
