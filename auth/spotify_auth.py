import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

def get_spotify_client():
    """
    Initialize Spotify client with OAuth
    User will be prompted to authorize in browser
    """
    scope = "user-top-read user-read-recently-played playlist-modify-public playlist-modify-private"
    
    auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=scope,
            open_browser=True
        )
    sp = spotipy.Spotify(auth_manager=auth_manager)
    
    return sp