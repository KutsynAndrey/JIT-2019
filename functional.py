import numpy as np
import pandas as pd
import os
from objects import Point


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
    session['polygon_has_less_than_3_dots'] = [False, 0]
    session['polygon_has_self-intersection'] = [False, 0]
    session["start-point-doesn't-exist"] = False
    session["choose one operation"] = False
    session["photos doesn't exist"] = False
    session['map-creator-image-error'] = False
    session['map-creator-file-error'] = False
    session['map-creator-format-error'] = False
    session['map-creator-memory-error'] = False
    session['map-ready'] = False
    session['map-name'] = None


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
    session['polygon_has_less_than_3_dots'] = [False, 0]
    session['polygon_has_self-intersection'] = [False, 0]
    session["start-point-doesn't-exist"] = False
    session["choose one operation"] = False
    session["photos doesn't exist"] = False
    session['map-creator-image-error'] = False
    session['map-creator-file-error'] = False
    session['map-creator-format-error'] = False
    session['map-creator-memory-error'] = False
    session['map-ready'] = False
    session['map-name'] = None


def validation_csv(file):
    file.save(os.path.join('static/uploads', file.filename))
    table = pd.read_csv(os.path.join('static/uploads', file.filename))
    table = table.to_numpy()
    gate = np.array([-1, -1, '-1', '-1'], dtype=object)
    polygons = []
    coordinates = [[], [], [], []]
    for ii, row in enumerate(table):
        if np.array_equal(row, gate):
            polygons.append(coordinates)
            coordinates = [[], [], [], []]
            continue

        coordinates[0].append(row[0])
        coordinates[1].append(row[1])
        coordinates[2].append(row[2])
        coordinates[3].append(row[3])

        for i, item in enumerate(row):
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


def validate_polygon(polygons):

    print(polygons)
    for index, polygon in enumerate(polygons):
        dots = []
        last_segments = []
        for ii in range(len(polygon[0])):
            dot = Point(polygon[0][ii], polygon[1][ii])
            dots.append(dot)
        print(dots)
        if len(dots) < 4:
            return 1, index
        for ii in range(len(dots)-1):
            segment = (dots[ii], dots[ii+1])
            if len(last_segments) > 0:
                for ind, seg in enumerate(last_segments):
                    print("LEN", len(last_segments))
                    if ii - ind == 1:
                        break
                    if intersect_segments(seg[0], seg[1], segment[0], segment[1]):
                        print("INTERSECTION in", seg[0], seg[1], segment[0], segment[1])
                        return 2, index
            last_segments.append(segment)

    return 0, 0


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


def oriented_triangle_area(dot1, dot2, dot3):
    return (dot2.x - dot1.x) * (dot3.y - dot1.y) - (dot2.y - dot1.y) * (dot3.x - dot1.x)


def projection_intersect(a, b, c, d):
    if a > b:
        a, b = b, a
    if c > d:
        c, d = d, c
    return max(a, c) <= min(b, d)


def intersect_segments(a, b, c, d):
    return (projection_intersect(a.x, b.x, c.x, d.x)
            and projection_intersect(a.y, b.y, c.y, d.y)
            and oriented_triangle_area(a, b, c) * oriented_triangle_area(a, b, d) <= 0
            and oriented_triangle_area(c, d, a) * oriented_triangle_area(c, d, b) <= 0)


def size_photo(widthCamera, heightCamera, H, F):
    print(widthCamera, heightCamera, H, F)
    width = widthCamera * (H / F)
    height = heightCamera * (H / F)
    print('WIDTH:', width, 'HEIGHT:', height)
    return [width, height]