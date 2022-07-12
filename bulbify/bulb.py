from pifx import PIFX
from random import randint
from colour import Color
import os


class Bulb:
    def __init__(self):
        self.p = PIFX(os.getenv("LIFX_KEY"))
        self.BASE_COLOUR = "hue:240 kelvin:9000"
        self.DURATION = 1
        self.BRIGHTNESS = 1

    def flow(self, colour):
        self.p.set_state(
            color=colour, brightness=self.BRIGHTNESS, duration=self.DURATION)

    def pulse(self, colour, period, cycles, dark, random=False):
        if not dark:
            if random:
                to_colour = self.random_colour().hex_l
            else:
                to_colour = self.invert_colour(Color(colour)).hex_l
        else:
            to_colour = "#000000"

        self.p.pulse_lights(from_color=colour, color=to_colour,
                            period=period, cycles=cycles)

    def breathe(self, colour, period, cycles, dark, random=False):
        if not dark:
            to_colour = self.invert_colour(Color(colour)).hex_l
        else:
            to_colour = "#000000"

        self.p.breathe_lights(
            from_color=colour, color=to_colour, period=period*2, cycles=cycles/2)

    def reset(self):
        self.p.set_state(color=self.BASE_COLOUR)

    def invert_colour(self, colour):
        """ Invert colour """
        new_red = 1.0 - colour.red
        new_green = 1.0 - colour.green
        new_blue = 1.0 - colour.blue
        return Color(red=new_red, green=new_green, blue=new_blue)

    def random_colour(self):
        """ Create random Colour object """
        num = randint(0, 16777215)
        hex_str = "#" + f"{hex(num)[2:]}".zfill(6)
        return Color(hex_str)
