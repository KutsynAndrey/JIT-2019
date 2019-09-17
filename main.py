from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route('/')
@app.route('/add_task')
@app.route('/tr')
def add_task():
	return render_template('add-task.html')


def tr():
	return render_template('tr.html')


if __name__ == '__main__':
	app.run(debug = True)