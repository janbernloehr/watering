#!/usr/bin/python

# wiring stuff
from time import sleep
import wiringpi as wiringpi

# web stuff
import json
import falcon

# data stuff
import dataset
from datetime import date, datetime, timedelta

# constants
WATERING = 1

INPUT = 0
OUTPUT = 1
PWM_OUTPUT = 2
GPIO_CLOCK = 3
SOFT_PWM_OUTPUT = 4
SOFT_TONE_OUTPUT = 5
PWM_TONE_OUTPUT = 6

LOW = 0
HIGH = 1

s_to_ml_factor = 250.0/20.0 # 20s == 250ml


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError('Not sure how to serialize %s' % (obj,))


def water_all(volume, username):
    duration = int(float(volume) / s_to_ml_factor)

    wiringpi.digitalWrite(WATERING, HIGH)

    try:
        sleep(duration)

        db = dataset.connect('sqlite:///mydatabase.db')

        db_waterings = db['waterings']
        db_waterings.insert(dict(waterdate=datetime.utcnow(), user=username, quantity=volume))
    finally:
        wiringpi.digitalWrite(WATERING, LOW)

    return duration


def record_filling(volume, username):
    db = dataset.connect('sqlite:///mydatabase.db')

    db_fillings = db['fillings']
    db_fillings.insert(dict(filldate=datetime.utcnow(), user=username, quantity=volume))


def get_history():
    db = dataset.connect('sqlite:///mydatabase.db')

    db_fillings = db['fillings']

    last_filling = db_fillings.find_one(order_by='-filldate', _limit=1)

    db_waterings = db['waterings']

    recent_waterings = db_waterings.find(db_waterings.table.columns.waterdate >= last_filling['filldate'], order_by='waterdate')

    lst = []
    total = last_filling['quantity']
    taken = 0

    for x in recent_waterings:
        taken += x['quantity']
        lst.append({
            'waterdate': x['waterdate'],
            'user': x['user'],
            'quantity': x['quantity']
        })

    return json.dumps({
            'last_filling': last_filling,
            'remaining' : total-taken,
            'history': lst
        }, default=json_serial)


def start_this_app():
    # we use the wiring pi schema
    wiringpi.wiringPiSetup()

    # set the watering port to output
    wiringpi.pinMode(WATERING, OUTPUT)

    # to start with a clean state
    wiringpi.digitalWrite(WATERING, LOW)


class DoWatering:
    def on_get(self, req, resp, volume):
        duration = water_all(int(volume), 'Jan')
        origin = req.get_header('Origin')
        resp.set_header('Access-Control-Allow-Origin', origin)
        resp.body = json.dumps({
            'action': 'water',
            'volume': volume,
            'duration': duration
        })
        resp.status = falcon.HTTP_200


class RecordFilling:
    def on_get(self, req, resp, volume):
        record_filling(int(volume), 'Jan')

        origin = req.get_header('Origin')

        resp.set_header('Access-Control-Allow-Origin', origin)
        resp.body = json.dumps({
            'action': 'record_filling',
            'volume': volume
        })
        resp.status = falcon.HTTP_200


class GetHistory:
    def on_get(self, req, resp):

        origin = req.get_header('Origin')
        resp.set_header('Access-Control-Allow-Origin', origin)
        resp.body = get_history()
        resp.status = falcon.HTTP_200


# Initialize Wiring etc.
start_this_app()

# Start Web
app = falcon.API()

app.add_route('/watering.api/water/{volume}', DoWatering())
app.add_route('/watering.api/fill/{volume}', RecordFilling())
app.add_route('/watering.api/history', GetHistory())
