from flask import session, render_template, request
from flask_login import current_user

    
def check_pass(password: str) -> tuple[bool, list[str]]:
    spec = "!@#$%^&*"
    num = "1234567890"
    words = "ABCDEFGHIJKLMNOPQRSTUYXWZVЙЦУКЕНГШЩЗЗХЪФЫВАПРОЛДЖЖЖЭЯЧСМИТЬБЮЁ"
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
    
def check_name(name: str) -> tuple[bool, str]:
    if name:
        if len(name) >= 4:
            return True, ""
        else:
            return False, "Имя должно быть больше 4 символов"
    else:
        return False, "Имя не должно быть пустым"
    
def check_file(file: str, allowed: tuple[str, ...]) -> tuple[bool, list[str]]:
    check = {}
    print(len(file))
    if file.rsplit(".", 1)[1] == "png":
        check["Файл должен быть расширения .png"] = True
    else:
        check["Файл должен быть расширения .png"] = False

    if len(file) <= 20:
        check["Файл слишком большой"] = True
    else:
        check["Файл слишком большой"] = False
    if all([x for x in check.values()]):
        return True, []
    else:
        return False, [x for x in check.keys() if check[x] == False]

def check_tech(ticket: str) -> tuple[bool, str]:
    if not current_user.is_authenticated:
        return False, "Зарегистрируйтесь, чтобы отправить"
    
    elif not ticket:
        return False, "Тикет не должен быть пустой"
    
    else:
        return True, "Тикет успешно отправлен"
    



    