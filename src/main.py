# src/main.py
from spotify_client import create_spotify_client, get_playlist_tracks
from tidal_client import create_tidal_client, create_playlist, search_track, test_tidal_search
import time
def display_all_playlists(spotify):
    """Display all available Spotify playlists"""
    playlists = spotify.current_user_playlists()['items']
    print("\nYour Spotify playlists:")
    print("----------------------")
    for playlist in playlists:
        print(f"- {playlist['name']} ({playlist['tracks']['total']} tracks)")
    print("----------------------")
    return playlists

def find_playlist_by_name(spotify, name):
    """Find a playlist that matches the given name"""
    playlists = spotify.current_user_playlists()['items']
    for playlist in playlists:
        if playlist['name'].lower() == name.lower():
            return playlist
    return None


def migrate_playlist(spotify_tracks, tidal_session, playlist_name):
    """Migrate tracks from Spotify to Tidal"""
    print(f"\nCreating new Tidal playlist: {playlist_name}")
    tidal_playlist = create_playlist(tidal_session, playlist_name)
    
    if not tidal_playlist:
        print("Failed to create Tidal playlist!")
        return 0, []
    
    found_tracks = []
    not_found = []
    
    print("\nSearching for tracks on Tidal...")
    for i, track in enumerate(spotify_tracks, 1):
        print(f"\nProcessing track {i}/{len(spotify_tracks)}")
        print(f"Spotify track: '{track['name']}' by '{track['artist']}'")
        
        track_id = search_track(tidal_session, track['name'], track['artist'])
        
        if track_id:
            try:
                print(f"Adding track {track_id} to playlist...")
                tidal_playlist.add([track_id])
                print("Successfully added track")
                found_tracks.append(track_id)
                time.sleep(0.1) 
            except Exception as e:
                print(f"Error adding track: {e}")
                print(f"Track ID that failed: {track_id}")
                import traceback
                traceback.print_exc()
        else:
            not_found.append(f"{track['name']} by {track['artist']}")
            print("✗ Not found on Tidal")
    
    return len(found_tracks), not_found

def main():
    try:
        print("Connecting to Spotify...")
        spotify = create_spotify_client()
        print("\nConnecting to Tidal...")
        tidal = create_tidal_client()
        
        if spotify and tidal:
            test_tidal_search(tidal)
            playlists = display_all_playlists(spotify)
            
            while True:
                print("\nEnter 'quit' to exit")
                print("Enter 'list' to see all playlists again")
                playlist_name = input("Enter the name of the playlist you want to migrate: ").strip()
                
                if playlist_name.lower() == 'quit':
                    break
                    
                if playlist_name.lower() == 'list':
                    display_all_playlists(spotify)
                    continue
                
                playlist = find_playlist_by_name(spotify, playlist_name)
                
                if playlist:
                    print(f"\nFound playlist: {playlist['name']} ({playlist['tracks']['total']} tracks)")
                    tracks = get_playlist_tracks(spotify, playlist['id'])
                    
                    # Actually migrate the playlist
                    found_count, not_found = migrate_playlist(tracks, tidal, playlist['name'])
                    
                    print(f"\nMigration complete!")
                    print(f"Successfully migrated: {found_count}/{len(tracks)} tracks")
                    
                    if not_found:
                        print("\nTracks not found on Tidal:")
                        for track in not_found:
                            print(f"- {track}")
                    
                else:
                    print(f"\nCouldn't find a playlist named '{playlist_name}'")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()