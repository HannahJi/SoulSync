from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.emotion_analyzer import emotion_analyzer_agent
from agents.taste_profiler import taste_profiler_agent
from agents.music_recommender import music_recommender_agent
from agents.taste_ranker import taste_ranker_agent
from services.spotify_resolver import resolve_recommendations_to_spotify
from services.spotify_service import create_spotify_playlist
from auth.spotify_auth import get_spotify_client


def create_soulsync_workflow():
    """
    Build the complete SoulSync workflow using LangGraph
    
    Flow:
    1. Emotion Analyzer → Analyzes user's emotional state
    2. Taste Profiler → Builds music taste DNA from Spotify data
    3. Music Recommender → Discovers therapeutic songs from universe
    4. Taste Ranker → Ranks by distance to user's taste
    5. Spotify Resolver → Resolves to actual Spotify tracks & creates playlist
    
    Returns:
        Compiled LangGraph workflow
    """
    
    # Initialize the state graph
    workflow = StateGraph(AgentState)
    
    # Add all agent nodes
    workflow.add_node("analyze_emotion", emotion_analyzer_agent)
    workflow.add_node("profile_taste", taste_profiler_agent)
    workflow.add_node("discover_music", music_recommender_agent)
    workflow.add_node("rank_recommendations", taste_ranker_agent)
    workflow.add_node("resolve_spotify", resolve_and_create_playlist_node)
    
    # Define the flow (sequential execution)
    workflow.set_entry_point("analyze_emotion")
    workflow.add_edge("analyze_emotion", "profile_taste")
    workflow.add_edge("profile_taste", "discover_music")
    workflow.add_edge("discover_music", "rank_recommendations")
    workflow.add_edge("rank_recommendations", "resolve_spotify")
    workflow.add_edge("resolve_spotify", END)
    
    # Compile and return
    return workflow.compile()


def resolve_and_create_playlist_node(state: AgentState) -> AgentState:
    """
    Final node in the workflow:
    1. Resolves GPT's recommendations to actual Spotify tracks
    2. Creates a Spotify playlist with those tracks
    
    Args:
        state: Current AgentState with ranked_recommendations
    
    Returns:
        Updated state with spotify_tracks and playlist_url
    """
    
    print("\n🎧 Final Step: Creating your Spotify playlist...")
    
    try:
        # Get authenticated Spotify client
        spotify_client = get_spotify_client()
        
        # Resolve recommendations to Spotify tracks
        print("\n📡 Searching for songs on Spotify...")
        spotify_tracks = resolve_recommendations_to_spotify(
            recommendations=state["ranked_recommendations"],
            spotify_client=spotify_client
        )
        
        if not spotify_tracks:
            raise Exception("Could not resolve any tracks to Spotify")
        
        # Extract track IDs for playlist creation
        track_ids = [track["spotify_id"] for track in spotify_tracks]
        
        # Create the playlist
        print("\n🎵 Creating playlist...")
        playlist_url = create_spotify_playlist(
            spotify_client=spotify_client,
            user_id=state["user_id"],
            tracks=track_ids,
            emotion_context={
                "primary_emotion": state["emotion_analysis"]["primary_emotion"],
                "description": (
                    f"A therapeutic journey from {state['emotion_analysis']['primary_emotion']} "
                    f"to {state['emotion_analysis']['desired_outcome']}. "
                    f"Curated by SoulSync based on your emotional needs and music taste."
                )
            }
        )
        
        print(f"✅ Playlist created successfully!")
        
        return {
            **state,
            "spotify_tracks": spotify_tracks,
            "playlist_url": playlist_url
        }
        
    except Exception as e:
        print(f"❌ Error in playlist creation: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            **state,
            "spotify_tracks": [],
            "playlist_url": "",
            "errors": state.get("errors", []) + [f"Playlist creation failed: {str(e)}"]
        }