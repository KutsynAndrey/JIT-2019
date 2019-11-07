from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float, Boolean
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime
from validate_email import validate_email
from functional import time_now, validation_csv, fill_session_by_valid_code, validate_polygon, size_photo
from algorithm import algorithm


engine = create_engine("mysql+mysqlconnector://user:Dgk.cf[ytn,eleotuj@localhost/JIT")
metadata = MetaData()
Session = sessionmaker(bind=engine)

user_table = Table('users', metadata,
                   Column('id', Integer, primary_key=True),
                   Column('nickname', String(50)),
                   Column('password', String(50)),
                   Column('email', String(50)),
                   Column('time', DateTime)
                   )

query_table = Table('queries', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('query_date', DateTime),
                    Column('focal_length', Float),
                    Column('ps_width', Integer),
                    Column('ps_height', Integer),
                    Column('photo_loss', Integer),
                    Column('fly_height', Integer),
                    Column('fly_loss', Integer),
                    Column('battery_capacity', Integer),
                    Column('user_id', Integer, ForeignKey("users.id")),
                    Column('status', Integer),
                    Column('start_lat', Float),
                    Column('start_lon', Float),
                    Column('fly_speed', Float),
                    Column('radian', Float),
                    Column('spent_battery', Float),
                    Column('fly_time', Float),
                    Column('length_route', Float)
                    )

polygon_table = Table('polygon', metadata,
                      Column('id', Integer, primary_key=True),
                      Column('polygon_type', Boolean),
                      Column('query_id', Integer, ForeignKey('queries.id'))
                      )

coordinates_table = Table('coordinates', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('latitude_gc', Float),
                          Column('longitude_gc', Float),
                          Column('latitude_dms', String(20)),
                          Column('longitude_dms', String(20)),
                          Column('polygon_id', Integer, ForeignKey('polygon.id'))
                          )

path_coordinates = Table('path_coordinates', metadata,
                         Column('id', Integer, primary_key=True),
                         Column('latitude_gc', Float),
                         Column('longitude_gc', Float),
                         Column('query_id', Integer, ForeignKey('queries.id'))
                         )

metadata.create_all(engine)


class User(object):

    def __init__(self, nickname, password, email, time):

        self.nickname = nickname
        self.email = email
        self.password = password
        self.time = time

    def __repr__(self):
        return "<User('%s', '%s', %s)>" % (self.nickname, self.email, self.password)


class Query(object):

    def __init__(self,  user_id, time, focal_length, w, h, fly_height, capacity, f_loss, p_loss, status, radian, spent_battery, fly_time, fly_speed, s_lat, s_lon, length_route):
        self.user_id = user_id
        self.query_date = time
        self.focal_length = focal_length
        self.ps_width = w
        self.ps_height = h
        self.fly_height = fly_height
        self.battery_capacity = capacity
        self.fly_loss = f_loss
        self.photo_loss = p_loss
        self.status = status
        self.fly_speed = fly_speed
        self.radian = radian
        self.start_lat = s_lat
        self.start_lon = s_lon
        self.spent_battery = spent_battery
        self.fly_time = fly_time
        self.length_route = length_route

    def __repr__(self):
        return "<Query('%s', '%s')>" % (self.fly_height, self.query_date)


class Coord(object):

    def __init__(self, latitude_gc, longitude_gc, latitude_dms, longitude_dms, polygon_id):
        self.latitude_gc = latitude_gc
        self.longitude_gc = longitude_gc
        self.latitude_dms = latitude_dms
        self.longitude_dms = longitude_dms
        self.polygon_id = polygon_id

    def __repr__(self):
        return "<Coord('%s', '%s') from Polygon('%s')>" % (self.longitude_gc, self.latitude_gc, self.polygon_id)


class Polygon(object):

    def __init__(self, polygon_type, query_id):
        self.polygon_type = polygon_type
        self.query_id = query_id

    def __repr__(self):
        return "pass"


class PathCoord(object):

    def __init__(self, latitude_gc, longitude_gc, query_id):
        self.latitude_gc = latitude_gc
        self.longitude_gc = longitude_gc
        self.query_id = query_id

    def __repr__(self):
        return "<PathCoord('%s', '%s') from Polygon('%s')>" % (self.longitude_gc, self.latitude_gc, self.query_id)


mapper(User, user_table)
mapper(Query, query_table)
mapper(Coord, coordinates_table)
mapper(Polygon, polygon_table)
mapper(PathCoord, path_coordinates)


def set_user(params, db_session, session):
    code = validate_email(params['email'])
    if params['pass'] != params['checkpass']:
        session['password_match_error'] = True
        session['identiсal_nick_error'] = False
    elif same_nickname(db_session, params["nick"]):
        session['identiсal_nick_error'] = True
        session['password_match_error'] = False
    elif not code:
        session['valid_email'] = False
    else:
        user = User(params['nick'],
                    params['pass'],
                    params['email'],
                    time_now(str(datetime.now())))

        db_session.add(user)
        db_session.commit()


