from flask import session, render_template, request


def ch_session(ch):
    session["login"] = ch

def dl_session():
    session.pop("login")

def check():
    if session.get('login', False) != False:
        return True
    else:
        return False
    
def check_pass(password):
    spec = "!@#$%^&*"
    num = "1234567890"
    words = "ABCDEFGHIJKLMNOPQRSTUYXWZV"
    check = {}
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
    check["Хотя бы одна заглавная буква"] = True

def render_session(url, log=None, gam=None):
    if check():
        if log:
            if gam:
                return render_template(url, name=f"/profile/{session['login']}", log=log, gam=gam)
            else:
                return render_template(url, name=f"/profile/{session['login']}", log=log)
        else:
            return render_template(url, name=f"/profile/{session['login']}")
    else:
        return render_template(url, name="/login")
    
def check_tech():
    if not check():
        return False, "Зарегистрируйтесь, чтобы отправить"
    
    elif not request.form.get("comment"):
        return False, "Тикет не должен быть пустой"
    
    else:
        return True, "Тикет успешно отправлен"
    



    