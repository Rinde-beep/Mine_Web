from flask import Flask, Response, render_template, request, flash, redirect, session, make_response
import requests
import json
import sqlite3
import asyncio
import sqlalchemy
from ormdbs import get_image, get_liked, insert_orm_user, select_from_orm, create_db, select_posts, update_disliked, update_dislikes, update_liked, update_likes, Users, insert_orm_post
from werkzeug.security import generate_password_hash, check_password_hash
from checks_and_session import check_pass, check_tech, check_name, check_file
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from classes import PostForm, TechForm, UserLogin, LoginForm, RegForm
import os
from send_emails import send_email


print("Hello world!")
app = Flask(__name__)
app.config["SECRET_KEY"] = "abh183fkvm17302234ifldmxhvm129kk"
app.config["UPLOAD_FOLDER"] = "../static/img"

ALLOWED_EXT = ("png", "jpg", "jpeg")
lm = LoginManager(app)
lm.login_view = "login"
lm.login_message = "Авторизуйтесь чтобы получить доступ"
lm.login_message_category = "error"

@app.route("/")
def main() -> Response:
    return render_template("ind.html")

@app.route("/info")
def info() -> Response:
    return render_template("info.html")

@app.route("/rule")
def rule() -> Response:
    return render_template("rule.html")

@app.route("/tech", methods=["POST", "GET"])
def tech() -> Response:
    form = TechForm()
    if form.validate_on_submit():
        ticket = form.textarea.data
        print("-------------------------------------------------")
        if check_tech(ticket)[0]:
            flash(check_tech(ticket)[1], category='success')
            send_email(form.email.data, form.login.data)
        else:
            flash(check_tech(ticket)[1], category='error')
        return redirect("/tech")
    return render_template("tech.html", form=form)

@app.route("/login", methods=["POST", "GET"])
def login() -> Response: 
    form = LoginForm()
    if not current_user.is_authenticated:
        if form.validate_on_submit():
            name = form.login.data
            passw = form.password.data
            print(name, passw)
            passch = select_from_orm(name, Users.password)
            try:
                if check_password_hash(passch, passw):
                    flash("Вы вошли", 'success')
                    userlogin = UserLogin().create(name)
                    login_user(userlogin, remember=True)
                    return redirect("/profile")
                else:
                    flash("Неправильный логин или пароль", "error")
            except AttributeError:
                flash("Пользователь не найден", "error")
    else:
        return render_template("signout.html", gam=current_user.name)
    return render_template("login.html", form=form)

@app.route("/reg", methods=["POST", "GET"])
def reg() -> Response:
    form = RegForm()
    if form.validate_on_submit():
        name = form.login.data
        passw = form.password.data
        passw_again = form.password_2.data
        print(name, passw)
        if check_pass(passw)[0] and check_name(name)[0]:
            if passw == passw_again:
                try:
                    insert_orm_user(name, generate_password_hash(passw))
                    flash("Регистрация прошла успешно", "success")
                    return redirect("/login")
                except sqlalchemy.exc.IntegrityError:
                    flash("Такой пользователь уже зарегистрирован", "error")
            else:
                flash("Пароли не совпадают", "error")
        else:
            bol, flas = check_name(name)
            if flas:
                flash(flas, "error")
            for i in check_pass(passw)[1]:
                flash(i, "error")
    return render_template("reg.html", form=form)

@app.route("/profile")
@login_required
def profile() -> Response:
    balance = select_from_orm(current_user.name, Users.balance)
    status = select_from_orm(current_user.name, Users.status)
    return render_template("profile.html", log=current_user.name, balance=balance, status=status)

@app.route("/signout")
def signout() -> Response:
    logout_user()
    flash("Вы вышли", "error")
    return redirect("/login")

@app.route("/upload", methods=["post", "get"])
@login_required
def upload() -> Response:
    form = PostForm()
    if form.validate_on_submit:
        f = form.image
        file = request.files.get(f.name, None)
        if check_file(file.filename, ALLOWED_EXT)[0]:
            file = file.read()
            name = current_user.name
            post = form.description.data
            insert_orm_post(post, name, file)
        else:
            for i in check_file(file.filename, ALLOWED_EXT)[1]:
                flash(i, "error")         
            return redirect("/post")
        return redirect("/community")

@app.route("/community")
def comm() -> Response:
    posts = select_posts()
    return render_template("community.html", posts=posts)


@app.route("/likes/<idx>")
@login_required
def likes(idx: int) -> Response:
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
def getimg(idx: int) -> Response:
    img = get_image(idx)
    if img:
        h = make_response(img)
        h.headers["Content-Type"] = "image/png"
    else:
        h = ""
    return h
    
@app.route("/post")
@login_required
def post() -> Response:
    form = PostForm()
    return render_template("post.html", form=form)
        
@lm.user_loader
def load_user(id: int) -> Response:
    print("Load user")
    return UserLogin().get_name(id)

@app.errorhandler(404)
def error404(error: Exception) -> Response:
    return render_template("error404.html")

@app.route("/history")
def history() -> Response:
    return render_template("history.html")

@app.route("/download")
def download() -> Response:
    return render_template("download.html")


if __name__ == "__main__":
    create_db()
    app.run(debug=True)
