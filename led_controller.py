"""REST API for controlling LEDs via PCA9685
"""
from __future__ import division, print_function

import Adafruit_PCA9685

from flask.views import MethodView
from flask import jsonify, Flask, request

LED_API = Flask(__name__)

LED_CONTROLLER = Adafruit_PCA9685.PCA9685()


def _init_controller():
    """ Initilize the LED controller.
    """
    LED_CONTROLLER.set_pwm_freq(1525)


def _check_rgb_types(red, green, blue):
    return bool(
        isinstance(red, int) and
        isinstance(green, int) and
        isinstance(blue, int)
    )


def _change_leds(red, green, blue):
    """ Change LED brightness
    """
    if _check_rgb_types(red, green, blue):
        red = int(4095*_convert_percent_to_dec(red))
        green = int(4095*_convert_percent_to_dec(green))
        blue = int(4095*_convert_percent_to_dec(blue))
    else:
        raise TypeError("Expected variable type INT")

    LED_CONTROLLER.set_pwm(0, 0, red)
    LED_CONTROLLER.set_pwm(0, 1, green)
    LED_CONTROLLER.set_pwm(0, 2, blue)


def _convert_percent_to_dec(percent):
    """ Convert a percentage to a decimal. IE. 100% = 1.0, 50% = 0.5
    """
    dec = percent/100

    return dec


class LEDStateHolder(object):
    """ Object for holding LED state.
    """
    def __init__(self):
        self._red = 0
        self._green = 0
        self._blue = 0

    def set_state(self, red, green, blue):
        """ Set LED state
        """
        if _check_rgb_types(red, green, blue):
            self._red = red
            self._green = green
            self._blue = blue
        else:
            raise TypeError("Expected variable type INT")

    def get_state(self):
        """ Get LED state.
        """
        return (self._red, self._green, self._blue)

STATE_HOLDER = LEDStateHolder()


class LEDAPI(MethodView):
    """ API for controlling LEDs.
    """
    def get(self):  # pylint: disable=no-self-use
        """ Get current state of LED settings.
        """
        red, green, blue = STATE_HOLDER.get_state()

        led_state = {
            "red": red,
            "green": green,
            "blue": blue
        }

        return jsonify(led_state)

    def post(self):  # pylint: disable=no-self-use
        """ Set state of LED settings.
        """
        data = request.json

        try:
            STATE_HOLDER.set_state(
                data['red'],
                data['green'],
                data['blue']
            )

            red, green, blue = STATE_HOLDER.get_state()

            _change_leds(
                red,
                green,
                blue
            )
        except TypeError as error:
            print("Error processing post. Incorrect data provided: %s", error)

        return jsonify(dict(ok=True))


LED_API.add_url_rule('/leds/', view_func=LEDAPI.as_view('leds'))


if __name__ == "__main__":
    LED_API.run(host='0.0.0.0', port=8080)
