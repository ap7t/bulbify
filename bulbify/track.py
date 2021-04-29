import spotipy.util as util
from spotipy import Spotify
import os

class Track:
    def __init__(self, sp):
        self.sp = sp
        response = self.sp.current_playback()
        self.uri = response["item"]["uri"]
        self.name = response["item"]["name"]
        self.artists = ", ".join([response["item"]["artists"][i]["name"] for i in range(len(response["item"]["artists"]))])
        self.album = response["item"]["album"]["name"]
        self.progress_ms = response["progress_ms"]
        self.is_playing = response["is_playing"]
        
        anal_response = sp.audio_analysis(self.uri)
        self.sections = [Section(section) for section in anal_response["sections"]] 

    def update(self):
        response = self.sp.current_playback()
        uri = response["item"]["uri"]
        progress_ms = response["progress_ms"]
        is_playing = response["is_playing"] 
        
        return progress_ms, uri

class Section:
    def __init__(self, section):
        self.start = section["start"] * 1000 # convert to ms 
        self.duration = section["duration"] * 1000 # convert to ms  
        self.end = self.start + self.duration 
        self.loudness = section["loudness"]
        self.tempo = section["tempo"]
        self.colour = None

        duration = section["duration"]
        totalbeats = (duration / 60 ) * self.tempo
        if totalbeats == 0:
            self.period = self.cycles = 0
        else:
            self.period = duration / totalbeats 
            self.cycles = duration / self.period

