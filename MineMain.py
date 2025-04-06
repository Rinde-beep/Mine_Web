from flask import Flask, render_template, request, flash
import requests
import json

print("Hello world!")
app = Flask(__name__)



app.config["SECRET_KEY"] = "SDFSFJDhfofsf"
@app.route("/")
def main():
    fact = json.loads((requests.get("https://catfact.ninja/fact?max_length=40")).text)["fact"]
    return render_template("ind.html", http=fact)

@app.route("/info")
def info():
    return render_template("info.html")
@app.route("/tech", methods=["POST", "GET"])
def tech():
    if request.method == "POST":
        if len(request.form["name"]) > 2:
            flash("Тикет отправлен", category='success')
        else:
            flash("Ошибка отправки", category='error')

    return render_template("tech.html")
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        flash("Неправильный логин или пароль", "error")
    return render_template("login.html")

if __name__ == "__main__":
    app.run()