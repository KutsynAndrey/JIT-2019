from flask import Flask
from flask import render_template, session, request
from db import Session
from db import User, Query, Coord
from datetime import datetime


db_session = Session
app = Flask(__name__)


@app.route('/')
@app.route('/add_task')
def add_task():
	return render_template('add-task.html')


@app.route('/sign-up-page')
def registration():
	return render_template('sign-up-page.html')


@app.route('/sign-in-page')
def login():
	return render_template('sign-in-page.html')


if __name__ == '__main__':
	app.run(debug=True)


def registration():
	user = User(request.form['nickname'],
				request.form['password'],
				request.form['email'],
				time_now(str(datetime.now())))

	db_session.add(user)
	db_session.commit()



def time_now(time):
	t = ''
	for i in time:
		if i == '.':
			break
		t += i

	return t