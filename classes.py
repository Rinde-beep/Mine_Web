
import email
from pydantic import BaseModel, EmailStr, Field
from wtforms import EmailField, FileField, PasswordField, StringField, SubmitField, TextAreaField
from flask_wtf import FlaskForm
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BLOB
from ormdbs import select_orm_equal, select_from_orm, Posts, Users


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
        return str(select_from_orm(self.name, Users.id))
    
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

class TechForm(FlaskForm):
    login = StringField()
    email = EmailField()
    textarea = StringField()
    submit = SubmitField("Отправить")



# class UserSchema(BaseModel):
#     id: int
#     user: str = Field(min_length=4)
#     password: str = Field(min_length=4)


# class PostSchema(BaseModel):
#     id: int
#     post: str = Field(max_length=200)
#     imag: BLOB | None = Field(max_digits=1024)
#     user: str
#     likes: int = Field(ge=0)
#     likes: str

# class TicketShema(BaseModel):
#     user: str
#     email: EmailStr
#     ticket: str = Field(max_length=100)