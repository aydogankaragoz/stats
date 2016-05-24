from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    moment = Column(DateTime)
    user_id = Column(String(100))

    def __init__(self, moment, user_id):
        self.moment = moment
        self.user_id = user_id


class Splash(Base):
    __tablename__ = 'splashs'
    splash_id = Column(String, primary_key=True)
    user_id = Column(String)

    def __init__(self, splash_id, user_id):
        self.splash_id = splash_id
        self.user_id = user_id


class Impression(Base):
    __tablename__ = 'impressions'
    id = Column(Integer, primary_key=True)
    moment = Column(DateTime)
    splash_id = Column(String)

    def __init__(self, moment, splash_id):
        self.moment = moment
        self.splash_id = splash_id