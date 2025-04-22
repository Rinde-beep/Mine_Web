from flask import Flask, request, flash, redirect, session, make_response
import requests
import json
import sqlite3
from database import insert_orm_user, select_orm, create_db
from werkzeug.security import generate_password_hash, check_password_hash
from checks_and_session import ch_session, dl_session, check, check_pass, render_session, check_tech
from database import Users
from flask_login import LoginManager
from classes import UserLogin


print("Hello world!")
app = Flask(__name__)
app.config["SECRET_KEY"] = "abh183fkvm17302234ifldmxhvm129kk"
lm = LoginManager(app)


@app.route("/")
def main():
    # fact = json.loads((requests.get("https://catfact.ninja/fact?max_length=40")).text)["fact"]
    return render_session("ind.html")

@app.route("/info")
def info():
    return render_session("info.html")

@app.route("/rule")
def rule():
    return render_session("rule.html")

@app.route("/tech", methods=["POST", "GET"])
def tech():
    if request.method == "POST":
        if check_tech()[0]:
            flash(check_tech()[1], category='success')
        else:
            flash(check_tech()[1], category='error')
    return render_session("tech.html")

@app.route("/login", methods=["POST", "GET"])
def login(): 
    if not check():
        if request.method == "POST":
            name = request.form.get("login")
            passw = request.form.get("password")
            print(name, passw)
            if check_password_hash(select_orm(name, Users.password), passw):
                flash("Вы вошли", 'success')
                ch_session(name)
                return render_session("profile.html", name)
            else:
                flash("Неправильный логин или пароль", "error")
    else:
        return render_session("signout.html", session["login"], session["login"])
    return render_session("login.html")

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
                    return redirect(f"/login")
                else:
                    flash("Пароли не совпадают", "error")
            else:
                for i in check_pass(passw)[1]:
                    flash(i, "error")
    except:
        flash("Такой пользователь уже зарегистрирован", "error")
    return render_session("reg.html")

@app.route("/profile/<name>")
def profile(name):
    if name != session["login"]:
        return make_response("", 401)
    return render_session("profile.html", name)

@app.route("/signout/<name>")
def signout(name):
    dl_session()
    flash("Вы вышли", "error")
    return redirect("/login")
        
@lm.user_loader
def load_user(id):
    return UserLogin.get_name(id)


if __name__ == "__main__":
    create_db()
    app.run(debug=True)