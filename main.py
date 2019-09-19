from flask import Flask
from flask import render_template, session, request, redirect
from db import Session
from db import User, Query, Coord
from datetime import datetime

db_session = Session()
app = Flask(__name__)
app.secret_key = '1234567'


@app.route('/')
@app.route('/new-polygon', methods=['POST', 'GET'])
def add_task():
	if 'is_logged' in session:
		pass
	else:
		session['is_logged'] = False
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
			registration()
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


def registration():
	user = User(request.form['nick'],
				request.form['pass'],
				request.form['email'],
				time_now(str(datetime.now())))

	db_session.add(user)
	db_session.commit()
	return


def time_now(time):
	t = ''
	for i in time:
		if i == '.':
			break
		t += i

	return t


if __name__ == '__main__':
	app.run(debug=True)