def set_query(session, params, db_session, l_files):
    print("file", l_files['myCSV'].content_type)
    file = l_files['myCSV']
    if params['lat-dot'] == '':
        session["start-point-doesn't-exist"] = True
        return -1
    elif params['latitude-GC'] == '' and file.content_type == 'application/octet-stream':
        print("WoW")
        session["polygon-doesn't-exist"] = True
        return -1
    elif params['latitude-GC'] != '' and file.content_type != 'application/octet-stream':
        session['two-ways-building'] = True
        return -1
    elif params['latitude-GC'] == '' and file.content_type != 'text/csv':
        session['not-a-csv'] = True
        return -1
    elif params['latitude-GC'] == '' and file.content_type == 'text/csv':
        code, row, column = validation_csv(file)
        err, p = validate_polygon(column)
        if err == 1:
            session['polygon_has_less_than_3_dots'] = [True, p]
            return -1
        elif err == 2:
            session['polygon_has_self-intersection'] = [True, p]
            return -1
        elif code:
            fill_session_by_valid_code(session, code, row, column)
            return -1
        else:
            query = Query(session['user_id'],
                          time_now(str(datetime.now())),
                          params['focal_length'],
                          params['ps_width'],
                          params['ps_height'],
                          params['fly_height'],
                          params['battery_capacity'],
                          params['fly_loss'],
                          params['photo_loss'],
                          -1,
                          0,
                          0,
                          0,
                          params['fly_speed'],
                          params['lat-dot'],
                          params['lon-dot'],
                          0
                          )

            db_session.add(query)
            db_session.commit()
            obj = db_session.query(Query).filter_by(user_id=session['user_id'])[-1]
            query_id = obj.id

            print(column)
            for i in range(len(column)):
                pol_coordinates = column[i]
                if i == 0:
                    set_polygon(db_session, 1, query_id, pol_coordinates, True)
                else:
                    set_polygon(db_session, 0, query_id, pol_coordinates, True)

            size = size_photo(float(params['ps_width']),
                              float(params['ps_height']),
                              float(params['fly_height']),
                              float(params['focal_length']))

            polygons = get_polygon_coords(db_session, query_id, 1)
            start_point = [float(params['lat-dot']), float(params['lon-dot'])]
            valid, path, radian, spent_battery, fly_time, length_route = algorithm(polygons,
                                    size,
                                    start_point,
                                    float(params['fly_speed']),
                                    float(params['fly_loss']),
                                    float(params['photo_loss']),
                                    float(params['battery_capacity']))
            if valid:
                print("VALID", query_id)
                tmp_query = db_session.query(Query).filter_by(id=query_id).first()
                tmp_query.status = 0
                tmp_query.radian = radian
                tmp_query.spent_battery = spent_battery
                tmp_query.fly_time = fly_time
                tmp_query.length_route = length_route
                db_session.commit()
                set_path_coords(db_session, path, query_id)
            else:
                tmp_query = db_session.query(Query).filter_by(id=query_id).first()
                tmp_query.status = 1
                db_session.commit()

    else:
        print(time_now(str(datetime.now())))

        query = Query(session['user_id'],
                      time_now(str(datetime.now())),
                      params['focal_length'],
                      params['ps_width'],
                      params['ps_height'],
                      params['fly_height'],
                      params['battery_capacity'],
                      params['fly_loss'],
                      params['photo_loss'],
                      -1,
                      0,
                      0,
                      0,
                      params['fly_speed'],
                      params['lat-dot'],
                      params['lon-dot'],
                      0
                      )

        db_session.add(query)
        db_session.commit()
        obj = db_session.query(Query).filter_by(user_id=session['user_id'])[-1]
        query_id = obj.id

        latitude_gc = params['latitude-GC'].split('$')
        longitude_gc = params['longitude-GC'].split('$')
        latitude_dms = params['latitude-DMS'].split('$')
        longitude_dms = params['longitude-DMS'].split('$')

        for i in range(len(latitude_gc)):
            pol_coordinates = [latitude_gc[i], longitude_gc[i], latitude_dms[i], longitude_dms[i]]
            if i == 0:
                set_polygon(db_session, 1, query_id, pol_coordinates)
            else:
                set_polygon(db_session, 0, query_id, pol_coordinates)
        size = size_photo(float(params['ps_width']),
                          float(params['ps_height']),
                          float(params['fly_height']),
                          float(params['focal_length']))

        polygons = get_polygon_coords(db_session, query_id, 1)
        start_point = [float(params['lat-dot']), float(params['lon-dot'])]
        print("START_POINT_PARAMS:", start_point)
        valid, path, radian, spent_battery, fly_time, length_route = algorithm(polygons,
                                size,
                                start_point,
                                float(params['fly_speed']),
                                float(params['fly_loss']),
                                float(params['photo_loss']),
                                float(params['battery_capacity']))
        if valid:
            print("VALID", query_id)
            tmp_query = db_session.query(Query).filter_by(id=query_id).first()
            tmp_query.status = 0
            tmp_query.radian = radian
            tmp_query.spent_battery = spent_battery
            tmp_query.fly_time = fly_time
            tmp_query.length_route = length_route
            print(tmp_query.fly_speed)
            db_session.commit()
            set_path_coords(db_session, path, query_id)
        else:
            tmp_query = db_session.query(Query).filter_by(id=query_id).first()
            tmp_query.status = 1
            tmp_query.spent_battery = spent_battery
            tmp_query.fly_time = fly_time
            tmp_query.length_route = length_route
            db_session.commit()


