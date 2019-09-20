from flask import Flask
from flask import render_template, session, request, redirect
from db import Session
from db import User, Query, Coord
from db import set_coord, set_query, set_user


db_session = Session()
app = Flask(__name__)
app.secret_key = '1234567'


@app.route('/', methods=['POST', 'GET'])
@app.route('/new-polygon', methods=['POST', 'GET'])
def add_task():
	if 'is_logged' in session:
		pass
	else:
		session['is_logged'] = False

	if request.method == 'POST':
		print("POST yeah")
		print(request.form)
		set_query(session['user_id'], request.form, db_session)
	return render_template('add-task.html', session=session)


@app.route('/sign-up-page', methods=['POST', 'GET'])
def registration():
	if request.method == 'POST':
		if request.form['pass'] != request.form['checkpass']:
			session['password_match_error'] = True
			session['identiсal_nick_error'] = False
		elif same_nickname():
			session['identiсal_nick_error'] = True
			session['password_match_error'] = False
		else:
			set_user(request.form, db_session)
			session['identiсal_nick_error'] = False
			session['password_match_error'] = False
	return render_template('sign-up-page.html', session=session)


@app.route('/sign-in-page', methods=['POST', 'GET'])
def sign_in():
	if request.method == 'POST':
		if request.form['nickname']:
			login(request.form['nickname'], request.form['password'])
			if 'admin' not in session:
				return redirect('/sign-in-page')
			elif session['admin']:
				return redirect('/admin')
			else:
				return redirect('/profile/' + session['nickname'])
		if session['is_logged']:
			return redirect('/')
	return render_template('sign-in-page.html', session=session)


@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')


@app.route('/tasks')
def tasks():
	return render_template('tasks.html', session=session)


def same_nickname():
	for person in db_session.query(User):
		if person.nickname == request.form['nick']:
			return True
	return False


def login(nickname, password):
	obj = db_session.query(User).filter_by(nickname=nickname).first()
	if obj is None:
		session['Wrong_nickname'] = True
	elif obj.password != password:
		session['Wrong_password'] = True
		session['Wrong_nickname'] = False
	else:
		session['Wrong_nickname'] = False
		session['Wrong_password'] = False
		session['is_logged'] = True
		session['nickname'] = obj.nickname
		session['email'] = obj.email
		session['user_id'] = obj.id


if __name__ == '__main__':
	app.run(debug=True)

