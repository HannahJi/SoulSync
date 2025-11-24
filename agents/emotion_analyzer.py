from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from agents.state import AgentState
from services.llm_service import get_llm

def emotion_analyzer_agent(state:AgentState) -> AgentState:
    """
    Agent 1: Analyze user's emotional state from their input
    
    Extracts:
    - Primary emotion
    - Secondary emotions
    - Intensity (0-10)
    - Story context
    - Desired emotional outcome
    """
    print("Analyzing your emotions...")
    llm = get_llm()
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         """You are an empathetic emotional analyst. Your task is to deeply understand the user's emotional state based on their input.
                 Analyze their input and extract:
                    1. Primary emotion (e.g., anxious, sad, overwhelmed, angry, lonely)
                    2. Secondary emotions (supporting emotions)
                    3. Intensity (0-10 scale, where 10 is most intense)
                    4. Story context (what happened to them)
                    5. Desired outcome (how they want to feel after music therapy)
        """
        ),
        ("user",
         """User input: {user_input}
         
         Please provide the analysis in the following JSON format:
         {{
            "primary_emotion": "<primary_emotion>",
            "secondary_emotions": ["<secondary_emotion1>", "<secondary_emotion2>"],
            "intensity": <intensity>,
            "story_context": "<story_context>",
            "desired_outcome": "<desired_outcome>"
         }}
         """
        )
    ])
    parser = JsonOutputParser()
    chain = prompt | llm | parser
    try:
        emotion_analysis = chain.invoke({
            "user_input": state["user_input"]
        })
        
        print(f"   ✓ Identified: {emotion_analysis['primary_emotion']} (intensity: {emotion_analysis['intensity']}/10)")
        
        return {
            **state,
            "emotion_analysis": emotion_analysis
        }
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"Emotion analysis failed: {e}"]
        }