def set_polygon(db_session, polygon_type, query_id, coordinates, from_csv=False):

    if from_csv is False:
        coordinates[0] = coordinates[0].split()
        coordinates[1] = coordinates[1].split()
        coordinates[2] = coordinates[2].split()
        coordinates[3] = coordinates[3].split()

    polygon = Polygon(polygon_type, query_id)
    db_session.add(polygon)
    db_session.commit()
    obj = db_session.query(Polygon).filter_by(query_id=query_id)[-1]
    polygon_id = obj.id
    print("BUG\n\n", coordinates, "\n\n\n")
    for i in range(len(coordinates[0])):
        dot_coordinates = [coordinates[0][i], coordinates[1][i], coordinates[2][i], coordinates[3][i]]
        set_coord(dot_coordinates, db_session, polygon_id)


def set_coord(coordinates, db_session, polygon_id):

    coord = Coord(coordinates[0],
                  coordinates[1],
                  coordinates[2],
                  coordinates[3],
                  polygon_id
                  )

    db_session.add(coord)
    db_session.commit()


def get_user(db_session, nickname, password, session):
    obj = db_session.query(User).filter_by(nickname=nickname)[-1]
    print(obj)
    if obj is None:
        session['Wrong_password'] = False
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


def get_queries(db_session, session):
    obj = db_session.query(Query).filter_by(user_id=session['user_id']).all()
    return obj


def get_query(db_session, session, query_id):
    obj = db_session.query(Query).filter_by(id=query_id).first()
    return obj


def same_nickname(db_session, nickname):
    for person in db_session.query(User):
        if person.nickname == nickname:
            return True
    return False


def get_coord(db_session, query_list):
    coord_list = []
    for query in query_list:
        coord_list.append(db_session.query(Coord).filter_by(query_id=query.query_id))
    return coord_list


def get_polygon_coords(db_session, query_id, for_algorithm=False):
    polygons = db_session.query(Polygon).filter_by(query_id=query_id).all()
    if for_algorithm:
        polygons_list = []
        for i, polygon in enumerate(polygons):
            polygon = polygons[i]
            coords = db_session.query(Coord).filter_by(polygon_id=polygon.id).all()
            dots_list = []
            for ii, coord in enumerate(coords):
                dot = [coord.latitude_gc, coord.longitude_gc]
                dots_list.append(dot)
            del dots_list[-1]
            polygons_list.append(dots_list)

        return polygons_list

    else:
        coordinates_x = ''
        coordinates_y = ''
        for i, polygon in enumerate(polygons):

            coords = db_session.query(Coord).filter_by(polygon_id=polygon.id).all()
            new_coords_x = ''
            new_coords_y = ''
            for ii, coord in enumerate(coords):
                new_coords_x += str(coord.latitude_gc)
                new_coords_y += str(coord.longitude_gc)
                if ii != len(coords) - 1:
                  new_coords_x += ' '
                  new_coords_y += ' '
            coordinates_x += str(new_coords_x)
            coordinates_y += str(new_coords_y)
            if i != len(polygons) - 1:
              coordinates_x += '$'
              coordinates_y += '$'
        return coordinates_x, coordinates_y


def set_path_coords(db_session, dot_list, query_id):
    for i in range(len(dot_list)):
        point = PathCoord(str(dot_list[i][0]),
                          str(dot_list[i][1]),
                          query_id
                          )
        db_session.add(point)
    db_session.commit()


def get_path_coords(db_session, query_id, like_str=False):
    dots = db_session.query(PathCoord).filter_by(query_id=query_id).all()
    print(dots)
    if like_str:
        lat = ''
        lon = ''
        for i in range(len(dots)):
            lat += str(dots[i].latitude_gc)
            lon += str(dots[i].longitude_gc)
            if i != len(dots) - 1:
                lat += ' '
                lon += ' '
        print(lat)
        return lat, lon

    return dots
