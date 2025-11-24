
from config.settings import (
    LLM_PROVIDER,
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
)


def get_llm(temperature=0.7, model=None):
    
    provider = LLM_PROVIDER.lower()
    
    if provider == "openai":
        return _get_openai_llm(temperature, model)
    elif provider == "google":
        return _get_google_llm(temperature, model)
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}. Use: openai, google")


def _get_openai_llm(temperature, model):
    """OpenAI GPT models"""
    from langchain_openai import ChatOpenAI
    
    if model is None:
        model = "gpt-4o-mini"  # Cheaper default
    
    return ChatOpenAI(
        model=model,
        temperature=temperature,
        api_key=OPENAI_API_KEY
    )

def _get_google_llm(temperature, model):
    """
    Google Gemini models (FREE!)
    """
    from langchain_google_genai import ChatGoogleGenerativeAI
    
    if model is None:
        model = "models/gemini-2.5-flash"  # FREE and fast
    
    return ChatGoogleGenerativeAI(
        model=model,
        temperature=temperature,
        google_api_key=GOOGLE_API_KEY,
        convert_system_message_to_human=True
    )