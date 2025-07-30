from enum import Enum

from flask import g

from mwauth import KongAuth, SessionAuth


class AuthType(Enum):
    '''
    该类型支持程序启动时，选择auth 方式
    '''
    # kong_auth.KongAuth,同时支持jwt和session认证方式
    jwt = 'jwt'
    # session_auth3.SessionAuth，只支持非kong的cookie认证
    session = 'session'


def auth(auth_type=AuthType.jwt.value, app=None):
    '''
    支持在程序启动的时候，选择认证类型
    :param auth_type: 认证类型，比如：jwt，session...
    :param app:
    :return:
    '''
    if auth_type== AuthType.jwt.value:
        return KongAuth(app)
    elif auth_type== AuthType.session.value:
        return SessionAuth(app)
    else:
        assert False,'auth_type(%s) is not supoort!'%auth_type


def current_user():
    return g.user