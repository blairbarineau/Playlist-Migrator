# src/spotify_client.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config.settings import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_REDIRECT_URI

def create_spotify_client():
    """Initialize and return an authenticated Spotify client"""
    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope='playlist-read-private playlist-read-collaborative'
    )
    return spotipy.Spotify(auth_manager=auth_manager)

def get_user_playlists(spotify):
    """Fetch all playlists from the authenticated user"""
    results = spotify.current_user_playlists()
    for item in results['items']:
        print(f"Playlist: {item['name']}")
        
def get_playlist_tracks(spotify, playlist_id: str):
    """Fetch all tracks from a specific playlist with their details"""
    results = spotify.playlist_tracks(playlist_id)
    tracks = []
    
    while results:
        for item in results['items']:
            track = item['track']
            track_info = {
                'name': track['name'],
                'artist': track['artists'][0]['name'],
                'album': track['album']['name'],
                'duration_ms': track['duration_ms']
            }
            tracks.append(track_info)
            
        if results['next']:
            results = spotify.next(results)
        else:
            break
    
    return tracks