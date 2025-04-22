from flask_login import LoginManager, UserMixin
from database import select_orm, select_orm_equal
from database import Users

class UserLogin(UserMixin):
    def get_name(self, id):
        self.name = select_orm_equal(id, Users.id)

    def create(self, name):
        self.name = name

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(select_orm(self.name, Users.id))