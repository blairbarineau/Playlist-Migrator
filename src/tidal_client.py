# src/tidal_client.py
import tidalapi
import json
import os
from typing import Optional

def load_tidal_token():
    """Load Tidal token from config file"""
    try:
        if os.path.exists('config/tidal_token.json'):
            with open('config/tidal_token.json', 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading token: {e}")
    return None

def save_tidal_token(token_info):
    """Save Tidal token to config file"""
    try:
        os.makedirs('config', exist_ok=True)
        with open('config/tidal_token.json', 'w') as f:
            json.dump(token_info, f)
    except Exception as e:
        print(f"Error saving token: {e}")

def create_tidal_client() -> Optional[tidalapi.Session]:
    """Initialize and return an authenticated Tidal session"""
    try:
        session = tidalapi.Session()
        token = load_tidal_token()
        if token:
            try:
                session.load_oauth_session(
                    token['token_type'],
                    token['access_token'],
                    token['refresh_token']
                )
                if session.check_login():
                    print("Successfully logged into Tidal using saved token")
                    return session
            except Exception as e:
                print(f"Error using saved token: {e}")
        print("No valid token found. Please login via browser (one-time setup)...")
        session.login_oauth_simple()
        if session.check_login():
            token_info = {
                'token_type': session.token_type,
                'access_token': session.access_token,
                'refresh_token': session.refresh_token
            }
            save_tidal_token(token_info)
            print("Token saved for future use")
            return session
            
        print("Tidal login failed")
        return None
            
    except Exception as e:
        print(f"Error connecting to Tidal: {e}")
        return None

def test_tidal_connection(session: tidalapi.Session):
    """Test the Tidal connection by fetching user playlists"""
    try:
        playlists = session.user.playlists()
        print("\nYour Tidal playlists:")
        for playlist in playlists:
            print(f"- {playlist.name}")
    except Exception as e:
        print(f"Error fetching Tidal playlists: {e}")

def delete_all_playlists(session: tidalapi.Session):
    """Delete all playlists from the user's Tidal account"""
    try:
        playlists = session.user.playlists()
        total = len(playlists)
        
        if total == 0:
            print("No playlists found to delete.")
            return
            
        print(f"Found {total} playlists. Starting deletion...")
        
        for i, playlist in enumerate(playlists, 1):
            print(f"Deleting {i}/{total}: {playlist.name}")
            playlist.delete()
        print("\nAll playlists have been deleted!")
        
    except Exception as e:
        print(f"Error while deleting playlists: {e}")
        
def search_track(session, track_name: str, artist_name: str):
    """Search for a track on Tidal with more lenient matching"""
    try:
        track_name = track_name.replace("&", "and").split("-")[0].strip()
        artist_name = artist_name.replace("&", "and").split("(")[0].strip()
        
        query = f"{track_name} {artist_name}"
        print(f"\nSearching Tidal for: '{query}'")
        results = session.search(query)
        
        if results and 'tracks' in results:
            tracks = results['tracks'] 
            if tracks:
                print(f"Found {len(tracks)} potential matches")
                
                for track in tracks[:5]:
                    print(f"Checking: '{track.name}' by '{track.artist.name}'")
                    
                    if (track_name.lower() in track.name.lower() or 
                        track.name.lower() in track_name.lower()) and \
                       (artist_name.lower() in track.artist.name.lower() or 
                        track.artist.name.lower() in artist_name.lower()):
                        print(f"Found match: '{track.name}' by '{track.artist.name}'")
                        return track.id
                
                first_track = tracks[0]
                if track_name.lower() in first_track.name.lower() or \
                   first_track.name.lower() in track_name.lower():
                    print(f"Found partial match: '{first_track.name}' by '{first_track.artist.name}'")
                    return first_track.id
        
        print("No matches found on Tidal")
        return None
            
    except Exception as e:
        print(f"\nError searching: {e}")
        import traceback
        traceback.print_exc()
        return None

def create_playlist(session, name: str):
    """Create a new playlist on Tidal"""
    try:
        playlist = session.user.create_playlist(name, "Migrated from Spotify")
        print(f"Created playlist: {playlist.name} (ID: {playlist.id})")
        return playlist
    except Exception as e:
        print(f"\nError creating playlist: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_tidal_search(session):
    """Test the Tidal search functionality with a simple query"""
    try:
        print("\nTesting Tidal search...")
        print("Searching for 'Drake'...")
        results = session.search('Drake')
        
        print("\nFull results structure:")
        for key in results.keys():
            print(f"\nKey: {key}")
            print(f"Content: {results[key]}")
            
        if 'tracks' in results:
            print("\nFirst track details:")
            first_track = results['tracks']['items'][0]
            print("Track keys:", first_track.keys())
            print("Track details:", first_track)
            
    except Exception as e:
        print(f"Test search error: {e}")
        import traceback
        traceback.print_exc()