from flask import session, render_template, request
from flask_login import current_user

    
def check_pass(password):
    spec = "!@#$%^&*"
    num = "1234567890"
    words = "ABCDEFGHIJKLMNOPQRSTUYXWZV"
    check = {}
    if password:
        if len(password) >= 8:
            check["Пароль не меньше 8 символов"] = True
        else:
            check["Пароль не меньше 8 символов"] = False
        for i in spec:
            if i in password:
                check["Хотя бы один специальный символ"] = True
                break
            else:
                check["Хотя бы один специальный символ"] = False

        for i in num:
            if i in password:
                check["Хотя бы одна цифра"] = True
                break
            else:
                check["Хотя бы одна цифра"] = False

        for i in words:
            if i in password:
                check["Хотя бы одна заглавная буква"] = True
                break
            else:
                check["Хотя бы одна заглавная буква"] = False
        
        if all([x for x in check.values()]):
            return True, []
        else:
            return False, [x for x in check.keys() if check[x] == False]
    else:
        return False, ["Пароль не должен быть пуст"]
    
def check_name(name):
    if name:
        if len(name) >= 4:
            return True, ""
        else:
            return False, "Имя должно быть больше 4 символов"
    else:
        return False, "Имя не должно быть пустым"
    
def check_file(file, allowed):
    print(file)
    if file.rsplit(".", 1)[1] in allowed:
        return True

def check_tech():
    if not current_user.is_authenticated:
        return False, "Зарегистрируйтесь, чтобы отправить"
    
    elif not request.form.get("comment"):
        return False, "Тикет не должен быть пустой"
    
    else:
        return True, "Тикет успешно отправлен"
    



    