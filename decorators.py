from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user
from app import app

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
