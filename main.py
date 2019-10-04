from flask import Flask
from flask import render_template, session, request, redirect
from db import Session
from db import set_coord, set_query, set_user, get_user, get_queries, get_coord, get_query, get_polygon_coords
from functional import clear_errors, init_session


db_session = Session()
app = Flask(__name__)
app.secret_key = '1234567'


@app.route('/', methods=['POST', 'GET'])
def main_page():
    if 'is_logged' in session:
        pass
    else:
        init_session(session)
    return render_template('main.html', session=session)


@app.route('/new-polygon', methods=['POST', 'GET'])
def add_task():
    clear_errors(session)
    if request.method == 'POST':
        set_query(session, request.form, db_session, request.files)
    return render_template('add-task.html', session=session)


@app.route('/sign-up-page', methods=['POST', 'GET'])
def registration():
    clear_errors(session)
    if request.method == 'POST':
        set_user(request.form, db_session, session)
    return render_template('sign-up-page.html', session=session)


@app.route('/sign-in-page', methods=['POST', 'GET'])
def sign_in():
    clear_errors(session)
    if request.method == 'POST':
        if request.form['nickname']:
            get_user(db_session, request.form['nickname'], request.form['password'], session)
        if session['is_logged']:
            return redirect('/new-polygon')
    return render_template('sign-in-page.html', session=session)


@app.route('/profile/<nickname>', methods=['POST', 'GET'])
def profile(nickname):
    last_queries = get_queries(db_session, session)
    print("LAST", last_queries)
    return render_template('profile.html', session=session, queries=last_queries, length=len(last_queries))


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/task/<int:task_id>')
def task(task_id):
    obj = get_query(db_session, session, task_id)
    x, y = get_polygon_coords(db_session, session, task_id)
    print(obj)
    return render_template('task.html', session=session, obj=obj, coordinates=(x, y))


if __name__ == '__main__':
    app.run(debug=True)

