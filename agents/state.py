from typing_extensions import TypedDict
from typing import Annotated, Any
import operator

class AgentState(TypedDict):
    """State passed between agents in SoulSync workflow"""
    
    # User inputs
    user_input: str  # Raw emotional story
    user_id: str  # Spotify user ID
    
    # Spotify data
    spotify_profile: dict  # Complete profile from Spotify
    
    # Agent 1 outputs
    emotion_analysis: dict  # Primary emotion, intensity, story, desired outcome
    
    # Agent 2 outputs
    taste_profile: dict  # Music taste DNA (genres, themes, sonic preferences)
    
    # Agent 3a outputs
    universe_candidates: list  # 20-30 songs from universe with lyrical matches
    
    # Agent 3b outputs
    ranked_recommendations: list  # Top 10 with distance scores & reasoning
    
    # Final outputs
    spotify_tracks: list  # Resolved Spotify track objects
    playlist_url: str  # Created playlist URL
    
    # Meta
    errors: Annotated[list, operator.add]  # Accumulated errors