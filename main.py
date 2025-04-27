from flask import Flask, render_template, request, flash, redirect, session, make_response
import requests
import json
import sqlite3

import sqlalchemy
from database import get_image, get_liked, insert_orm_user, select_orm, create_db, select_posts, update_disliked, update_dislikes, update_liked, update_likes
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from checks_and_session import check_pass, check_tech, check_name, check_file
from database import Users, insert_orm_post
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from classes import PostForm, UserLogin, LoginForm, RegForm
import os


print("Hello world!")
app = Flask(__name__)
app.config["SECRET_KEY"] = "abh183fkvm17302234ifldmxhvm129kk"
app.config["UPLOAD_FOLDER"] = "../static/img"

ALLOWED_EXT = ("png", "jpg", "jpeg")
lm = LoginManager(app)
lm.login_view = "login"
lm.login_message = "Авторизуйтесь чтобы войти"
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
    form = LoginForm()
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            name = form.login.data
            passw = form.password.data
            print(name, passw)
            if check_password_hash(select_orm(name, Users.password), passw):
                flash("Вы вошли", 'success')
                userlogin = UserLogin().create(name)
                login_user(userlogin, remember=True)
                return redirect("/profile")
            else:
                flash("Неправильный логин или пароль", "error")
    else:
        return render_template("signout.html", gam=current_user.name)
    return render_template("login.html", form=form)

@app.route("/reg", methods=["POST", "GET"])
def reg():
    try:
        form = RegForm()
        if form.validate_on_submit():
            name = form.login.data
            passw = form.password.data
            passw_again = form.password_2.data
            print(name, passw)
            if check_pass(passw)[0] and check_name(name)[0]:
                if passw == passw_again:
                    insert_orm_user(name, generate_password_hash(passw))
                    flash("Регистрация прошла успешно", "success")
                    return redirect("/login")
                else:
                    flash("Пароли не совпадают", "error")
            else:
                if check_name(name)[1]:
                    flash(check_name(name)[1], "error")
                for i in check_pass(passw)[1]:
                    flash(i, "error")
                
    except sqlalchemy.exc.IntegrityError as e:
        print(e)
        flash("Такой пользователь уже зарегистрирован", "error")
    return render_template("reg.html", form=form)

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
@login_required
def upload():
    form = PostForm()
    if form.validate_on_submit:
        f = form.image
        file = request.files.get(f.name, None)
        if check_file(file.filename, ALLOWED_EXT):
            file = file.read()
            name = current_user.name
            post = form.description.data
            insert_orm_post(post, name, file)
        return redirect("/community")

@app.route("/community")
def comm():
    posts = select_posts()
    return render_template("community.html", posts=posts)


@app.route("/likes/<idx>")
@login_required
def likes(idx):
    print(idx)
    if current_user.name not in get_liked(idx).split(";"):
        print(get_liked(idx).split(";"))
        update_likes(idx)
        update_liked(idx)
        print(current_user.name + "-" * 36)
    else:
        print(get_liked(idx).split(";"))
        update_dislikes(idx) 
        update_disliked(idx)
        print(current_user.name + "-" * 36)
    return redirect("/community")

    

@app.route("/getimg/<idx>")
def getimg(idx):
    img = get_image(idx)
    if img:
        h = make_response(get_image(idx))
        h.headers["Content-Type"] = "image/png"
    else:
        h = ""
    return h
    


@app.route("/post")
@login_required
def post():
    form = PostForm()
    return render_template("post.html", form=form)
        
@lm.user_loader
def load_user(id):
    print("Load user")
    return UserLogin().get_name(id)

if __name__ == "__main__":
    create_db()
    app.run(debug=True)