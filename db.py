from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float, Boolean
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime
from validate_email import validate_email
from functional import time_now, validation_csv, fill_session_by_valid_code, validate_polygon


engine = create_engine("mysql+mysqlconnector://ollegg:sqlollegg@localhost/JIT", echo=True)
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
                    Column('focal_length', Integer),
                    Column('ps_width', Integer),
                    Column('ps_height', Integer),
                    Column('photo_loss', Integer),
                    Column('fly_loss', Integer),
                    Column('battery_capacity', Integer),
                    Column('user_id', Integer, ForeignKey("users.id"))
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
                         Column('latitude_dms', String(20)),
                         Column('longitude_dms', String(20)),
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

    def __init__(self,  user_id, time, focal_length, w, h, fly_height, capacity, f_loss, p_loss):
        self.user_id = user_id
        self.query_date = time
        self.focal_length = focal_length
        self.ps_width = w
        self.ps_height = h
        self.fly_height = fly_height
        self.battery_capacity = capacity
        self.fly_loss = f_loss
        self.photo_loss = p_loss

    def __repr__(self):
        return "<Query('%s', '%s')>" % (self.user_id, self.query_date)


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

    def __init__(self, latitude_gc, longitude_gc, latitude_dms, longitude_dms, query_id):
        self.latitude_gc = latitude_gc
        self.longitude_gc = longitude_gc
        self.latitude_dms = latitude_dms
        self.longitude_dms = longitude_dms
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
    if params['latitude-GC'] == '' and file.content_type == 'application/octet-stream':
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
                          params['photo_loss']
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
                      params['photo_loss']
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
    return db_session.query(Query).filter_by(user_id=session['user_id'])


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









