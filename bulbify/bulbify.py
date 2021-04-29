import spotipy.util as util
from spotipy import Spotify
from track import Track
import os
from colour import Color
from pifx import PIFX
from random import randint, choice, shuffle
import time
import argparse
from bulb import Bulb
from rich.console import Console 

def output(track, faster, louder):
    console.print(f"Track: {track.name}") 
    console.print(f"Artist: {track.artists}")
    console.print(f"Album: {track.album}")
    console.print(f"Duration: {convert_ms(track.sections[-1].end)}\n")

    console.print(f"Section: {i+1}/{len(track.sections)}")
    console.print(f'Current position: {convert_ms(cur_ms)}')
    console.print(f'When it\'ll change: {convert_ms(track.sections[i].end)}\n')
    if args.tempo:
        print(f"Tempo: {'+' if faster else '-' }")
    if args.loudness:
        print(f"Loundess: {'+' if louder else '-' }")


def convert_ms(t):
    """ Convert milliseconds to mm:ss notation """
    return f"{int((t / 1000)) // 60}:{int(t // 1000) % 60:0>2}"
    
def random_colour():
    """ Create random Colour object """
    num = randint(0, 16777215) 
    hex_str = "#" + f"{hex(num)[2:]}".zfill(6)
    return Color(hex_str)


# command line args
parser = argparse.ArgumentParser()
parser.add_argument("-s",  "--strobe", action="store_true", help="Strobe effect")
parser.add_argument("-b",  "--breathe", action="store_true", help="Breathe effect")
parser.add_argument("-c",  "--colour", action="store_true", help="Breathe/strobe to inverted colour")
parser.add_argument("-t",  "--tempo", action="store_false", help="Relative changes in tempo between sections have no effect")
parser.add_argument("-l",  "--loudness", action="store_false", help="Relative changes in loudness between sections have no effect")
parser.add_argument("-i",  "--invert", action="store_true", help="Invert when strobe and breathe effects occur")


args = parser.parse_args()

# spotify
username = os.getenv("SPOTIFY_USER_ID") 
scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
spotify_token = util.prompt_for_user_token(username, scope)
sp = Spotify(auth=spotify_token) if spotify_token else print("Cannot get Spotify token")

# lifx
bulb = Bulb()

# terminal
console = Console()


try:
    # main loop
    while True:
        i = 0
        track = Track(sp)

        start_colour = random_colour()
        end_colour = bulb.invert_colour(Color(start_colour))

        colours = list(start_colour.range_to(end_colour, len(track.sections)))
        shuffle(colours)

        faster = False
        louder = False

        # loop for track
        while i < len(track.sections):
            cur_ms, _ = track.update()
    
            colour = colours[i].hex_l
            period = track.sections[i].period
            cycles = track.sections[i].cycles

            # Changes in tempo
            if i == 0 or not args.tempo or track.sections[i-1].tempo > track.sections[i].tempo:
                # first section/-t flag provided/slower than previous section
                faster = False
            else:
                faster = True

            if not faster:
                period *= 2
                cycles /= 2

            # Changes in loudness 
            if i == 0 or not args.loudness or track.sections[i-1].loudness > track.sections[i].loudness:
                # first section/-t flag provided/quiter than previous section
                louder = False
            else:
                louder = True 

            if louder and not args.invert:
                args.strobe = True
                args.breathe = False
            else:
                args.strobe = False
                args.breathe = True
        
            # Set colour before affect for smoother transition 
            bulb.flow(colour)

            # edge case where seciton has no tempo 
            if period == 0:
                bulb.flow(colour)
            # Check command args and do appropriate affect 
            elif args.strobe:
                dark = False if args.colour else True
                bulb.strobe(colour, period, cycles, dark)
            elif args.breathe:
                dark = False if args.colour else True
                bulb.breathe(colour, period, cycles, dark)
            
            # section is playing 
            while cur_ms < track.sections[i].end - bulb.DURATION:
                # behind
                if cur_ms > track.sections[i].end:
                    i += 1
                    colour = colours[i].hex_l 
                    continue
                # ahead
                elif cur_ms < track.sections[i].start:
                    i -= 1 
                    colour = colours[i].hex_l
                    continue
                
                os.system("clear")
                output(track, faster, louder)
                
                time.sleep(1)

                cur_ms, uri = track.update()
                if uri != track.uri:
                    i = len(track.sections)
                    break
            
            i += 1

finally:
    bulb.reset()

            
