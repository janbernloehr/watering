#!/usr/bin/python

# wiring stuff
from time import sleep
import wiringpi as wiringpi

# web stuff
import json
import falcon

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


def water_all(duration):
    wiringpi.digitalWrite(WATERING, HIGH)

    sleep(duration)

    wiringpi.digitalWrite(WATERING, LOW)


def start_this_app():
    wiringpi.wiringPiSetup()

    wiringpi.pinMode(WATERING, OUTPUT)


class DoWatering:
    def on_get(self, req, resp, duration):
        water_all(int(duration))
        origin = req.get_header('Origin')
        resp.set_header('Access-Control-Allow-Origin', origin)
        resp.body = json.dumps({
            'status': 'watering',
            'thrust': duration
        })
        resp.status = falcon.HTTP_200


# Initialize Wiring etc.
start_this_app()

# Start Web
app = falcon.API()

app.add_route('/water/{duration}', DoWatering())