# ============================================================================
# FILE: agents/taste_ranker.py
# ============================================================================
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.state import AgentState
from services.llm_service import get_llm

def taste_ranker_agent(state: AgentState) -> AgentState:
    """
    Agent 3b: Rank candidates by distance to user's taste
    
    Calculate multi-dimensional distance:
    1. Lyrical similarity to their story
    2. Sonic similarity to their preferences
    3. Therapeutic fit for their emotion
    4. Discovery balance (familiar vs. novel)
    
    Output: Top 10 ranked recommendations with reasoning
    """
    
    print("🎯 Agent 3b: Ranking recommendations by taste-distance...")
    
    llm = get_llm(temperature=0.4)  # Moderate temp for balanced ranking
    
    emotion = state["emotion_analysis"]
    taste = state["taste_profile"]
    candidates = state["universe_candidates"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a precision recommendation algorithm with deep understanding 
        of music therapy and personalization.
        
        Your task: Rank the candidate songs by calculating multi-dimensional "distance" 
        to the user's needs. Lower distance = better match.
        
        Distance factors:
        1. Lyrical resonance (how well lyrics match their story)
        2. Sonic compatibility (matches their audio preferences)
        3. Therapeutic effectiveness (helps emotional transition)
        4. Discovery balance (not too safe, not too alien)
        
        Select the TOP 10 songs that optimize all factors."""),
        
        ("user", """
        **User's Emotional Need:**
        {emotion_summary}
        
        **User's Taste Profile:**
        {taste_summary}
        
        **Candidate Songs ({num_candidates} total):**
        {candidates_json}
        
        **Task:**
        1. Calculate distance scores for each candidate (0-1, lower is better)
        2. Select TOP 10 songs that balance therapeutic value + taste match + discovery
        3. Provide detailed reasoning for each selection
        
        Return JSON array of TOP 10:
        [
            {{
                "track_name": "...",
                "artist": "...",
                "album": "...",
                "year": "...",
                "therapeutic_reason": "comprehensive explanation of therapeutic value",
                "taste_distance_score": 0.23,
                "lyrical_match_score": 0.92,
                "sonic_match_score": 0.85,
                "discovery_score": 0.7,
                "progression_stage": 5,
                "spotify_search_query": "...",
                "ranking_rationale": "why this made top 10"
            }},
            ...
        ]
        
        Order by overall best match (considering all factors).
        """)
    ])
    
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    
    try:
        import json
        
        emotion_summary = f"{emotion['primary_emotion']} (intensity {emotion['intensity']}/10) → {emotion['desired_outcome']}"
        taste_summary = f"Genres: {', '.join(taste['genre_clusters'][:3])}, Themes: {', '.join(taste['lyrical_themes'][:3])}"
        
        ranked_recommendations = chain.invoke({
            "emotion_summary": emotion_summary,
            "taste_summary": taste_summary,
            "num_candidates": len(candidates),
            "candidates_json": json.dumps(candidates, indent=2)
        })
        
        print(f"   ✓ Selected top {len(ranked_recommendations)} recommendations")
        
        return {
            **state,
            "ranked_recommendations": ranked_recommendations
        }
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Ranking failed: {e}"]
        }