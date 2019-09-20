from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker
from datetime import datetime


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

coordinates_table = Table('coordinates', metadata,
                          Column('id', Integer, primary_key=True),
                          Column('latitude', Integer),
                          Column('longitude', Integer),
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
        return "<Query('%s', '%s')>" % (self.user_id, self.time)


class Coord(object):

    def __init__(self, latitude, longitude, query_id):
        self.latitude = latitude
        self.longitude = longitude
        self.query_id = query_id

    def __repr__(self):
        return "<Coord('%s', '%s')>" % (self.longitude, self.latitude)


def set_user(params, session):
    user = User(params['nick'],
                params['pass'],
                params['email'],
                time_now(str(datetime.now())))
    session.add(user)
    session.commit()


def set_query(user_id, params, session):
    print(time_now(str(datetime.now())))
    query = Query(user_id,
                  time_now(str(datetime.now())),
                  params['focal_length'],
                  params['ps_width'],
                  params['ps_height'],
                  params['fly_height'],
                  params['battery_capacity'],
                  params['fly_loss'],
                  params['photo_loss']
                  )
    session.add(query)
    session.commit()


def set_coord(params, session):
    coord = Coord(params['latitude'],
                  params['longitude'],
                  params['query_id'])

    session.add(coord)
    session.commit()


def time_now(t_now):
    t = ''
    for i in t_now:
        if i == '.':
            break
        t += i
    return t


mapper(User, user_table)
mapper(Query, query_table)
mapper(Coord, coordinates_table)




