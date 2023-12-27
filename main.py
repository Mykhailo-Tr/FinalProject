from flask import Flask, redirect, render_template, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort, NotFound
from werkzeug.utils import secure_filename
from markupsafe import escape
from SQL_db import DataBase
from validation import Validator
import logging
import os


logging.basicConfig(level=logging.INFO)


UPLOAD_FOLDER = '/static/img'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


app = Flask(__name__)
site_db = DataBase('database.db')
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///db.sqlite"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "abc"
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.username


db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
           
           
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(f"static/img/{filename}")
        img_path = f"img/{filename}"
        return img_path


def logout():
    """Log out the user."""
    session['isLogged'] = False
    session['username'] = None
    session['password'] = None
    session['email'] = None


@app.route("/home")
@app.route("/index")
@app.route("/")
def index():
    news = site_db.get_news()
    return render_template("index.html", page='index', title='Головна - РОГАТИНСЬКИЙ ЛІЦЕЙ №1', news=news)


@app.route("/about")
def about():
    return render_template('about/index.html', page='about', title='Про Ліцей - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/contacts")
def contacts():
    return render_template('contact/contact.html', page='contacts', title='Контакти - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/heros")
def heros():
    return render_template("main/geroi.html", page='index', title='Герої не вмирають! - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about/history")
def history():
    return render_template('about/history.html', page='about', title='Історія Ліцею - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/about/olympiads")
def olympiads():
    olymp = site_db.get_olympiads()
    print(olymp)
    return render_template('about/olymp.html', 
                           page='about', 
                           title='Олімпіади та конкурси - РОГАТИНСЬКИЙ ЛІЦЕЙ №1', 
                           olymp=olymp)


@app.route("/about/symbols")
def symbols():
    return render_template('about/symbol.html', page='about', title='Символіка Ліцею - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/login", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        username = request.form.get("username")
        user = Users.query.filter_by(username=username).first()
        print(user)
        if user:
            if user.password == request.form.get("password"):
                login_user(user)
                session['isLogged'] = True
                session["username"] = request.form.get("username")
                session["password"] = request.form.get("password")
                session["email"] = Users.query.filter_by(username=session.get("username")).first().email
                return redirect(url_for("account"))
            else:
                flash("Wrong password!")
                redirect(url_for('sign_in'))
        else:
            flash("Wrong username!")
            redirect(url_for('sign_in'))

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
def logout_from_account():
    logout_user()
    logout()
    return redirect(url_for("index"))


@app.route("/account")
def account():
    if current_user.is_authenticated:
        user_data = {"username": session["username"]}
        return render_template("profile/account.html", title="Account home page", user_data=user_data, page="account")
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))


@app.route("/profile/edit")
@app.route("/account/edit")
def edit_profile():
    if current_user.is_authenticated:
        return render_template("profile/edit.html", title="Edit Profile", page="edit_profile", user=session)
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))


@app.route("/profile/update", methods=["GET", "POST"])
@app.route("/account/update", methods=["GET", "POST"])
def update_profile():
    if current_user.is_authenticated:
        if request.method == "POST":
            try:
                old_username = session.get("username")
                new_username = request.form.get("username")
                new_email = request.form.get("email")

                Users.query.filter_by(username=old_username).update(
                    dict(email=new_email, username=new_username))

                session["username"] = new_username
                session["email"] = new_email
                db.session.commit()
                flash("User Updated Successfully! ")
                return redirect(url_for('account'))
            except Exception as error:
                flash(f"Error: {error}")
                return redirect(url_for('edit_profile'))
        else:
            return redirect(url_for('edit_profile'))
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))


@app.route("/profile/change_password", methods=["GET", "POST"])
@app.route("/account/change_password", methods=["GET", "POST"])
def change_password():
    if current_user.is_authenticated:
        if request.method == "POST":
            try:
                old_password = session.get("password")
                new_password = request.form.get("password")
                username = session.get("username")

                if old_password == new_password:
                    raise ValueError("New password cannot be the same as your current password.")

                Users.query.filter_by(username=username).update(
                    dict(password=new_password))

                db.session.commit()

                flash("Password Updated Successfully!")
                return redirect(url_for('account'))

            except ValueError as error:
                flash(f"{error}")
                return redirect(url_for('change_password'))

            except Exception as error:
                flash(f"Error: {error}")
                return redirect(url_for('change_password'))

        elif request.method == "GET":
            return render_template('profile/password.html', page='change_pass')

    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    
    
