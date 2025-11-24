from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.state import AgentState
from services.llm_service import get_llm

def taste_profiler_agent(state: AgentState) -> AgentState:
    """
    Agent 2: Build user's music taste profile
    
    Analyzes Spotify data to create a "Taste DNA" profile:
    - Lyrical themes they connect with
    - Rhythm/tempo preferences
    - Genre clusters
    - Emotional range in music
    - Personality traits reflected in music taste
    """
    
    print("🎸 Agent 2: Profiling your music taste DNA...")
    
    llm = get_llm(temperature=0.5)
    
    profile = state["spotify_profile"]

    # prompt = ChatPromptTemplate.from_messages([
    #     ("system", """You are a music psychologist who understands how music taste 
    #     reflects personality, values, and emotional needs.
        
    #     Analyze the user's Spotify listening history to create a comprehensive 
    #     "Taste DNA" profile that will guide therapeutic music recommendations.
        
    #     Be insightful and nuanced - go beyond surface-level genre labels."""),
        
    #     ("user", """
    #     User's Spotify Profile:
        
    #     **Top Artists:** {top_artists}
    #     **Top Genres:** {top_genres}
    #     **Recent Tracks:** {recent_tracks}
        
    #     **Audio Feature Preferences:**
    #     - Average Tempo: {tempo} BPM
    #     - Average Energy: {energy} (0-1 scale)
    #     - Average Valence (positivity): {valence} (0-1 scale)
    #     - Average Danceability: {danceability} (0-1 scale)
    #     - Average Acousticness: {acousticness} (0-1 scale)
        
    #     Create a "Taste DNA" profile. Return JSON:
    #     {{
    #         "lyrical_themes": ["theme1", "theme2", "theme3"],
    #         "sonic_preferences": {{
    #             "tempo_range": "slow/moderate/fast/varied",
    #             "energy_preference": "low/medium/high/dynamic",
    #             "emotional_range": "melancholic/balanced/upbeat"
    #         }},
    #         "genre_clusters": ["cluster1", "cluster2"],
    #         "personality_traits": ["trait1", "trait2"],
    #         "discovery_openness": 0.7,
    #         "comfort_zone_description": "brief description of their musical comfort zone"
    #     }}
    #     """)
    # ])

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a music psychologist who understands how music taste 
        reflects personality, values, and emotional needs.
        
        Analyze the user's Spotify listening history to create a comprehensive 
        "Taste DNA" profile that will guide therapeutic music recommendations.
        
        Be insightful and nuanced - go beyond surface-level genre labels."""),
        
        ("user", """
        User's Spotify Profile:
        
        **Top Artists:** {top_artists}
        **Top Genres:** {top_genres}
        **Recent Tracks:** {recent_tracks}
        
        Create a "Taste DNA" profile. Return JSON:
        {{
            "lyrical_themes": ["theme1", "theme2", "theme3"],
            "sonic_preferences": {{
                "tempo_range": "slow/moderate/fast/varied",
                "energy_preference": "low/medium/high/dynamic",
                "emotional_range": "melancholic/balanced/upbeat"
            }},
            "genre_clusters": ["cluster1", "cluster2"],
            "personality_traits": ["trait1", "trait2"],
            "discovery_openness": 0.7,
            "comfort_zone_description": "brief description of their musical comfort zone"
        }}
        """)
    ])
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        # Format data for prompt
        top_artists_str = ", ".join([a["name"] for a in profile["top_artists"][:10]])
        top_genres_str = ", ".join(profile["top_genres"][:10])
        recent_tracks_str = ", ".join([
            f"{t['name']} by {t['artist']}" 
            for t in profile["recent_tracks"][:10]
        ])
        
        # audio = profile["audio_features"]
        
        taste_profile = chain.invoke({
            "top_artists": top_artists_str,
            "top_genres": top_genres_str,
            "recent_tracks": recent_tracks_str,
            # "tempo": f"{audio.get('tempo', 120):.0f}",
            # "energy": f"{audio.get('energy', 0.5):.2f}",
            # "valence": f"{audio.get('valence', 0.5):.2f}",
            # "danceability": f"{audio.get('danceability', 0.5):.2f}",
            # "acousticness": f"{audio.get('acousticness', 0.5):.2f}"
        })
        
        print(f"   ✓ Taste DNA created: {', '.join(taste_profile['genre_clusters'])}")
        
        return {
            **state,
            "taste_profile": taste_profile
        }
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Taste profiling failed: {e}"]
        }
