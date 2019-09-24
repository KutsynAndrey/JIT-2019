from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime
from validate_email import validate_email


engine = create_engine("mysql+mysqlconnector://user:Dgk.cf[ytn,eleotuj@localhost/JIT", echo=True)
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

coordinates_table = Table('coordinates', metadata,
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

    def __init__(self, latitude_gc, longitude_gc, latitude_dms, longitude_dms, query_id):
        self.latitude_gc = latitude_gc
        self.longitude_gc = longitude_gc
        self.latitude_dms = latitude_dms
        self.longitude_dms = longitude_dms
        self.query_id = query_id

    def __repr__(self):
        return "<Coord('%s', '%s')>" % (self.longitude_gc, self.latitude_gc)


def set_user(params, db_session, session):
    print("valid", validate_email(params['email'], check_mx=True))
    if params['pass'] != params['checkpass']:
        session['password_match_error'] = True
        session['identiсal_nick_error'] = False
    elif same_nickname(db_session, params["nick"]):
        session['identiсal_nick_error'] = True
        session['password_match_error'] = False
    elif not validate_email(params['email'], check_mx=True):
        session['valid_email'] = False
    else:
        user = User(params['nick'],
                    params['pass'],
                    params['email'],
                    time_now(str(datetime.now())))

        db_session.add(user)
        db_session.commit()


def set_query(session, params, db_session, l_files):
    print("file", l_files['myFile'].content_type)
    if params['latitude-GC'] == '' and 'myFile' not in l_files:
        print("WoW")
        session["polygon doesn't exist"] = True
        return -1

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

        obj = db_session.query(Query).filter_by(user_id=session['user_id']).first()

        return obj.id


def set_coord(params, db_session, query_id):

    latitude_gc = params['latitude-GC'].split()
    longitude_gc = params['longitude-GC'].split()
    latitude_dms = params['latitude-DMS'].split()
    longitude_dms = params['longitude-DMS'].split()

    print(longitude_dms)
    print(latitude_dms)
    print(latitude_gc)
    print(longitude_gc)

    for i in range(len(latitude_dms)):
        coord = Coord(latitude_gc[i],
                      longitude_gc[i],
                      latitude_dms[i],
                      longitude_dms[i],
                      query_id
                      )

        db_session.add(coord)

    db_session.commit()


def get_user(db_session, nickname, password, session):
    obj = db_session.query(User).filter_by(nickname=nickname).first()
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


def get_query(db_session, session):
    return db_session.query(Query).filter_by(user_id=session['user_id'])


def get_coord(db_session, query_list):
    coord_list = []
    for query in query_list:
        coord_list.append(db_session.query(Coord).filter_by(query_id=query.query_id))
    return coord_list


def time_now(t_now):
    t = ''
    for i in t_now:
        if i == '.':
            break
        t += i
    return t


def same_nickname(db_session, nickname):
    for person in db_session.query(User):
        if person.nickname == nickname:
            return True
    return False


def fill_session(session):
    session['Wrong_nickname'] = False
    session['is_logged'] = False
    session['Wrong_password'] = False
    session['valid_email'] = True
    session['password_match_error'] = False
    session['identiсal_nick_error'] = False


def clear_errors(session):
    session['Wrong_nickname'] = False
    session['valid_email'] = True
    session['Wrong_password'] = False
    session['password_match_error'] = False
    session['identiсal_nick_error'] = False
    session["polygon doesn't exist"] = False


mapper(User, user_table)
mapper(Query, query_table)
mapper(Coord, coordinates_table)




