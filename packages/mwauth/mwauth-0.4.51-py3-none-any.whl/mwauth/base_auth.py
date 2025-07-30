#encoding=utf8
from collections import namedtuple
User = namedtuple('User', ['uid', 'uname', 'systemuser','manageuser','manageuserid','companyid','phone','type'])

class BaseAuth(object):
    """docstring for ClassName"""
    #
    def init_app(self, app):
        pass

    def valid_login(self, func):
        pass
