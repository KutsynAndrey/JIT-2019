from flask import Flask
from flask import render_template, session, request, redirect, send_file, send_from_directory
from db import Session
from db import set_query, set_user, get_user, get_queries, get_coord, get_query, get_polygon_coords, get_path_coords
from functional import clear_errors, init_session
from TLogParser import csv_parser
from photo_processing.functional import photo_page_solution, clear_folder, save_img_list, load_img_list
from photo_processing.mapper import MapCreator
from cv2 import imwrite
import datetime

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


@app.route('/task/<int:task_id>', methods=['POST', 'GET'])
def task(task_id):
    obj = get_query(db_session, session, task_id)
    x, y = get_polygon_coords(db_session, obj.id)
    path_coords = get_path_coords(db_session, task_id, True)
    return render_template('task.html', session=session, obj=obj, coordinates=(x, y), path=path_coords)


@app.route('/img-processing', methods=['POST', 'GET'])
def img_processing():
    clear_errors(session)
    result = [0, 0]
    name = None
    if request.method == 'POST':
        images = request.files.getlist("improve-quality")
        images2 = request.files.getlist("sort-quality")
        image = request.files["AI-improving"]

        result = photo_page_solution(images, images2, image, session)
        name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
        imwrite("static/tmp-photos/" + name + '.jpeg', result[1])
    return render_template('newphotos.html', session=session, status=result[0], p_name=name)


@app.route('/map-creator', methods=['POST', 'GET'])
def map_creator():
    clear_errors(session)
    if request.method == 'POST':
        images = request.files.getlist("input")
        addition = request.files["input-information"]
        scale = float(request.form['scale'])

        if images[0].content_type == 'application/octet-stream':
            session['map-creator-image-error'] = True
        elif addition.content_type == 'application/octet-stream':
            session['map-creator-file-error'] = True
        elif addition.content_type != "text/csv":
            session['map-creator-format-error'] = True

        clear_folder("static/tmp-photos")
        clear_folder("static/uploads")
        save_img_list(images)
        img_list = load_img_list("static/tmp-photos")
        params = csv_parser(addition)
        result = MapCreator(img_list, params, scale=scale)
        if result == -1:
            session['map-creator-memory-error'] = True
        else:
            name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            imwrite("static/tmp-photos/" + name + ".jpeg", result.map)
            session['map-ready'] = True
            session['map-name'] = name
    return render_template('create_map.html', session=session)


@app.route('/download-result/<name>', methods=['GET'])
def img_download(name):
    path = "static/tmp-photos/" + name + ".jpeg"
    return send_file(path, as_attachment=True, attachment_filename=name + ".jpeg", cache_timeout=0)


if __name__ == '__main__':
    app.run(debug=True)

