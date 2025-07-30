##################################
#提供基于api gateway kong的JWT认证和cookie认证
#认证失败时返回401
#################################
from mwauth.base_auth import BaseAuth,User
from flask import request,make_response,g,current_app,session
from flask_babel import _
from functools import wraps
import inspect
from .redis_session import RedisSessionInterface
import hashlib
class KongAuth(BaseAuth):
    # '''
    # 1，在request前提取 user info
    # '''
    def __set_auth(self):
        '''
        保存用户，jwt等auth info
        :return:
        '''
        if not isinstance(current_app.session_interface,RedisSessionInterface):
            raise Exception('请在app/__init__.py的create_app_swagger方法中增加下列代码：\n app.session_interface = RedisSessionInterface(app, rds)')
        # redis 中session的过期时间，为0时，为第一次设定的时间
        session_expiration_time = current_app.config.get('SESSION_EXPIRATION_TIME', 0)
        if current_app.config.get('DEVELOPMENT', False):
            g.user_name = current_app.config.get('LOGIN_USER_NAME')  # 'user_dev'
            g.user_id = current_app.config.get('LOGIN_USER_ID')
            g.current_user = User(uid=current_app.config.get('LOGIN_USER_ID'),
                                  uname=current_app.config.get('LOGIN_USER_NAME'),
                                  systemuser=current_app.config.get('LOGIN_USER_SYSTEMUSER', False),
                                  manageuser=current_app.config.get('LOGIN_USER_MANAGEUSER', False),
                                  manageuserid=current_app.config.get('LOGIN_USER_MANAGEUSER_ID'),
                                  companyid=current_app.config.get('LOGIN_USER_COMPANYID',''),
                                  phone = current_app.config.get('LOGIN_USER_PHONE'),
                                  type=session.get('type', 'appuser')
                                  )
            g.jwt = session.sid
            # 只有session 認證才需要設定這個redis的有效期
            session.temp_expiration_time = session_expiration_time
            session.update({'uid':g.current_user.uid,'uname':g.current_user.uname,
                            'systemuser':g.current_user.systemuser,
                            'manageuser':g.current_user.manageuser,
                            'manageuserid':g.current_user.manageuserid})
            return
        # 通过了jwt 或 key 认证的 api 一定会回传username和userid，否则视为kong的认证不成功
        g.user_name = request.headers.get('X-Consumer-Username')
        g.user_id = request.headers.get('X-Consumer-Custom-Id')
        # key auth 或jwt auth
        g.jwt = request.args.get('jwt') or request.args.get('apikey')or request.args.get('sessionid') or request.args.get('token')
        if g.jwt is None:
            # jwt header authorization: bearer jwt...
            jwt = request.headers.get('authorization', None)
            if jwt:
                # 去掉前面的bearer
                g.jwt = jwt[7:]
            elif session:
                g.jwt = session.sid
                # session 认证可能不经过kong，但也需保证auth 成功，确保代码兼容
                g.user_name = session.get('uname')
                g.user_id = session.get('uid')
            else:
                # header，query，和cookie中都没有 jwt or sessionid or token or apikey，需要重新认证
                g.user_name = None
                g.user_id = None
                return
            # 只有session 認證才需要設定這個redis的有效期
            session.temp_expiration_time = session_expiration_time
        elif session and session.sid!=g.jwt:
            # 如果有传jwt ，就使用jwt的，cookie中的session可能是上一次的，需刷新为jwt的
            session.sid = g.jwt
            mysession = current_app.session_interface.get_session(g.jwt)
            # 只有session 認證才需要設定這個redis的有效期
            session.temp_expiration_time = session_expiration_time
            session.update(dict(mysession))
        if not session:
            # 当非session认证时，还需保存session，保证app中的代码的兼容性
            session.sid = g.jwt
            # 临时session 不需要送cookie，避免浪费流量
            session.seend_cookie = False
            mysession = current_app.session_interface.get_session(g.jwt)
            # 如果只通过了Kong 认证，且没有在redis中存该session key ，如：key auth，则写入kong 认证的信息给session
            if request.headers.get('X-Consumer-Username') \
                and request.headers.get('X-Consumer-Custom-Id') \
                and not mysession:
                # 有 X-Consumer-Username 可能是JWT和key auth, 没有mysession 只有key auth 认证时，才需要更新session
                if request.args.get('apikey')==g.jwt :
                    session.update(dict({'uid':g.user_id ,'uname':g.user_name,
                                'systemuser':False,
                                'manageuser':False,
                                'manageuserid':'',
                                'type':'appuser'}))
                else: # logout 后redis session已经被清除, 但jwt 还在, 通过jwt传递参数的api,需要重新认证
                    g.user_name = None
                    g.user_id = None
                    return
            else:
                # 只有session 認證才需要設定這個redis的有效期
                # session.temp_expiration_time = session_expiration_time
                session.update(dict(mysession))
        g.current_user = User(uid=session.get('uid'),
                              uname=session.get('uname'),
                              systemuser=session.get('systemuser', False),
                              manageuser=session.get('manageuser', False),
                              manageuserid=session.get('manageuserid'),
                              companyid=session.get('companyid',''),
                              type=session.get('type','appuser'),
                              phone=session.get('phone','')
                )
        g.user_name = session.get('uname')
        g.user_id = session.get('uid')


    def __init__(self, app=None):
        super(KongAuth, self).__init__()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        app.auth = self
        # self.app.register_blueprint(auth)

    def valid_login(self, func):
        @wraps(func)
        def _request_login(*args, **kw):
            # 给g 赋 用户等信息
            self.__set_auth()
            if g.user_name or g.user_id :
                return func(*args, **kw)
            # 没有认证则返回401
            response = make_response()
            response.status_code = 401
            return response
        return _request_login


    def valid_sign(self,func):
        @wraps(func)
        def _request_sign(*args, **kw):
            # key认证的token为key，浏览器端因访问不到jwt，可以传username
            # json.dumps(json_body)+token(或用户名)+noncestr+timestamp 转md5
            sign = request.headers.get('X-MW-Sign') or request.args.get("sign")
            # 资料库不区分大小写，会导致前后sign 不一致
            sign_source_str = f'{request.data.decode()}{g.current_user.uname.lower()}' \
                              f'{request.headers.get("X-MW-Noncestr") or request.args.get("noncestr", "")}' \
                              f'{request.headers.get("X-MW-Timestamp") or request.args.get("timestamp", "")}'
            sign_md5 = hashlib.md5(sign_source_str.encode()).hexdigest()
            current_app.logger.info(f'sign_source_user:{sign_source_str}, sign_md5:{sign_md5}, sign_web:{sign}')
            if sign_md5 == sign:
                return func(*args, **kw)
            else:
                sign_source_str = f'{request.data.decode()}{g.jwt}' \
                                  f'{request.headers.get("X-MW-Noncestr") or request.args.get("noncestr", "")}' \
                                  f'{request.headers.get("X-MW-Timestamp") or request.args.get("timestamp", "")}'
                sign_md5_jwt = hashlib.md5(sign_source_str.encode()).hexdigest()
                current_app.logger.info(f'sign_source_jwt:{sign_source_str}, sign_md5_jwt:{sign_md5_jwt},sign_web:{sign}')
                if sign_md5_jwt == sign:
                    return func(*args, **kw)
            # 没有认证则返回400
            response = make_response({ "error": f'sign error,web sign:{sign},'
                                                f'srv sign_user {sign_md5},'
                                                f'srv sign_jwt{sign_md5_jwt},'
                                                f'noncestr:{request.headers.get("X-MW-Noncestr") or request.args.get("noncestr", "")},'
                                                f'timestamp:{request.headers.get("X-MW-Timestamp") or request.args.get("timestamp", "")}'},
                                     400, {"content-type": "application/json;charset=utf8"})
            response.status_code = 400
            return response
        return _request_sign

    def valid_phone_code(self,phone_code_arg_name:str):
        '''
        检查验证码，需要传入验证码的参数名称
        :param phone_code_arg_name: 函数中电话验证码的参数名称
        :return:
        '''
        def wrapper(func):
            @wraps(func)
            def valid_phone_code(*args, **kwargs):
                # 根据phone_code的参数名称获取phone_code验证码
                phone_code = inspect.signature(func).bind_partial(*args, **kwargs).arguments.get(phone_code_arg_name)
                assert phone_code is not None, f'验证码的参数名称{phone_code_arg_name}在函数中不存在'
                phone = g.current_user.phone
                rds = current_app.session_interface.redis
                valid_code, hits = rds.hmget(f'session:phone.valid.code:{phone}', ['valid_code', 'hits'])
                if valid_code:
                    self.max_hits = rds.hincrby(f'session:phone.valid.code:{phone}', 'max_hits', 1)
                if valid_code and valid_code.decode() == phone_code:
                    rds.delete(f'session:phone.valid.code:{phone}')
                    return func(*args, **kwargs)
                rds.hincrby(f'session:phone.valid.code:{phone}', 'hits', -1)
                if hits and int(hits.decode()) <= 0:
                    rds.delete(f'session:phone.valid.code:{phone}')
                return  make_response({ "error": _('The phone valid code is error,please retry enter.')},  400, {"content-type": "application/json;charset=utf8"})
            return valid_phone_code
        return wrapper


