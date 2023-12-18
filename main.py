from flask import Flask, redirect, render_template, url_for, request
from SQL_db import DataBase


app = Flask(__name__)
db = DataBase('database.db')


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", page='index', title='Головна - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about")
def about():
    return render_template('about/index.html', page='about', title='Про Ліцей - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/contacts")
def contacts():
    return render_template('contact/contact.html', page='contacts', title='Контакти - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/sign-in", methods=["GET", "POST"])
def sign_in():
    if request.method == "GET":
        return render_template('auth/sign_in.html', title='Увійти - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')
    elif request.method == "POST":
        
        return render_template('auth/sign_in.html', title='Увійти - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')
    

@app.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "GET":
        return render_template('auth/sign_up.html', title='Зареєструватися - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')
    elif request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        db.add_user(username, email, password)
        
        users = db.get_users()
        return f"{users}"  
    
    
@app.route("/heros")
def heros():
    return render_template("main/geroi.html", page='index', title='Герої не вмирають! - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about/history")
def history():
    return render_template('about/history.html', page='about', title='Історія Ліцею - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about/olympiads")
def olympiads():
    return render_template('about/olymp.html', page='about', title='Олімпіади та конкурси - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about/symbols")
def symbols():
    return render_template('about/symbol.html', page='about', title='Символіка Ліцею - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')
    



if __name__ == '__main__':
    app.run(debug=True, port=5555)
