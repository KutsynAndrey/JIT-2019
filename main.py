from flask import Flask
from flask import render_template, session, request, redirect
from db import Session, fill_session, clear_errors
from db import set_coord, set_query, set_user, get_user, get_query, get_coord


db_session = Session()
app = Flask(__name__)
app.secret_key = '1234567'


@app.route('/', methods=['POST', 'GET'])
def main_page():
	if 'is_logged' in session:
		pass
	else:
		fill_session(session)
	return render_template('main.html', session=session)


@app.route('/new-polygon', methods=['POST', 'GET'])
def add_task():
	clear_errors(session)
	if request.method == 'POST':
		query_id = set_query(session, request.form, db_session, request.files)
		print(session["polygon doesn't exist"], query_id)
		if query_id != -1:
			set_coord(request.form, db_session, query_id)
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
		if session['is_logged']:
			return redirect('/new-polygon')
	return render_template('sign-in-page.html', session=session)


@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')


@app.route('/tasks')
def tasks():
	tasks_list = get_query(db_session, session)
	coord_list = get_coord(db_session, tasks_list)
	return render_template('tasks.html', session=session, tasks_list=tasks_list, coord_list=coord_list)


if __name__ == '__main__':
	app.run(debug=True)

