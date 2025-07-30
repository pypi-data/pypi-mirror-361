class BaseUser(object):
    def get_password(self):
        pass
    def check(self,password):
        pass
    def make(self,password):
        pass
    def to_json(self):
        pass
    @staticmethod
    def FindUser(username):
        pass