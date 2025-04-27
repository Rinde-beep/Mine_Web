from flask import Flask, render_template, request, flash, redirect, session, make_response
import requests
import json
import sqlite3
from database import insert_orm_user, select_orm, create_db
from werkzeug.security import generate_password_hash, check_password_hash
from checks_and_session import check_pass, check_tech
from database import Users, insert_orm_post
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from classes import UserLogin


print("Hello world!")
app = Flask(__name__)
app.config["SECRET_KEY"] = "abh183fkvm17302234ifldmxhvm129kk"
lm = LoginManager(app)
lm.login_view = "login"
lm.login_message = "Авторизуйтесь чтобы войти в профиль"
lm.login_message_category = "error"

@app.route("/")
def main():
    # fact = json.loads((requests.get("https://catfact.ninja/fact?max_length=40")).text)["fact"]
    return render_template("ind.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/rule")
def rule():
    return render_template("rule.html")

@app.route("/tech", methods=["POST", "GET"])
def tech():
    if request.method == "POST":
        if check_tech()[0]:
            flash(check_tech()[1], category='success')
        else:
            flash(check_tech()[1], category='error')
    return render_template("tech.html")

@app.route("/login", methods=["POST", "GET"])
def login(): 
    if not current_user.is_authenticated:
        if request.method == "POST":
            name = request.form.get("login")
            passw = request.form.get("password")
            if check_password_hash(select_orm(name, Users.password), passw):
                flash("Вы вошли", 'success')
                userlogin = UserLogin().create(name)
                login_user(userlogin, remember=True)
                return redirect("/profile")
            else:
                flash("Неправильный логин или пароль", "error")
    else:
        return render_template("signout.html", gam=current_user.name)
    return render_template("login.html")

@app.route("/reg", methods=["POST", "GET"])
def reg():
    try:
        if request.method == "POST":
            name = request.form.get("name")
            passw = request.form.get("pass")
            passw_again = request.form["pass_again"]
            print(name, passw)
            if check_pass(passw)[0]:
                if passw == passw_again:
                    insert_orm_user(name, generate_password_hash(passw))
                    flash("Регистрация прошла успешно", "success")
                    return redirect("/login")
                else:
                    flash("Пароли не совпадают", "error")
            else:
                for i in check_pass(passw)[1]:
                    flash(i, "error")
    except:
        flash("Такой пользователь уже зарегистрирован", "error")
    return render_template("reg.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", log=current_user.name)

@app.route("/signout")
def signout():
    logout_user()
    flash("Вы вышли", "error")
    return redirect("/login")

@app.route("/upload", methods=["post", "get"])
def upload():
    image = sqlite3.Binary(request.files.get("file"))
    post = request.form.get("textarea")
    user = current_user.name
    if not image:
        insert_orm_post(post, user)
    else:
        insert_orm_post(post, user, image)

@app.route("/community")
def comm():
    return render_template("community.html")

@app.route("/post")
def post():
    return render_template("post.html")
        
@lm.user_loader
def load_user(id):
    print("Load user")
    return UserLogin().get_name(id)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)