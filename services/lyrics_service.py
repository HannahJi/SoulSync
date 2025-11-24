import requests
from typing import Optional, Dict
from config.settings import GENIUS_ACCESS_TOKEN

class LyricsService:
    """fetches lyrics and song meanings from Genius API"""
    def __init__(self):
        self.base_url = "https://api.genius.com"
        self.headers = {
            "Authorization": f"Bearer {GENIUS_ACCESS_TOKEN}"
        }
    def search_song(self, track_name:str, artist_name: str) -> Optional[Dict]:
        try:
            search_url = f"{self.base_url}/search"
            params = {"q": f"{track_name} {artist_name}"}
            response = requests.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            results = response.json()["response"]["hits"]
            if results:
                song = results[0]["result"]
                return {
                    "genius_id": song["id"],
                    "title": song["title"],
                    "artist": song["primary_artist"]["name"],
                    "url": song["url"],
                    "annotation_count": song.get("annotation_count", 0),
                    "description": song.get("description", {}).get("plain", "")
                }
        except Exception as e:
            print(f"Error searching song on Genius: {e}")
            return None
    def get_song_details(self, genius_id: int) -> Optional[Dict]:
        try:
            song_url = f"{self.base_url}/songs/{genius_id}"
            response = requests.get(song_url, headers=self.headers)
            response.raise_for_status()
            song = response.json()["response"]["song"]
            return {
                "genius_id": song["id"],
                "title": song["title"],
                "artist": song["primary_artist"]["name"],
                "url": song["url"],
                "annotation_count": song.get("annotation_count", 0),
                "description": song.get("description", {}).get("plain", "")
            }
        except Exception as e:
            print(f"Error fetching song details from Genius: {e}")
            return None
    def _extract_song_meaning(self, song_data: Dict) -> str:
        """Extract song meaning/story from description"""
        description = song_data.get("description", {})
        
        if isinstance(description, dict):
            return description.get("plain", "")
        return str(description)
    
    def _extract_themes(self, song_data: Dict) -> list:
        """Extract thematic tags/topics from song"""
        # Genius has tags/annotations that hint at themes
        themes = []
        
        # From song tags
        if "tags" in song_data:
            themes.extend([tag["name"] for tag in song_data.get("tags", [])])
        
        return themes[:5]  # Return top 5 themes




def enrich_track_with_lyrics_context(track_info: Dict) -> Dict:
    """
    Enrich a track with lyrics context from Genius
    
    Args:
        track_info: Dict with 'track_name' and 'artist' keys
    
    Returns:
        Enhanced dict with lyrics_context added
    """
    lyrics_service = LyricsService()
    
    song_data = lyrics_service.search_song(
        track_info["track_name"],
        track_info["artist"]
    )
    
    if song_data and song_data["genius_id"]:
        details = lyrics_service.get_song_details(song_data["genius_id"])
        
        track_info["lyrics_context"] = {
            "song_meaning": details.get("song_meaning", ""),
            "themes": details.get("themes", []),
            "genius_url": song_data.get("url", "")
        }
    else:
        track_info["lyrics_context"] = {
            "song_meaning": "No lyrics context available",
            "themes": [],
            "genius_url": ""
        }
    
    return track_info