@app.route("/profile/delete")
@app.route("/account/delete")
def delete_account():
    if current_user.is_authenticated:
        Users.query.filter_by(username=session['username']).delete()
        logout_user()
        logout()
        db.session.commit()
        flash("Your account deleted!")
        return redirect(url_for("index"))
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    
    
@app.route("/site/edit/news")
def edit_news():
    if current_user.is_authenticated:
        news = site_db.get_news()
        return render_template('editSite/news/news.html', news=news, edit_mode=True)
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    
    
@app.route('/site/edit/news/create', methods=['GET', 'POST'])
def create_news():
    if current_user.is_authenticated:
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            img_path = upload_file()
            if type(img_path) not in (str, None):
                return img_path
              
            if not title:
                flash('Title is required!')
            else:
                site_db.add_news(title, content, img_path)
                return redirect(url_for('edit_news'))

        return render_template('editSite/news/create.html')
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))


@app.route("/site/edit/news/edit/<int:id>" , methods=["POST", "GET"])
def edit_news_post(id):
    if current_user.is_authenticated:
        post = site_db.get_news_post(id)

        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')

            if not title:
                flash('Title is required!')
            else:
                site_db.update_news(id, title, content)
                return redirect(url_for('edit_news'))

        return render_template('editSite/news/edit.html', post=post)

    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    
    
@app.route("/site/edit/news/delete/<int:id>", methods=["POST"])
def delete_news(id):
    if current_user.is_authenticated:
        post = site_db.get_news_post(id)
        site_db.delete_news_post(id)
        flash('"{}" was successfully deleted!'.format(post[2]))
        return redirect(url_for('edit_news'))
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))



@app.route("/site/preview/news")
def preview_news():
    if current_user.is_authenticated:
        news = site_db.get_news()
        return render_template('editSite/news/news.html', news=news, edit_mode=True)
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in")) 
    
    
@app.route("/site/edit/olympiads")
def edit_olymp():
    if current_user.is_authenticated:
        olymp = site_db.get_olympiads()
        return render_template('editSite/olympiads/olympiads.html', olymp=olymp, edit_mode=True)
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    

@app.route('/site/edit/olympiads/create', methods=['GET', 'POST'])
def create_olymp():
    if current_user.is_authenticated:
        if request.method == 'POST':
            content = request.form.get('content')
            
            img_path = upload_file()
            if type(img_path) not in (str, None):
                return img_path
              
            if not content:
                flash('Content is required!')
            else:
                site_db.add_olympiad(content, img_path)
                return redirect(url_for('edit_olymp'))

        return render_template('editSite/olympiads/create.html')
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    

@app.route("/site/edit/olympiads/edit/<int:id>" , methods=["POST", "GET"])
def edit_olymp_post(id):
    if current_user.is_authenticated:
        post = site_db.get_olympiad_post(id)

        if request.method == 'POST':
            content = request.form.get('content')

            if not content:
                flash('Content is required!')
            else:
                site_db.update_olympiad(id, content)
                return redirect(url_for('edit_olymp'))

        return render_template('editSite/olympiads/edit.html', post=post)

    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))
    
    
@app.route("/site/edit/olympiads/delete/<int:id>", methods=["POST"])
def delete_olymp(id):
    if current_user.is_authenticated:
        post = site_db.get_olympiad_post(id)
        site_db.delete_olympiad_post(id)
        flash('"{}" was successfully deleted!'.format(post[2]))
        return redirect(url_for('edit_olymp'))
    else:
        flash("You are not logged in!")
        return redirect(url_for("sign_in"))

    
    
    
    

        

if __name__ == '__main__':
    app.run(debug=True, port=5555)
