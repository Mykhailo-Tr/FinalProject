from flask import Flask, redirect, render_template, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.exceptions import abort, NotFound
from werkzeug.utils import secure_filename
from markupsafe import escape
from functools import wraps
from SQL_db import DataBase
from validation import Validator
from logger import logger
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DATABASE_FILE, SQLALCHEMY_DATABASE


app = Flask(__name__)
app.logger = logger
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SECRET_KEY"] = "abc"
site_db = DataBase(DATABASE_FILE)
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.init_app(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return f'<User {self.username}, {self.email}>'


db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


def handle_error(error_page = 'index'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            
                try:
                    return func()
                except ValueError as error:
                    app.logger.error(f"ValueError: {error}")
                    flash(f"ValueError: {error}")
                    return redirect(url_for(error_page))
                except Exception as error:
                    app.logger.error(f"Error during page access: {error}")
                    flash(f"ValueError: {error}")
                    return redirect(url_for(error_page))

        return wrapper
    return decorator


def check_auth(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if current_user.is_authenticated:
            return func()
        else:
            app.logger.warning(f"{request.remote_addr}: Unauthorized access to page. Redirecting to sign_in.")
            flash("You are not logged in!")
            return redirect(url_for("sign_in"))
        
    return inner



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
        app.logger.info(f"Attempting to sign in user: {username}")

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
                app.logger.warning(f"Failed login attempt for user '{username}' due to wrong password.")
                redirect(url_for('sign_in'))
        else:
            flash("Wrong username!")
            app.logger.warning(f"Failed login attempt for user '{username}' due to wrong username.")
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
            app.logger.warning(f"Registration failed for user '{username}' due to validation error.")
            return redirect(url_for("sign_up"))
        except Exception as error:
            flash(f"Error: {error}")
            app.logger.error(f"Error during user registration: {error}")
            return redirect(url_for("sign_up"))
        else:
            try:
                user = Users(username=user_data.username,
                             email=user_data.email,
                             password=user_data.password)
                db.session.add(user)
                db.session.commit()
                app.logger.info(f"User '{username}' successfully registered.")
            except Exception as error:
                flash(f"Error: {error}")
                app.logger.error(f"Error during user registration: {error}")
                return redirect(url_for("sign_up"))
            else:
                return redirect(url_for("sign_in"))

    else:
        return render_template("auth/sign_up.html", title='Зареєструватися - РОГАТИНСЬКИЙ ЛІЦЕЙ №1')


@app.route("/logout")
def logout_from_account():
    try:
        logout_user()
        logout()
        app.logger.info("User successfully logged out.")
    except Exception as error:
        app.logger.error(f"Error during logout: {error}")
    return redirect(url_for("index"))


@app.route("/account", endpoint='account')
@handle_error('index')
@check_auth
def account():
    user_data = {"username": session["username"]}
    app.logger.info(f"User '{session['username']}' is accessing their account page.")
    return render_template("profile/account.html", title="Account home page", user_data=user_data, page="account")




@app.route("/profile/edit", endpoint='edit_profile')
@app.route("/account/edit", endpoint='edit_profile')
@handle_error('account')
@check_auth
def edit_profile():
    app.logger.info(f"User '{session['username']}' is accessing the edit profile page.")
    return render_template("profile/edit.html", title="Edit Profile", page="edit_profile", user=session)



@app.route("/profile/update", methods=["GET", "POST"])
@app.route("/account/update", methods=["GET", "POST"])
@handle_error('account')
@check_auth
def update_profile():
    if request.method == "POST":
        old_username = session.get("username")
        old_email = session.get("email")
        new_username = request.form.get("username")
        new_email = request.form.get("email")

        user = Users.query.filter_by(username=old_username)
        user.update(dict(email=new_email, username=new_username))

        session["username"] = new_username
        session["email"] = new_email
        db.session.commit()
        app.logger.info(f"{new_username}, {new_email} updated profile successfully, old data: {old_username}, {old_email} ")
        flash("User Updated Successfully! ")
        return redirect(url_for('account'))
    else:
        return redirect(url_for('edit_profile'))




@app.route("/profile/change_password", methods=["GET", "POST"])
@app.route("/account/change_password", methods=["GET", "POST"])
@handle_error('change_password')
@check_auth
def change_password():
    if request.method == "POST":
        old_password = session.get("password")
        new_password = request.form.get("password")
        username = session.get("username")

        if old_password == new_password:
            raise ValueError("New password cannot be the same as your current password.")

        Users.query.filter_by(username=username).update(
            dict(password=new_password))

        db.session.commit()

        app.logger.info(f"User '{username}' changed their password successfully. {old_password} : {new_password}")
        flash("Password Updated Successfully!")
        return redirect(url_for('account'))

    elif request.method == "GET":
        return render_template('profile/password.html', page='change_pass')

    
@app.route("/profile/delete")
@app.route("/account/delete")
@handle_error('account')
@check_auth
def delete_account():
    Users.query.filter_by(username=session['username']).delete()
    logout_user()
    logout()
    db.session.commit()
    app.logger.info(f"{request.remote_addr}-{session['username']} : deleted account!")
    flash("Your account deleted!")
    return redirect(url_for("index"))


    
@app.route("/site/edit/news")
@handle_error('account')
@check_auth
def edit_news():
    news = site_db.get_news()
    app.logger.info(f"{request.remote_addr}-{session['username']} : accessing.")
    return render_template('editSite/news/news.html', news=news, edit_mode=True)

    
    
@app.route('/site/edit/news/create', methods=['GET', 'POST'])
@handle_error('account')
@check_auth
def create_news():
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
            flash(f"Created new news: {title}")
            app.logger.info(f"{request.remote_addr}-{session['username']} : created news : [title: {title}, img: {img_path}]")
            return redirect(url_for('edit_news'))


    return render_template('editSite/news/create.html')


@app.route("/site/edit/news/edit/<int:id>" , methods=["POST", "GET"])
def edit_news_post(id):
    try:
        if current_user.is_authenticated:
            post = site_db.get_news_post(id)

            if request.method == 'POST':
                title = request.form.get('title')
                content = request.form.get('content')

                if not title:
                    flash('Title is required!')
                else:
                    site_db.update_news(id, title, content)
                    app.logger.info(f"{request.remote_addr}-{session['username']} : edited news : [title: {title}, id: {id}]")
                    return redirect(url_for('edit_news'))

            return render_template('editSite/news/edit.html', post=post)
        else:
            app.logger.warning(f"{request.remote_addr}: Unauthorized access to page. Redirecting to sign_in.")
            flash("You are not logged in!")
            return redirect(url_for("sign_in"))
    except ValueError as error:
        app.logger.error(f"ValueError: {error}")
        print(error)
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
    except Exception as error:
        app.logger.error(f"Error during page access: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
        
 
@app.route("/site/edit/news/delete/<int:id>", methods=["POST"])
def delete_news(id):
    try:
        if current_user.is_authenticated:
            post = site_db.get_news_post(id)
            site_db.delete_news_post(id)
            flash('"{}" was successfully deleted!'.format(post[2]))
            app.logger.info(f"{request.remote_addr}-{session['username']} : deleted news <id: {id}>")
            return redirect(url_for('edit_news'))
        else:
            app.logger.warning(f"{request.remote_addr}: Unauthorized access to page. Redirecting to sign_in.")
            flash("You are not logged in!")
            return redirect(url_for("sign_in"))
        
    except ValueError as error:
        app.logger.error(f"ValueError: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
    except Exception as error:
        app.logger.error(f"Error during page access: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
        


@app.route("/site/preview/news")
@handle_error('account')
@check_auth
def preview_news():
    news = site_db.get_news()
    return render_template('editSite/news/news.html', news=news, edit_mode=True)

    
@app.route("/site/edit/olympiads")
@handle_error('account')
@check_auth
def edit_olymp():
    olymp = site_db.get_olympiads()
    app.logger.info(f"{request.remote_addr}-{session['username']} : accessing to edit olympiads.")
    return render_template('editSite/olympiads/olympiads.html', olymp=olymp, edit_mode=True)


@app.route('/site/edit/olympiads/create', methods=['GET', 'POST'])
@handle_error('account')
@check_auth
def create_olymp():
    if request.method == 'POST':
        content = request.form.get('content')
        
        img_path = upload_file()
        if type(img_path) not in (str, None):
            return img_path
            
        if not content:
            flash('Content is required!')
        else:
            site_db.add_olympiad(content, img_path)
            flash(f"Created olympiad content: {content}")
            app.logger.info(f"{request.remote_addr}-{session['username']} : created olympiad img: {img_path}")
            return redirect(url_for('edit_olymp'))

    return render_template('editSite/olympiads/create.html')

    

@app.route("/site/edit/olympiads/edit/<int:id>" , methods=["POST", "GET"])
def edit_olymp_post(id):
    try:
        if current_user.is_authenticated:
            post = site_db.get_olympiad_post(id)

            if request.method == 'POST':
                content = request.form.get('content')

                if not content:
                    flash('Content is required!')
                else:
                    site_db.update_olympiad(id, content)
                    flash(f"Edited olympiad")
                    app.logger.info(f"{request.remote_addr}-{session['username']} : edited olympiad <id: {id}>")
                    return redirect(url_for('edit_olymp'))

            return render_template('editSite/olympiads/edit.html', post=post)
        
        else:
            app.logger.warning(f"{request.remote_addr}: Unauthorized access to page. Redirecting to sign_in.")
            flash("You are not logged in!")
            return redirect(url_for("sign_in"))
        
    except ValueError as error:
        app.logger.error(f"ValueError: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
    
    except Exception as error:
        app.logger.error(f"Error during page access: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
        
    
@app.route("/site/edit/olympiads/delete/<int:id>", methods=["POST"])
def delete_olymp(id):
    try:
        if current_user.is_authenticated:
            post = site_db.get_olympiad_post(id)
            site_db.delete_olympiad_post(id)
            flash('"{}" was successfully deleted!'.format(post[2]))
            app.logger.info(f"{request.remote_addr}-{session['username']} : deleted olympiad <id: {id}>")
            return redirect(url_for('edit_olymp'))
        
        else:
            app.logger.warning(f"{request.remote_addr}: Unauthorized access to page. Redirecting to sign_in.")
            flash("You are not logged in!")
            return redirect(url_for("sign_in"))
        
    except ValueError as error:
        app.logger.error(f"ValueError: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))
    
    except Exception as error:
        app.logger.error(f"Error during page access: {error}")
        flash(f"ValueError: {error}")
        return redirect(url_for('account'))



if __name__ == '__main__':
    app.run(debug=True, port=5555)
