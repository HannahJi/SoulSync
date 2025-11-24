from auth.spotify_auth import get_spotify_client
from services.spotify_service import fetch_user_profile
from workflows.soulsync_graph import create_soulsync_workflow



def main():
    """SoulSync CLI - Main entry point"""
    
    print("=" * 60)
    print("🎵 Welcome to SoulSync - Your Music Therapy Companion")
    print("=" * 60)
    print()
    
    # Phase 1: Spotify Authentication
    print("Step 1: Connecting to your Spotify account...")
    print("(A browser window will open for authorization)")
    print()
    
    try:
        spotify_client = get_spotify_client()
        print("✅ Successfully connected to Spotify!\n")
    except Exception as e:
        print(f"❌ Failed to connect to Spotify: {e}")
        return
    
    # Phase 2: Fetch user profile
    try:
        user_profile = fetch_user_profile(spotify_client)
        print()
    except Exception as e:
        print(f"❌ Failed to fetch profile: {e}")
        return
    
    # Phase 3: Get user's emotional input
    print("=" * 60)
    print("Step 2: Tell me what you're feeling")
    print("=" * 60)
    print()
    print("Share your emotions, what happened, and how you'd like to feel.")
    print("The more you share, the better I can help you.\n")
    
    user_input = input("💭 Tell me what you feel now:\n> ")
    print()
    
    if not user_input.strip():
        print("❌ Please share your feelings to continue.")
        return
    
    # Phase 4: Run SoulSync workflow
    print("=" * 60)
    print("🔮 SoulSync is working its magic...")
    print("=" * 60)
    print()
    
    workflow = create_soulsync_workflow()
    
    initial_state = {
        "user_input": user_input,
        "user_id": user_profile["user_id"],
        "spotify_profile": user_profile,
        "emotion_analysis": {},
        "taste_profile": {},
        "universe_candidates": [],
        "ranked_recommendations": [],
        "spotify_tracks": [],
        "playlist_url": "",
        "errors": []
    }
    
    try:
        result = workflow.invoke(initial_state)
        
        # Display results
        print("\n" + "=" * 60)
        print("✨ Your Personalized Therapeutic Playlist")
        print("=" * 60)
        print()
        
        display_results(result)
        
    except Exception as e:
        print(f"❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()


def display_results(result):
    """Display final results to user"""
    
    # Show emotion analysis
    emotion = result["emotion_analysis"]
    print(f"🎭 Emotional Analysis:")
    print(f"   Primary emotion: {emotion.get('primary_emotion', 'N/A')}")
    print(f"   Intensity: {emotion.get('intensity', 'N/A')}/10")
    print(f"   Desired outcome: {emotion.get('desired_outcome', 'N/A')}")
    print()
    
    # Show recommendations
    print(f"🎵 Your Therapeutic Journey ({len(result['ranked_recommendations'])} songs):")
    print()
    
    for i, rec in enumerate(result["ranked_recommendations"], 1):
        print(f"{i}. {rec['track_name']} - {rec['artist']}")
        print(f"   💡 {rec['therapeutic_reason']}")
        print(f"   ✨ Discovery Score: {'🌟' * int(rec['discovery_score'] * 5)}")
        print(f"   🎭 Journey Stage: {rec['progression_stage']}/10")
        print()
    
    # Show playlist
    if result["playlist_url"]:
        print("=" * 60)
        print(f"🎧 Your playlist is ready!")
        print(f"   {result['playlist_url']}")
        print("=" * 60)


if __name__ == "__main__":
    main()