import os
import sqlite3

from flask import Flask, render_template, url_for, request, flash, redirect, session, abort, g

DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'ya_petuh_228'

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path, 'flsite.db')))

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row # представление таблицы в виде словаря
    return conn

def create_db():
    """ создание бд """
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()

def get_db():
    """соединение с бд, если ещё не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

menu = [{'name': 'Установка', 'url': 'install-flask'},
        {'name': 'Первое приложение', 'url': 'first-app'},
        {'name': 'Обратная связь', 'url': 'contact'}]


@app.teardown_appcontext # вызывается, когда уничтожается контекст приложения (в момент завершения обработки запроса)
def close_db(error):
    """закрываем соещинение с бд"""
    if hasattr(g, 'link_db'): # если в контексте приложения есть link_db
        g.link_db.close()

@app.route('/')
def index():
    db = get_db()
    return render_template('index.html', menu=menu)


@app.route('/contact', methods=['POST', 'GET'])
def contact():
    if request.method == 'POST':
        # print(request.form)
        if len(request.form['username']) > 2:
            flash('Сообщение отправлено', category='success')
        else:
            flash('Ошибка отправки', category='error')
    return render_template('contact.html', title='Обратная связь', menu=menu)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['username'] == 'selfedu' and request.form['psw'] == '123':
            session['userLogged'] = request.form['username']
            return redirect(url_for('profile', username=session['userLogged']))

    return render_template('login.html', title='Авторизация', menu=menu)

@app.route('/profile/<username>')
def profile(username):
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return f'Профиль {username}'

# with app.test_request_context():
#     print(url_for('index'))

@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title='Страница не найдена', menu=menu), 404


if __name__ == '__main__':
    app.run(debug=True)
