
import spotipy.util as util
from spotipy import *
import os



        
def main():
    username = os.getenv('SPOTIFY_USER_ID')

    scope = 'user-top-read user-library-read playlist-modify-public'
    spotify_token = util.prompt_for_user_token(username, scope)
    
    sp = Spotify(auth=spotify_token) if spotify_token else print('Cannot get Spotify token')
    uris = []
    playlists = sp.current_user_playlists()
    for playlist in playlists["items"]:
        if playlist["name"].startswith("Filtered"):
            uris.append(playlist["id"])
    total = len(uris)
    for uri in uris:
        sp.current_user_unfollow_playlist(uri)
    print(f"Deleted: {total} Filtered playlists")
main()
