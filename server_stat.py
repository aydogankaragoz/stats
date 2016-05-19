from flask import Flask, request, render_template
import msgpack
from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from datetime import datetime
from collections import defaultdict
from heapq import nlargest
from operator import itemgetter
import json
import os.path

engine = create_engine('sqlite:///stats.db', echo=False)

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

if not os.path.isfile('stats.db'):
    print "Creating db file"
    Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


app = Flask(__name__)


def dau():
    active_users = []
    active_users.append(['Day', 'Active Users'])
    for value in session.query(
                               func.date(Activity.moment),
                               func.count(Activity.user_id.distinct())).\
                               group_by(func.date(Activity.moment)).all():

        active_users.append(list(value))
    return json.dumps(active_users)


def wpu():
    weekly_active_users = defaultdict(lambda: defaultdict(int))
    for value in session.query(func.date(Impression.moment), Splash.user_id, func.count(Splash.splash_id)).\
                               join(Splash, Impression.splash_id == Splash.splash_id).\
                               group_by(func.date(Impression.moment), Splash.user_id).all():

        day = datetime.strptime(value[0], '%Y-%m-%d').isocalendar()

        week_id = str(day[0]) + '_' + str(day[1])
        user_id = str(value[1])
        daily_impressions = int(value[2])

        weekly_active_users[week_id][user_id] += daily_impressions

        weeks = sorted(weekly_active_users, key=lambda key: weekly_active_users[key])
    results = []
    for week in weeks:
        results.append(nlargest(10, weekly_active_users[week].iteritems(), itemgetter(1)))
    return zip(weeks, results)


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/wpu")
def weeklyPopulerUsers():
    results = wpu()
    return render_template('wpu.html', results=results)


@app.route("/dau")
def dailyActiveUsers():
    daily_active_users = dau()
    return render_template('chart.html', daily_active_users=daily_active_users)


@app.route('/submit', methods=['POST'])
def submit():
    payload = msgpack.unpackb(request.get_data())
    for msg in payload:
        moment = datetime.fromtimestamp(int(msg[0][:-9]))
        user_id = msg[2]
        event_type = msg[1]

        new_activity = Activity(moment, user_id)
        session.add(new_activity)
        if event_type == 'viorama':
            splash_id = msg[3]
            new_splash = Splash(splash_id, user_id)
            session.add(new_splash)
        elif event_type == 'view':
            splash_id = msg[3]
            new_impression = Impression(moment, splash_id)
            session.add(new_impression)
    session.commit()
    return "OK"

if __name__ == "__main__":
    app.run()
