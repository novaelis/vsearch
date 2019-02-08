from flask import Flask, render_template, request, escape, session, copy_current_request_context

from search_for_vowels import search_for_letters

from DBcm import UseDatabase, ConnectionError, CredentialsError, SQLError
from checker import check_logged_in

from time import sleep

from threading import Thread
#import mysql.connector

app = Flask(__name__)

app.config['dbconfig'] = { 'host': '127.0.0.1',
                           'user': 'vsearch2',
                           'password': 'vsearchpass',
                           'database': 'vsearchlogDB', }

app.secret_key = 'NekiZajeban'

@app.route('/login', methods=['GET','POST'])
def do_login() -> 'html':
    username = request.form['username']
    password = request.form['password']
    if request.form['submit_button'] == 'Log in!':
        if does_exist_in_mysql(username, password):
            session['logged_in'] = True
            return view_the_log()
        else:
            return render_template('login_user_dont_exist.html',
                                   the_title='ERROR LOGIN')
    elif request.form['submit_button'] == 'Sign up!':
        insertovanje_usera_u_bazu(request)
        return render_template('confirmation_sign_up.html',
                               the_title = 'CONFIRMATION OF SIGN UP!',
                               the_username = username,
                               the_password = password)
        
def does_exist_in_mysql(username: str, password: str) -> bool:
    """Send query to base so it can check does user and pass exist in there"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """select id from user where username = %s and password = %s"""
        cursor.execute(_SQL, (username, password))
        answer = cursor.fetchall()
        return answer

def insertovanje_usera_u_bazu(req: 'flash_request'):
    """Ubacivanje usera u bazu tako sto se preuzme request objekat"""
    with UseDatabase(app.config['dbconfig']) as cursor:
        _SQL = """insert into user
                  (username, password)
                  values
                  (%s, %s)"""
        cursor.execute(_SQL, (req.form['username'],
                              req.form['password']))

@app.route('/logout', methods = ['GET','POST'])
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are now logged out'


@app.route('/search4', methods=['GET','POST'])
def do_search() -> 'html':
    phrase = request.form['phrase']
    letters = request.form['letters']
    results = str(search_for_letters(phrase,letters))
    @copy_current_request_context
    def log_request(req: 'flask_request', res: str) -> None:
        """Log details of the web request and the results."""
        #raise Exception("Something awful just happened.")
        #sleep(15)
        try:
            with UseDatabase(app.config['dbconfig']) as cursor:
                _SQL = """insert into log
                          (phrase, letters, ip, browser_string, results)
                          values
                          (%s, %s, %s, %s, %s)"""
                cursor.execute(_SQL, (req.form['phrase'],
                                      req.form['letters'],
                                      req.remote_addr,
                                      req.user_agent.browser,
                                      res))
        except ConnectionError as err:
            print('Is your database switched on? Error:', str(err))
        except CredentialsError as err:
            print('Is your credentials correct? Error:', str(err))
        except SQLError as err:
            print('Is your query correct? Error:', str(err))
        except Exception as err:
            print('Something went wrong:', str(err))
        return 'Error'
            
    try:
        #log_request(request,results)
        t = Thread(target=log_request, args=(request,results))
        t.start()
    except Exception as err:
        print('***** Logging failed with this error.', str(err))
    title = 'Here are your results:'
    return render_template('results.html',
                           the_results = results,
                           the_phrase = phrase,
                           the_letters = letters,
                           the_title=title)

@app.route('/viewlog')
@check_logged_in
def view_the_log() -> 'html':
    """Display the contents of the log file as a HTML table."""
    try:
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """select phrase, letters, ip, browser_string, results
                      from log """
            cursor.execute(_SQL)
            contents = cursor.fetchall()
            titles = ('Phrase', 'Letters', 'Remote_addr','User_agent','Results')
            return render_template('viewlog.html',
                                   the_title = 'View Log',
                                   the_row_titles = titles,
                                   the_data = contents)
    except ConnectionError as err:
        print('Is your database switched on? Error:', str(err))
        #return 'Is your database switched on? Error: '+ str(err)
    except CredentialsError as err:
        print('Is your credentials right? Error:', str(err))
        #return 'Is your credentials right? Error:'+ str(err)
    except SQLError as err:
        print('Is your query correct? Error:', str(err))
        #return 'Is your query correct? Error:'+ str(err)
    except Exception as err:
        print('Something went wrong:', str(err))
        #return 'Something went wrong:'+ str(err)
    return 'Error'


@app.route('/delete')
@check_logged_in
def delete_page() -> 'html':
    return render_template('delete.html', the_title='BRISANJE')

@app.route('/delete_action', methods=['GET', 'POST'])
def delete_all() -> None:
    if request.form['submit_button'] == 'Delete log items!':
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """DELETE FROM log"""
            cursor.execute(_SQL)
            return render_template('confirmation_delete.html')
    elif request.form['submit_button'] == 'Delete user items!':
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """DELETE FROM user"""
            cursor.execute(_SQL)
            return render_template('confirmation_delete.html')

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html', the_title='Welcome to search4letters in the web!')

if __name__ == '__main__':
    app.run(debug=True)

