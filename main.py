from flask import redirect, render_template, url_for, request, flash, session
from flask_login import LoginManager, login_user, logout_user, current_user
from werkzeug.exceptions import abort, NotFound
from markupsafe import escape
from validation import Validator
from decorators import handle_error, check_auth
from core import upload_file
from models import Users
from app import app, db, site_db, titles


login_manager = LoginManager()
login_manager.init_app(app)

db.init_app(app)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def loader_user(user_id):
    return Users.query.get(user_id)


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
    title = titles.get_title('index')
    return render_template("index.html", page='index', title=title, news=news)


@app.route("/about")
def about():
    return render_template('about/index.html', page='about', title=titles.get_title('about'))


@app.route("/contacts")
def contacts():
    return render_template('contact/contact.html', page='contacts', title=titles.get_title('contacts'))


@app.route("/heroes")
def heros():
    return render_template("main/geroi.html", page='index', title=titles.get_title('heroes'))


@app.route("/about/history")
def history():
    return render_template('about/history.html', page='about', title=titles.get_title('history'))


@app.route("/about/olympiads")
def olympiads():
    olymp = site_db.get_olympiads()
    title = titles.get_title('olympiads')
    return render_template('about/olymp.html', 
                           page='about', 
                           title=title, 
                           olymp=olymp)


@app.route("/about/symbolics")
def symbols():
    return render_template('about/symbol.html', page='about', title=titles.get_title('symbolics'))


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

    return render_template("auth/sign_in.html", title=titles.get_title('login'))


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
        return render_template("auth/sign_up.html", title=titles.get_title('register'))


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
    title = titles.get_title('account')
    return render_template("profile/account.html",
                           title=title,
                           user_data=user_data,
                           page="account")


@app.route("/profile/edit", endpoint='edit_profile')
@app.route("/account/edit", endpoint='edit_profile')
@handle_error('account')
@check_auth
def edit_profile():
    app.logger.info(f"User '{session['username']}' is accessing the edit profile page.")
    title = titles.get_title('edit_profile')
    return render_template("profile/edit.html",
                           title=title,
                           page="edit_profile",
                           user=session)


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
        return render_template('profile/password.html',
                               page='change_pass',
                               title=titles.get_title('change_password'))

    
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
    title = titles.get_title('edit_news')
    app.logger.info(f"{request.remote_addr}-{session['username']} : accessing.")
    return render_template('editSite/news/news.html', news=news, edit_mode=True, title=title)


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

    return render_template('editSite/news/create.html', title=titles.get_title('create_news'))


@app.route("/site/edit/news/edit/<int:id>", methods=["POST", "GET"])
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

            else:
                title = titles.get_title('edit_news_post')
                return render_template('editSite/news/edit.html', post=post, title=title)

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
    title = titles.get_title('edit_olympiads')
    olymp = site_db.get_olympiads()
    app.logger.info(f"{request.remote_addr}-{session['username']} : accessing to edit olympiads.")
    return render_template('editSite/olympiads/olympiads.html',
                           olymp=olymp,
                           edit_mode=True,
                           title=title)


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

    return render_template('editSite/olympiads/create.html', title=titles.get_title('create_olympiad'))


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

            return render_template('editSite/olympiads/edit.html',
                                   post=post,
                                   title=titles.get_title('edit_olympiad_post'))
        
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
