import spotipy.util as util
from spotipy import Spotify
from track import Track
import os
from colour import Color
from pifx import PIFX
from random import randint, choice, shuffle
import time


def invert_colour(colour):
    """ Invert colour """
    new_red = 1.0 - colour.red
    new_green = 1.0 - colour.green
    new_blue = 1.0 - colour.blue
    return Color(red=new_red, green=new_green, blue=new_blue)

def convert_ms(t):
    """ Convert milliseconds to mm:ss notation """
    return f"{int((t / 1000)) // 60}:{int(t // 1000) % 60:0>2}"

def random_colour():
    """ Create random Colour object """
    num = randint(0, 16777215) 
    hex_str = f"#{hex(num)[2:]}".zfill(7)
    return Color(hex_str)

# spotify
username = os.getenv("SPOTIFY_USER_ID") 
scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
spotify_token = util.prompt_for_user_token(username, scope)
sp = Spotify(auth=spotify_token) if spotify_token else print("Cannot get Spotify token")

# lifx
bulb = PIFX(os.getenv("LIFX_KEY")) 

DURATION = 1
while True:
    i = 0
    track = Track(sp)

    # start_colour = Color(choice(["red", "orange", "yellow", "green", "blue"]))
    start_colour = random_colour()
    end_colour = invert_colour(start_colour)

    colours = list(start_colour.range_to(end_colour, len(track.sections)))
    shuffle(colours)

    while i < len(track.sections):
        cur_ms, _ = track.update()
 

        bulb.set_state(color=colours[i].hex_l, brightness=1, duration=DURATION)
        while cur_ms < track.sections[i].end - 0.5 - DURATION:
            # behind
            if cur_ms > track.sections[i].end:
                i += 1 
                bulb.set_state(color=colours[i].hex_l, brightness=1, duration=DURATION)
                continue
            # ahead
            elif cur_ms < track.sections[i].start:
                i -= 1 
                bulb.set_state(color=colours[i].hex_l, brightness=1, duration=DURATION)
                continue
            
            os.system("clear")
            print(f"Track: {track.name}") 
            print(f"Artist: {track.artists}")
            print(f"Album: {track.album}")
            print(f"Duration: {convert_ms(track.sections[-1].end)}\n")
            print(f"Section: {i+1}/{len(track.sections)}")
            print(f'Current position: {convert_ms(cur_ms)}')
            print(f'When it\'ll change: {convert_ms(track.sections[i].end)}\n')

            time.sleep(1)
            cur_ms, uri = track.update()
            if uri != track.uri:
                i = len(track.sections)
                break
        
        i += 1

        
