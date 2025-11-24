# ============================================================================
# FILE: services/spotify_resolver.py
# ============================================================================
def resolve_recommendations_to_spotify(recommendations, spotify_client):
    """
    Resolve GPT's universe recommendations to actual Spotify tracks
    
    Args:
        recommendations: List of dicts with 'spotify_search_query' field
        spotify_client: Authenticated Spotify client
    
    Returns:
        List of resolved Spotify track objects
    """
    
    print("🔍 Resolving songs on Spotify...")
    
    resolved_tracks = []
    failed_tracks = []
    
    for i, rec in enumerate(recommendations, 1):
        search_query = rec.get("spotify_search_query", 
                               f"track:{rec['track_name']} artist:{rec['artist']}")
        
        try:
            # Search Spotify
            results = spotify_client.search(
                q=search_query,
                type="track",
                limit=3
            )
            
            if results["tracks"]["items"]:
                # Take best match
                track = results["tracks"]["items"][0]
                
                resolved_tracks.append({
                    "spotify_id": track["id"],
                    "spotify_uri": track["uri"],
                    "track_name": track["name"],
                    "artist": track["artists"][0]["name"],
                    "album": track["album"]["name"],
                    "preview_url": track.get("preview_url"),
                    "external_url": track["external_urls"]["spotify"],
                    # Preserve GPT metadata
                    "therapeutic_reason": rec.get("therapeutic_reason", ""),
                    "discovery_score": rec.get("discovery_score", 0.5),
                    "progression_stage": rec.get("progression_stage", 5),
                    "taste_distance_score": rec.get("taste_distance_score", 0.5)
                })
                
                print(f"   ✓ [{i}/{len(recommendations)}] Found: {track['name']} - {track['artists'][0]['name']}")
            else:
                print(f"   ✗ [{i}/{len(recommendations)}] Not found: {rec['track_name']} - {rec['artist']}")
                failed_tracks.append(rec)
                
        except Exception as e:
            print(f"   ✗ [{i}/{len(recommendations)}] Error searching: {e}")
            failed_tracks.append(rec)
    
    # Handle failed tracks with GPT alternatives
    if failed_tracks:
        print(f"\n⚠️  {len(failed_tracks)} songs not found, getting alternatives...")
        alternatives = get_spotify_alternatives(failed_tracks, spotify_client)
        resolved_tracks.extend(alternatives)
    
    print(f"\n✅ Successfully resolved {len(resolved_tracks)} tracks")
    return resolved_tracks


def get_spotify_alternatives(failed_tracks, spotify_client):
    """
    Use GPT to suggest Spotify-available alternatives for failed tracks
    """
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from services.llm_service import get_llm
    
    llm = get_llm(temperature=0.7)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a music expert helping find alternative songs 
        that ARE available on Spotify and serve the same therapeutic purpose."""),
        
        ("user", """
        These songs couldn't be found on Spotify:
        {failed_tracks}
        
        For each song, suggest ONE alternative that:
        1. Serves the same therapeutic purpose
        2. IS available on Spotify (popular/well-known songs)
        3. Matches the original's emotional intent
        
        Return JSON array:
        [
            {{
                "track_name": "alternative song",
                "artist": "artist name",
                "therapeutic_reason": "why this replaces the original",
                "spotify_search_query": "track:song artist:name"
            }},
            ...
        ]
        """)
    ])
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        import json
        failed_json = json.dumps([
            {
                "original": f"{t['track_name']} - {t['artist']}",
                "purpose": t.get("therapeutic_reason", "therapeutic value")
            }
            for t in failed_tracks
        ], indent=2)
        
        alternatives = chain.invoke({"failed_tracks": failed_json})
        
        # Resolve alternatives
        return resolve_recommendations_to_spotify(alternatives, spotify_client)
        
    except Exception as e:
        print(f"   ✗ Failed to get alternatives: {e}")
        return []
