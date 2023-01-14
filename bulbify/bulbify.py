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


def output(track, faster, louder, i):
    console.print(f"Track: {track.name}")
    console.print(f"Artist: {track.artists}")
    console.print(f"Album: {track.album}")
    console.print(f"Duration: {convert_ms(track.sections[-1].end)}\n")

    console.print(f"Section: {i+1}/{len(track.sections)}")
    console.print(f'Current position: {convert_ms(cur_ms)}')
    console.print(f'When it\'ll change: {convert_ms(track.sections[i].end)}\n')
    if args.tempo:
        console.print(f"Tempo: {'+' if faster else '-' }")
    if args.loudness:
        console.print(f"Loundess: {'+' if louder else '-' }")


def convert_ms(t):
    """ Convert milliseconds to mm:ss notation """
    return f"{int((t / 1000)) // 60}:{int(t // 1000) % 60:0>2}"


# command line args
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--flow", action="store_true", help="Flow effect")
parser.add_argument("-p",  "--pulse", action="store_true", help="Pulse effect")
parser.add_argument("-b",  "--breathe", action="store_true",
                    help="Breathe effect")
parser.add_argument("-c",  "--colour", action="store_true",
                    help="Breathe/Pulse to inverted colour")
parser.add_argument("-d", "--dark", action="store_true", help="Lights out")
parser.add_argument("-t",  "--tempo", action="store_false",
                    help="Relative changes in tempo between sections have no effect")
parser.add_argument("-l",  "--loudness", action="store_false",
                    help="Relative changes in loudness between sections have no effect")
parser.add_argument("-i",  "--invert", action="store_true",
                    help="Invert when Pulse and breathe effects occur")
parser.add_argument("-r",  "--random", action="store_true",
                    help="Random colours instead of range")
parser.add_argument("-s", "--selector",
                    choices=["main", "secondary"], help="Choose which bulb to run on")


args = parser.parse_args()

# spotify
username = os.getenv("SPOTIFY_USER_ID")
scope = "user-read-currently-playing user-read-playback-state user-modify-playback-state"
spotify_token = util.prompt_for_user_token(username, scope)
sp = Spotify(auth=spotify_token) if spotify_token else print(
    "Cannot get Spotify token")

# lifx
bulb = Bulb(args.selector)

# terminal
console = Console()

try:
    while True:
        # main loop
        i = 0
        track = Track(sp)

        start_colour = bulb.random_colour()
        end_colour = bulb.invert_colour(Color(start_colour))

        if args.random:
            colours = [bulb.random_colour()
                       for _ in range(len(track.sections))]
        else:
            colours = list(start_colour.range_to(
                end_colour, len(track.sections)))

        faster = False
        louder = False

        # loop for track
        while i < len(track.sections):
            cur_ms, _ = track.update()

            if cur_ms > track.sections[i].end:
                i += 1
                continue
            elif cur_ms < track.sections[i].start:
                i -= 1
                continue

            colour = colours[i].hex_l
            track.sections[i].colour = colour
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

            if louder:
                pulse = True if not args.invert else False
                breathe = False if not args.invert else True

            else:
                pulse = False if not args.invert else True
                breathe = True if not args.invert else False

            if args.pulse:
                pulse = True
                breathe = False
            elif args.breathe:
                pulse = False
                breathe = True

            # Set colour before affect for smoother transition
            bulb.flow(colour)
            # TODO: try see if passing duration as a arg makes it smoother

            # edge case where section has no tempo
            if period == 0 or args.flow:
                bulb.flow(colour)
            # Check command args and do appropriate affect
            elif pulse:
                dark = True if args.dark else False
                if args.random:
                    bulb.pulse(colour, period, cycles,  dark,  True)
                else:
                    bulb.pulse(colour, period, cycles,  dark)
            elif breathe:
                dark = True if args.dark else False
                if args.random:
                    bulb.breathe(colour, period, cycles,  dark, True)
                else:
                    bulb.breathe(colour, period, cycles,  dark)

            while cur_ms > track.sections[i].start - (bulb.DURATION * 1000 * 2) and cur_ms < track.sections[i].end - (bulb.DURATION * 1000 * 2):
                # see if * 2 for duration makes it smoother between sections if setting to colour first
                os.system("clear")
                output(track, faster, louder, i)

                time.sleep(0.5)
                cur_ms, uri = track.update()
                if uri != track.uri:
                    i = len(track.sections)
                    break

            i += 1

except Exception as e:
    print(e)

finally:
    bulb.reset()
    print("done")
