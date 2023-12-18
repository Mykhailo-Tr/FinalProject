from flask import Flask, redirect, render_template, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort
from SQL_db import DataBase
from validation import Validator


app = Flask(__name__)
# db = DataBase('database.db')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


db.init_app(app)


with app.app_context():
	db.create_all()
 
 
@login_manager.user_loader
def loader_user(user_id):
	return Users.query.get(user_id)

@app.route("/home")
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


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        user = Users.query.filter_by(
        username=request.form.get("username")).first()
        if user.password == request.form.get("password"):
            login_user(user)
            return redirect(url_for("index"))
        
    return render_template("auth/sign_in.html")
    

@app.route("/register", methods=["GET", "POST"])
def sign_up():    
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        try:
            user_data = Validator(username=username, email=email, password=password)
        except ValueError as error:
            flash(f"{error}")
            return redirect(url_for("sign_up"))
        except Exception as error:
            flash(f"Error: {error}")
            return redirect(url_for("sign_up"))
        else:
            try:
                user = Users(username=user_data.username,
                            email=user_data.email,
                            password=user_data.password)
                db.session.add(user)
                db.session.commit()
            except Exception as error:
                flash(f"Error: {error}")
                return redirect(url_for("sign_up"))
            else:
                return redirect(url_for("sign_in"))

    else:
        return render_template("auth/sign_up.html", title='Зареєструватися - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for("index"))


@app.route("/account")
def account():
    if current_user.is_authenticated:
        return render_template("profile/account.html", title="Account home page")
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))

    
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
