import numpy as np
import pandas as pd
import os


def time_now(t_now):
    t = ''
    for i in t_now:
        if i == '.':
            break
        t += i
    return t


def init_session(session):
    session['Wrong_nickname'] = False
    session['is_logged'] = False
    session['Wrong_password'] = False
    session['valid_email'] = True
    session['password_match_error'] = False
    session['identiсal_nick_error'] = False

    session['two-ways-building'] = False
    session['not-a-csv'] = False
    session["polygon-doesn't-exist"] = False

    session['is_nan'] = [False, 0, 0]
    session['long_gc_out'] = [False, 0, 0]
    session['lat_gc_out'] = [False, 0, 0]
    session['long_not_3'] = [False, 0, 0]
    session['lat_not_3'] = [False, 0, 0]
    session['lat_dms_out_d'] = [False, 0, 0]
    session['long_dms_out_d'] = [False, 0, 0]
    session['lat_dms_out_m'] = [False, 0, 0]
    session['long_dms_out_m'] = [False, 0, 0]
    session['lat_dms_out_s'] = [False, 0, 0]
    session['long_dms_out_s'] = [False, 0, 0]


def clear_errors(session):
    session['Wrong_nickname'] = False
    session['valid_email'] = True
    session['Wrong_password'] = False
    session['password_match_error'] = False
    session['identiсal_nick_error'] = False
    session["polygon doesn't exist"] = False
    session['two-ways-building'] = False
    session['not-a-csv'] = False
    session["polygon-doesn't-exist"] = False

    session['is_nan'] = [False, 0, 0]
    session['long_gc_out'] = [False, 0, 0]
    session['lat_gc_out'] = [False, 0, 0]
    session['long_not_3'] = [False, 0, 0]
    session['lat_not_3'] = [False, 0, 0]
    session['lat_dms_out_d'] = [False, 0, 0]
    session['long_dms_out_d'] = [False, 0, 0]
    session['lat_dms_out_m'] = [False, 0, 0]
    session['long_dms_out_m'] = [False, 0, 0]
    session['lat_dms_out_s'] = [False, 0, 0]
    session['long_dms_out_s'] = [False, 0, 0]


def validation_csv(file):
    file.save(os.path.join('static/uploads', file.filename))
    table = pd.read_csv(os.path.join('static/uploads', file.filename))
    table = table.to_numpy()
    gate = np.array([-1, -1, '-1', '-1'], dtype=object)
    polygons = []
    coordinates = [[], [], [], []]
    print(table)
    for ii, row in enumerate(table):
        if np.array_equal(row, gate):
            polygons.append(coordinates)
            coordinates = [[], [], [], []]
            continue

        coordinates[0].append(row[0])
        coordinates[1].append(row[1])
        coordinates[2].append(row[2])
        coordinates[3].append(row[3])

        print(ii, row.size)
        for i, item in enumerate(row):
            print("ITEM", type(item))
            if item != item:
                return 1, ii, i
        long_dms = row[2].split('-')
        lat_dms = row[3].split('-')
        if row[0] > 180 or row[0] < -180:
            return 2, ii, 0
        if row[1] > 90 or row[1] < -90:
            return 3, ii, 1
        if len(long_dms) != 3:
            return 4, ii, 2
        if len(lat_dms) != 3:
            return 5, ii, 3
        if int(long_dms[0]) > 180 or int(long_dms[0]) < -180:
            return 6, ii, 2
        if int(lat_dms[0]) > 180 or int(lat_dms[0]) < -180:
            return 7, ii, 3
        if int(long_dms[1]) > 60 or int(long_dms[1]) < 0:
            return 8, ii, 2
        if int(lat_dms[1]) > 60 or int(lat_dms[1]) < 0:
            return 9, ii, 3
        if int(long_dms[2]) > 60 or int(long_dms[2]) < 0:
            return 10, ii, 2
        if int(lat_dms[2]) > 60 or int(lat_dms[2]) < 0:
            return 11, ii, 3
    polygons.append(coordinates)
    return 0, 0, polygons


def validate_polygon(coordinates):
    sx = coordinates[0][0]
    sy = coordinates[0][1]


def fill_session_by_valid_code(session, code, row, column):
    if code == 1:
        session['is_nan'][0] = True
        session['is_nan'][1] = row
        session['is_nan'][2] = column
    elif code == 2:
        session['long_gc_out'][0] = True
        session['long_gc_out'][1] = row
        session['long_gc_out'][2] = column
    elif code == 3:
        session['lat_gc_out'][0] = True
        session['lat_gc_out'][1] = row
        session['lat_gc_out'][2] = column
    elif code == 4:
        session['long_not_3'][0] = True
        session['long_not_3'][1] = row
        session['long_not_3'][2] = column
    elif code == 5:
        session['lat_not_3'][0] = True
        session['lat_not_3'][1] = row
        session['lat_not_3'][2] = column
    elif code == 6:
        session['long_dms_out_d'][0] = True
        session['long_dms_out_d'][1] = row
        session['long_dms_out_d'][2] = column
    elif code == 7:
        session['lat_dms_out_d'][0] = True
        session['lat_dms_out_d'][1] = row
        session['lat_dms_out_d'][2] = column
    elif code == 8:
        session['long_dms_out_m'][0] = True
        session['long_dms_out_m'][1] = row
        session['long_dms_out_m'][2] = column
    elif code == 9:
        session['lat_dms_out_m'][0] = True
        session['lat_dms_out_m'][1] = row
        session['lat_dms_out_m'][2] = column
    elif code == 10:
        session['long_dms_out_s'][0] = True
        session['long_dms_out_s'][1] = row
        session['long_dms_out_s'][2] = column
    else:
        session['lat_dms_out_s'][0] = True
        session['lat_dms_out_s'][1] = row
        session['lat_dms_out_s'][2] = column
