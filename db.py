from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy import Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

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
                    Column('user_id', Integer, ForeignKey("users.id"))
                    )

coordinates_table = Table('polygon_coordinates', metadata,
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

    def __init__(self,  user_id, time):
        self.user_id = user_id
        self.time = time

    def __repr__(self):
        return "<Query('%s', '%s')>" % (self.user_id, self.time)


class Coord(object):

    def __init__(self, latitude, longitude, query_id):
        self.latitude = latitude
        self.longitude = longitude
        self.query_id = query_id

    def __repr__(self):
        return "<Coord('%s', '%s')>" % (self.longitude, self.latitude)


mapper(User, user_table)
mapper(Query, query_table)
mapper(Coord, coordinates_table)
