from flask_login import LoginManager, UserMixin
from wtforms import FileField, PasswordField, StringField, SubmitField, TextAreaField
from database import select_orm, select_orm_equal
from database import Users
from flask_wtf import FlaskForm


class UserLogin:
    def get_name(self, id):
        self.name = select_orm_equal(id, Users.user)
        return self

    def create(self, name):
        self.name = name
        return self

    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(select_orm(self.name, Users.id))
    
class LoginForm(FlaskForm):
    password = PasswordField()
    login = StringField()
    submit = SubmitField("Войти")

class RegForm(LoginForm):
    password_2 = PasswordField()
    submit = SubmitField("Регистрация")

class PostForm(FlaskForm):
    image = FileField("Загрузи изображение")
    description = StringField()
    submit = SubmitField("Запостить")
