from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.state import AgentState
from services.llm_service import get_llm

def music_recommender_agent(state: AgentState) -> AgentState:
    """
    Agent 3a: Discover therapeutic songs from the universe
    
    Based on:
    - User's emotion and story
    - Their taste profile (as guidance, not constraint)
    
    Focus on finding songs with:
    - Similar lyrical themes/stories
    - Therapeutic value for their emotional state
    - Discovery potential (new to them)
    """
    
    print("🌍 Agent 3a: Discovering therapeutic music from the universe...")
    
    llm = get_llm(temperature=0.9)  # High creativity for discovery
    
    emotion = state["emotion_analysis"]
    taste = state["taste_profile"]
    profile = state["spotify_profile"]

    # print("THIS IS EMOTION",emotion)
    # print("THIS IS TASTE",taste)
    # print("THIS IS PROFILE",profile)
    
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a world-class music therapist with encyclopedic knowledge 
        of music across all genres, eras, and cultures.
        
        Your mission: Find therapeutic songs from the ENTIRE music universe that will 
        help the user heal emotionally. Prioritize songs they likely haven't heard.
        
        Consider:
        1. Lyrical content that mirrors or resolves their emotional story
        2. Sonic qualities that match therapeutic approach
        3. Cultural/historical context that adds meaning
        4. Discovery value - introduce them to new healing music
        
        Use their taste profile as GUIDANCE (not limitation) to ensure compatibility."""),
        
        ("user", """
        **User's Emotional State:**
        Primary Emotion: {primary_emotion}
        Intensity: {intensity}/10
        Story: {story_context}
        Desired Outcome: {desired_outcome}
        
        **User's Taste DNA (for compatibility guidance):**
        Lyrical Themes: {lyrical_themes}
        Sonic Preferences: {sonic_preferences}
        Genre Comfort Zone: {genre_clusters}
        Discovery Openness: {discovery_openness}/1.0
        
        **Recent Listening (to avoid):**
        {recent_tracks}
        
        **Mission:**
        Recommend 25 songs from the music universe that:
        1. Have lyrical themes/stories similar to their emotional experience
        2. Will therapeutically guide them from {primary_emotion} → {desired_outcome}
        3. Match their taste DNA enough to resonate (but push boundaries!)
        4. Are likely NEW discoveries for them
        5. Span different progression stages (1-10) of their emotional journey
        
        Return JSON array with 25 songs:
        [
            {{
                "track_name": "song title",
                "artist": "artist name",
                "album": "album name (if notable)",
                "year": "release year",
                "lyrical_theme": "how lyrics relate to user's story",
                "therapeutic_reason": "why this helps their emotional state",
                "sonic_match": "how it matches their taste",
                "discovery_score": 0.85,
                "progression_stage": 3,
                "spotify_search_query": "track:song_title artist:artist_name"
            }},
            ...
        ]
        
        Be bold in discovery while being therapeutic!
        """)
    ])
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        # Format recent tracks to avoid
        recent_tracks_str = ", ".join([
            f"{t['name']} by {t['artist']}" 
            for t in profile["recent_tracks"][:20]
        ])
        
        universe_candidates = chain.invoke({
            "primary_emotion": emotion["primary_emotion"],
            "intensity": emotion["intensity"],
            "story_context": emotion["story_context"],
            "desired_outcome": emotion["desired_outcome"],
            # "therapeutic_approach": emotion["therapeutic_approach"],
            "lyrical_themes": ", ".join(taste["lyrical_themes"]),
            "sonic_preferences": str(taste["sonic_preferences"]),
            "genre_clusters": ", ".join(taste["genre_clusters"]),
            "discovery_openness": taste["discovery_openness"],
            "recent_tracks": recent_tracks_str
        })
        
        print(f"   ✓ Found {len(universe_candidates)} therapeutic candidates")
        
        return {
            **state,
            "universe_candidates": universe_candidates
        }
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Music discovery failed: {e}"]
        }