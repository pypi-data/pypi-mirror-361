# encoding=utf8
'''
在没有认证的情况下，直接跳转到登录页面
'''
import json
import urllib

# import datetime
# import hashlib
from functools import wraps
from flask import request, session, redirect, g, render_template, \
    Blueprint, make_response, current_app
from mwauth.base_auth import BaseAuth
from werkzeug.wrappers import Response
from werkzeug.wsgi import get_current_url
from werkzeug.urls import uri_to_iri, url_quote, url_join, iri_to_uri

auth = Blueprint("auth", __name__, static_folder="./static", template_folder="./templates")


def get_host(environ):
    if 'HTTP_HOST' in environ:
        rv = environ['HTTP_HOST']
    else:
        rv = environ['SERVER_NAME']
        if (environ['wsgi.url_scheme'], environ['SERVER_PORT']) not \
                in (('https', '443'), ('http', '80')):
            rv += ':' + environ['SERVER_PORT']
    return rv


def get_current_url(environ):
    tmp = [environ['wsgi.url_scheme'], '://', get_host(environ)]
    cat = tmp.append
    return uri_to_iri(''.join(tmp) + '/')
    cat(url_quote(wsgi_get_bytes(environ.get('SCRIPT_NAME', ''))).rstrip('/'))
    cat('/')
    return uri_to_iri(''.join(tmp))


def correct_location(location, request):
    '''
    把location 改为完整的URL
    :param location: url path 如：/auth/login
    :param request:
    :return: 完整url，如:http://location:8082/auth/login
    '''
    current_url = get_current_url(request.environ)
    current_url = iri_to_uri(current_url)
    return url_join(current_url, location)


class Redirect_Respose(Response):
    # pass
    def __init__(self, response=None, status=None, headers=None,
                 mimetype=None, content_type=None, direct_passthrough=False):
        super().__init__(response, status, headers,
                         mimetype, content_type, direct_passthrough)
        # 屏蔽 wrappers.py 的 1143行代码，不对location做host纠正
        self.autocorrect_location_header = False


class SessionAuth(BaseAuth):
    """docstring for ClassName"""
    app = None
    db = None
    user_class = None
    home_url = None

    def __init__(self, app=None, home_url=None):
        super(SessionAuth, self).__init__()
        self.home_url = home_url
        if not self.home_url:
            # 用于登录用户进入登录页面跳转链接问题
            self.home_url = "/"
        if app is not None:
            self.init_app(app)

    def init_app(self, app, home_url=None):
        self.app = app
        app.auth = self
        if home_url:
            self.home_url = home_url + '/' if not home_url.endswith('/') else home_url
        self.app.register_blueprint(auth, url_prefix='%sauth' % self.home_url)

    def valid_login(self, func):
        @wraps(func)
        def _request_login(*args, **kw):
            # redis 中session的过期时间，为0时，为第一次设定的时间
            session.temp_expiration_time = current_app.config.get('SESSION_EXPIRATION_TIME', 0)
            url_to = request.args.get("to")
            user_id = session.get('uid')
            if user_id:
                userObj = self.user_class()
                user_dict = userObj.to_json()
                for key in user_dict:
                    setattr(userObj, key, session.get(key))
                g.current_user = userObj
                # g.redirect_url = request.headers.get("Referer","/")
                return func(*args, **kw)
            # 判断是否为ajax请求
            request_with = request.headers.get("x-requested-with")
            if request_with and request_with.lower() == "XMLHttpRequest".lower():
                response = make_response()
                response.status_code = 401
                return response
            if not url_to:
                if request.full_path[-1] == '?':
                    full_path = request.full_path[:-1]
                else:
                    full_path = request.full_path
                # 如果没有to 参数，则转到根
                if full_path == '/':
                    url_to = '../'
                else:
                    url_to = urllib.parse.quote(full_path)
            return redirect(correct_location("%sauth/login?to=%s" % (self.home_url, url_to), request),
                            Response=Redirect_Respose)

        return _request_login

    def valid_login_redirect(self, redirect_url=None):
        def _valid_login(func):
            r_to_url = redirect_url

            @wraps(func)
            def _request_login(*args, **kw):
                url_to = request.args.get("to")
                # redis 中session的过期时间，为0时，为第一次设定的时间
                session.temp_expiration_time = current_app.config.get('SESSION_EXPIRATION_TIME', 0)
                user_id = session.get('uid')
                if user_id:
                    userObj = self.user_class()
                    user_dict = userObj.to_json()
                    for key in user_dict:
                        setattr(userObj, key, session.get(key))
                    g.current_user = userObj
                    # g.redirect_url = request.headers.get("Referer","/")
                    return func(*args, **kw)
                # 判断是否为ajax请求
                request_with = request.headers.get("x-requested-with")
                if request_with and request_with.lower() == "XMLHttpRequest".lower():
                    response = make_response()
                    response.status_code = 401
                    return response
                if not url_to:
                    if request.full_path[-1] == '?':
                        full_path = request.full_path[:-1]
                    else:
                        full_path = request.full_path
                    # 如果没有to 参数，则转到根
                    if full_path == '/':
                        url_to = '../'
                    else:
                        url_to = urllib.parse.quote(full_path)
                if r_to_url is not None:
                    return redirect(correct_location(redirect_url, request),
                                    Response=Redirect_Respose)
                else:
                    return redirect(correct_location("%sauth/login?to=%s" % (self.home_url, url_to), request),
                                    Response=Redirect_Respose)

            return _request_login

        return _valid_login


def valid_cookie():
    cookies = request.cookies
    if not cookies: return False
    sid = cookies.get("sessionid")
    if sid and sid == session.get("uid"): return True
    return False


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        url = request.args.get("to", current_app.auth.home_url)
        user_id = session.get("uid")
        # if not user_id:
        #     user_id = session.get(b'uid')
        if user_id:
            return redirect(correct_location(urllib.parse.unquote(url), request), Response=Redirect_Respose)
        return render_template("auth/login.html", url=urllib.parse.unquote(url),base_uri=current_app.auth.home_url)
    username = request.form.get("username")
    pwd = request.form.get("password")
    # 请指定user_class类
    assert current_app.auth.user_class != None
    userObj = current_app.auth.user_class.FindUser(username)

    if not userObj: return json.dumps({"msg": "用户名不存在"})
    if not userObj.check(pwd): return json.dumps({"msg": "密码错误"})
    userjson = userObj.to_json()

    session.update(userjson)
    response = make_response(json.dumps({"success": True}))
    return response


@auth.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(correct_location("%sauth/login"%current_app.auth.home_url, request), Response=Redirect_Respose)

@auth.route("/user-logout", methods=["GET", "POST"])
def user_logout():
    session.clear()
    response = make_response(json.dumps({"success": True}))
    return response
