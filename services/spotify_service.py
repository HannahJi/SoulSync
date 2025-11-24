def fetch_user_profile(spotify_client):
    """
    Fetch comprehensive user profile from Spotify
    Returns: dict with top artists, genres, audio features, recent tracks
    """
    print("📊 Fetching your Spotify profile...")
    
    # Top artists (long term)
    top_artists = spotify_client.current_user_top_artists(limit=20, time_range='long_term')
    # Top tracks (for audio feature analysis)
    top_tracks = spotify_client.current_user_top_tracks(limit=50, time_range='long_term')
    
    # Recently played
    recent = spotify_client.current_user_recently_played(limit=50)
    
    # Extract data
    profile = {
        "user_id": spotify_client.current_user()["id"],
        "top_artists": [
            {"name": artist["name"], "genres": artist["genres"], "popularity": artist["popularity"]}
            for artist in top_artists["items"]
        ],
        "top_genres": extract_top_genres(top_artists["items"]),
        "top_tracks": [
            {
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "id": track["id"]
            }
            for track in top_tracks["items"]
        ],
        "recent_tracks": [
            {
                "name": item["track"]["name"],
                "artist": item["track"]["artists"][0]["name"],
                "played_at": item["played_at"]
            }
            for item in recent["items"]
        ],
        # "audio_features": calculate_avg_audio_features(spotify_client, top_tracks["items"])
    }
    
    print(f"✅ Profile loaded: {len(profile['top_artists'])} artists, {len(profile['top_genres'])} genres")
    return profile




def extract_top_genres(artists, top_n=10):
    """Extract most common genres from artist list"""
    genre_count = {}
    for artist in artists:
        for genre in artist["genres"]:
            genre_count[genre] = genre_count.get(genre, 0) + 1
    
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    return [genre for genre, count in sorted_genres[:top_n]]





# def calculate_avg_audio_features(spotify_client, tracks):
#     """Calculate average audio features from user's top tracks"""
#     track_ids = [track["id"] for track in tracks]
#     features = spotify_client.audio_features(track_ids)
    
#     # Filter out None values
#     valid_features = [f for f in features if f is not None]
    
#     if not valid_features:
#         return {}
    
#     avg = {
#         "tempo": sum(f["tempo"] for f in valid_features) / len(valid_features),
#         "energy": sum(f["energy"] for f in valid_features) / len(valid_features),
#         "valence": sum(f["valence"] for f in valid_features) / len(valid_features),
#         "danceability": sum(f["danceability"] for f in valid_features) / len(valid_features),
#         "acousticness": sum(f["acousticness"] for f in valid_features) / len(valid_features),
#         "instrumentalness": sum(f["instrumentalness"] for f in valid_features) / len(valid_features),
#     }
#     return avg



def create_spotify_playlist(spotify_client, user_id, tracks, emotion_context):
    """
    Create a new Spotify playlist with recommended tracks
    
    Args:
        spotify_client: Authenticated Spotify client
        user_id: Spotify user ID
        tracks: List of track URIs or IDs
        emotion_context: Dict with emotion info for playlist description
    
    Returns:
        Playlist URL
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%B %d, %Y")
    playlist_name = f"SoulSync: {emotion_context.get('primary_emotion', 'Healing')} Journey - {timestamp}"
    
    description = f"Therapeutic playlist curated by SoulSync for your {emotion_context.get('primary_emotion', 'emotional')} state. {emotion_context.get('description', '')}"
    
    # Create playlist
    playlist = spotify_client.user_playlist_create(
        user=user_id,
        name=playlist_name,
        public=False,
        description=description[:300]  # Spotify has 300 char limit
    )
    
    # Add tracks (ensure they're URIs)
    track_uris = [
        f"spotify:track:{t}" if not t.startswith("spotify:") else t
        for t in tracks
    ]
    
    spotify_client.playlist_add_items(playlist["id"], track_uris)
    
    print(f"✅ Playlist created: {playlist['external_urls']['spotify']}")
    return playlist["external_urls"]["spotify"]