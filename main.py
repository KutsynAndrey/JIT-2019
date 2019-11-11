from flask import Flask
from flask import render_template, session, request, redirect, send_file, send_from_directory
from db import Session
from db import set_query, set_user, get_user, get_queries, get_coord, get_query, get_polygon_coords, get_path_coords
from functional import clear_errors, init_session
from TLogParser import csv_parser, is_tlog, parser
from photo_processing.functional import clear_folder, save_img_list, load_img_list
from photo_processing.upgrade_qual import photo_page_solution
from photo_processing.mapper import MapCreator
from photo_processing.water import watering
from photo_processing.obj_detection import obj_detection
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
        params_file = request.files["params"]
        status, result = photo_page_solution(images, images2, image, params_file, session)
        if status:
            pass
        else:
            name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            imwrite("static/tmp-photos/" + name + '.JPG', result)
            session["upgrade-task-img-name"] = name
    return render_template('newphotos.html', session=session, p_name=name)


@app.route('/map-creator', methods=['POST', 'GET'])
def map_creator():
    clear_errors(session)
    if request.method == 'POST':
        images = request.files.getlist("input")
        addition = request.files["input-information"]
        scale = float(request.form['scale'])

        if images[0].content_type == 'application/octet-stream':
            session['map-creator-image-error'] = True
        elif addition.content_type == 'application/octet-stream' and not is_tlog(addition.filename):
            session['map-creator-file-error'] = True
        elif addition.content_type != "text/csv" and not is_tlog(addition.filename):
            session['map-creator-format-error'] = True
        elif addition.content_type == "text/csv":
            clear_folder("static/tmp-photos")
            clear_folder("static/uploads")
            save_img_list(images)
            img_list = load_img_list("static/tmp-photos")
            params = csv_parser(addition)
            result = MapCreator(img_list, params, scale=scale)
            print("TYPE", type(result))
            if result == -1:
                session['map-creator-memory-error'] = True
            else:
                name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
                imwrite("static/tmp-photos/" + name + ".JPG", result.map)
                session['map-ready'] = True
                session['map-name'] = name

        elif is_tlog(addition.filename):
            clear_folder("static/tmp-photos")
            clear_folder("static/uploads")
            save_img_list(images)
            print("SAVED")
            img_list = load_img_list("static/tmp-photos")
            print("LOADED")
            status, params = parser(addition)
            print("PARAMS")
            result = MapCreator(img_list, params, scale=scale)
            print("TYPE", type(result))
            if result == -1:
                session['map-creator-memory-error'] = True
            else:
                name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
                imwrite("static/tmp-photos/" + name + ".JPG", result.map)
                session['map-ready'] = True
                session['map-name'] = name

    return render_template('create_map.html', session=session)


@app.route('/download-result/<name>', methods=['GET'])
def img_download(name):
    path = "static/tmp-photos/" + name + ".JPG"
    return send_file(path, as_attachment=True, attachment_filename=name + ".JPG", cache_timeout=0)


@app.route('/watering', methods=['GET', 'POST'])
def water_advices():
    clear_errors(session)
    if request.method == 'POST':

        if request.files['input'].content_type == "application/octet-stream":
            session['watering-photo-error'] = True
        else:
            clear_folder("static/tmp-photos")
            save_img_list([request.files['input']])
            print("PATH:", request.files['input'])

            img = load_img_list('static/tmp-photos')[0]
            max_H = int(request.form['max-H'])
            min_H = int(request.form['min-H'])
            print("SERVER DATA:", min_H, max_H)

            result = watering(img, min_H, max_H)
            print("TYPE RESULT", type(result))
            name = datetime.datetime.now().strftime("%m%d%Y%H%M%S")
            imwrite("static/tmp-photos/" + name + ".JPG", result)
            session['watering-ready'] = True
            session['watering-name'] = name

    return render_template('watering.html', session=session)


@app.route("/moving-objects", methods=['GET', 'POST'])
def moving_objects():
    clear_errors(session)
    if request.method == 'POST':
        if request.files['input1'].content_type == "application/octet-stream":
            session['obj-detection-photo-error'] = True
        else:
            clear_folder("static/tmp-photos")
            save_img_list([request.files['input1'], request.files['input2']])

            images = load_img_list('static/tmp-photos')[:2]

            result = obj_detection(images[0], images[1], int(request.form['threshold_v']))
            print("TYPE RESULT", type(result))
            name1 = datetime.datetime.now().strftime("%m%d%Y%H%M%S") + "1"
            name2 = datetime.datetime.now().strftime("%m%d%Y%H%M%S") + "2"
            imwrite("static/tmp-photos/" + name1 + ".JPG", result[0])
            imwrite("static/tmp-photos/" + name2 + ".JPG", result[1])
            session['obj-detection-ready'] = True
            session['obj-detection-name'] = [name1, name2]

    return render_template('obj_detection.html', session=session)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')