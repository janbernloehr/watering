from time import sleep
import wiringpi2 as wiringpi

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


def start_this_app():
    wiringpi.wiringPiSetup()

    wiringpi.pinMode(WATERING, OUTPUT)

    wiringpi.digitalWrite(WATERING, HIGH)

    sleep(5)

    wiringpi.digitalWrite(WATERING, LOW)


start_this_app()
