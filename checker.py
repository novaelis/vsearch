from flask import render_template,session

from functools import wraps

def check_logged_in(func: object):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'logged_in' in session:
            return func(*args, **kwargs)
        return render_template('login.html', the_title='You are not log in!')
    return wrapper
